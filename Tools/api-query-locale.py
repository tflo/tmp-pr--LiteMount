#!/usr/bin/python3 -tt

import requests, os
from pprint import pprint
from argparse import ArgumentParser

auth = (os.environ['WOW_API_CLIENT_ID'], os.environ['WOW_API_CLIENT_SECRET'])

parser = ArgumentParser()
parser.add_argument('-t', '--type', default='item', nargs='?')
parser.add_argument('-s', '--search', action='store_true')
parser.add_argument('id', nargs='+')
args = parser.parse_args()

r = requests.post('https://oauth.battle.net/token', auth=auth, params={ 'grant_type': 'client_credentials' })
r.raise_for_status()

s = requests.session()
s.headers['Authorization'] = 'Bearer {}'.format(r.json()['access_token'])
s.headers['Battlenet-Namespace'] = 'static-us'

rows = []

for id in args.id:
    if '=' in id:
        type, id = id.split('=')
    else:
        type = args.type

    if args.search:
        params = { 'name.en_US': id }
        r = s.get('https://us.api.blizzard.com/data/wow/search/{}'.format(type), params=params)
        r.raise_for_status()
        data = [ x['data'] for x in r.json()['results'] ]
    else:
        r = s.get('https://us.api.blizzard.com/data/wow/{}/{}'.format(type, id))
        r.raise_for_status()
        data = [ r.json() ]

    for d in data:
        for locale, name in d['name'].items():
            if locale != 'en_US':
                rows.append((locale, 'L["{}"] = "{}"'.format(d['name']['en_US'], name)))

current_locale = ''

for r in sorted(rows):
    if r[0] != current_locale:
        print(r[0])
        current_locale = r[0]
    print(r[1])
