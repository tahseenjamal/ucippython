from ucipclient import UcipClient


def check_offer():
    count = 0
    ucip = UcipClient('10.100.2.179:83', 'gprs_bundle', 'gprs+2012')
    ucip.connect()
    with open("c:\\temp\\offerlist.txt") as fp:
        subscriber = fp.readline().strip()
        while subscriber:
            #print("subs = '{}'".format(subscriber))
            r = ucip.get_offers(subscriber)
            #if list of offers is not empty
            if r['offers']:
                print("==> {} has offer {}".format(subscriber, r['offers']) )
            count += 1
            subscriber = fp.readline().strip()
    print(count)

if __name__ == '__main__':
    ucip = UcipClient('10.100.2.179:83', 'gprs_bundle', 'gprs+2012')
    ucip.connect()
    #r = ucip.get_balance_date('966601471')
    #print(r)
    numbers = ['966601202', '966601203', '966601208', '966601215']
    for subno in numbers:
        r  = ucip.get_offers(subno)
        print(r)
    # r = ucip.set_offer('966601923', 317)
    # print(r)
    # r = ucip.delete_offer('966601923', 317)
    # print(r)
    # r = ucip.update_da_balance('966601923', 86, 100, '20191215T23:59:59')
    # print(r)
    # r = ucip.update_balance_date('966601923', 100)
    # print(r)
    # r = ucip.update_da_balance('966601923', 86, 100)
    # print(r)
    # r = ucip.get_balance_date('966601923', 86)
    # print(r)
    # r = ucip.update_tempblock('966601923', False)
    # print(r)
    #ucip.delete_all_offers('966601423')
    #numbers = ['966273333']
    #numbers = ['966171396']
    # for num in numbers:
    #     #r = ucip.update_balance_date(num, 100, True)
    #     r = ucip.get_balance_date(num)
    #     print('MA = ', r['ma'])
    #     #rr = ucip.update_balance_date(r['subno'], - r['ma'], False)
    #     #print(rr)
    #numbers = ['966179165', '966179148', '965200415', '966601230']
    # for subno in numbers:
    #     r = ucip.install_subscriber_sdp(subno, 301, True)
    #     print(r)
    # for subno in numbers:
    #     r = ucip.update_tempblock(subno, False)
    #     print(r)
    #r = ucip.install_subscriber_sdp('966000000', 301, True)
    #r = ucip.delete_subscriber_sdp('966000000')
    #print(r)
    #check_offer()