#!/usr/bin/env python
import argparse
import pprint
import yaml
import json
import client                   # local wrapper for python-zimbra
import logging
from itertools import *

log = logging.getLogger("share_ps_cals")
log.setLevel(logging.WARN)

def pdump(data):
    """Return YAML representation of the data, washed through json just to remove
    all the unicode notations."""
    return yaml.dump(yaml.load(json.dumps(data)))

def getAllAccounts(z, opts):
    """ Return a generator of all account names. """
    response = z.request('GetAllAccountsRequest', opts=opts)
    if response:
        for account in response['GetAllAccountsResponse']['account']:
            yield account['name']

def accountPscal(z, account, opts):
    """ Return the data of the first external PowerSchool calendar found for the account, or None. """
    context = { 'account': { '_content': account, 'by': 'name' }}
    params = { 'view': 'appointment' }
    req = 'GetFolderRequest'
    urn = client.urn_for_request(req)
    response = z.request(req, params=params, context=context, urn=urn, opts=opts)
    folders = response['GetFolderResponse']['folder']['folder']
    return findfolders(folders)

def findfolders(folders):
    """ Recursively search for a PS calendar folder and return data of first found. """
    for folder in folders:
        if 'url' in folder and folder['url'].find('/pscal/u/') > 0:
            return folder
        if 'folder' in folder:
            subfolders = folder['folder']
            ret = findfolders(subfolders)
            if ret:
                return ret
    return None

def grantAll(z, account, folder):
    """ Grant read permission on given account and folder to the allstaff@imsa.edu group. """
    id_parts = folder['id'].split(':')
    assert(len(id_parts) == 2)
    folderid = id_parts[1]

    context = { 'account': { '_content': account, 'by': 'name' }}
    params = {
        'action': {
            'op': 'grant',
            'id': folderid,
            'grant': {
                'gt': 'grp',
                'd': 'allstaff@imsa.edu',
                'perm': 'r',
            }
        }
    }
    req = 'FolderActionRequest'
    urn = client.urn_for_request(req)
    log.debug("params = %s", pdump(params))
    response = z.request(req, params=params, context=context, urn=urn, opts=opts)
    log.debug("response = %s", pdump(response))

def hasGrant(folderdata):
    """ Return True iff the folder already has the desired grant. """
    if 'acl' in folderdata:
        acl = folderdata['acl']
        if 'grant' in acl:
            for agrant in acl['grant']:
                log.debug('agrant = %s', agrant)
                if agrant['d'] == 'allstaff@imsa.edu' and 'r' in agrant['perm']:
                    return True
    return False
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Grant read access to PowerSchool cals")
    parser.add_argument('--debug', '-d', action='store_true')
    parser.add_argument('--howmany', '-n', type=int, default=1, help='How many calendars to modify')
    args = parser.parse_args()
    if args.debug:
        log.setLevel(logging.DEBUG)

    opts = { 'xml': False, 'debug': args.debug }
    z = client.Zimbra()
    z.connect()

    accounts = getAllAccounts(z, opts)
    pscals = imap(lambda account: (account, accountPscal(z, account, opts)), accounts)
    pscals = ifilter(lambda x: x[1], pscals)

    pscalsUngranted = ifilter(lambda x: not hasGrant(x[1]), pscals)

    for account, pscal in islice(pscalsUngranted, args.howmany):
        print "==", account, "=="
        log.debug("pscal = %s", pdump(pscal))
        grantAll(z, account, pscal)
    
