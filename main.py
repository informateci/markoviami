import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from markovate import Markovator

import sys
import tweepy

CONSUMER_KEY = '5EPAag0iguaXtRaO9fvA'
CONSUMER_SECRET = 'zcVUGgtcUxqZI1nHLhqDmzt2jZDiQENmsgqDB2Vc'


def create_markovated_tweet(tweets, max_length):
    filtered = map(lambda t: t.text.replace('@','').replace('#','').strip(), tweets)
    filtered = map(lambda t: ' '.join(filter(lambda word:(not 'http://' in word) and (not 'https://' in word), t.split())), filtered )
    tweets_texts = map(lambda t: t.strip(), filtered)
    markovator = Markovator()
    markovator.parse_sentences(tweets_texts)
    markovation = markovator.markovate()

    count = 0
    while len(markovation) > max_length:
        markovation = markovator.markovate()
        count += 1
        if count > 20:
            return None

    return markovation

class TweetsProcessor(webapp.RequestHandler):
    def get(self):
        users_id = self.request.get_all("tweetid")
        if (len(users_id) <= 0):
            self.response.out.write('Nessun id twitter passato come parametro')
        else:
            # Just get the latest tweets
            auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
            auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
            api = tweepy.API(auth)

            tweets = []
            for id in users_id:
                try:
                    tweets.extend(api.user_timeline(id, count=800))
                except:
                    continue
            if len(tweets) <= 1:
                self.response.out.write('Could not generate tweet (not enough eligible tweets)')
                return

            best_tweet = create_markovated_tweet(tweets, 140)

            if best_tweet != None:
                self.response.out.write(best_tweet)
            else:
                self.response.out.write('Could not generate tweet')

application = webapp.WSGIApplication([('/', TweetsProcessor)])

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

