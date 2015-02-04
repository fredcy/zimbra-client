#!/usr/bin/env python
import client
import utils
from itertools import *
import pprint
import logging

log = logging.getLogger("showgrants")
log.setLevel(logging.WARN)

def grantsInFolders(folders):
    """Traverse the folder tree and return a list of interesting grants. Each item
    is a tuple of (folderName, grantee, permissions).
    """
    allgrants = []
    for f in folders:
        if 'acl' in f and 'grant' in f['acl']:
            #print utils.pdump(f)
            for g in f['acl']['grant']:
                if 'd' in g:
                    if g['perm'] != 'r':
                        allgrants.append( (f['name'], g['d'], g['perm']) )
                    # else read-only grant; not interesting
                # else public grant (no explicit grantee d)
        if 'folder' in f:
            subfolders = f['folder']
            allgrants += grantsInFolders(subfolders)
    return allgrants

def getAccountGrants(z, accountname, opts):
    context = { 'account': { '_content': accountname, 'by': 'name' }}
    params = { 'view': 'appointment' }
    req = 'GetFolderRequest'
    urn = client.urn_for_request(req)
    response = z.request(req, params=params, context=context, urn=urn, opts=opts)
    folders = response['GetFolderResponse']['folder']['folder']
    return grantsInFolders(folders)

if __name__ == '__main__':
    z = client.Zimbra()
    z.connect()

    opts = { 'xml': False, 'debug': False }
    accounts = utils.getAllRooms(z, opts) # :: [string]
    #accounts = ["fcy@imsa.edu", "rm-a110@imsa.edu"]

    for account in accounts:
        grants = getAccountGrants(z, account, opts)
        for grant in grants:
            print "\t".join([account] + list(grant))
        #print utils.pdump(grants)
        
    
    
