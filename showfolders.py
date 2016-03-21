#!/usr/bin/env python
import client
import utils
from itertools import *
import pprint
import logging

log = logging.getLogger("showfolders")
log.setLevel(logging.WARN)


def getFolderPaths(folders):
    """Extract and generate all "absFolderPath" values from the folder list,
    including subfolders."""
    for folder in folders:
        yield folder['absFolderPath']
        if 'folder' in folder:
            for path in getFolderPaths(folder['folder']):
                yield path

    
def getAccountFolders(z, accountname, opts):
    context = { 'account': { '_content': accountname, 'by': 'name' }}
    params = { 'view': 'message' }
    req = 'GetFolderRequest'
    urn = client.urn_for_request(req)
    response = z.request(req, params=params, context=context, urn=urn, opts=opts)
    folders = response['GetFolderResponse']['folder']['folder']
    return folders
                

def main():
    z = client.Zimbra()
    z.connect()

    opts = { 'xml': False, 'debug': True }

    folders = getAccountFolders(z, "jtorres@imsa.edu", opts)
    print utils.pdump(folders)

    paths = getFolderPaths(folders)
    for path in paths:
        print path


if __name__ == '__main__':
    main()
