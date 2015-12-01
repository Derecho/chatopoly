#) -*- coding: utf-8 -*-
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
            self.game.prepare_board('us')

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

    def load(self, cardinal, user, channel, msg):
        nick, ident, vhost = user.group(1), user.group(2), user.group(3)
        if not self._check_admin(nick):
            cardinal.sendMsg(channel, "{}: You are not permitted to execute "
                    "this command.".format(nick))
            return

        args = msg.split(' ')
        if len(args) != 2:
            cardinal.sendMsg(channel, "{}: Usage: 'load <id>'".format(nick))
            return

        c = self.conn.cursor()
        c.execute("SELECT state FROM games WHERE rowid = ?", (args[1],))
        result = c.fetchone()

        if not result:
            cardinal.sendMsg(channel, "{}: Failed to find game".format(nick))
            return

        self.state = ChatopolyState.INPROGRESS
        self.game = chatopoly.Game.from_savedata(result[0])

        self.logger.info("Loading game: {}".format(self.game.started))
        current_player = self.game.get_current_player()
        cardinal.sendMsg(channel, "Game {} loaded. "
                "It is {}'s turn (at {} with {}{}).".format(
                    self.game.started,
                    current_player.nick,
                    self.game.board.tiles[current_player.position].name,
                    self.game.board.cursymbol,
                    current_player.balance))

    load.commands = ['load']
    load.help = ["Load a gamestate from the database"]

    def listsaves(self, cardinal, user, channel, msg):
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
    
    def holdings(self, cardinal, user, channel, msg):
        nick, ident, vhost = user.group(1), user.group(2), user.group(3)

        if ((self.state == ChatopolyState.IDLE) |
                (self.state == ChatopolyState.STARTING)):
            cardinal.sendMsg(channel, "{}: No game is running at the "
            "moment.".format(nick))
            return

        if nick not in [player.nick for player in self.game.players]:
            return

        # If in channel, only player whose turn it is can run this command
        if nick != channel:
            if nick != self.game.get_current_player().nick:
                cardinal.sendMsg(channel, "{}: It is {}'s turn.".format(nick,
                    self.game.get_current_player().nick))
                return

        args = msg.split(' ')
        if len(args) == 1:
            subject_nick = nick
        elif len(args) == 2:
            subject_nick = args[1]
        else:
            cardinal.sendMsg(channel, "{}: Usage: 'holdings [player]'".format(
                nick))
            return

        subject = None
        for player in self.game.players:
            if player.nick == subject_nick:
                subject = player

        if subject == None:
            cardinal.sendMsg(channel, "{}: No such player found".format(nick))
            return

        # All various wrong situations have been handled, now actually print
        # the holdings of the requested player

        cardinal.sendMsg(channel, "{}'s holdings:".format(subject_nick))
        cardinal.sendMsg(channel, "Balance: {}{}".format(
            self.game.board.cursymbol,
            subject.balance))

        for prop in subject.properties:
            price_str = str(prop.price)
            if len(price_str) < 3:
                price_str = " " * (3 - len(price_str)) + price_str

            # Name, spacing, price, mortgaged, houses, rent
            cardinal.sendMsg(channel, "{}{}{} {} {} {}".format(
                # TODO Get max name width from config
                prop.name[:25],
                " " * (25 - len(prop.name)),
                price_str,
                "M" if prop.mortgaged else " ",
                prop.buildlevel if isinstance(prop, chatopoly.Street) else "-",
                prop.rent(1)))

        # TODO Get-out-of-jail-free card

    holdings.commands = ['holdings', 'h']
    holdings.help = ["Show holdings of a player (own if no argument)"]

    def mortgage(self, cardinal, user, channel, msg):
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
            for line in self.game.interactive_cb('mortgage', msg.split(' ')):
                cardinal.sendMsg(channel, line)
            return

        args = msg.split(' ')
        if len(args) == 1:
            cardinal.sendMsg(channel, "{}: Usage: 'mortgage <property>'".format(
                nick))
            cardinal.sendMsg(channel, "(You may specify just part of a "
                    "property's name)")
            return

        for line in self.game.mortgage(" ".join(args[1:])):
            cardinal.sendMsg(channel, line)

        if self.game.interactive_cb:
            self.state = ChatopolyState.INTERACTIVE

    mortgage.commands = ['mortgage', 'm']
    listsaves.help = ["Manage the mortgage on your properties"]

def setup(cardinal, config):
    return ChatopolyPlugin(cardinal, config)
