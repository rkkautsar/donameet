import os
import tweepy
import requests
from geopy.geocoders import Nominatim
from wit import Wit

access_token = os.environ.get('WIT_ACCESS_TOKEN')
client = Wit(access_token)
geolocator = Nominatim()

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

    def on_status(self, status):
        print('[*] New Tweet: {}'.format(status.text))

        print('[*] Requesting Wit...')
        resp = client.get_message(status.text)

        if self.get_first_entity_value(resp, 'intent') == 'patient':

            blood_type = self.get_first_entity_value(resp, 'blood_type')
            rhesus = self.get_first_entity_value(resp, 'rhesus')
            location = self.get_first_entity_value(resp, 'location')
            phone_number = self.get_first_entity_value(resp, 'phone_number')

            geocode = geolocator.geocode(location)
            geocode_val = '[Unable to geocode]'
            if geocode is not None:
                geocode_val = '(Lat: {}, Long: {}, Addr: {})'.format(geocode.latitude, geocode.longitude, geocode.address)

            data = {
                'value1': '{}{}, di {}, geocode {}'.format(blood_type, rhesus, location, geocode_val),
                'value2': phone_number,
                'value3': status.text,
            }

            print('[*] Notifying Line...')
            requests.post(
                'https://maker.ifttt.com/trigger/donameet_test/with/key/cJRfaUDbCTM1eNchebpS33', data=data)


if __name__ == "__main__":

    consumer_key = os.environ.get('TWITTER_KEY')
    consumer_secret = os.environ.get('TWITTER_SECRET')
    access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    stream = tweepy.Stream(auth=api.auth, listener=TweetListener())
    stream.filter(track=['@Blood4LifeID', 'donor darah',
                         'butuh darah', 'perlu darah', 'dicari donor', 'cari darah'])
