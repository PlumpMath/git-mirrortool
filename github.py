import requests
import errors
import json
import readline
import sys
from getpass import getpass
from git_mirrortool import git


API_ENDPOINT = 'https://api.github.com'

class Client(object):

    def __init__(self, token):
        self.token = token

    def create_repo(self, name):
        response = requests.post(
            API_ENDPOINT + '/user/repos',
            headers={'Authorization': 'token %s' % self.token},
            data=json.dumps({
                'name': name,
            })

def get_token(username, password):
    response = requests.post(
        API_ENDPOINT + '/authorizations',
        auth=requests.HTTPBasicAuth(username, password),
        data=json.dumps({
            'scopes': ['repo'],
            'note': 'git-mirrortool',
        })
    )
    if response.status_code < 200 or response.status_code >= 300:
        raise errors.RequestFailed(response)
    try:
        result = response.json()
        return result['hashed_token']
    except ValueError:
        raise errors.UnexpectedResponse(response, "Body is not JSON")


def save_config(accountname, username, token):
    account = 'mirrortool.account.%s' % accountname
    git(['config', '--global', '%s.type' % account,  'github'])
    git.config('%s.username' % account, username, globl=True)
    git.config('%s.token' % account, token, globl=True)


def client(accountname):
    token = git(['config', '--global', 'mirrortool.account.%s.token' %
        accountname])
    return Client(token)

def prompt():
    sys.stdout.write('Github Username: ')
    username = raw_input()
    password = getpass()
    token = get_token()
    accountname = 'github/%s' % username
    save_config(accountname, username, token)
    sys.stdout.write('Enable by default? [Y/n]: ')
    enable = raw_input()
    if enable in ('Y', 'y', ''):
        enable = True
    else:
        enable = False
    if enable:
        git(['config', '--global', '--add', 'mirrortool.account', accountname)
