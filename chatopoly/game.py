class Game(object):
    def __init__(self):
        self.players = []

    def add_player(self, nick):
        # TODO Player objects
        if nick not in self.players:
            self.players.append(nick)
            return True
        return False

    def get_player_nicks(self):
        # TODO Player objects
        return [nick for nick in self.players]
