import requests 


class Player(object):
    def __init__(self, user=""):
        self.hand = []
        self.chips = 200
        self.user = user
        self.fold = False
        self.value = ""
        self.bet = 0
        self.strength = None

class TexasHold(object):
    def __init__(self):
        self.players = {}     #dic of player objects in this game
        self.gameID = 0       #game ID is equivalent to the tweet ID
        self.river = []       #set of face up cards for the round
        self.pot = 0          #current pot for the the round
        self.deck = requests.get("https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1")    #gets API request for a new deck 
        self.deck = self.deck.json()    #coverts api request to json
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
        #draws cards and adds it to the players pile (hand)
        self.draw_to_pile(2, user)
        #adds the card codes to the players hand
        req = requests.get("https://deckofcardsapi.com/api/deck/{}/pile/{}/list/".format(self.deckID, user)).json()
        for card in req["piles"][user]["cards"]:
            self.players[user].hand.append(card["code"])
        self.players[user] = Player(user)

    #running a round texas hold em
    #param & return: none
    def round(self):
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
        strongest = Player()
        #go through each player and see which one has the best hand
        for player in self.players:
            strength = optimal_hand(player.hand, self.river)
            if strength[0] < strongest.strength[0]:
                strongest = player
            #if the hand strength ties, check which one has the highest card
            elif strength[0] == strongest[0]:
                if strength[1]>strongest[1]:
                    strongest = player
        #ending the round and  declaring the winner,giving them the chips from the pot
        print(f"the winner of this round is {strongest.user}, wining {self.pot} chips!")
        strongest.player.chips+=self.pot
        self.pot = 0
        #looping through each player and reducing their bets down to 0
        for player  in self.players:
            player.bet = 0
            player.fold = False

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
                if not player.fold and player.chips!=0:
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
                #if the player doesn't have enough to call
                if player.chips < currBet-player.bet:
                    print("not enough to call, you are instead going all in")
                    #gives the pot the rest of the players chips
                    self.pot+=player.chips  
                    player.chips = 0
                else:
                    #subtracts the necessary chips from the player and gives them to the pot
                    player.chips-=currBet-player.bet    
                    self.pot+=currBet-player.bet        
                player.bet = currBet    #makes the players current bet match the round's current bet
            return True
        #if the player raises 
        elif value > 0:   
            #if the player raises more than they have then return false
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
    #param: player object(player whose hand to evaluate)
    #return: tuple of an int (signifying how strong the hand is), and the highest int number for that hand(for ties) 
    def hand_value(self, hand):
        suits = []  #list to hold all card's suit
        values = []  #list to hold all card's values
        self. suits_and_values(hand, values, suits)

        flush = is_flush(suits)
        straight = is_straight(values)
        numOfAKind = num_of_a_kind(values)

        #check if its a straight flush
        if flush and straight[0]:
            return (1,straight[1])
        #check if its a 4 of a kind
        elif numOfAKind[0][0] == "quad":
            return (2, numOfAKind[0][1])
        #check for full house and 2 pair, 
        elif len(numOfAKind)>1:
            #full house 1st check, gives bakc high card of triple
            if numOfAKind[0][0] == "pair" and numOfAKind[1][0] == "triple":
                return (3, numOfAKind[1][1])
            #full house 2nd check, gives back high cardof triple
            elif numOfAKind[0][0] == "triple" and numOfAKind[1][0] == "pair":
                return (3, numOfAKind[0][1])
            #check for 2 pair, gives back the high values of both pairs
            elif numOfAKind[0][0] == "pair" and numOfAKind == "pair":
                return (7, numOfAKind[0][1], numOfAKind[1][1])
        #check of the hand is a flush
        elif flush:
            return (4)
        #check for straight
        elif straight[0]:
            return (5,straight[1])
        #check for triples
        elif numOfAKind[0][0] == "triple":
            return (6,numOfAKind[0][1])
        #check for a pair, returns an extra int for high card in case the pair's tie
        elif numOfAKind[0][0] == "pair":
            return (8,numOfAKind[0][1], values[0])
        #check for high card
        else:
            return (9, values[0])
        
    #divides a player's hand into 2 seperate lists, 1 for every suit in the hand, one for every number value
    #param: hand(list of your hand), values(list that will hold all the numbers), suits(list that will hold every card suit)
    #return: none
    def suits_and_values(self, hand, values, suits):
        #breaks the cards up into suits and values
        for card in hand:
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
        values.sort(revere=True)    

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
    #return: list that holds: bool(if a straight or not), highest value of Hand
    def is_straight(self, hand):
        for x in range(len(hand)):
            if hand[x+1] != hand[x]+1:
                return [False,hand[0]]
        return [True, hand[0]]

    #checks if your hand has any pairs, triples, or quads
    #param:hand(list of ints of all the hand values)
    #return: a list of tuples contatining if its  a quad,tiple, or a pair, and what value it is
    def num_of_a_kind(self, hand):
        sameCard = 0
        value = []
        alreadyFound = []
        #go through every value in the hand to find duplicates
        for x in range(len(hand)):
            #avoid finding __ of a kind for the same value
            if hand[x] not in alreadyFound:
                for y in range(len(hand)):
                    if hand[x] == hand[y]:
                        sameCard+=1
                    else:
                        break
            alreadyFound.append(hand[x])
            if sameCard == 3:
                value.append(("quad", hand[x]))
                return value
            elif sameCard == 2:
                value.append(("triple", hand[x]))
            elif sameCard == 1:
                value.append(("pair", hand[x]))
                
        return [True, hand[0]]
    
    #goes through every combination to find the strongest hand for a player
    #param: hand(list of the players card codes) and River(list of the card codes in the river)
    #return: Tuple(contining the hand strength and the highest value card in that combo)
    def optimal_hand(self, hand, river):
        strength = []                   #list of every possible hand strength
        self.river.sort(reverse=True)   #sort the river by descending order
        #loop through every hand card combination
        for x in range(len(self.river)):
            hand.append(hand[0])                #append first card
            for y in range(len(self.river)-1):
                #make sure you arent testing a card being currently used
                if y!=x:
                    hand.append(hand[0])        #append 2nd card
                    for z in range(len(self.river)-2):
                        #make sure you arent testing a card being currently used
                        if z!=x and z!=y:
                            hand.append(hand[0])#append 3rd card
                            strength.append(self.hand_value(hand))      #add the strength of the current hand combination
                            del hand[len(hand)-1]                  #deletes the 3rd test card
                    del hand[len(hand)-1]                          #deletes the 2nd test card
            del hand[len(hand)-1]                                  #deletes the 1st test card
        #check to find the strongest possible combo 
        strongest = strength[0]
        for combo in strength:
            #check if the ranking of the strength is lower  (lower is stronger)
            if strongest[0] > combo[0]:
                strongest = combo
            #if tie, check the strength of each other hand's high card
            elif strongest[0] ==  combo[0]:
                if strongest[1] < combo[1]:
                    strongest = combo
        return strongest

    #function that will run multiple rounds of the game, game only ends if 
    def game(self):
        #creates new player and adds it to the player list
        self.players.append(Player("player 1"))  
        self.players.append(Player("player 2"))  
        self.players.append(Player("player 3"))  
        self.players.append(Player("player 4"))  
        going = True
        while going:
            self.ante()
            self.round()
            for user, _ in self.players:
                if self.players[user].chips == 0:
                    del self.players[user]
            if len(self.players<2):
                going = False
            
    #deals with player's ante'ing in to enter a round
    #param and return: none
    def ante(self):
        for user, _ in self.players:
            ans = input("press 0 to put in your ante for the round, 1 to sit out of this round, and 2 to quit the game entirely")
            if ans == 0:
                if self.players[user].chips<10:
                    self.pot+=self.players[user].chips
                    self.players[user].chips = 0    
                else:
                    self.pot+=10
                    self.players[user].chip-=10
            elif ans == 1:
                self.playerz[user].fold = True
            elif ans == 2:
                del self.player[user]
        






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