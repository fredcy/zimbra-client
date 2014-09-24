import re

def parse_param(sparam):
    """ Parse a parameter string into dict following Zimbra json conventions.
    >>> parse_param("@depth=4")
    {'depth': '4'}

    >>> parse_param("/folder@path=/foobar")
    {'folder': {'path': '/foobar'}}

    >>> parse_param("/query=foo or bar")
    {'query': {'_content': 'foo or bar'}}

    >>> parse_param("/signature/content=foo bar")
    {'signature': {'content': {'_content': 'foo bar'}}}
    """
    path, value = sparam.split('=')
    pathlist = split(path)
    return path_to_dict(pathlist, value)

def path_to_dict(path, value):
    first, rest = path[0], path[1:]
    if first.startswith("@"):
        attr_name = first[1:]
        if rest:
            raise Exception("path_to_dict(%s, %s): path continues after %s" % (path, value, first))
        return {attr_name: value}
    elif first.startswith("/"):
        elmt_name = first[1:]
        if not rest:
            return {elmt_name: {'_content': value}}
        else:
            return {elmt_name: path_to_dict(rest, value)}
    else:
        raise Exception("path_to_dict: bad first value: %s" % first)
    
def split(str):
    """
    >>> split("/foo/bar")
    ['/foo', '/bar']

    >>> split("@what")
    ['@what']
    """
    split_re = re.compile(r'[/@]\w+')
    parts = split_re.findall(str)
    return parts

if __name__ == '__main__':
    import doctest
    doctest.testmod()
