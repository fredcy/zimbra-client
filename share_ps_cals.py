#!/usr/bin/env python
import pprint
import yaml
import json
import client                   # local wrapper for python-zimbra

def pdump(data):
    """Return YAML representation of the data, washed through json just to remove
    all the unicode notations."""
    return yaml.dump(yaml.load(json.dumps(data)))

def getAllAccounts(z, opts):
    """ Return a list of all account names. """
    response = z.request('GetAllAccountsRequest', opts=opts)
    names = []
    if response:
        for account in response['GetAllAccountsResponse']['account']:
            names.append(account['name'])
    return names

def accountHasPSCal(z, account, opts):
    """ Return the name of the first PS calendar found for the account, or None. """
    context = { 'account': { '_content': account, 'by': 'name' }}
    params = { 'view': 'appointment' }
    req = 'GetFolderRequest'
    urn = client.urn_for_request(req)
    response = z.request(req, params=params, context=context, urn=urn, opts=opts)
    folders = response['GetFolderResponse']['folder']['folder']
    return findfolders(folders)

def findfolders(folders):
    """ Recursively search for a PS calendar folder and return name of first found. """
    for folder in folders:
        if 'url' in folder and folder['url'].find('/pscal/u/') > 0:
            return folder['absFolderPath']
        if 'folder' in folder:
            subfolders = folder['folder']
            ret = findfolders(subfolders)
            if ret:
                return ret
    return None

def grantAll(z, account, folderid):
    """ Grant read permission on given account and folderid to the allstaff@imsa.edu group. """
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
    response = z.request(req, params=params, context=context, urn=urn, opts=opts)
   
    TODO continue here...


if __name__ == '__main__':
    opts = { 'xml': False, 'debug': False }
    z = client.Zimbra()
    z.connect()

    accounts = getAllAccounts(z, opts)
    for account in accounts:
        pscal = accountHasPSCal(z, account, opts)
        if pscal:
            print account + "\t" + pscal
