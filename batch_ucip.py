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
    res = None
    for msisdn in numbers:
        r = ucip.install_subscriber_sdp(msisdn, 400, False)
        print(r)

