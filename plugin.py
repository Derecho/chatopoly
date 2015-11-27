import logging
import sqlite3
import os
from enum import Enum

import chatopoly

ChatopolyState = Enum('ChatopolyState', 'IDLE STARTING INPROGRESS')

class ChatopolyPlugin(object):
    logger = None

    def __init__(self, cardinal, config):
        self.logger = logging.getLogger(__name__)
        self._connect_or_create_db(cardinal)

        self.state = ChatopolyState.IDLE
        self.game = None

        self.logger.info("Chatopoly started")

    def _connect_or_create_db(self, cardinal):
        try:
            self.conn = sqlite3.connect(os.path.join(
                cardinal.storage_path,
                'chatopoly-%s.db' % cardinal.network
            ))
        except Exception:
            self.conn = None
            self.logger.exception("Unable to access local chatopoly database")
            return

        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS highscores ("
                  "nick TEXT PRIMARY KEY, "
                  "wins INTEGER)")
        c.execute("CREATE TABLE IF NOT EXISTS games ("
                  "id INTEGER PRIMARY KEY ASC, "
                  "start INTEGER, "
                  "saved INTEGER, "
                  "state TEXT)")
        self.conn.commit()

    def newgame(self, cardinal, user, channel, msg):
        nick, ident, vhost = user.group(1), user.group(2), user.group(3)
        if nick == channel:
            cardinal.sendMsg(channel, "This is a channel command.")
            return

        if self.state != ChatopolyState.IDLE:
            cardinal.sendMsg(channel, "{}: You can not start a new game "
                    "currently.".format(nick))
            return

        self.state = ChatopolyState.STARTING
        self.game = chatopoly.Game()
        cardinal.sendMsg(channel, "Setting up a new game. Please type .join "
                "to participate, followed by .start to commence.")

    newgame.commands = ['newgame']
    newgame.help = ["Starts a new game",
            "Chatopoly enters the game creation state after which players can "
            "join the new game before it commences."]

    def join(self, cardinal, user, channel, msg):
        nick, ident, vhost = user.group(1), user.group(2), user.group(3)
        if nick == channel:
            cardinal.sendMsg(channel, "This is a channel command.")
            return

        if self.state != ChatopolyState.STARTING:
            cardinal.sendMsg(channel, "{}: No game is being set up at the "
                    "moment.".format(nick))
            return

        if self.game.add_player(nick):
            cardinal.sendMsg(channel, "{}: You have succesfully joined the "
                "game.".format(nick))
        else:
            cardinal.sendMsg(channel, "{}: You have already joined the game"
                    .format(nick))

    join.commands = ['join', 'j']

    def start(self, cardinal, user, channel, msg):
        nick, ident, vhost = user.group(1), user.group(2), user.group(3)
        if nick == channel:
            cardinal.sendMsg(channel, "This is a channel command.")
            return

        if self.state != ChatopolyState.STARTING:
            cardinal.sendMsg(channel, "{}: No game is being set up at the "
                    "moment.".format(nick))
            return

        if nick not in self.game.get_player_nicks():
            cardinal.sendMsg(channel, "{}: You need to have joined in order to "
                    "start the game.".format(nick))
            return

        self.state = ChatopolyState.INPROGRESS
        self.logger.info("Started new game with players: {}".format(
            " ".join(self.game.get_player_nicks())))

        # TODO Actually start the game
    start.commands = ['start']

    def roll(self, cardinal, user, channel, msg):
        # TODO Replace stub
        nick, ident, vhost = user.group(1), user.group(2), user.group(3)
        cardinal.sendMsg(channel, "user: {}, channel: {}, message {}".format(nick, channel, msg))

    roll.commands = ['roll', 'r']
    roll.help = ["Roll the dice"]

def setup(cardinal, config):
    return ChatopolyPlugin(cardinal, config)
