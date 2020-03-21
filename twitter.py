from requests_oauthlib import OAuth1Session

dotenv.load_dotenv('.env')

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

tweet_ID = None   #ID of the tweet/game

#makes a tweet or comment on a  tweet
#param: status,(string content you want to tweet or comment), statusID(ID of the tweet you want to reply to)
#return: none
def tweet(status):
    #tries to make a tweet
    try:
        resp = session.post(tweet_url, {'status': status, 'in_reply_to_status_id': tweet_ID})
    except: #if fail print out the error and stop the func
        print("failed to tweet")
        print(resp.text)
        return
    #print(resp.text)
    resp = resp.json()  #converts response to json dic
    #checks if this is the first tweet for the game
    print(resp)
    print(resp['id'])
    if(tweet_ID == None):
        tweet_ID = resp['id']

temp = tweet("testing post")
temp1 = tweet("testing comment 1", 1240733416393281536)
