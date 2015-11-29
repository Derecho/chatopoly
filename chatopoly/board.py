# -*- coding: utf-8 -*-
from tile import *

class Board(object):
    def __init__(self, players):
        self.tiles = []
        self.players = {}
        self.cursymbol = "$"
        
        for i in range(len(players)):
            self.players[players[i]] = i

class UKBoard(Board):
    def __init__(self, players):
        super(UKBoard, self).__init__(players)
        self.cursymbol = "£"
        self.tiles.append(Go())
        self.tiles.append(Street("Mediteranean Avenue (P)",
            60, 50, [2, 10, 30, 90, 160, 250]))
        self.tiles.append(CommunityChest(1))
        self.tiles.append(Street("Baltic Avenue (P)",
            60, 50, [4, 20, 60, 180, 320, 450]))
        self.tiles.append(IncomeTax())
        self.tiles.append(Railroad("Reading"))
        self.tiles.append(Street("Oriental Avenue (L)",
            100, 50, [6, 30, 90, 270, 400, 550]))
        self.tiles.append(Chance(1))
        self.tiles.append(Street("Vermont Avenue (L)",
            100, 50, [6, 30, 90, 270, 400, 550]))
        self.tiles.append(Street("Connecticut Avenue (L)",
            120, 50, [8, 40,100, 300, 450, 600]))
        self.tiles.append(Jail())
