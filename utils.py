import yaml
import json

def pdump(data):
    """Return YAML representation of the data, washed through json just to remove
    all the unicode notations."""
    return yaml.dump(yaml.load(json.dumps(data)))

def getAllAccounts(z, opts):
    """ Return list of all account names. """
    response = z.request('GetAllAccountsRequest', opts=opts)
    names = [account['name'] for account in response['GetAllAccountsResponse']['account']]
    return sorted(names)
