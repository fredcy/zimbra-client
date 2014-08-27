import logging
import os
import pprint
import json
import argparse
import urllib2
# github.com/Zimbra-Community/python-zimbra
from pythonzimbra.tools import auth
from pythonzimbra.request_xml import RequestXml
from pythonzimbra.response_xml import ResponseXml
from pythonzimbra.communication import Communication

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

class Zimbra():
    def __init__(self):
        self.comm = None
        self.token = None

    def connect(self):
        url = os.environ['ZIMBRA_URL']
        account = os.environ['ZIMBRA_ACCOUNT']
        password = os.environ['ZIMBRA_PASSWORD']
        try:
            self.comm = Communication(url)
            self.token = auth.authenticate(url, account, password, admin_auth=True)
        except:
            log.exception("locals=%s", locals())
        if not self.token:
            raise Exception("Authentication failed: locals=%s", locals())

    def request(self, request_name, params=None, context=None):
        request = RequestXml()
        try:
            urn = 'urn:zimbraAccount' if context and 'account' in context else 'urn:zimbraAdmin'
            request.add_request(request_name, params or {}, urn)
            if context:
                request.set_context_params(context)
            request.set_auth_token(self.token)
        except:
            log.exception("failed to build request: request_name=%s, params=%s, context=%s",
                          request_name, params, context)
            return None
        log.debug("request = %s", request.get_request())

        response = ResponseXml()
        try:
            self.comm.send_request(request, response)
        except urllib2.HTTPError as e:
            log.error("send_request HTTP Error %s: %s; request=%s",
                          e.code, e.reason, request.get_request())
            return None
        except Exception as e:
            log.exception("send_request failed (%s): request=%s", type(e), request.get_request())
            return None
        if response.is_fault():
            log.error("send_request returned fault: request=%s", request.get_request())
            return None
        info = response.get_response()
        return info

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
    try:
        comm.send_request(request, response)
    except:
        log.exception("send_request failed: request=%s", request.get_request())
        return none
    if response.is_fault():
        raise Exception("response is fault")
    info = response.get_response()
    pprint.pprint(info)

def main():
    parser = argparse.ArgumentParser(description="Make Zimbra SOAP requests")
    parser.add_argument('request', help='Name of request')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--account', help='Account name for context')
    parser.add_argument('--params', help='Parameters of request')
    parser.add_argument('--depth', type=int,  default=None, help='Depth of structure prints')
    args = parser.parse_args()

    log.setLevel(logging.DEBUG if args.debug else logging.INFO)

    z = Zimbra()
    z.connect()

    context = { 'account': { '_content': args.account, 'by': 'name' } } if args.account else None
    request_name = args.request if args.request.endswith('Request') else args.request + 'Request'
    params = json.loads(args.params) if args.params else None
    pprint.pprint(z.request(request_name, params=params, context=context), depth=args.depth)

if __name__ == "__main__":
    main()
