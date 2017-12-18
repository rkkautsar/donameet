import os
import tweepy
import requests
import json
from geopy.geocoders import Nominatim
from wit import Wit

access_token = os.environ.get('WIT_ACCESS_TOKEN')
client = Wit(access_token)
geolocator = Nominatim(timeout=3)

consumer_key = os.environ.get('TWITTER_KEY')
consumer_secret = os.environ.get('TWITTER_SECRET')
access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
access_token_secret = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, retry_count=2,
                 retry_delay=451)  # 15 min delay / 2 retry


class TweetListener(tweepy.StreamListener):

    def get_first_entity_value(self, resp, entity):
        outcome = resp['outcomes'][0]
        entities = outcome['entities'].get(entity, [])
        if len(entities) > 0:

            if entity == 'phone_number':
                entities = list(
                    filter(lambda e: e['value'][0] == '0', entities))
            elif entity == 'location':
                entities = list(
                    filter(lambda e: len(e['value']) > 3, entities))

            entities.sort(key=lambda x: -x['confidence'])
            return entities[0]['value']
        else:
            return '[{} missing]'.format(entity)

    def on_status(self, received):

        tweet = received._json

        if 'retweeted_status' not in tweet:
            if tweet['truncated']:
                status = tweet['extended_tweet']['full_text']
            else:
                status = tweet['text']

            print('[*] New Tweet: {}'.format(status))

            print('[*] Requesting Wit...')
            resp = client.get_message(status)

            if self.get_first_entity_value(resp, 'intent') == 'patient':

                blood_type = self.get_first_entity_value(resp, 'blood_type')
                rhesus = self.get_first_entity_value(resp, 'rhesus')
                location = self.get_first_entity_value(resp, 'location')
                phone_number = self.get_first_entity_value(
                    resp, 'phone_number')

                geocode = geolocator.geocode(location)
                geocode_val = '[Unable to geocode]'
                if geocode is not None:
                    geocode_val = '(Lat: {}, Long: {}, Addr: {})'.format(
                        geocode.latitude, geocode.longitude, geocode.address)

                data = {
                    'value1': '{}{}, di {}, geocode {}'.format(blood_type, rhesus, location, geocode_val),
                    'value2': phone_number,
                    'value3': status,
                }

                print('[*] Notifying Line...')
                requests.post(
                    'https://maker.ifttt.com/trigger/donameet_test/with/key/cJRfaUDbCTM1eNchebpS33', data=data)


class UserStreamListener(tweepy.StreamListener):

    def on_data(self, data):
        data = json.loads(data)

        if 'direct_message' in data:
            self.on_direct_message(data['direct_message'])
        elif 'in_reply_to_screen_name' in data and data['in_reply_to_screen_name'] == 'donameet_bot':
            self.on_mention(data)

    def on_direct_message(self, data):
        text = data['text']
        user = data['sender']['screen_name']

        try:
            api.send_direct_message(
                user, text='Hi! you just sent me: {}'.format(text))
        except tweepy.error.TweepError as e:
            print("Error: {}".format(e.reason))

    #-----------------------------------------------------------------------
    # Format Mention : 'Name|BloodType_Rhesus|Location|Contact| @donameet_bot'
    # 'Farida|O+|Depok|081234567890| @donameet_bot'
    #-----------------------------------------------------------------------
    def on_mention(self, data):
        tweet = data['text']
        result = tweet.split('|')
        name = result[0]
        blood_type = result[1][:1]
        rhesus = result[1][1:]
        location = result[2]
        contact = result[3]
        # todo add to db


    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_data disconnects the stream
            return False
        else:
            print('Error {}'.format(status_code))


if __name__ == "__main__":

    # stream = tweepy.Stream(
    #     auth=api.auth, listener=TweetListener(), tweet_mode='extended')
    # stream.filter(track=['@Blood4LifeID', 'donor darah',
    #                      'butuh darah', 'perlu darah', 'dicari donor', 'cari darah'])

    stream = tweepy.Stream(
        auth=api.auth, listener=UserStreamListener(), tweet_mode='extended')
    stream.userstream()
