# Author: Everaldo Ailton Sariot Menout
# Description: UCIP client to connect to AIR using xml over RPC
# License: Public Domain

import xmlrpc.client as client
import http.client
import base64
import datetime
import time
import os
from requests.exceptions import ConnectionError


class UcipClient:

    def __init__(self, hostport, username, password):
        credential = f'{username}:{password}'
        auth =  base64.standard_b64encode(credential.encode())
        self.hostport = hostport
        self.username = username
        self.password = password
        self.rpcserver = None
        self.headers = {"Host": self.hostport, "User-Agent": "GPRSBUNDLE/4.0/1.0", "Content-type": "text/xml; charset=\"UTF-8\"", "Content-length": 0, "Connection": "Close", "Authorization":"Basic %s" % auth}


    def connect(self):
        if self.rpcserver == None:
            try:
                self.rpcserver = http.client.HTTPConnection(self.hostport, timeout=25)
            except http.client.HTTPException as e:
                print(e)
        
        

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
        response = None
        try:
            xml_request = client.dumps( (params,), method )
            #print(params)
            self.headers['Content-length'] = len(xml_request)
            self.rpcserver.request("POST","/Air", "", self.headers)
            self.rpcserver.send(xml_request.encode())
            rpc_response = self.rpcserver.getresponse()
            xml_response = rpc_response.read()
            response = client.loads(xml_response)
        except client.Fault as e:
            print("There is an error. FaultError: {}, FaultString: {}".format(e.faultCode, e.faultString))
        return response


    def get_balance_date(self, subno, ded_account_id=2):
        dict_response = {'response':-100, 'subno':subno}
        isodatetimetime = client.DateTime(time.time())
        transdate = client.DateTime(str(isodatetimetime) +  '+0000')
        params =  {"originNodeType": "EXT", "originHostName":"SHAREDACCOUNT", "originTransactionID":"123455", "originTimeStamp":transdate,
            "subscriberNumberNAI":2, "subscriberNumber": subno}
        res = self.run_rpc_command(params, 'GetBalanceAndDate')
        response_code = res[0][0]['responseCode']
        dict_response['response'] = response_code
        if response_code == 0 :
            dict_response['ma'] =  int(res[0][0]['accountValue1'])/100
            davalue =  self.get_da_amount2(res[0][0]['dedicatedAccountInformation'], ded_account_id)
            dict_response['da'] = int(davalue)
        return dict_response
    

    def update_balance_date(self, subno, amount, isabsolute=False):
        if type(amount) != float and type(amount) != int:
            raise ValueError("amount should be an int or float. A string was passed instead.")
        amount = round(amount*100)
        isodatetimetime = client.DateTime(time.time())
        transdate = client.DateTime(str(isodatetimetime) +  '+0000')
        parameters =  {"originNodeType": "EXT", "originHostName":"SHAREDACCOUNT", "originTransactionID":"123455", "originTimeStamp":transdate,
            "subscriberNumberNAI":2, "subscriberNumber": subno, "transactionCurrency": "CFA"}
        if isabsolute:
            parameters['mainAccountValueNew'] = str(amount)
        else:
            parameters['adjustmentAmountRelative'] = str(amount)
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
        response_code = res[0][0]['responseCode']
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
        response_code = res[0][0]['responseCode']
        dict_response['response'] = response_code
        offers = []
        offer_type = - 1
        if response_code == 0 :
            if 'offerInformation' in res[0][0]:
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
        dict_response['response'] = res[0][0]['responseCode']
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
        dict_response['response'] = res[0][0]['responseCode']
        return dict_response
    
    
    def update_tempblock(self, subno, flag=True):
        dict_response = {'response':-100, 'subno':subno}
        isodatetime = client.DateTime(time.time())
        transdate = client.DateTime(str(isodatetime) +  '+0000')
        parameters =  {"originNodeType": "EXT", "originHostName":"SHAREDACCOUNT", "originTransactionID":"123455", "originTimeStamp":transdate,
            "subscriberNumberNAI":2, "subscriberNumber": subno, 'temporaryBlockedFlag': flag}
        res = self.run_rpc_command(parameters, 'UpdateTemporaryBlocked')
        
        dict_response['response'] = res[0][0]['responseCode']
        return dict_response

    def delete_all_offers(self, subno):
        offer_dict = self.get_offers(subno)
        result = -1
        for offer in offer_dict['offers']:
            result = self.delete_offer(offer_dict['subno'], offer['offerId'])
            print("subno ={} , offerID={} , offerType={} - responseCode={}".format(offer_dict['subno'], offer['offerId'], offer['offerType'], result['response']))
        
    
    def install_subscriber_sdp(self, subno, serv_class, is_blocked):
        dict_response = {'response':-100, 'subno':subno}
        isodatetime = client.DateTime(time.time())
        transdate = client.DateTime(str(isodatetime) +  '+0000')
        parameters =  {"originNodeType": "EXT", "originHostName":"SHAREDACCOUNT", "originTransactionID":"123455", "originTimeStamp":transdate,
            "subscriberNumberNAI":2, "subscriberNumber": subno, "originOperatorID":"EveraldoMenout", "serviceClassNew": serv_class , 'temporaryBlockedFlag': is_blocked}
        res = self.run_rpc_command(parameters, 'InstallSubscriber')
        dict_response['response'] = res[0][0]['responseCode']
        return dict_response
    

    def delete_subscriber_sdp(self, subno):
        dict_response = {'response':-100, 'subno':subno}
        isodatetime = client.DateTime(time.time())
        transdate = client.DateTime(str(isodatetime) +  '+0000')
        parameters =  {"originNodeType": "EXT", "originHostName":"SHAREDACCOUNT", "originTransactionID":"123455", "originTimeStamp":transdate,
            "subscriberNumberNAI":2, "subscriberNumber": subno, "originOperatorID":"EveraldoMenout"}
        res = self.run_rpc_command(parameters, 'DeleteSubscriber')
        dict_response['response'] = res[0][0]['responseCode']
        return dict_response

    