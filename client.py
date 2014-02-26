import logging
import os
import pprint
from pythonzimbra.tools import auth
from pythonzimbra.request_xml import RequestXml
from pythonzimbra.response_xml import ResponseXml
from pythonzimbra.communication import Communication

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

url = os.environ['ZIMBRA_URL']
account = os.environ['ZIMBRA_ACCOUNT']
password = os.environ['ZIMBRA_PASSWORD']
preauthkey = os.environ['ZIMBRA_PREAUTHKEY']

comm = None
token = None

def connect():
    global comm
    global token
    comm = Communication(url)
    token = auth.authenticate(
        url,
        account,
        password,
        admin_auth=True,
    )
    if not token:
        raise Exception("Authentication failed")

def getalladminaccounts():
    request = RequestXml()
    request.add_request('GetAllAdminAccountsRequest', {}, 'urn:zimbraAdmin')
    request.set_auth_token(token)
    log.debug("request = %s", request.get_request())

    response = ResponseXml()
    comm.send_request(request, response)
    if response.is_fault():
        raise Exception("response is fault")
    info = response.get_response()
    accounts = info['GetAllAdminAccountsResponse']['account']
    pprint.pprint([a['name'] for a in accounts])
    
def getallaccounts():
    request = RequestXml()
    params = { 'server': { 'by': 'name', '_content': 'collaboration.devnet.imsa.edu' } }
    request.add_request('GetAllAccountsRequest', params,'urn:zimbraAdmin')
    request.set_auth_token(token)
    log.debug("request = %s", request.get_request())
    response = ResponseXml()
    comm.send_request(request, response)
    if response.is_fault():
        raise Exception("response is fault")
    info = response.get_response()
    accounts = info['GetAllAccountsResponse']['account']
    pprint.pprint([account['name'] for account in accounts])
    for account in accounts:
        if account['name'].startswith('fcy@'):
            pprint.pprint(account)
            break
    
def getallservers():
    request = RequestXml()
    request.add_request('GetAllServersRequest', {}, 'urn:zimbraAdmin')
    request.set_auth_token(token)
    log.debug("request = %s", request.get_request())

    response = ResponseXml()
    comm.send_request(request, response)
    if response.is_fault():
        raise Exception("response is fault")
    info = response.get_response()
    pprint.pprint(info['GetAllServersResponse']['server']['name'])
    
def getallcalendarresources():
    request = RequestXml()
    request.add_request('GetAllCalendarResourcesRequest', {'attrs':'sn'}, 'urn:zimbraAdmin')
    request.set_auth_token(token)
    log.debug("request = %s", request.get_request())

    response = ResponseXml()
    comm.send_request(request, response)
    if response.is_fault():
        raise Exception("response is fault")
    info = response.get_response()
    cals = info['GetAllCalendarResourcesResponse']['calresource']
    pprint.pprint([cal['name'] for cal in cals])
    for cal in cals:
        pprint.pprint(cal['a'])
        break

def getallmailboxes():
    request = RequestXml()
    request.add_request('GetAllMailboxesRequest', {'limit':0}, 'urn:zimbraAdmin')
    request.set_auth_token(token)
    log.debug("request = %s", request.get_request())

    response = ResponseXml()
    comm.send_request(request, response)
    if response.is_fault():
        raise Exception("response is fault")
    info = response.get_response()
    mboxes = info['GetAllMailboxesResponse']['mbox']
    return mboxes

def getmailbox(accountid):
    request = RequestXml()
    params = {'mbox': {'id': accountid}}
    request.add_request('GetMailboxRequest', params, 'urn:zimbraAdmin')
    request.set_auth_token(token)
    log.debug("request = %s", request.get_request())

    response = ResponseXml()
    comm.send_request(request, response)
    if response.is_fault():
        raise Exception("response is fault")
    info = response.get_response()
    mbox = info['GetMailboxResponse']['mbox']
    return mbox

def getcalendarresource():
    request = RequestXml()
    params = { 'calresource': { '_content': 'itsconfroom@devnet.imsa.edu', 'by': 'name' },
               'attrs': 'sn,zimbraId',
    }
    request.add_request('GetCalendarResourceRequest', params, 'urn:zimbraAdmin')
    request.set_auth_token(token)
    log.debug("request = %s", request.get_request())

    response = ResponseXml()
    comm.send_request(request, response)
    if response.is_fault():
        raise Exception("response is fault")
    info = response.get_response()
    pprint.pprint(info)

def main():
    connect()
    #getallservers()
    #getallaccounts()
    #getallcalendarresources()
    #getcalendarresource()
    mboxes = getallmailboxes()
    for mbox in mboxes[100:101]:
        mailbox = getmailbox(mbox['accountId'])
        pprint.pprint(mailbox)

if __name__ == "__main__":
    main()
