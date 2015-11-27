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
        self.currentplayer = 0
        self.dice = []

        for i in range(DICE_AMOUNT):
            self.dice += [0]

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

    def prepare_board(self, variant):
        if self.board != None:
            return False

        if variant == 'uk':
            self.board = UKBoard(self.players)
            return True

        return False

    def roll(self):
        msg = []

        dicetotal = 0
        for i in range(len(self.dice)):
            self.dice[i] = random.randint(1, DICE_MAX)
            dicetotal += self.dice[i]

        currentplayer = self.players[self.currentplayer]
        currentplayer.last_dice = dicetotal
        currentplayer.position += dicetotal

        if currentplayer.position > len(self.board.tiles):
            msg += ["You have passed GO and collect {}{}".format(
                self.board.cursymbol,
                GO_REWARD)]
            currentplayer.position -= len(self.board.tiles)
            currentplayer.balance += GO_REWARD

        currenttile = self.board.tiles[currentplayer.position]

        msg += ["{} moves to {}.".format(currentplayer.nick, currenttile.name)]

        if isinstance(currenttile, Property):
            if currenttile.owner == None:
                # TODO Offer to buy property
                pass
            else:
                # Property owned, pay rent
                currentplayer.balance -= currenttile.rent()
                currenttile.owner.balance += currenttile.rent()
                msg += ["Property is owned by {}, {} pays {}{} rent.".format(
                    currenttile.owner.nick,
                    currentplayer.nick,
                    self.board.cursymbol,
                    currenttile.rent())]
        elif isinstance(currenttile, Special):
            # TODO User interaction and feedback
            currenttile.on_entry(currentplayer)
        else:
            # TODO Invalid tile
            msg += ["ERROR: Invalid tile"]

        self.currentplayer = (self.currentplayer + 1) % len(self.players)
        msg += ["Turn goes to {}".format(self.players[self.currentplayer].nick)]

        return msg
