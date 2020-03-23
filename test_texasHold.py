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
        assert game.players[user].chips == 200
        assert game.players[user].user == user
        assert game.players[user].fold == False
        assert game.players[user].bet == 0
        assert game.players[user].strength == None
    
    def test_river(self):
        game = TexasHold()
        game.make_river()
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
        assert game.players[user1].chips == 200                      #make sure the players chips havent changed
        assert game.betting(0, game.players[user1], 100) == True    #player calls
        assert game.players[user1].chips == 100                      #make sure the appropriate chips were subtracted
        assert game.players[user1].bet == 100                        #make sure the player's bet increased accordingly
       
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
        hand =["AS", "KH", "QC", "JD", "10S"]
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
        test4 = game.num_of_a_kind([14, 14, 10, 10, 10])    #full house
        test5 = game.num_of_a_kind([14, 14, 12, 11, 10])    #pair
        test6 = game.num_of_a_kind([14, 14, 12, 12, 10])    #2 pair
        
        #high card tests
        assert len(test1) == 1
        assert test1[0] == 14

        # 4 of a kind tests
        assert len(test2) == 1
        assert test2[0][0] == "quad"
        assert test2[0][1] == 14

        #triples tests
        assert len(test3) == 1
        assert test3[0][0] == "triple"
        assert test3[0][1] == 14

        #full house tests
        assert len(test4) == 2
        assert test4[0][0] == "triple"
        assert test4[0][1] == 10
        assert test4[1][0] == "pair"
        assert test4[1][1] == 14

        #pair tests
        assert len(test5) == 1
        assert test5[0][0] == "pair"
        assert test5[0][1] == 14

        #2 pair tests
        assert len(test6) == 1
        assert test6[0][0] == "pair"
        assert test6[0][1] == 12
        assert test6[1][0] == "pair"
        assert test6[1][1] == 14
