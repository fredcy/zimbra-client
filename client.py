import logging
import os
from pythonzimbra.tools import auth
from pythonzimbra.request_xml import RequestXml
from pythonzimbra.response_xml import ResponseXml
from pythonzimbra.communication import Communication

logging.basicConfig(level=logging.DEBUG)

url = os.environ['ZIMBRA_URL']
preauthkey = os.environ['ZIMBRA_PREAUTHKEY']

def main():
    print "hello"
    comm = Communication(url)
    token = auth.authenticate(
        url,
        "admin",
        preauthkey,
    )
    print token

    request = RequestXml()
    request.add_request('GetVersionInfoRequest', {}, 'urn:zimbraAdmin')
    response = ResponseXml()
    comm.send_request(request, response)
    if not response.is_fault():
        print response.get_response()['GetVersionInfoResponse']['info']['version']
    else:
        print "FAULT"

if __name__ == "__main__":
    main()
