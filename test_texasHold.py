from texasHold import TexasHold, Player
import requests

class TestTexasHold:
    def test_draw_to_pile(self):
        game = TexasHold()
        user = "test"
        game.draw_to_pile(2, user)
        req = requests.get("https://deckofcardsapi.com/api/deck/{}/pile/{}/list/".format(game.deckID, user))
        req = req.json()
        assert req["remaining"] == 50
        assert len(req["piles"]["test"]["cards"]) == 2
    
    def test_deal_player(self):
        game = TexasHold()
        user = "test"
        game.players[user] = Player(user)
        game.deal_player(user)
        assert game.players[user] != None
        assert len(game.players[user].hand) == 2
        print(game.players[user].hand)
        assert game.players[user].chips == 200
        assert game.players[user].user == user
        assert game.players[user].fold == False
        assert game.players[user].bet == 0
        assert game.players[user].strength[0] == 10
    
    def test_make_river(self):
        game = TexasHold()
        game.river = game.make_river(game.deckID)
        req = requests.get("https://deckofcardsapi.com/api/deck/{}/pile/discard/list/".format(game.deckID))
        req = req.json()
        assert len(game.river) == 5
        assert len(req["piles"]["discard"]["cards"]) == 3
    
    def test_betting(self):
        game = TexasHold()
        user1 = "test1"
        game.players[user1] = Player(user1)
        #check or call assert cases
        game.deal_player(user1)
        assert game.betting(0, game.players[user1], 0) == True      #player checks
        assert game.players[user1].chips == 200                     #make sure the players chips havent changed
        assert game.betting(0, game.players[user1], 100) == True    #player calls
        assert game.players[user1].chips == 100                     #make sure the appropriate chips were subtracted
        assert game.players[user1].bet == 100                       #make sure the player's bet increased accordingly
       
        #fold assert case:
        user2 = "test2"
        game.players[user2] = Player(user2)
        game.deal_player(user2)
        assert game.betting(-1, game.players[user2], 0) == True     #make sur
        assert game.players[user2].fold == True                     #make sure the fold bool was changed

        #raising assert cases:
        user3 = "test3"
        game.players[user3] = Player(user3)
        game.deal_player(user3)
        assert game.betting(100, game.players[user3], 150) == False   #invalid raise
        assert game.players[user3].chips == 200                        #make sur
        assert game.players[user3].bet == 0
        assert game.betting(160, game.players[user3], 150) == True   #valid raise
        assert game.players[user3].chips == 40                         #make sur
        assert game.players[user3].bet == 160
        
    def test_suits_and_values(self):
        game = TexasHold()
        hand =["AS", "KH", "QC", "JD", "0S"]
        suits = []
        values = []
        game.suits_and_values(hand, values, suits)
        assert values == [14, 13, 12, 11, 10]
        assert suits == ["S", "H", "C", "D", "S"]

    def test_is_flush(self):
        game = TexasHold()
        assert game.is_flush(["S", "H", "C", "D", "S"]) == False
        assert game.is_flush(["S", "S", "S", "S", "S"]) == True

    def test_is_straight(self):
        game = TexasHold()
        test1 = game.is_straight([14, 13, 12, 11, 10])
        assert test1[0] == True
        assert test1[1] == 14
        test1 = game.is_straight([10, 9, 4, 3, 2])
        assert test1[0] == False
        assert test1[1] == 10

    def test_num_of_a_kind(self):
        game = TexasHold()
        test1 = game.num_of_a_kind([14, 13, 12, 11, 10])    #high card only
        test2 = game.num_of_a_kind([14, 14, 14, 14, 10])    #4 of a kind
        test3 = game.num_of_a_kind([14, 14, 14, 11, 10])    #triples
        test4 = game.num_of_a_kind([14, 14, 10, 10, 10])    #full house ver 1
        test5 = game.num_of_a_kind([14, 14, 14, 10, 10])    #full house ver 2
        test6 = game.num_of_a_kind([14, 14, 12, 11, 10])    #pair
        test7 = game.num_of_a_kind([14, 14, 12, 12, 10])    #2 pair
        
        #high card tests
        assert len(test1) == 1
        assert test1[0][1] == 14

        #4 of a kind tests
        assert len(test2) == 1
        assert test2[0][0] == "quad"
        assert test2[0][1] == 14

        #triples tests
        assert len(test3) == 1
        assert test3[0][0] == "triple"
        assert test3[0][1] == 14

        #full house ver 1 tests 
        assert len(test4) == 2
        assert test4[0][0] == "triple"
        assert test4[0][1] == 10
        assert test4[1][0] == "pair"
        assert test4[1][1] == 14

        #full house ver 2 tests 
        assert len(test5) == 2
        assert test5[0][0] == "pair"
        assert test5[0][1] == 10
        assert test5[1][0] == "triple"
        assert test5[1][1] == 14

        #pair tests
        assert len(test6) == 1
        assert test6[0][0] == "pair"
        assert test6[0][1] == 14

        #2 pair tests
        assert len(test7) == 2
        assert test7[0][0] == "pair"
        assert test7[0][1] == 12
        assert test7[1][0] == "pair"
        assert test7[1][1] == 14

    def test_hand_value(self):
        game = TexasHold()
        test1 = game.hand_value(["0S", "9S", "8S", "7S", "6S"])    #straight flush
        test2 = game.hand_value(["AS", "AH", "AD", "AC", "0S"])    #4 of a kind
        test3 = game.hand_value(["2S", "2C", "2D", "0S", "0D"])   #full house version 2
        test4 = game.hand_value(["AS", "4S", "2S", "2D", "4D"])     #2 pair
        test5 = game.hand_value(["AS", "2S", "6S", "8S", "9S"])     #flush
        test6 = game.hand_value(["4D", "3C", "5C", "6H", "7S"])     #straight 
        test7 = game.hand_value(["9D", "7S", "7S", "7S", "8C"])     #triples
        test8 = game.hand_value(["9H", "6S", "2C", "0S", "6H"])    #pair
        test9 = game.hand_value(["0S", "4H", "2C", "JS", "QD"])    #high card

        #tests straight flush
        assert test1[0] == 1
        assert test1[1] == 10
        assert test1[2] == ["0S", "9S", "8S", "7S", "6S"]

        #tests for 4 of a kind
        assert test2[0] == 2
        assert test2[1] == 14
        assert test2[2] == ["AS", "AH", "AD", "AC", "0S"]

        #tests for full house 
        assert test3[0] == 3
        assert test3[1] == 2
        assert test3[2] == ["2S", "2C", "2D", "0S", "0D"]

        #tests for 2 pair
        assert test4[0] == 7
        assert test4[1] == 2
        assert test4[2] == 4
        assert test4[3] == ["AS", "4S", "2S", "2D", "4D"]

        #tests for flush
        assert test5[0] == 4
        assert test5[1] == ["AS", "2S", "6S", "8S", "9S"]

        #tests for straight
        assert test6[0] == 5
        assert test6[1] == 7
        assert test6[2] == ["4D", "3C", "5C", "6H", "7S"]

        #tests triples
        assert test7[0] == 6
        assert test7[1] == 7
        assert test7[2] == ["9D", "7S", "7S", "7S", "8C"]

        #tests pairs
        assert test8[0] == 8
        assert test8[1] == 6
        assert test8[2] == 10
        assert test8[3] == ["9H", "6S", "2C", "0S", "6H"]

        #tests high card
        assert test9[0] == 9
        assert test9[1] == 12
        assert test9[2] == ["0S", "4H", "2C", "JS", "QD"]

    def test_optimal_hand(self):
        game = TexasHold()
        #pair
        hand1 = ["3S", "QC"]
        river1 = ["2C", "0C", "5H", "2D", "6H"]
        str1 = game.optimal_hand(hand1, river1)
        print(str1)

        #triples
        hand2 = ["KC", "5H"]
        river2 = ["4H", "3C", "8H", "5D", "5S"]
        str2 = game.optimal_hand(hand2, river2)
        print(str2)

        #2 pair 
        hand3 = ['3C', '5S']
        river3 = ['9C', 'JD', '6D', '3D', '9H']
        str3 = game.optimal_hand(hand3, river3)
        print(str3)

        #flush 
        hand4 = ["5C", "0H"]
        river4 = ["4H", "3H", "8H", "6H", "6S"]
        str4 = game.optimal_hand(hand4, river4)
        print(str4)

        #straight 
        hand5 = ["5C", "5H"]
        river5 = ["4H", "3C", "8H", "6D", "7S"]
        str5 = game.optimal_hand(hand5, river5)
        print(str5)

        #pair test
        assert len(str1) == 4
        assert str1[0] == 8
        assert str1[1] == 2
        assert str1[2] == 12
        assert '2C' in str1[3]
        assert '2D' in str1[3]

        #triples test
        assert len(str2) == 3
        assert str2[0] == 6
        assert str2[1] == 5

        #2 pair test
        assert len(str3) == 4
        assert str3[0] == 7
        assert str3[1] == 3
        assert str3[2] == 9

        #flush
        assert len(str4) == 2
        assert str4[0] == 4

        #straight
        assert len(str5) == 3
        assert str5[0] == 5
        assert str5[1] == 8

    def test_strongest_player(self):
        game = TexasHold()
        #create 2 sample users
        user1 = "test1"
        game.players[user1] = Player(user1)
        user2 = "test2"
        game.players[user2] = Player(user2)
        active = ["test1", "test2"]    #list of active users in the game
        #give each sample player a hand and make a sample river
        game.players[user1].hand = ['3C', '5S'] #should have 2 pair
        game.players[user2].hand = ['KH', '4S'] #should have a pair
        game.river = ['9C', 'JD', '6D', '3D', '9H']
    
        print(game.optimal_hand(game.players[user1].hand, game.river))
        print(game.optimal_hand(game.players[user2].hand, game.river))
        temp = game.strongest_player(active, game.players, game.river)
        print(temp.strength)

        assert temp == game.players[user1]  #strongest should be user1
