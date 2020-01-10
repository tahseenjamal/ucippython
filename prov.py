import argparse
import ucipclient
import sys

parser = argparse.ArgumentParser()
# Add the arguments to the parser
parser.add_argument("-m", "--method_id", type=int, required=False,
   help="first operand")
parser.add_argument("-p", "--parameters", required=False,
   help="second operand")
parser.add_argument("-l", action='store_true', help="List methods")
args = vars (parser.parse_args())

if  (not args['method_id'] and args['parameters']) or (args['method_id'] and not args['parameters']):
     parser.error('The - [method_id] and [parameters] should be provided')

if (args['l'] == True):
     print("\tMethods:")
     print("1 - Get_User_Details(subno)    ==> prov.py -m 1 -p subno")
     print("2 - Get_Offers                 ==> prov.py -m 2 -p subno")
     print("3 - Get_Balance_Date           ==> prov.py -m 3 -p subno,da_id")
     print("4 - Update_Balance_date        ==> prov.py -m 4 -p subno,amount")
     print("5 - Update_Balance_DA          ==> prov.py -m 5 -p subno,da_id,da_amount")
     print("6 - Set_Offer                  ==> prov.py -m 6 -p subno,offer_id")
     print("                                   prov.py -m 6 -p subno,offer_id,expirydate")
     print("                                   expirydate format is YYYYMMDDThh:mm:ss (e.g 20191215T23:59:59)")
     sys.exit(0)
ucip = ucipclient.UcipClient('10.100.2.179:83', 'gprs_bundle', 'gprs+2012')
ucip.connect()
method_id = args['method_id']
params = args['parameters'].split(",")
if method_id == 1:
     print(ucip.get_user_details(params[0]))
elif method_id == 2:
    print(ucip.get_offers(params[0]))
elif method_id == 3:
    print(ucip.get_balance_date(params[0], int(params[1])))
elif method_id == 4:
    print(ucip.update_balance_date(params[0], int(params[1])))
elif method_id == 5:
    print(ucip.update_da_balance(params[0], int(params[1]), int(params[2])))
elif method_id == 6:
    len_args = len(params)
    if len_args == 2:
        print(ucip.set_offer(params[0], int(params[1])))
    elif len_args == 3:
        print(ucip.set_offer(params[0], int(params[1]), 0, params[2]))
    else:
        print('Parameter syntax error: ', args['parameters'])
else:
     print('Unknown method id: ', method_id)
