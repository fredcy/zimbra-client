import yaml
import json
from params import dmerge, parse_param

def pdump(data):
    """Return YAML representation of the data, washed through json just to remove
    all the unicode notations."""
    return yaml.dump(yaml.load(json.dumps(data)))

def getAllAccounts(z, opts):
    """ Return list of all account names. """
    response = z.request('GetAllAccountsRequest', opts=opts)
    names = [account['name'] for account in response['GetAllAccountsResponse']['account']]
    return sorted(names)

def getAllRooms(z, opts):
    """ Return list of all room resource names. """
    params = {}
    dmerge(params, parse_param('@attrs=uid'))
    dmerge(params, parse_param('@types=resources'))
    #dmerge(params, parse_param('@limit=5'))
    response = z.request('SearchDirectoryRequest', params=params, opts=opts)
    names = [item['name'] for item in response['SearchDirectoryResponse']['calresource']]
    return names

if __name__ == '__main__':
    import client
    z = client.Zimbra()
    z.connect()
    opts = {'xml': False, 'debug': False }
    print getAllRooms(z, opts)
    
