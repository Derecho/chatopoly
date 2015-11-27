import jsonpickle

from player import *
from board import *

class Game(object):
    def __init__(self):
        self.players = []
        self.board = Board()

    @staticmethod
    def from_savedata(savedata):
        obj = jsonpickle.decode(savedata)
        if isinstance(obj, Game):
            return obj
        return None

    def to_savedata(self):
        return jsonpickle.encode(self)

    def add_player(self, nick):
        if nick not in self.get_player_nicks():
            self.players.append(Player(nick))
            return True
        return False

    def get_player_nicks(self):
        return [player.nick for player in self.players]
