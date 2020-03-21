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

    #function that handles the betting phase
    #param: none
    #return: none
    def betting_phase(self):
        done = False
        currBet = 0     #the current betting amoutn you have to meet for this round
        timesBet = 0    #variable to make sure every player has been allwoed to try betting at least once
        #keep betting until alll is done
        while not done:
            #loop through ech player to see thier bets
            done = True
            #go through each player and to get their bets
            for player in self.players:
                #players can only bet if they haven't folded yet
                if not player.fold:
                    #ask for user input for bet, only will take num >= -1
                    valid = False
                    #player inputs bet and then program checks if bet is above the bet as a whole
                    while not valid:
                        value = input("enter your bet (0 to check or call, -1 to fold): ")
                        valid = self.betting(int(value), player, currBet)      
                    if player.bet>currBet and timesBet>3:
                        currBet = player.bet
                        done = False
                timesBet+=1

    #checks if a player bet is a call, raise, check, or a fold. then changes the pot and player's bet accordingly
    #param: user string whos betting, amount number that theyre betting
    #return: Bool for if the bet was valid or not
    def betting(self, value, player, currBet):
        #if the player folds
        if value == -1:     
            player.fold = True
            return True
        #if the player checks or calls
        if value == 0:     
            #for when the player is calling
            if player.bet<currBet:
                #if the player does'nt have enough to call
                if player.chips < currBet-player.bet:
                    print("you don't have enough for that")
                    return False
                self.pot+=currBet-player.bet
                player.bet = currBet
                player.chip-=
            return True
        #if the player raises 
        elif value > 0:   
            #if the player raises more than they have
            if value>player.chips:
                print("you don't have enough for that")
                return False
            #if the bet is either too low or it only calls the bet then return false
            if player.bet+value <= currBet:
                print("invalid, bet too low")
                return False
            player.bet+=value
            self.pot+=value
            return True
        else:
            print("not a valid")
            return False


    #function for identifying value of your hand
    def hand_value(self, player):
        suits = []  #list to hold all card's suit
        values = []  #list to hold all card's values
        #breaks the cards up into suits and values
        for card in self.hand:
            value = card[0]
            #checks if the value code is a face card or ACE
            if value == "J":
                value = 11
            elif value == "Q":
                value = 12
            elif value == "K":
                value = 13
            elif value == "A":
                value = 14
            values.append(int(value))   #add to the list of hand values
            suits.append(card[1])       #add to the lsit of hand suits
        flush = is_flush(suits)
        straight = is_straight(values)

    #checks if your hand is a flush
    #param: hand(list of strings of all the suits)
    #return: bool(if a flush or not )
    def is_flush(self, hand):
        suits = ["H", "S", "D", "C"]
        temp = hand[0]
        for suit in suits:
            if suit in hand:
                if suit!=temp:
                    return False
        return True

     #checks if your hand is straight
    #param: hand(list of ints of all hand values)
    #return: bool(if a straight or not)
    def is_straight(self, hand):
        hand.sort()
        for x in range(len(hand)):
            if hand[x+1] != hand[x]+1:
                return False
        return True


        
            


#notes: shuffling/reshuffling takes all the cards from the pile and puts them back into the main deck
#       you can draw specific cards  isntead of jsut a general number
#       you cant add cards directly to the deck

# deck = requests.get("https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1")    #makes a new deck for this game
# deck = deck.json()
# deckID  = deck["deck_id"]
# drawn = requests.get("https://deckofcardsapi.com/api/deck/{}/draw/?cards=AS".format(deckID))
# drawn = drawn.json()        #requests api to draw 2 cards ad then convert that response to json
# temp = requests.get("https://deckofcardsapi.com/api/deck/{}/pile/sample/add/?cards=AS".format(deckID))
# print(temp.text)
# temp1 = requests.get("https://deckofcardsapi.com/api/deck/{}/shuffle/".format(deckID))
    
# print(temp1.text)
# # print(temp)