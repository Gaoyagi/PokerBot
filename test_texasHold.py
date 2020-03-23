from texasHold import TexasHold
import requests

class TestTexasHold:
    def test_draw_to_pile(self):
        game = TexasHold()
        user = "test"
        game.draw_to_pile(2, user)
        req = requests.get("https://deckofcardsapi.com/api/deck/{}/pile/{}/list/".format(game.deckID, user))
        req = req.json()
        assert req["remaining"] == "50"
        assert len(req["piles"]["test"]["cards"]) == 2
    
    def test_add_player(self):
        game = TexasHold()
        user = "test"
        game.add_player(user)
        assert game.players[user] != None
        assert len(game.players[user].hand) == 2
    
    def test_river(self):
        game = TexasHold()
        game.river()
        req = requests.get("https://deckofcardsapi.com/api/deck/{}/pile/discard/list/".format(game.deckID))
        req = req.json()
        assert len(game.river) == 5
        assert len(req["piles"]["discard"]["cards"]) == 2
    
    def test_betting(self):
        game = TexasHold()

        #check or call assert cases
        user1 = "test1"
        game.add_player(user1)
        assert game.betting(0, game.players[user1], 0) == True      #player checks
        assert game.player[user1].chips == 200                      #make sure the players chips havent changed
        assert game.betting(0, game.players[user1], 100) == True    #player calls
        assert game.player[user1].chips == 100                      #make sure the appropriate chips were subtracted
        assert game.player[user1].bet == 100                        #make sure the player's bet increased accordingly
       
        #fold assert case:
        user2 = "test2"
        game.add_player(user2)
        assert game.betting(-2, game.players[user1], 0) == True     #make sur
        assert game.players[user2].fold == True                     #make sure the fold bool was changed

        #raising assert cases:
        user3 = "test3"
        game.add_player(user3)
        assert game.betting(100, game.players[user3], 150) == False   #invalid raise
        assert game.player[user3].chips == 200                        #make sur
        assert game.player[user3].bet == 0
        assert game.betting(160, game.players[user3], 150) == False   #valid raise
        assert game.player[user3].chips == 40                         #make sur
        assert game.player[user3].bet == 160
        
    def test_suits_and_values(self):
        game = TexasHold()
        hand =["AS", "KH", "QC", "JD", "10S"]
        suits = []
        values = []
        game.suits_and_values(hand, values, suits)
        assert values == ["A", "K", "Q", "J", "10"]
        assert suits == ["S", "H", "C", "D", "S"]

    def test_is_flush(self):
        game = TexasHold()
        assert game.is_flush(["S", "H", "C", "D", "S"]) == False
        assert game.is_flush(["S", "S", "S", "S", "S"]) == True

    

