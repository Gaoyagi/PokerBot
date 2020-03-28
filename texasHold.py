import requests 

class Player(object):
    def __init__(self, user=""):
        self.hand = []          #holds the card codes for what cards are in your hands
        self.chips = 200        #total chips a player has
        self.user = user        #makes the "name" of the user
        self.fold = False       #bool flag for if the player has folded a round
        self.bet = 0            #int counter for how much a player has bet this round
        self.strength = (10,)   #a tuple for what the strength of your hand is

class TexasHold(object):
    def __init__(self):
        self.players = {}                       #dic of player objects in this game
        self.river = []                         #set of face up cards for the round
        self.pot = 0                            #current pot for the the round
        self.currBet = 0                        #the amount each player should have in the pot
        self.deck = requests.get("https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1")    #gets API request for a new deck 
        self.deck = self.deck.json()            #coverts api request to json
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
        
    #adds all the players to the game
    #param: user(a list of strings of players twitter handles)
    #return: dictionary of player objects
    def add_players(self, users):
        players = {}
        for name in users:
            players[name] = Player(name)
        return players
            
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
    #param: deckID(deck ID for this game)
    #return: list of card codes that makes up the river
    def make_river(self, deckID):
        self.draw_to_pile(3, "discard")
        self.draw_to_pile(5, "river")
        faceUp = requests.get("https://deckofcardsapi.com/api/deck/{}/pile/{}/list/".format(deckID, "river"))
        faceUp = faceUp.json()
        river = []
        for card in faceUp["piles"]["river"]["cards"]:
            river.append(card["code"])
        return river

    #running a round texas hold em
    #param: deck(api request for a deck object), deckID(id for a deck used for api requests), players(ditionary of all players in the game)
    #       currBet(int of how muche each player should have bet this round), pot(int for the total bet in the round), 
    #       river(list of card codes that make up the river for this round)
    #return: none
    def round(self, deck, deckID, players, currBet, pot, river):
        #check of the deck has enouch cards left for a full round and if not reshuffle
        if self.deck["remaining"] < 16:
            requests.get("https://deckofcardsapi.com/api/deck/{}/shuffle/".format(self.deckID))
        #only deals all the players in if they paid the ante and then adds them to an active users list
        active = []     #list to hold all the users of active in the round
        for key in self.players:
            if self.players[key].fold == False:
                self.deal_player(key)
                print(f"{key}'s hand is: {self.players[key].hand}")
                active.append(key)

        self.betting_phase(active, self.players, self.currBet)              #betting phase 1
        #make the river 
        self.river = self.make_river(self.deckID)
        tempRiver = []
        # reveal the first 3 cards phase
        for x in range(3):
            tempRiver.append(self.river[x])
        print("\nThe Flop: ")
        print(tempRiver)
        self.print_hands(active, self.players)
        self.betting_phase(active, self.players, self.currBet)              #betting phase 2
        #reveal the 4th card phase
        tempRiver.append(self.river[3])
        print("\nThe Turn: ")
        print(tempRiver)
        self.print_hands(active, self.players)
        self.betting_phase(active, self.players, self.currBet)              #betting phase 3 (last)
        #reveal 5th card phase
        tempRiver.append(self.river[4])
        print("\nThe River: ")
        print(tempRiver)
        self.print_hands(active, self.players)
        strongest = self.strongest_player(active, self.players, self.river)
        #ending the round and  declaring the winner,giving them the chips from the pot
        print(f"the winner of this round is {strongest.user}, with {strongest.strength[len(strongest.strength)-1]} and has won {self.pot} chips!\n")
        strongest.chips+=self.pot
        self.round_reset(active)
    
    #prints out all active player hands
    #param: activePlayers(list of active players usernames), players(dictionary of all the player objects in game)
    #return: none
    def print_hands(self, activePlayers, players):
        for key in activePlayers:
            if players[key].fold == False:
                print(f"{key}'s hand: {players[key].hand}")

    #function that handles the betting phase
    #param: activePlayers(list of active players usernames), players(dictionary of all the player objects in game), 
    #       currBet(int of how much each player should have in the pot), pot(int of the total pot amount)
    #return: none
    def betting_phase(self, activePlayers, players, currBet):
        done = False
        timesBet=0
        #keep betting until all is done
        while not done:
            done = True
            #go through each player that hasnt folded and to get their bets
            for user in activePlayers:
                #players can only bet if they have chips (if a player went all in before they also get skipped)
                if players[user].chips!=0:
                    #check if the players current bet matches the round's current bet AND everyone in this betting phase has had a chance to bet already
                    if players[user].bet == currBet and timesBet>len(activePlayers)-1:
                        continue
                    #ask for user input for bet, only will take num >= -1
                    valid = False
                    #player inputs bet and then program checks if bet is above the bet as a whole
                    while not valid:
                        print(f"\ncurrent bet per person: {currBet}")
                        print(f"current pot: {self.pot}")
                        print(f"{user} current chips: {players[user].chips}")
                        print(f"{user}'s current bet: {players[user].bet}")
                        value = input(f"({user}): enter your bet (0 to check or call, -1 to fold, other to raise): ")
                        valid = self.betting(int(value), players[user], currBet)     
                    #if everyone has gotten a chance to bet at least once and there is a raise, then continue the betting loop
                    if players[user].bet>currBet:
                        done = False
                    currBet = players[user].bet
                    timesBet+=1 
    
    #checks if a player bet is a call, raise, check, or a fold. then changes the pot and player's bet accordingly
    #param: value(amount number that theyre betting), player(player object who is betting), 
    #       currBet(current bet per player in this round). pot(total amount bet for this rounf)
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
            elif value == "0":
                value = 10

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
                                            #print("Possible", possible)
                                            strength = self.hand_value(possible.copy())    #calculate current hand strength
                                            strengths.append(strength)       #add the strength to strengths list
                                            # print("Appending", strength)
                                            del possible[len(possible)-1]
                                    del possible[len(possible)-1]
                            del possible[len(possible)-1]
                    del possible[len(possible)-1]
            del possible[len(possible)-1]
        #check to find the strongest possible combo 
        # print(strengths)
        strongest = strengths[0]
        # print("First strongest", strongest)
        for combo in strengths:
            # print("Combo", combo)
            #check if the ranking of the strength is lower  (lower is stronger)
            if strongest[0] > combo[0]:
                strongest = combo
            #if tie, check the strength of each other hand's high card
            elif strongest[0] ==  combo[0]:
                if strongest[1] < combo[1]:
                    strongest = combo
        # print(strongest)
        return strongest

    #finds the player with the strongest hand
    #param: activePlayers(list of username strings in this round), players(dictionary of all the player objects in the game), river(lsit of card codes in the round's river)
    #return: player object with the strongest hand
    def strongest_player(self, activePlayers, players, river):
        strongest = Player("temp")  #place holder for strongest player
        #go through each active player and see which one has the best hand
        for user in activePlayers:
            strength = self.optimal_hand(players[user].hand, river)   #current player's strength
            self.players[user].strength = strength
            #compare by hand type strength first
            if strength[0] < strongest.strength[0]:
                strongest = players[user]      #reassign strongest if current strength is stronger
            #if the hand strength ties, check which one has the highest card then reassign
            elif strength[0] == strongest.strength[0]:
                if strength[1]>strongest.strength[1]:
                    strongest = players[user]
                #if the first hgih card check ties then check the other high card, this case only applies to 2 pairs and pairs
                elif strength[1] == strongest.strength[1]:
                    if strength[2]>strongest.strength[2]:
                        strongest = players[user]
        return strongest    
        
    #function to reset values and clear hands after a round ends
    #param: activePlayer(lsit of players partaking in the round)
    #return: none
    def round_reset(self, activePlayers):
        self.currBet = 0
        #looping through each player to: clear his hand, reset the fold bool, reset player bet for the round
        for player in activePlayers:
            self.players[player].bet = 0
            self.players[player].fold = False
            #moves cards from player hands pile to the discard pile
            toEmpty = requests.get("https://deckofcardsapi.com/api/deck/{}/pile/{}/draw/?count=2".format(self.deckID, self.players[player].user))
            toEmpty = toEmpty.json()
            for card in toEmpty["cards"]:
                requests.get("https://deckofcardsapi.com/api/deck/{}/pile/discard/add/?cards={}".format(self.deckID, card["code"]))
            self.players[player].hand.clear()
        #clear the river
        riverEmpty = requests.get("https://deckofcardsapi.com/api/deck/{}/pile/river/draw/?count=2".format(self.deckID))
        riverEmpty = riverEmpty.json()
        for card in riverEmpty["cards"]:
            requests.get("https://deckofcardsapi.com/api/deck/{}/pile/discard/add/?cards={}".format(self.deckID, card["code"]))
        self.river.clear()

    #function that will run multiple rounds of the game, game only ends if 1 person remains
    #param and return: none
    def game(self):
        going = True
        users = ["player1", "player2", "player3", "player3", "player3", "player4"]
        game.players = self.add_players(users)
        while going:
            self.ante(self.players)
            if len(self.players)<1:
                print("not enough people, game ending")
                break
            self.round(self.deck, self.deckID, self.players, self.currBet, self.pot, self.river)
            #find players with 0 chips and remove them from the game
            delete = []
            for user in self.players:
                if self.players[user].chips == 0:
                    delete.append(user)
            for user in delete:
                del self.players[user]
            #if the amount of players is less than 2 then the game's over
            if len(self.players)<2:
                going = False
            
    #deals with player's ante'ing in to enter a round
    #param: players(dic of all player objects in the game), pot(int of the total chips bet)
    #return: none
    def ante(self, players):
        remove = []
        for user in players:
            invalid = True
            while invalid:
                ans = input(f"({user}): press 0 to put in your ante (10 chips) for the round, 1 to sit out of this round, and 2 to quit the game entirely: ")
                invalid = False
                ans = int(ans)
                if ans == 0:
                    if players[user].chips<10:
                        self.pot+=players[user].chips
                        players[user].chips = 0    
                    else:
                        self.pot+=10
                        players[user].chips-=10
                elif ans == 1:
                    players[user].fold = True
                elif ans == 2:
                    remove.append(user)
                else:
                    print("not a valid option")
                    invalid = True
        for user in remove:
            del players[user]
        






#notes: shuffling/reshuffling takes all the cards from the pile and puts them back into the main deck
#       you can draw specific cards  isntead of jsut a general number
#       you cant add cards directly to the deck



if __name__ == '__main__':
    game = TexasHold()
    game.game()
    