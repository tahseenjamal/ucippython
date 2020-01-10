import zeep
from zeep import xsd

wsdl = 'http://10.195.5.7:8998/cai3g1_2/Provisioning/?wsdl'
client = zeep.Client(wsdl=wsdl)
#print(client.service.Method1('Zeep', 'is cool'))

order_type = client.get_type('ns0:AnyMOIdType')
print(order_type)
el = client.get_element('ns0:CreateMODefinition')
dir(el)

# factory = client.type_factory('ns0')
# dir(factory)

# AnyMOIdType  = order_type(_value_1="cai3g")
# print(AnyMOIdType)
# MOType =  xsd.Element('Username', xsd.String())
# print('teste', MOType)
#Create(MOType: xsd:string, MOId: ns0:AnyMOIdType, MOAttributes: ns0:CreateMODefinition, extension: ns0:AnySequenceType, _soapheaders={SessionId: xsd:string, TransactionId: xsd:string, SequenceId: xsd:integer})


#Create(MOType: xsd:string, MOId: ns0:AnyMOIdType, MOAttributes: ns0:CreateMODefinition, extension: ns0:AnySequenceType, _soapheaders={SessionId: xsd:string, TransactionId: xsd:string, SequenceId: xsd:integer})

# from zeep import Client
# from zeep import xsd
# from zeep.plugins import HistoryPlugin
# import lxml.etree as etree

# wsdl = 'http://localhost/services/Assets?wsdl'
# history = HistoryPlugin()
# client = Client(wsdl, plugins=[history])
# credentialType = client.get_type('ns0:UserCredentialsType')
# credentials = credentialType(Username='user', Password='passwortd')
# credentialTest = { 'UserCredentials': { 'Username':'user', 'Password':'password'}} 
# param = client.get_type('ns0:GetChildrenType')
# params = param(InterplayURI='uri') 
# header = xsd.ComplexType([
#     xsd.Sequence([
#         xsd.Element('Username', xsd.String()),
#         xsd.Element('Password', xsd.String())
#         ])
#     ])
# header_value = header(Username='user', Password='password')
# response = client.create_message(client.service, 'GetChildren', params, _soapheaders=[credentials])
# request = etree.tostring(response)
# serverResponse = client.service.GetChildren(request)
# print(request)
# print(serverResponse