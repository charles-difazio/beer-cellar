import re
import requests
import time
import urllib2

import tokens

query = { 'name' : 'Old Stock Ale',
          'brewery' : 'North Coast Brewing Company',
          'filename' : 'old_stock_ale.txt' }
current_beers = []

base_url = 'http://api.untappd.com/v4/search/beer'
r = requests.get(base_url, params={ 'q' : '%s %s' % (query['brewery'],
                                                     query['name']),
                                    'client_id' : tokens.client_id,
                                    'client_secret' : tokens.client_secret})
search_results = r.json()
name_re = re.compile('^%s \(([0-9]{4})\)$' % query['name'])
for b in search_results['response']['beers']['items']:
    if b['brewery']['brewery_name'] != query['brewery']:
        continue
    m = name_re.match(b['beer']['beer_name'])
    if m:
        current_beers.append((int(m.group(1)),
                              int(b['beer']['bid'])))

current_beers.sort(key=lambda tup: tup[0])
print current_beers

of = open(query['filename'], 'a+')

for (year, beer_id) in current_beers:
    url_params = { 'client_id' : tokens.client_id,
                   'client_secret' : tokens.client_secret,
                   'limit' : 50 }

    print >>of, "# %d %d" % (year, beer_id)
    print "# %d %d" % (year, beer_id)

    base_url = 'http://api.untappd.com/v4/beer/checkins/%d' % beer_id
    url = base_url
    start = time.mktime(time.strptime('01 Jan %d' % year, '%d %b %Y'))
    while True:
        r = requests.get(url, params=url_params)
        while r.status_code == 500:
            print 'Sleeping for an hour...', time.strftime("%H:%M:%S")
            time.sleep(60*65)
            r = requests.get(url, params=url_params)
        checkins = r.json()
        ratings = [(time.mktime(
                    time.strptime(x['created_at'],
                                  '%a, %d %b %Y %H:%M:%S +0000')) - start,
                    float(x['rating_score']),
                    x['checkin_id']) for x in
                   checkins['response']['checkins']['items']]

        for rating in ratings:
            print '%d %s %s' % rating
            print >>of, '%d %s %s' % rating
        print >>of, ""
        of.flush()

        if checkins['response'].has_key('pagination'):
            url_params['max_id'] = checkins['response']['pagination']['max_id']
        else:
            break

of.close()
