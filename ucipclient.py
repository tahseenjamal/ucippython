import xmlrpc.client as client
import http.client
import base64
import datetime
import time


class UcipClient:

    def __init__(self, host, username, password):
        credential = f'{username}:{password}'
        auth =  base64.standard_b64encode(credential.encode())
        self.host = host
        self.username = username
        self.password = password
        self.rpcserver = None
        self.headers = {"Host": "10.100.2.179:83", "User-Agent": "GPRSBUNDLE/4.0/1.0", "Content-type": "text/xml; charset=\"UTF-8\"", "Content-length": 0, "Connection": "Close", "Authorization":"Basic %s" % auth}


    def connect(self):
        if self.rpcserver == None:
            self.rpcserver = http.client.HTTPConnection("10.100.2.179:83")


    def get_da_amount(self, das, daid):
        for da in das:
            if da['dedicatedAccountID'] == daid:
                return int(da['dedicatedAccountValue1'])/100
        return -1


    def get_da_amount2(self, das, daid):
        """
        This method return the amount for a DAID given. It is implement binary search to search on List of DA object
        The method used is very versatil consuming only log(n). However, the list should be sorted previously.

        """
        final = len(das) - 1
        begin = 0
        elem = -1
        found = False
        #print('Length : ', final)
        while begin <= final and not found:
            index = (begin + final) // 2
            if int(das[index]['dedicatedAccountID']) == daid:
                found = True
                elem = int(das[index]['dedicatedAccountValue1'])/100
            elif  daid < int(das[index]['dedicatedAccountID']):
                final = index - 1
            else:
                begin = index + 1
        return elem
    

    def run_rpc_command(self, params, method):
        xml_request = client.dumps( (params,), method )
        self.headers['Content-length'] = len(xml_request)
        self.rpcserver.request("POST","/Air", "", self.headers)
        self.rpcserver.send(xml_request.encode())
        rpc_response = self.rpcserver.getresponse()
        xml_response = rpc_response.read()
        response = client.loads(xml_response)
        return response


    def get_balance_date(self, subno, ded_account_id=2):
        dict_response = {'response':-100, 'subno':subno}
        isodatetimetime = client.DateTime(time.time())
        transdate = client.DateTime(str(isodatetimetime) +  '+0000')
        params =  {"originNodeType": "EXT", "originHostName":"SHAREDACCOUNT", "originTransactionID":"123455", "originTimeStamp":transdate,
            "subscriberNumberNAI":2, "subscriberNumber": subno}
        res = self.run_rpc_command(params, 'GetBalanceAndDate')
        response_code = int(res[0][0]['responseCode'])
        dict_response['response'] = response_code
        if response_code == 0 :
            dict_response['ma'] =  int(res[0][0]['accountValue1'])/100
            davalue =  self.get_da_amount2(res[0][0]['dedicatedAccountInformation'], ded_account_id)
            dict_response['da'] = int(davalue)
        return dict_response
    

    def update_balance_date(self, subno, amount):
        amount = amount * 100
        isodatetimetime = client.DateTime(time.time())
        transdate = client.DateTime(str(isodatetimetime) +  '+0000')
        parameters =  {"originNodeType": "EXT", "originHostName":"SHAREDACCOUNT", "originTransactionID":"123455", "originTimeStamp":transdate,
            "subscriberNumberNAI":2, "subscriberNumber": subno, "adjustmentAmountRelative": str(amount), "transactionCurrency": "CFA"}
        res = self.run_rpc_command(parameters, 'UpdateBalanceAndDate')
        return res[0][0]['responseCode']
    

    def update_da_balance(self, subno, daid, amount, expiry_date=None):
        amount = amount * 100
        isodatetimetime = client.DateTime(time.time())
        transdate = client.DateTime(str(isodatetimetime) +  '+0000')   
        dedicated_account = {'dedicatedAccountID':daid, 'adjustmentAmountRelative': str(amount)}
        if expiry_date != None:
            exp_date = client.DateTime(expiry_date  + '+0000')
            dedicated_account['expiryDate'] = exp_date
        dalist = [dedicated_account]
        parameters =  {"originNodeType": "EXT", "originHostName":"SHAREDACCOUNT", "originTransactionID":"123455", "originTimeStamp":transdate,
            "subscriberNumberNAI":2, "subscriberNumber": subno, "transactionCurrency": "CFA",'dedicatedAccountUpdateInformation': dalist}
        res = self.run_rpc_command(parameters, 'UpdateBalanceAndDate')
        return res[0][0]['responseCode']


    def get_user_details(self, subno):
        dict_response = {'response':-100, 'subno':subno}
        isodatetimetime = client.DateTime(time.time())
        transdate = client.DateTime(str(isodatetimetime) +  '+0000')
        parameters =  {"originNodeType": "EXT", "originHostName":"SHAREDACCOUNT", "originTransactionID":"123455", "originTimeStamp":transdate,
            "subscriberNumberNAI":2, "subscriberNumber": subno}
        res = self.run_rpc_command(parameters, 'GetAccountDetails')
        response_code = int(res[0][0]['responseCode'])
        dict_response['response'] = response_code
        if response_code == 0 :
            dict_response['sc'] = res[0][0]['serviceClassCurrent']
            dict_response['languageId'] = res[0][0]['languageIDCurrent']
            dict_response['isActive'] = res[0][0]['accountFlags']['activationStatusFlag']
            if (dict_response['isActive']):
                dict_response['activationDate'] = res[0][0]['activationDate']
        return dict_response

    
    def get_offers(self, subno):
        dict_response = {'response':-100, 'subno':subno}
        isodatetime = client.DateTime(time.time())
        transdate = client.DateTime(str(isodatetime) +  '+0000')
        parameters =  {"originNodeType": "EXT", "originHostName":"SHAREDACCOUNT", "originTransactionID":"123455", "originTimeStamp":transdate,
            "offerRequestedTypeFlag": "11111111", "subscriberNumberNAI":2, "subscriberNumber": subno}
        self.headers['User-Agent'] = 'GPRSBUNDLE/4.2/1.0'
        res = self.run_rpc_command(parameters, 'GetOffers')
        self.headers['User-Agent'] = 'GPRSBUNDLE/4.0/1.0' # Turn to default
        response_code = int(res[0][0]['responseCode'])
        dict_response['response'] = response_code
        offers = []
        offer_type = - 1
        if response_code == 0 :
            for offer in res[0][0]['offerInformation']:
                dict_offers = {}
                offer_type = offer['offerType']
                dict_offers['offerType'] =  offer_type
                dict_offers['offerId'] =  offer['offerID']
                if offer_type == 2:
                    dict_offers['startDate'] =  offer['startDateTime']
                    dict_offers['expiryDate'] =  offer['expiryDateTime']
                else:
                    dict_offers['startDate'] =  offer['startDate']
                    dict_offers['expiryDate'] =  offer['expiryDate']
                offers.append(dict_offers)
        dict_response['offers'] = offers
        return dict_response

    
    def set_offer(self, subno, offer_id, offer_type=0, expiry_date=None):
        dict_response = {'response':-100, 'subno':subno}
        isodatetime = client.DateTime(time.time())
        transdate = client.DateTime(str(isodatetime) +  '+0000')
        parameters =  {"originNodeType": "EXT", "originHostName":"SHAREDACCOUNT", "originTransactionID":"123455", "originTimeStamp":transdate, "subscriberNumberNAI":2, "subscriberNumber": subno, "offerID": offer_id, "offerType":offer_type}
        if expiry_date != None:
            if offer_type == 0:
                parameters['expiryDate'] = client.DateTime(expiry_date + '+0000')
            else:
                parameters['expiryDateTime'] = client.DateTime(expiry_date  + '+0000')
        self.headers['User-Agent'] = 'GPRSBUNDLE/4.2/1.0'
        res = self.run_rpc_command(parameters, 'UpdateOffer')
        self.headers['User-Agent'] = 'GPRSBUNDLE/4.0/1.0' # Turn to default
        response_code = int(res[0][0]['responseCode'])
        dict_response['response'] = response_code
        return dict_response
    
    
    def delete_offer(self, subno, offer_id):
        dict_response = {'response':-100, 'subno':subno}
        isodatetime = client.DateTime(time.time())
        transdate = client.DateTime(str(isodatetime) +  '+0000')
        parameters =  {"originNodeType": "EXT", "originHostName":"SHAREDACCOUNT", "originTransactionID":"123455", "originTimeStamp":transdate,
            "subscriberNumberNAI":2, "subscriberNumber": subno, "offerID": offer_id}
        self.headers['User-Agent'] = 'GPRSBUNDLE/4.2/1.0'
        res = self.run_rpc_command(parameters, 'DeleteOffer')
        self.headers['User-Agent'] = 'GPRSBUNDLE/4.0/1.0' # Turn to default
        response_code = int(res[0][0]['responseCode'])
        dict_response['response'] = response_code
        return dict_response
    
    
    def update_tempblock(self, subno, flag=True):
        dict_response = {'response':-100, 'subno':subno}
        isodatetime = client.DateTime(time.time())
        transdate = client.DateTime(str(isodatetime) +  '+0000')
        parameters =  {"originNodeType": "EXT", "originHostName":"SHAREDACCOUNT", "originTransactionID":"123455", "originTimeStamp":transdate,
            "subscriberNumberNAI":2, "subscriberNumber": subno, 'temporaryBlockedFlag': flag}
        res = self.run_rpc_command(parameters, 'UpdateTemporaryBlocked')
        dict_response['response'] = int(res[0][0]['responseCode'])
        return dict_response

