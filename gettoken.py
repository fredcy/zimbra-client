import os

from pythonzimbra.tools import auth 

def get_token():
    url = os.environ['ZIMBRA_URL']
    account = os.environ['ZIMBRA_ACCOUNT']
    password = os.environ['ZIMBRA_PASSWORD']
    try:
        token = auth.authenticate(url, account, password, admin_auth=True)
    except:
        log.exception("locals=%s", locals())
    return token


if __name__ == "__main__":
    token = get_token()
    print token

