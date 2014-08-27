"""Zimbra client.

Note: This code sometimes uses yaml rather than json to display JSON values for debugging, only
because json displays every string as unicode with "u" prefix.

"""

import logging
import os
import pprint
import json
import argparse
import urllib2
import xml.dom.minidom
import yaml                # install PyYAML via pip
# github.com/Zimbra-Community/python-zimbra
from pythonzimbra.tools import auth
from pythonzimbra.request_json import RequestJson
from pythonzimbra.request_xml import RequestXml
from pythonzimbra.response_json import ResponseJson
from pythonzimbra.response_xml import ResponseXml
from pythonzimbra.communication import Communication

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

request_urn_suffix = {
    'GetInfo': 'Account',

    'GetAppointment': 'Mail',
    'GetFolder': 'Mail',
    'GetMailboxMetadata': 'Mail',
    'Search': 'Mail',
}

def urn_for_request(request_name):
    if request_name.endswith('Request'):
        request_name = request_name[:-len('Request')]
    return 'zimbra' + request_urn_suffix.get(request_name, 'Admin')

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

    def request(self, request_name, params=None, context=None, urn=None, args={}):
        request = RequestJson()
        response = ResponseJson()
        try:
            if urn == None:
                urn = urn_for_request(request_name)
            request.add_request(request_name, params or {}, "urn:"+urn)
            if context:
                request.set_context_params(context)
            request.set_auth_token(self.token)
        except:
            log.exception("failed to build request: request_name=%s, params=%s, context=%s",
                          request_name, params, context)
            return None
        if args.debug:
            if isinstance(request, RequestXml):
                print xml.dom.minidom.parseString(request.get_request()).toprettyxml(indent=".   ")
            else:
                pprint.pprint(yaml.load(request.get_request()))

        try:
            self.comm.send_request(request, response)
        except urllib2.HTTPError as e:
            requestbody = request.get_request()
            responsebody = e.read()
            log.error('''send_request HTTP Error %s: %s; request="%s" response="%s"''',
                          e.code, e.reason, requestbody, responsebody)
            if isinstance(request, RequestXml):
                requestdoc = xml.dom.minidom.parseString(requestbody)
                print "REQUEST=", requestdoc.toprettyxml(indent=".   ")
            else:
                print "REQUEST=\n", pprint.pformat(yaml.load(requestbody))
            if isinstance(response, ResponseXml):
                responsedoc = xml.dom.minidom.parseString(responsebody)
                print "RESPONSE=", responsedoc.toprettyxml(indent=".   ")
            else:
                print "RESPONSE=\n", pprint.pformat(yaml.load(responsebody))
            return None
        except Exception as e:
            log.exception("send_request failed (%s): request=%s", type(e), request.get_request())
            return None
        if response.is_fault():
            log.error("send_request returned fault: request=%s", request.get_request())
            return None
        info = response.get_response()
        return info

def main():
    parser = argparse.ArgumentParser(description="Make Zimbra SOAP requests")
    parser.add_argument('request', help='Name of request')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--account', help='Account name for context')
    parser.add_argument('--params', help='Parameters of request')
    parser.add_argument('--urn', help='URN of request: Admin, Account, etc')
    parser.add_argument('--depth', type=int,  default=None, help='Depth of structure prints')
    args = parser.parse_args()

    log.setLevel(logging.DEBUG if args.debug else logging.INFO)

    z = Zimbra()
    z.connect()

    context = { 'account': { '_content': args.account, 'by': 'name' } } if args.account else None
    request_name = args.request if args.request.endswith('Request') else args.request + 'Request'
    params = json.loads(args.params) if args.params else None
    urn = (args.urn if args.urn.startswith('zimbra') else 'zimbra'+args.urn) if args.urn else None

    pprint.pprint(z.request(request_name, params=params, context=context, urn=urn, args=args), depth=args.depth)

if __name__ == "__main__":
    main()
