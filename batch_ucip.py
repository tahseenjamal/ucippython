import ucipclient

def get_numbers():
    fp = open('C:\\Users\\emenout\\Desktop\\temp\\list.txt' , 'r')
    lines = fp.readlines()
    mylist = []
    for line in lines:
        #print(line.strip())
        mylist.append(line.strip())
    fp.close()
    return mylist



if __name__ == '__main__':
    numbers = get_numbers()
    ucip = ucipclient.UcipClient('10.100.2.179:83', 'gprs_bundle', 'gprs+2012')
    ucip.connect()
    print (ucip.set_offer('966363636', 645, 2, '20200110T23:59:59'))
    # res = None
    # for msisdn in numbers:
    #     r = ucip.install_subscriber_sdp(msisdn, 400, False)
    #     print(r)
    

