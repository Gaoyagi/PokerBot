import requests 

class Player(object):
    def __init__(self, user=""):
        self.hand = []          #holds the card codes for what cards are in your hands
        self.chips = 200        #total chips a player has
        self.user = user        #makes the "name" of the user
        self.fold = False       #bool flag for if the player has folded a round
        self.bet = 0            #int counter for how much a player has bet this round
        self.strength = None    #a tuple for what the strength of your hand is

class TexasHold(object):
    def __init__(self):
        self.players = {}     #dic of player objects in this game
        self.gameID = 0       #game ID is equivalent to the tweet ID
        self.river = []       #set of face up cards for the round
        self.pot = 0          #current pot for the the round
        self.currBet = 0      #the amount each player should have in the pot
        self.deck = requests.get("https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1")    #gets API request for a new deck 
        self.deck = self.deck.json()    #coverts api request to json
        self.deckID = self.deck["deck_id"]      #deck ID

    #draws a card from a deck or a pile and adds it to another pile
    #param: num(number of cards you want to draw), pile(pile name that you want to put the cards)
    #return: none
    def draw_to_pile(self, num, pile):
        #sends API request to draw cards and converts response to json dic
        drawn = requests.get("https://deckofcardsapi.com/api/deck/{}/draw/?count={}".format(self.deckID, num))
        drawn = drawn.json()
        #goes through the drawn cards and adds it to pile
        for card in drawn["cards"]: 
            requests.get("https://deckofcardsapi.com/api/deck/{}/pile/{}/add/?cards={}".format(self.deckID, pile, card["code"]))
        
    #deals a player into this round
    #param: user(twitter user name/id string)
    #return: none
    def deal_player(self, user):
        #draws cards and adds it to the players hand pile
        self.draw_to_pile(2, user)
        #adds the card codes to the players hand list
        req = requests.get("https://deckofcardsapi.com/api/deck/{}/pile/{}/list/".format(self.deckID, user))
        req = req.json()
        for card in req["piles"][user]["cards"]:
            self.players[user].hand.append(card["code"])

    #draws the 5 cards for the river and burns 3 cards to discard
    #param: none
    #return: none
    def make_river(self):
        self.draw_to_pile(3, "discard")
        self.draw_to_pile(5, "river")
        faceUp = requests.get("https://deckofcardsapi.com/api/deck/{}/pile/{}/list/".format(self.deckID, "river"))
        faceUp = faceUp.json()
        for card in faceUp["piles"]["river"]["cards"]:
            self.river.append(card["code"])

    #running a round texas hold em
    #param & return: none
    def round(self):
        #check of the deck has enouch cards left for a full round and if not reshuffle
        if self.deck["remaining"] < 16:
            requests.get("https://deckofcardsapi.com/api/deck/{}/shuffle/".format(self.deckID))
        active = []
        #only deals all the players in if they paid the ante
        for key in self.players:
            if self.players[key].fold == False:
                self.deal_player(key)
                print(f"{key}'s hand is: {self.players[key].hand}")
                active.append(key)

        self.betting_phase(active)              #betting phase 1
        #make the river 
        self.make_river()
        # reveal the first 3 cards
        for x in range(3):
            print(self.river[x] + " ")
        self.betting_phase(active)              #betting phase 2
        for x in range(4):
            print(self.river[x] + " ")
        self.betting_phase(active)              #betting phase 3 (last)
        for x in range(5):
            print(self.river[x] + " ")
        strongest = Player()
        #go through each player and see which one has the best hand
        for player in self.players:
            strength = self.optimal_hand(player.hand, self.river)
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
    
    #function that handles the betting phase
    #param & return: none
    def betting_phase(self, activePlayers):
        done = False
        #keep betting until all is done
        while not done:
            done = True
            #go through each player that hasnt folded and to get their bets
            print(activePlayers)
            for user in activePlayers:
                #players can only bet if they have chips (if a player goes all in they get skipped)
                if self.players[user].chips!=0:
                    #ask for user input for bet, only will take num >= -1
                    valid = False
                    #player inputs bet and then program checks if bet is above the bet as a whole
                    while not valid:
                        print(f"\ncurrent bet per person: {self.currBet}")
                        print(f"{user} current chips: {self.players[user].chips}")
                        print(f"{user}'s current bet: {self.players[user].bet}")
                        value = input(f"({user}): enter your bet (0 to check or call, -1 to fold, other to raise): ")
                        valid = self.betting(int(value), self.players[user], self.currBet)     
                    #if everyone has gotten a chance to bet at least once and there is a raise, then continue the betting loop
                    if self.players[user].bet>self.currBet:
                        done = False
                    self.currBet = self.players[user].bet
    
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
                print(f"you only have {player.chips}")
                return False
            #if the bet is either too low or it only calls the bet then return false
            if player.bet+value <= currBet:
                print("invalid raise, bet too low")
                return False
            #player has to raise so his bet will be greater than the current bet
            player.bet+=value
            self.pot+=value
            player.chips-=value
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
        self.suits_and_values(hand, values, suits)

        flush = self.is_flush(suits)
        straight = self.is_straight(values)
        numOfAKind = self.num_of_a_kind(values)

        #check if its a straight flush
        if flush and straight[0]:
            return (1, straight[1], hand)
        #check if its a 4 of a kind
        elif numOfAKind[0][0] == "quad":
            return (2, numOfAKind[0][1], hand)
        #check for full house and 2 pair, 
        elif len(numOfAKind)>1:
            #full house 1st check, gives back high card of triple
            if numOfAKind[0][0] == "pair" and numOfAKind[1][0] == "triple":
                return (3, numOfAKind[1][1], hand)
            #full house 2nd check, gives back high cardof triple
            elif numOfAKind[0][0] == "triple" and numOfAKind[1][0] == "pair":
                return (3, numOfAKind[0][1], hand)
            #check for 2 pair, gives back the high values of both pairs
            elif numOfAKind[0][0] == "pair" and numOfAKind[1][0] == "pair":
                return (7, numOfAKind[0][1], numOfAKind[1][1], hand)
        #check of the hand is a flush
        elif flush:
            return (4, hand)
        #check for straight
        elif straight[0]:
            return (5, straight[1], hand)
        #check for triples
        elif numOfAKind[0][0] == "triple":
            return (6, numOfAKind[0][1], hand)
        #check for a pair, returns an extra int for high card in case the pair's tie
        elif numOfAKind[0][0] == "pair":
            values.sort(reverse=True)
            return (8, numOfAKind[0][1], values[0], hand)
        #check for high card
        values.sort(reverse=True)
        return (9, values[0], hand)
        
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
            #check if the value is a 10
            if card[1] == "0":
                value = 10
                suits.append(card[2])       #add to the list of hand suits
            else:
                suits.append(card[1])       #add to the list of hand suits
            values.append(int(value))   #add to the list of hand values

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
        hand.sort()
        for x in range(len(hand)):
            if x!=len(hand)-1 and hand[x+1] != hand[x]+1:
                return [False, hand[len(hand)-1]]
        return [True, hand[len(hand)-1]]

    #checks if your hand has any pairs, triples, or quads
    #param:hand(list of ints of all the hand values)
    #return: a list(value) of tuples contatining if its a quad,tiple, or a pair, and what value it is
    def num_of_a_kind(self, hand):
        value = []
        alreadyFound = []
        hand.sort()
        #go through every value in the hand to find duplicates
        for x in range(len(hand)):
            sameCard = 0
            #avoid finding __ of a kind for the same value
            if hand[x] not in alreadyFound:
                for y in range(len(hand)):
                    if y!=x and hand[x] == hand[y]:
                        sameCard+=1
            alreadyFound.append(hand[x])    #add that number to list of numbers you dont need to use anymore
            if sameCard == 3:
                value.append(("quad", hand[x]))
                return value
            elif sameCard == 2:
                value.append(("triple", hand[x]))
            elif sameCard == 1:
                value.append(("pair", hand[x]))
        if len(value) == 0:
            value.append(("high card", hand[len(hand)-1]))

        return value
    
    #goes through every combination to find the strongest hand for a player
    #param: hand(list of the players card codes) and River(list of the card codes in the river)
    #return: Tuple(contining the hand strength and the highest value card in that combo)
    def optimal_hand(self, hand, river):
        strengths = []                  #list of every possible hand strength
        available = hand+river          #cards that available to make a hand out of
        possible = []                   #current iteration of the possible 5 card combination
        #loop through every 5 hand card combination
        for a in range(len(available)):
            possible.append(available[a])                                      #append 1st card
            for b in range(len(available)):
                if b!=a:
                    possible.append(available[b])                              #append 2nd card
                    for c in range(len(river)):
                        if c!=b and c!=a:
                            possible.append(available[c])                       #append 3rd card 
                            for d in range(len(river)):
                                #make sure you arent testing a card being currently used
                                if d!=c and d!=b and d!=a:
                                    possible.append(available[d])               #append 4th card
                                    for e in range(len(river)):
                                        #make sure you arent testing a card being currently used
                                        if e!=d and e!=c and e!=b and e!=a:
                                            possible.append(available[e])       #append 5th card
                                            strength = self.hand_value(possible)    #calculate current hand strength
                                            strengths.append(strength)       #add the strength to strengths list
            possible.clear()    #clears the current possible hand
        print(strengths)
        #check to find the strongest possible combo 
        strongest = strengths[0]
        for combo in strengths:
            #check if the ranking of the strength is lower  (lower is stronger)
            if strongest[0] > combo[0]:
                strongest = combo
            #if tie, check the strength of each other hand's high card
            elif strongest[0] ==  combo[0]:
                if strongest[1] < combo[1]:
                    strongest = combo
        return strongest

    #function to reset values and clear hands after a round ends
    def round_reset(self):
        #looping through each player to: clear his hand, reset the fold bool, reset player bet for the round
        for player in self.players:
            player.bet = 0
            player.fold = False
            #moves cards from player hands pile to the discard pile
            toEmpty = requests.get("https://deckofcardsapi.com/api/deck/{}/pile/{}/draw/?count=2".format(self.deckID, player.user))
            toEmpty = toEmpty.json()
            for card in toEmpty["piles"][player.user]["cards"]:
                requests.get("https://deckofcardsapi.com/api/deck/{}/pile/discard/add/?cards={}".format(self.deckID, card["code"]))
            player.hand.clear()
        #clear the river
        riverEmpty = requests.get("https://deckofcardsapi.com/api/deck/{}/pile/river/draw/?count=2".format(self.deckID))
        riverEmpty = riverEmpty.json()
        for card in riverEmpty["piles"]["river"]["cards"]:
            requests.get("https://deckofcardsapi.com/api/deck/{}/pile/discard/add/?cards={}".format(self.deckID, card["code"]))
        self.river.clear()

    #function that will run multiple rounds of the game, game only ends if 
    def game(self):
        going = True
        self.players["player1"] = Player("player1")
        self.players["player2"] = Player("player2")
        self.players["player3"] = Player("player3")
        self.players["player4"] = Player("player4")  
        while going:
            self.ante()
            self.round()
            for user in self.players:
                if self.players[user].chips == 0:
                    del self.players[user]
            if len(self.players<2):
                going = False
            
    #deals with player's ante'ing in to enter a round
    #param and return: none
    def ante(self):
        remove = []
        for user in self.players:
            invalid = True
            while invalid:
                ans = input(f"({user}): press 0 to put in your ante (10 chips) for the round, 1 to sit out of this round, and 2 to quit the game entirely: ")
                invalid = False
                ans = int(ans)
                if ans == 0:
                    if self.players[user].chips<10:
                        self.pot+=self.players[user].chips
                        self.players[user].chips = 0    
                    else:
                        self.pot+=10
                        self.players[user].chips-=10
                elif ans == 1:
                    self.players[user].fold = True
                elif ans == 2:
                    remove.append(user)
                else:
                    print("not a valid option")
                    invalid = True
        for user in remove:
            del self.players[user]
        






#notes: shuffling/reshuffling takes all the cards from the pile and puts them back into the main deck
#       you can draw specific cards  isntead of jsut a general number
#       you cant add cards directly to the deck



if __name__ == '__main__':
    game = TexasHold()
    # for _ in range(4):
    #     name = ("imput player name: ")
    #     game.players[name] = Player(name)  
    game.game()
    