#!/usr/bin/env python
import client
import utils
from itertools import *
from collections import namedtuple

def get_cals(account, opts):
    context = { 'account': { '_content': account, 'by': 'name' }}
    params = { 'view': 'appointment' }
    req = 'GetFolderRequest'
    urn = client.urn_for_request(req)
    response = z.request(req, params=params, context=context, urn=urn, opts=opts)
    folders = [response['GetFolderResponse']['folder']]
    return folders

def get_linked_cals(folders):
    """ Recursively search for linked calendars, generating iteration of those found """
    for folder in folders:
        if 'link' in folder:
            for linked_folder in folder['link']:
                yield linked_folder
        if 'folder' in folder:
            subfolders = folder['folder']
            for linked_folder in get_linked_cals(subfolders):
                yield linked_folder

if __name__ == "__main__":
    z = client.Zimbra()
    z.connect()
    opts = {'xml': False, 'debug': False}
    accounts = utils.getAllAccounts(z, opts)
    AccountCals = namedtuple('AccountCals', 'account, cals')

    all_cals = imap(lambda a: AccountCals(a, get_cals(a, opts)), accounts)
    # all accounts and each account's calendar folders (the latter structured with subfolders)
    linked_cals = imap(lambda item: AccountCals(item.account, list(get_linked_cals(item.cals))), all_cals)
    # all accounts and flat list of accounts linked from others for each
    ownertest = lambda cal: 'owner' in cal and cal['owner'].startswith('sruksak')
    linked_cals_owner = imap(lambda item: AccountCals(item.account, filter(ownertest, item.cals)), linked_cals)
    # all accounts with linked accounts from specific owner for each
    linked_cals_nonempty = ifilter(lambda item: item.cals, linked_cals_owner)
    # only those accounts that have at least one matching linked cal folder
    
    for item in linked_cals_nonempty:
        for cal in item.cals:
            owner = cal.get('owner', '*unknown*')
            # inactive accounts have no 'owner' in links to their calendars
            print "\t".join([item.account, owner, cal['name']])
