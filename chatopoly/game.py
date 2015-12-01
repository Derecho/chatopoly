# -*- coding: utf-8 -*-
import jsonpickle
import random
import datetime
from functools import partial

from player import *
from board import *

DICE_AMOUNT = 2
DICE_MAX = 6
GO_REWARD = 200

class Game(object):
    def __init__(self):
        self.players = []
        self.board = None
        self.current_player_id = 0
        self.dice = []
        self.interactive_cb = None

        for i in range(DICE_AMOUNT):
            self.dice += [0]

        self.started = datetime.datetime.now()

    def _end_turn(self):
        """Gives turn to next player (unless in debt), returns according message"""
        self.current_player_id = (self.current_player_id + 1) % len(self.players)
        # TODO Handle debt
        # TODO on_turn of tile
        return "Turn goes to {} (at {} with {}{}).".format(
                self.get_current_player().nick,
                self.board.tiles[self.get_current_player().position].name,
                self.board.cursymbol,
                self.get_current_player().balance)

    def _purchase_cb(self, cmd, args):
        """Callback handling property purchases"""
        msg = []

        if cmd == 'yes':
            current_player = self.get_current_player()
            current_tile = self.board.tiles[current_player.position]
            current_player.balance -= current_tile.price
            current_player.properties += [current_tile]
            current_tile.owner = current_player
            msg += ["{} has been purchased, you have {}{} left.".format(
                current_tile.name,
                self.board.cursymbol,
                current_player.balance)]
            self.interactive_cb = None
        elif cmd == 'no':
            # TODO Auction
            msg += ["Property is going up for action."]
            msg += ["(UNFINISHED)"]
            self.interactive_cb = None
        else:
            msg += ["Not a valid command. Your options are: 'yes' and 'no'."]

        if self.interactive_cb == None:
            msg += [self._end_turn()]

        return msg

    def _mortgage_cb(self, cmd, args, subject):
        msg = []
        player = self.get_current_player()

        if cmd == 'yes':
            # TODO Check for houses

            if subject.mortgaged:
                subject.unmortgage()
            else:
                subject.mortgage()

            msg += ["You have {}mortgaged {}.".format(
                "" if subject.mortgaged else "un",
                subject.name)]
        elif cmd == 'no':
            pass
        else:
            return ["Not a valid command. Your options are: 'yes' and 'no'."]

        msg += ["It is {}'s turn (at {} with {}{}).".format(
                player.nick,
                self.board.tiles[player.position].name,
                self.board.cursymbol,
                player.balance)]

        self.interactive_cb = None

        return msg

    @staticmethod
    def from_savedata(savedata):
        """Static creator method to recover a Game from savedata"""
        obj = jsonpickle.decode(savedata)
        if isinstance(obj, Game):
            return obj
        return None

    def to_savedata(self):
        """Serialise Game object for saving"""
        return jsonpickle.encode(self)

    def add_player(self, nick):
        """Create and store Player for the givn nick"""
        if nick not in self.get_player_nicks():
            self.players.append(Player(nick))
            return True
        return False

    def get_current_player(self):
        return self.players[self.current_player_id]

    def get_player_nicks(self):
        return [player.nick for player in self.players]

    def prepare_board(self, variant):
        """Build and store board layout"""
        if self.board != None:
            return False

        # TODO Cleaner way. Maybe a dictionary that Boards add themselves to.
        if variant == 'us':
            self.board = USBoard()
            return True
        elif variant == 'test':
            self.board = TestBoard()
            return True

        return False

    def roll(self, dice=None):
        """Rolls the dice for the current player and processes according
        actions. Takes an optional dice parameter to be used for debugging."""
        msg = []

        dicetotal = 0
        rolldetails = ""
        for i in range(len(self.dice)):
            if dice:
                self.dice[i] = dice[i]
            else:
                self.dice[i] = random.SystemRandom().randint(1, DICE_MAX)

            dicetotal += self.dice[i]

            if rolldetails != "":
                rolldetails += "+ "
            rolldetails += "{} ".format(self.dice[i])
        rolldetails += "= {}".format(dicetotal)

        current_player = self.get_current_player()
        current_player.position += dicetotal

        msg += ["You roll {}.".format(rolldetails)]

        if current_player.position >= len(self.board.tiles):
            msg += ["You have passed GO and collect {}{}.".format(
                self.board.cursymbol,
                GO_REWARD)]
            current_player.position %= len(self.board.tiles)
            current_player.balance += GO_REWARD

        current_tile = self.board.tiles[current_player.position]

        msg += ["You move to {}.".format(current_tile.name)]

        if isinstance(current_tile, Property):
            if current_tile.owner == None:
                msg += ["Property is unowned. Would you like to purchase it for {}{}?".format(
                    self.board.cursymbol,
                    current_tile.price)]
                self.interactive_cb = self._purchase_cb
            elif current_tile.owner == current_player:
                msg += ["You own this property."]
            else:
                msg += ["Property is owned by {}.".format(
                    current_tile.owner.nick)]
                if not current_tile.mortgaged:
                    current_player.balance -= current_tile.rent(dicetotal)
                    current_tile.owner.balance += current_tile.rent(dicetotal)
                    msg += ["You pay {}{} rent.".format(
                        self.board.cursymbol,
                        current_tile.rent(dicetotal))]

            if current_tile.mortgaged:
                msg += ["Property is mortgaged."]

        elif isinstance(current_tile, Special):
            on_entry_msg = current_tile.on_entry(self)
            if on_entry_msg:
                msg.extend(on_entry_msg)
        else:
            # TODO Invalid tile
            msg += ["ERROR: Invalid tile"]

        if self.interactive_cb == None:
            msg += [self._end_turn()]

        return msg

    def mortgage(self, query):
        """Attempt to manage the mortgage on a property"""
        msg = []

        # Search for property in user's posession
        found = False
        for prop in self.get_current_player().properties:
            if prop.name.lower().find(query.lower()) != -1:
                if not found:
                    found = True
                    subject = prop
                else:
                    msg += ["{}: Multiple properties match, please be more "
                    "specific.".format(self.get_current_player().nick)]
                    return msg

        if not found:
            msg += ["{}: Could not find a matching property.".format(
                self.get_current_player().nick)]
            return msg

        # Show mortgage/unmortgage choice
        msg += ["{} is currently {}mortgaged.".format(
            subject.name,
            "" if subject.mortgaged else "not ")]
        msg += ["Would you like to {}mortgage it for {}{}?".format(
                    "un" if subject.mortgaged else "",
                    self.board.cursymbol,
                    subject.unmortgage_cost() if
                    subject.mortgaged else
                    subject.mortgage_value())]

        self.interactive_cb = partial(self._mortgage_cb, subject=subject)
        return msg
