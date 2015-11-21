import requests
import json
import readline
import sys
from getpass import getpass
from git_mirrortool import errors
from git_mirrortool.git import git
import schema as s
import re


DEFAULT_API_ENDPOINT = 'https://api.github.com'

class Client(object):

    def __init__(self, username, token=None, endpoint=DEFAULT_API_ENDPOINT):
        self.endpoint = endpoint
        self.username = username
        self.default_headers = {
            'Accept': 'application/vnd.github.v3+json',
        }
        if token is not None:
            self._set_token(token)

    def _set_token(self, token):
        self.token = token
        self.default_headers['Authorization'] = 'token %s' % self.token

    def create_repo(self, name):
        response = requests.post(
            self.endpoint + '/user/repos',
            headers=self.default_headers,
            data=json.dumps({
                'name': name,
            })
        )
        response.text

    def get_token(self, password):
        response = requests.post(
            self.endpoint + '/authorizations',
            auth=(self.username, password),
            headers=self.default_headers,
            data=json.dumps({
                'scopes': ['repo'],
                'note': 'git-mirrortool',
            })
        )
        if response.status_code < 200 or response.status_code >= 300:
            raise errors.RequestFailed(response)
        try:
            result = response.json()
            s.Schema({
                'hashed_token': s.And(
                    basestring,
                    lambda t: re.match(r'^[0-9a-fA-F]+$', t)
                ),
                s.Optional(basestring): object,
            }).validate(result)
            self._set_token(result['hashed_token'])
        except ValueError:
            raise errors.UnexpectedResponse(response, "Body is not JSON")
        except s.SchemaError as e:
            raise errors.UnexpectedResponse(response, str(e))

    def save_token(self, accountname):
        account = 'mirrortool.account.%s' % accountname
        git(['config', '--global', '%s.type' % account,  'github'])
        git(['config', '--global', '%s.username' % account, self.username])
        git(['config', '--global', '%s.token' % account, self.token])

    @staticmethod
    def from_config(accountname):
        token = git(['config', '--global', 'mirrortool.account.%s.token' %
                     accountname])
        return Client(token)


def prompt():
    sys.stdout.write('Github Username: ')
    username = raw_input()
    password = getpass()
    client = Client(username)
    try:
        client.get_token(password)
    except errors.RequestFailed as e:
        print("Request failed. Response:")
        print(e.response.text)
        return
    accountname = 'github/%s' % username
    client.save_token(accountname)

    sys.stdout.write('Enable by default? [Y/n]: ')
    enable = raw_input()
    if enable in ('Y', 'y', ''):
        enable = True
    else:
        enable = False
    if enable:
        git(['config', '--global', '--add', 'mirrortool.account', accountname])
