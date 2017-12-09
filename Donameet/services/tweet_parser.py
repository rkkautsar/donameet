import os
import tweepy
import requests
from wit import Wit

access_token = os.environ.get('WIT_ACCESS_TOKEN')
client = Wit(access_token)

#override tweepy.StreamListener to add logic to on_status
class TweetListener(tweepy.StreamListener):

    def on_status(self, status):
        print('[*] New Tweet: {}'.format(status.text))
        
        print('[*] Requesting Wit...')
        resp = client.get_message(status.text)
        
        if resp['outcomes'][0]['entities']['intent'][0]['value'] == 'patient':

            blood_types = resp['outcomes'][0]['entities'].get('blood_type', [])
            rhesuses = resp['outcomes'][0]['entities'].get('rhesus', [])
            phone_numbers = resp['outcomes'][0]['entities'].get('phone_number', [])

            blood_type = blood_types[0]['value'] if len(blood_types) > 0 else '[Blood Type Missing]'
            rhesus = rhesuses[0]['value'] if len(rhesuses) > 0 else '[Rhesus Missing]'
            phone_number = phone_numbers[0]['value'] if len(rhesuses) > 0 else '[Phone Number Missing]'

            data = {
                'value1': '{}{}'.format(blood_type, rhesus),
                'value2': phone_number,
                'value3': status.text,
            }

            print('[*] Notifying Line...')
            requests.post('https://maker.ifttt.com/trigger/donameet_test/with/key/cJRfaUDbCTM1eNchebpS33', data=data)


if __name__ == "__main__":

    consumer_key = os.environ.get('TWITTER_KEY')
    consumer_secret = os.environ.get('TWITTER_SECRET')
    access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret) 
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    stream = tweepy.Stream(auth=api.auth, listener=TweetListener())
    stream.filter(track=['@Blood4LifeID', 'donor darah', 'butuh darah', 'perlu darah', 'dicari donor', 'cari darah'])

