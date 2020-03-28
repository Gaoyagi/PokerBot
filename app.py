from texasHold import TexasHold, Player
from twitter import Twitter

if __name__ == '__main__':
    gameRules = TexasHold()
    gameID = gameRules.deckID
    game = Twitter()
    game.game.deckID
    # for _ in range(4):
    #     name = ("imput player name: ")
    #     game.players[name] = Player(name)  
    game.game()