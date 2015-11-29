# -*- coding: utf-8 -*-
from tile import *
from monopoly import *

class Board(object):
    def __init__(self, players):
        self.tiles = []
        self.players = {}
        self.cursymbol = "$"
        
        for i in range(len(players)):
            self.players[players[i]] = i

class USBoard(Board):
    def __init__(self, players):
        super(USBoard, self).__init__(players)

        purple = Monopoly("P", 50)
        light_blue = Monopoly("L", 50)

        self.tiles.append(Go())
        self.tiles.append(Street("Mediteranean Avenue",
            purple, 60, [2, 10, 30, 90, 160, 250]))
        self.tiles.append(CommunityChest(1))
        self.tiles.append(Street("Baltic Avenue",
            purple, 60, [4, 20, 60, 180, 320, 450]))
        self.tiles.append(IncomeTax())
        self.tiles.append(Railroad("Reading"))
        self.tiles.append(Street("Oriental Avenue",
            light_blue, 100, [6, 30, 90, 270, 400, 550]))
        self.tiles.append(Chance(1))
        self.tiles.append(Street("Vermont Avenue",
            light_blue, 100, [6, 30, 90, 270, 400, 550]))
        self.tiles.append(Street("Connecticut Avenue",
            light_blue, 120, [8, 40,100, 300, 450, 600]))
        self.tiles.append(Jail())
