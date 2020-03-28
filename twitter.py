import os
import dotenv
from requests_oauthlib import OAuth1Session

dotenv.load_dotenv('.env')

class Twitter(object):
    def __init__(self):
        #twitter key variables
        consumer_key = os.environ.get('TWITTER_CONSUMER_KEY')
        consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET')
        access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
        access_token_secret = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

        #createsnew twitter session
        session = OAuth1Session(consumer_key,
                                client_secret=consumer_secret,
                                resource_owner_key=access_token,
                                resource_owner_secret=access_token_secret)

        # The URL endpoints to update a status 
        tweet_url = 'https://api.twitter.com/1.1/statuses/update.json'          #for tweets and comment
        dm_url = 'https://api.twitter.com/1.1/direct_messages/events/new.json'  #for DMs
        tweetID = None      #tweet ID
        users = []          #list of user handles that will particpate in the game

    #makes a tweet or comment on a  tweet
    #param: status(string content you want to tweet or comment), tweetID(ID of the tweet you want to reply to)
    #return: none
    def tweet(self, status, tweetID=None):
        #tries to make a tweet
        try:
            resp = self.session.post(self.tweet_url, {'status': status, 'in_reply_to_status_id': tweetID})
        except: #if fail print out the error and stop the func
            print("failed to tweet")
            print(resp.text)
            return
        resp = resp.json()  #converts response to json dic
        #checks if this is the first tweet for the game
        print(resp)
        print(resp['id'])
        if(tweetID == None):
            tweet_ID = resp['id']

# temp = tweet("testing post")
# temp1 = tweet("testing comment 1", 1240733416393281536)


# def dm_player(playerID, message):
#     resp = session.post({'type': 'message_create', 'message_create.target.recipient_id': playerID, 'message_create.message_data': {'text': message}})
#     print(resp.text)


# # The contents of status (i.e. tweet text)
# status = 'If you are reading this on Twitter, the API request worked! 2nd try'
# # Send a POST request to the url with a 'status' parameter
# resp = session.post(url, { 'status': status })
# # Show the text from the response
# print(resp.text)
