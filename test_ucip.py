from ucipclient import UcipClient

if __name__ == '__main__':
    ucip = UcipClient('10.100.2.179:83', 'gprs_bundle', 'gprs+2012')
    ucip.connect()
    nums = ['966601924','966601771','966601923','966601471']
    #nums = ['966601924']
    print('Starting...')
    #r = ucip.update_balance_date('966601924', 100)
    #print(f'Response Code = {r}')
    for s in nums:
        print(ucip.get_balance_date(s, 5))
