# -*- coding: utf-8 -*-
import jsonpickle
import random

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
        """Build and store board layout (after adding players!)"""
        if self.board != None:
            return False

        # TODO Cleaner way. Maybe a dictionary that Boards add themselves to.
        if variant == 'uk':
            self.board = UKBoard(self.players)
            return True

        return False

    def roll(self):
        """Rolls the dice for the current player and processes according
        actions"""
        msg = []

        dicetotal = 0
        rolldetails = ""
        for i in range(len(self.dice)):
            self.dice[i] = random.randint(1, DICE_MAX)
            dicetotal += self.dice[i]

            if rolldetails != "":
                rolldetails += "+ "
            rolldetails += "{} ".format(self.dice[i])
        rolldetails += "= {}".format(dicetotal)

        current_player = self.get_current_player()
        current_player.last_dice = dicetotal
        current_player.position += dicetotal

        msg += ["{} rolls {}.".format(current_player.nick, rolldetails)]

        if current_player.position >= len(self.board.tiles):
            msg += ["You have passed GO and collect {}{}.".format(
                self.board.cursymbol,
                GO_REWARD)]
            current_player.position -= len(self.board.tiles)
            current_player.balance += GO_REWARD

        current_tile = self.board.tiles[current_player.position]

        msg += ["{} moves to {}.".format(current_player.nick, current_tile.name)]

        if isinstance(current_tile, Property):
            if current_tile.owner == None:
                msg += ["Property is unowned. Would you like to purchase it for {}{}?".format(
                    self.board.cursymbol,
                    current_tile.price)]
                self.interactive_cb = self._purchase_cb
            else:
                # Property owned, pay rent
                current_player.balance -= current_tile.rent()
                current_tile.owner.balance += current_tile.rent()
                msg += ["Property is owned by {}, {} pays {}{} rent.".format(
                    current_tile.owner.nick,
                    current_player.nick,
                    self.board.cursymbol,
                    current_tile.rent())]
        elif isinstance(current_tile, Special):
            on_entry_msg = current_tile.on_entry(self)
            if on_entry_msg:
                msg.extend(on_entry_msg)
        else:
            # TODO Invalid tile
            msg += ["ERROR: Invalid tile"]

        if self.interactive_cb == None:
            msg += [self._next_player()]

        return msg

    def _next_player(self):
        """Gives turn to next player, returns according message"""
        self.current_player_id = (self.current_player_id + 1) % len(self.players)
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
            msg += ["(Not implemented yet)"]
            self.interactive_cb = None
        else:
            msg += ["Not a valid command. Your options are: 'yes' and 'no'."]

        if self.interactive_cb == None:
            msg += [self._next_player()]

        return msg
