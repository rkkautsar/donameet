import os
import tweepy
import requests
import json
import re
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

BOT_USERNAME = 'donameet_bot'


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

                username = tweet['screen_name']
                blood_type = self.get_first_entity_value(resp, 'blood_type')
                amount = self.get_first_entity_value(resp, 'blood_amount')
                rhesus = self.get_first_entity_value(resp, 'rhesus')
                location = self.get_first_entity_value(resp, 'location')
                contact_phone = self.get_first_entity_value(resp, 'phone_number')

                if not ('missing' in blood_type or 'missing' in rhesus or 'missing' in location or 'missing' in contact_phone):
                    
                    param = {
                        'username': username,
                        'contact_phone': contact_phone,
                        'amount': amount,
                        'blood_type': blood_type,
                        'rhesus': rhesus,
                        'location': location
                    }
                    geocode = geolocator.geocode(location)
                    if geocode is not None:
                        param['lat'] = geocode.latitude
                        param['lng'] = geocode.longitude
                    response = requests.post('http://localhost:4000/add-patient', data=param)
                    result = response.json()['match']

                    if result:
                        msg_reply = "You might want to contact these people:"
                        for entry in result:
                            msg_reply += " @{}".format(entry['username'])
                        api.update_status(msg_reply, tweet['id'])

                data = {
                    'value1': '{}{}'.format(blood_type, rhesus),
                    'value2': contact_phone,
                    'value3': status,
                }

                print('[*] Notifying Line...')
                requests.post(
                    'https://maker.ifttt.com/trigger/donameet_test/with/key/cJRfaUDbCTM1eNchebpS33', data=data)


class UserStreamListener(tweepy.StreamListener):

    def on_data(self, data):
        data = json.loads(data)

        if 'direct_message' in data and data['direct_message']['sender']['screen_name'] != BOT_USERNAME:
            self.on_direct_message(data['direct_message'])
        elif 'in_reply_to_screen_name' in data and data['in_reply_to_screen_name'] == BOT_USERNAME:
            self.on_mention(data)

    def on_direct_message(self, data):
        #format DM: '{Nama}|{Umur}|{Goldar}{Rh}|{Lokasi}|{NomorHP}'
        #           'Indra Pambudi|20|B+|Depok|083808844321'

        print('[+] Got DM:')
        print(data)

        text = data['text']
        user = data['sender']['screen_name']
        check = re.match(r'^.+\|[0-9]+\|(A|B|AB|O)(\+|\-|)\|.+\|(\+62|62|08)[0-9]+$', text)
        if check == None:
            try:
                api.send_direct_message(
                    user, text='Hi! if you want to donate your blood please message me with this \
                    format Name|Age|BloodType{Rhesus}|Location|PhoneNumber, ex: Indra Pambudi|20|B+|Depok|083808844321')
            except tweepy.error.TweepError as e:
                print("Error: {}".format(e.reason))
            return

        textArr = text.split('|')
        name = textArr[0]
        age = textArr[1]
        bloodType = textArr[2]
        rh = '+'
        if bloodType[-1] in ['-','+']:
            rh = bloodType[-1]
            bloodType = bloodType[:-1]
        loc = textArr[3]
        phone = textArr[4]
        twitName = data['sender']['name']

        #insert to database here
        param = {
            'username': user,
            'contact_phone': phone,
            'blood_type': bloodType,
            'rhesus': rh,
            'location': loc
        }
        geocode = geolocator.geocode(loc)
        if geocode is not None:
            param['lat'] = geocode.latitude
            param['lng'] = geocode.longitude
        
        print(param)

        response = requests.post('http://localhost:4000/add-donor', data=param)
        print(response.text)
        print(response.json())
        result = response.json()['match']

        if result:
            msg_reply = "You might want to contact these people:"
            for entry in result:
                msg_reply += " @{}".format(entry['username'])
        else:
            msg_reply = "OK! We will notice you if there is a good match!"

        try:
            api.send_direct_message(user, text=msg_reply)
        except tweepy.error.TweepError as e:
            print("Error: {}".format(e.reason))

    #-----------------------------------------------------------------------
    # Format Mention : 'Name|BloodType_Rhesus|Location|Contact|Amount|cc:@donameet_bot'
    # 'Farida|O+|Depok|081234567890|4|@donameet_bot'
    #-----------------------------------------------------------------------
    def on_mention(self, data):
        tweet_ID = data['id']
        username = data['screen_name']
        tweet = data['text']
        check = re.match(r'^.+\|(A|B|AB|O)(\+|\-|)\|.+\|(\+62|62|08)[0-9]+\|[0-9]+\|[^\|]+$', tweet)
        
        if check:
            result = tweet.split('|')
            name = result[0]
            blood_type = result[1][:1]
            rhesus = result[1][1:]
            location = result[2]
            contact = result[3]
            amount = result[4]
            # todo add to dbxxx
            param = {
                'username': username,
                'contact_phone': contact,
                'blood_type': blood_type,
                'amount': amount,
                'rhesus': rhesus,
                'location': location,
                'text': tweet
            }
            geocode = geolocator.geocode(location)
            if geocode is not None:
                param['lat'] = geocode.latitude
                param['lng'] = geocode.longitude
            response = requests.post('http://localhost:4000/add-request', data=param)
            result = response.json()['match']
            if result:
                msg_reply = "You might want to contact these people:"
                for entry in result:
                    msg_reply += " @{}".format(entry['username'])
            else:
                msg_reply = "OK! We will notice you if there is a good match!"
            
            api.update_status(msg_reply, tweet_ID)
        else:
            try:
                msg_reply = "Hello, kindly please follow the format below \nName|BloodType_Rhesus|Location|Contact|@donameet_bot :)"
                api.update_status(msg_reply, tweet_ID)
            except tweepy.error.TweepError as e:
                print("Error: {}".format(e.reason))
    

    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_data disconnects the stream
            return False
        else:
            print('Error {}'.format(status_code))


if __name__ == "__main__":

    stream_tweet = tweepy.Stream(
        auth=api.auth, listener=TweetListener(), tweet_mode='extended')
    # stream.filter(track=['@Blood4LifeID', 'donor darah',
    #                      'butuh darah', 'perlu darah', 'dicari donor', 'cari darah'], async=True)
    stream_tweet.filter(track=['#donameet_test'], async=True)

    stream_user = tweepy.Stream(
        auth=api.auth, listener=UserStreamListener(), tweet_mode='extended')
    stream_user.userstream()
