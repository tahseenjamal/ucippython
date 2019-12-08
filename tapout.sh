#!/usr/bin/python

import ftplib
import glob
import os
import MySQLdb
import time
import shutil
import re
import Logger
#log = None

def logdb(full_filename, db):
    t = os.stat(full_filename)
    creation_date = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(t.st_mtime))
    file_size = t.st_size
    file_name = os.path.basename(full_filename)
    current_date = time.strftime("%Y-%m-%d %H:%M:%S")
    roaming_operator = file_name[7:12]
    cursor = db.cursor()
    sql = "INSERT INTO tapout (file_name, creation_date, processed_date, file_size, operator) VALUES ('%s', '%s', '%s', %d , '%s')" % (file_name, creation_date, current_date, file_size, roaming_operator)
    try:
       # Execute the SQL command
       cursor.execute(sql)
       # Commit your changes in the database
       db.commit()
    except:
       # Rollback in case there is any error
       db.rollback()

def moveFiles(files, to_folder):
   cdfiles = glob.glob(files)
   for i in cdfiles:
      filename = os.path.basename(i)
      print "Moving " + i + " to " + to_folder
      shutil.move(i, os.path.join(to_folder, filename))
	
def processTapout():

    #initiate loggger
    log = Logger.Logger('/opt/tap/logs/tapout.log')
    log.write('--- TAPOUT Process started ---')
    #send files to nextgen
    try:
        ftp = ftplib.FTP('83.136.0.83')
        ftp.login('gnbsb', 'AMBb8Uv01')
        ftp.cwd('/TAP/TAPOUT')

        #Connect to database
        dbo = MySQLdb.connect("localhost","root","eves1981","tap" )
        # TABS push CD files to this directory
        cdfiles = glob.glob('/var/www/flipmode/TAP_OUT/[CT]D*')
        for cdfile in cdfiles:
            myfile = open(cdfile, 'rb')
            filename = os.path.basename(cdfile)
	    tempfile = filename + '.tmp'
	    print "Sending file: " + cdfile
            store = ftp.storbinary('STOR ' + tempfile, myfile)
	    if store != '226 Transfer complete.':
	        log.write(filename + ' not transfered due the error')
	    else:
                rename = ftp.rename(tempfile, filename)
                if rename != '250 Rename successful.':
		    log.write(tempfile + ' not renamed to ' + filename)
	        logdb(cdfile,dbo)
            myfile.close()
        ftp.quit()
        dbo.close()
    except ftplib.all_errors as e:
        log.write("FTP fail: " + str(e))
        log.close()
        return
    log.write('--- TAPOUT Process finished ---')
    log.close()
    #move to achive folder
    moveFiles('/var/www/flipmode/TAP_OUT/[CT]D*','/opt/tap/nextgen/archive/tapout')

#Download files
def download(ftpserver):
    ftpserver.cwd('EVE/coco')
    filenames = ftpserver.nlst()
    for filename in filenames:
        local_filename = os.path.join('/home/everaldo/tapfiles', filename)
        file = open(local_filename, 'wb')
        ftpserver.retrbinary('RETR '+ filename, file.write)
        file.close()

if __name__ == '__main__':
   processTapout();
   #moveFiles('/var/www/flipmode/TAP_OUT/CD*','/opt/tap/nextgen/archive/tapout')
