# Some examples of early tests that I tried.

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
