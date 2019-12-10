from ucipclient import UcipClient

if __name__ == '__main__':
    ucip = UcipClient('10.100.2.179:83', 'gprs_bundle', 'gprs+2012')
    ucip.connect()
    #r = ucip.set_offer('966601923', 317)
    #print(r)
    #r = ucip.delete_offer('966601923', 317)
    #print(r)
    # r = ucip.update_da_balance('966601923', 86, 100, '20191215T23:59:59')
    # print(r)
    # r = ucip.get_balance_date('966601923', 86)
    # print(r)
    r = ucip.update_tempblock('966601923', False)
    print(r)