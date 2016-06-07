from twython import Twython, TwythonError
import webapp2
import os
import cloudstorage as gcs
import urllib2
import re
import logging
from googleplay import GooglePlayAPI
from config import *
import sys
import json
from urllib2 import Request, urlopen, URLError
from datetime import date, timedelta

class GetRequest(urllib2.Request):
    def get_method(self):
        return "GET"

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Nothing to see here.')

class UpdateTwitterLog(webapp2.RequestHandler):
    
    def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)

    def add_to_file(self, filename, old, new):
        logging.debug("attempting to write to file")
        self.response.write('Appending file %s\n' % filename)

        write_retry_params = gcs.RetryParams(backoff_factor=1.1)
        gcs_file = gcs.open(filename,
                            'w',
                            content_type='text/plain',
                            retry_params=write_retry_params)
        gcs_file.write(old)
        gcs_file.write(new)
        gcs_file.close()

    def get(self):

	search_term = "your term here"

        bucket_name = os.environ.get('BUCKET_NAME',
                                 'log')

        self.response.headers['Content-Type'] = 'text/plain'

        logging.debug("reading old file")
        bucket = '/' + bucket_name
        filename = '/log/twitter.csv'
        gcs_file = gcs.open(filename)
        old_file = gcs_file.read()

        twitter = Twython('your keys here')

        yesterday = str(date.today() - timedelta(1))
        today = str(date.today())

        #print api.VerifyCredentials()
        last_id = '0'
        logging.debug("getting first tweet")
        try:
            tweets = twitter.search(q=search_term, count=100, until=today, since=yesterday)
        except TwythonError:
            e = sys.exc_info()[0]
            logging.error("Error Caught : " + e)
            raise
        for tweet in tweets['statuses']:
            time = tweet['created_at']
            text = re.sub("\n", " ", tweet['text'])
            text = re.sub(",", "", text)
            text = "".join(i for i in text if ord(i)<128)
            #text = self.removeNonAscii(text)
            #user = self.removeNonAscii(tweet['user']['name'])
            user = "".join(i for i in tweet['user']['name'] if ord(i)<128)
            last_id= tweet['id_str']
            new = last_id + ',' + time + ',' + user + ',' + text + "\n"
            new = new.encode('utf-8')
        logging.debug("get remaining tweets")
        while len(tweets['statuses']) > 1:
            tweets = twitter.search(q=search_term, count=100, max_id=last_id, until=today, since=yesterday)
            ignore_first = True  #max_id is inclusive, so we ditch the first result
            for tweet in tweets['statuses']:
                if (not ignore_first):
                    time = tweet['created_at']
                    #text = re.sub(u'\u2018', "", tweet['text'])
                    #text = re.sub(u'\u2019', "", text)
                    #text = re.sub(u'\u2026', "", text)
                    text = re.sub("\n", " ", tweet['text'])
                    text = re.sub(",", "", text)
                    #text = self.removeNonAscii(text)
                    #user = self.removeNonAscii(tweet['user']['name'])
                    text = "".join(i for i in text if ord(i)<128)
                    user = "".join(i for i in tweet['user']['name'] if ord(i)<128)
                    last_id= tweet['id_str']
                    new = new + last_id + ',' + time + ',' + user + ',' + text+ "\n"
                    new = new.encode('utf-8')
                else:
                    ignore_first = False
        logging.debug("appending file")
        self.add_to_file('/log/twitter.csv', old_file, new)
        logging.debug("fin")



app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/twitterLog', UpdateTwitterLog),
], debug=True)
