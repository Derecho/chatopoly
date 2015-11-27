class Player(object):
    def __init__(self, nick):
        self.nick = nick
        self.balance = 1500
        self.properties = []
        self.jailcard = False
        self.last_roll = 0
