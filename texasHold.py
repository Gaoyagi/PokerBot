import requests 


class Player(object):
    def __init__(self, user):
        self.hand = []
        self.chips = 200
        self.user = user
        self.fold = False
        self.value = ""
        self.bet

class TexasHold(object):
    def __init__(self):
        self.players = {}     #dic of player objects in this game
        self.gameID = 0       #game ID is equivalent to the tweet ID
        self.river = []       #set of face up cards for the round
        self.pot = 0          #current pot for the the round
        self.deck = requests.get("https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1").json()    #gets API request for a new deck and converts it to json
        self.deckID = self.deck["deck_id"]      #deck ID

    #draws a card from a deck or a pile and adds it to another pile
    #param: num(number of cards you want to draw), pile(pile name that you want to put the cards)
    #return: none
    def draw_to_pile(self, num, pile):
        #sends API request to draw cards and converts response to json dic
        drawn = requests.get("https://deckofcardsapi.com/api/deck/{}}/draw/?count={}".format(self.deckID), num)
        drawn = drawn.json()
        #goes through the drawn cards and adds it to pile
        for card in drawn["cards"]: 
            requests.get("https://deckofcardsapi.com/api/deck/{}/pile/{}/add/?cards={}".format(self.deckID, pile, card["code"]))

    #function to add a player to the game, draws 2 cards for them
    #param: user(twitter user name/id string)
    #return: none
    def add_player(self, user):
        #creates new player and adds it to the player list
        player = Player(user)       
        #draws cards and adds it to the players pile (hand)
        self.draw_to_pile(2, user)
        #adds the card codes to the players hand
        req = requests.get("https://deckofcardsapi.com/api/deck/{}/pile/{}/list/".format(self.deckID, user)).json()
        for card in req["piles"][user]["cards"]:
            player.append(card["code"])
        self.players[user] = Player(user)

    #running a round texas hold em
    #param & return: none
    def round(self):
        phase = 0
        # each round has 3 card reveal phases
        while phase<3:
            #check of the deck has enouch cards left for a full round and if not reshuffle
            if self.deck["remaining"] < 16:
                requests.get("https://deckofcardsapi.com/api/deck/{}/shuffle/".format(self.deckID))
            #deals all the players in
            for key, _ in self.players:
                self.add_player()
            #make the river 
            self.river()
            getRiver = requests.get("https://deckofcardsapi.com/api/deck/{}/pile/{}/list/".format(self.deckID, "river")).json()
            faceUp = river["piles"]["river"]["cards"]
            # reveal the first 3 cards
            for x in range(3):
                self.river.append(faceUp[x])
            self.bettingPhase()              #betting phase 1
            self.river.append(faceUp[3])     #1st reveal
            self.bettingPhase()              #2nd betting phase
            self.river.append(faceUp[4])     #final reveal
