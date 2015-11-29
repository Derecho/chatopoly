# -*- coding: utf-8 -*-
import logging
import sqlite3
import os
import random
import datetime
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
            self.conn = sqlite3.connect(
                    os.path.join(cardinal.storage_path, "chatopoly-{}.db".format(cardinal.network)),
                    detect_types=sqlite3.PARSE_DECLTYPES
                    )
        except Exception:
            self.conn = None
            self.logger.exception("Unable to access local chatopoly database")
            return

        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS highscores ("
                "nick TEXT PRIMARY KEY, "
                "wins INTEGER)")
        c.execute("CREATE TABLE IF NOT EXISTS games ("
                "start timestamp PRIMARY KEY, "  # module-provided type, not pure sqlite
                "saved timestamp, "
                "state TEXT)")
        self.conn.commit()

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

        output = self.game.interactive_cb(cmd, msg.split(' '))

        for line in output:
            cardinal.sendMsg(channel, line)

        if not self.game.interactive_cb:
            self.state = ChatopolyState.INPROGRESS

    def _check_admin(self, nick):
        if self.config is not None:
            if self.config.has_key('admins'):
                if nick in self.config['admins']:
                    return True

        self.logger.warning("Admin check failed for: {}".format(nick))
        return False

    def _save_game(self):
        c = self.conn.cursor()
        c.execute("INSERT OR REPLACE INTO games (start, saved, state) VALUES("
                "?, ?, ?)", (
                    self.game.started, 
                    datetime.datetime.now(),
                    self.game.to_savedata()))
        self.conn.commit()
        self.logger.info("Game saved")

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
        self.logger.info("Starting new game with players: {}".format(
            " ".join(self.game.get_player_nicks())))

        if self.config is not None:
            if self.config.has_key('board_variant'):
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
            should_roll = False
            output = self.game.interactive_cb('roll', msg.split(' '))
        else:
            should_roll = True
            if self.config is not None:
                if self.config.has_key('god_mode') and self.config['god_mode']:
                    args = msg.split(' ')
                    if len(args) == (1 + len(self.game.dice)):
                        output = self.game.roll(map(int, args[1:]))
                        should_roll = False

        if should_roll:
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

    def pay(self, cardinal, user, channel, msg):
        self._interactive_cmd('pay', cardinal, user, channel, msg)
    pay.commands = ['pay']

    def save(self, cardinal, user, channel, msg):
        nick, ident, vhost = user.group(1), user.group(2), user.group(3)
        if ((self.state == ChatopolyState.IDLE) |
                (self.state == ChatopolyState.STARTING)):
            cardinal.sendMsg(channel, "{}: No game is running at the "
            "moment.".format(nick))
            return
        elif self.state == ChatopolyState.INTERACTIVE:
            cardinal.sendMsg(channel, "{}: You cannot save the game until the "
                    "current interaction with a player has finished.".format(
                        nick))
            return

        if not self._check_admin(nick):
            cardinal.sendMsg(channel, "{}: You are not permitted to execute "
                    "this command.".format(nick))
            return

        self._save_game()
        cardinal.sendMsg(channel, "Game has been saved to the database.")

    save.commands = ['save']
    save.help = ["Save the current gamestate to the database"]

    def listsaves(self, cardinal, user,channel, msg):
        nick, ident, vhost = user.group(1), user.group(2), user.group(3)
        if not self._check_admin(nick):
            cardinal.sendMsg(channel, "{}: You are not permitted to execute "
                    "this command.".format(nick))
            return

        cardinal.sendMsg(channel, "Listing games present in the database:")
        c = self.conn.cursor()
        c.execute("SELECT rowid, start, saved FROM games")
        for result in c.fetchall():
            cardinal.sendMsg(channel, "Game: {}, started: {}, "
                    "last saved: {}".format(
                        result[0],
                        result[1],
                        result[2]))

    listsaves.commands = ['listsaves', 'ls']
    listsaves.help = ["List saved games present in the database"]

def setup(cardinal, config):
    return ChatopolyPlugin(cardinal, config)
