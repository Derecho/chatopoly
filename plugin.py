# -*- coding: utf-8 -*-
import logging
import sqlite3
import os
import random
from enum import Enum

import chatopoly

ChatopolyState = Enum('ChatopolyState', 'IDLE STARTING INPROGRESS INTERACTIVE')

class ChatopolyPlugin(object):
    logger = None

    def __init__(self, cardinal, config):
        self.logger = logging.getLogger(__name__)
        self._connect_or_create_db(cardinal)

        self.config = config
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

        if self.config is not None:
            if self.config['board_variant']:
                self.game.prepare_board(config['board_variant'])

        if self.game.board == None:
            self.game.prepare_board('uk')

        self.game.current_player_id = random.randint(0, len(self.game.players)-1)
        cardinal.sendMsg(channel, "Game started, {} starts.".format(
            self.game.get_current_player().nick))

    start.commands = ['start']

    def roll(self, cardinal, user, channel, msg):
        nick, ident, vhost = user.group(1), user.group(2), user.group(3)
        if nick == channel:
            cardinal.sendMsg(channel, "This is a channel command.")
            return

        if ((self.state == ChatopolyState.IDLE) |
                (self.state == ChatopolyState.STARTING)):
            cardinal.sendMsg(channel, "{}: No game is running at the "
            "moment.".format(nick))
            return

        if nick not in [player.nick for player in self.game.players]:
            return

        if nick != self.game.get_current_player().nick:
            cardinal.sendMsg(channel, "{}: It is {}'s turn.".format(nick,
                self.game.get_current_player().nick))
            return

        if self.state == ChatopolyState.INTERACTIVE:
            output = self.game.interactive_cb('roll', msg)
        else:
            output = self.game.roll()

        for line in output:
            cardinal.sendMsg(channel, line)

        if self.game.interactive_cb:
            self.state = ChatopolyState.INTERACTIVE

    roll.commands = ['roll', 'r']
    roll.help = ["Roll the dice"]

    def yes(self, cardinal, user, channel, msg):
        self._interactive_cmd('yes', cardinal, user, channel, msg)
    yes.commands = ['yes', 'y']

    def no(self, cardinal, user, channel, msg):
        self._interactive_cmd('no', cardinal, user, channel, msg)
    no.commands = ['no', 'n']

    def _interactive_cmd(self, cmd, cardinal, user, channel, msg):
        nick, ident, vhost = user.group(1), user.group(2), user.group(3)
        if nick == channel:
            cardinal.sendMsg(channel, "This is a channel command.")
            return

        if nick not in [player.nick for player in self.game.players]:
            return

        if nick != self.game.get_current_player().nick:
            cardinal.sendMsg(channel, "{}: It is {}'s turn.".format(nick,
                self.game.get_current_player().nick))
            return

        if self.state != ChatopolyState.INTERACTIVE:
            cardinal.sendMsg(channel, "{}: Not a valid command.".format(nick))
            return

        output = self.game.interactive_cb(cmd, msg)

        for line in output:
            cardinal.sendMsg(channel, line)

        if not self.game.interactive_cb:
            self.state = ChatopolyState.INPROGRESS

def setup(cardinal, config):
    return ChatopolyPlugin(cardinal, config)
