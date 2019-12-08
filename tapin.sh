#!/usr/bin/python

from ftplib import FTP
import glob
import os
import MySQLdb
import time
import shutil
import re
import Logger
import subprocess

def logdb(full_filename, db):
    t = os.stat(full_filename)
    creation_date = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(t.st_mtime))
    file_size = t.st_size
    file_name = os.path.basename(full_filename)
    operator_code = file_name[2:7]
    current_date = time.strftime("%Y-%m-%d %H:%M:%S")
    cursor = db.cursor()
    sql = "INSERT INTO tapin (file_name, creation_date, processed_date, file_size, operator) VALUES ('%s', '%s', '%s', %d, '%s' )" % (file_name, creation_date, current_date, file_size, operator_code)
    try:
       # Execute the SQL command
       cursor.execute(sql)
       # Commit your changes in the database
       db.commit()
    except:
       # Rollback in case there is any error
       db.rollback()

    

def moveTapin2Temp():
   cdfiles = glob.glob('/var/www/nextgen/TAP_IN/[CT]D*')
   refile = re.compile('^([^.]+)$') # files without extension, to skip .tmp files
   cdfiles = [f for f in cdfiles if refile.findall(f)]
   destination = '/opt/tap/nextgen/temp/tapin'
   for file in cdfiles:
      print "Moving " + file + " ==> " + destination
      shutil.move(file, destination)
     
	
def moveFiles(regex_files, to_folder):
   cdfiles = glob.glob(regex_files)
   for file in cdfiles:
      print "Moving " + file + " to " + to_folder
      shutil.move(file, to_folder)
     

def send_ra_tapin():
    print 'Sending file to RA'
    ftp = FTP('10.195.3.131')
    ftp.login('mtnftp', 'mtnftp')
    ftp.cwd('/rocra_polled/Polled/tapin')
    cdfiles = glob.glob('/opt/tap/nextgen/temp/tapin/CD*')
    for cdfile in cdfiles:
        myfile = open(cdfile, 'rb')
        filename = os.path.basename(cdfile);
	print "sending: " + filename
        ftp.storbinary('STOR ' + filename, myfile)
        myfile.close()
    ftp.quit()


# Send files to tabs
def processTapin():
    ''' Send files to NextGen server '''
    # Move first the files to temp, and then take them from temp folder and send it to tabs
    log = Logger.Logger('/opt/tap/logs/tapin.log')
    log.write('--- TAPIN process started ---')    
    ftp = FTP('10.194.3.204')
    ftp.login('tabs', 'tabs')
    ftp.cwd('/tabs/cdrs/roam/tap3/tap3_in')
    cdfiles = glob.glob('/opt/tap/nextgen/temp/tapin/CD*')
    # Connect to database, in order to log files processed
    db = MySQLdb.connect("localhost","root","eves1981","tap" )
    for cdfile in cdfiles:
        ### BEGIN no need to send TD files to TABS to process. Only CD files ####
        tapfile = os.path.basename(cdfile)
        if tapfile.startswith('TD'):
            logdb(cdfile,db)
	    print "[!] TD file found. It will not be sent."
            continue
	### END ####
        myfile = open(cdfile, 'rb')
        filename = os.path.basename(cdfile)
	print "Sending: " + filename
        ftp.storbinary('STOR ' + filename, myfile)
	#log the operation in the database
        logdb(cdfile, db)
        myfile.close()
    ftp.quit()
    db.close()
    log.write('--- TAPIN processing finish')
    log.close()
    # Send the same tapin files to RA
    #send_ra_tapin()
    subprocess.call(['/opt/tap/ftptapin.sh'])
    # Move CD files on TEMP folder to archive
    moveFiles('/opt/tap/nextgen/temp/tapin/[CT]D*', '/opt/tap/nextgen/archive/tapin')

############# MAIN #################
if __name__ == '__main__':
   moveTapin2Temp();   
   processTapin();
   subprocess.call(['/opt/tap/ftptapin.sh'])


