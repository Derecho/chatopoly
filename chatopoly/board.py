# -*- coding: utf-8 -*-
from tile import *
from monopoly import *

class Board(object):
    def __init__(self):
        self.tiles = []
        self.cursymbol = "$"

class TestBoard(Board):
    def __init__(self):
        super(TestBoard, self).__init__()

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

class USBoard(Board):
    def __init__(self):
        super(USBoard, self).__init__()

        purple = Monopoly("P", 50)
        light_blue = Monopoly("L", 50)
        violet = Monopoly("V", 100)
        orange = Monopoly("O", 100)
        red = Monopoly("R", 150)
        yellow = Monopoly("Y", 150)
        green = Monopoly("G", 200)
        dark_blue = Monopoly("D", 200)

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
            light_blue, 120, [8, 40, 100, 300, 450, 600]))
        self.tiles.append(Jail())
        self.tiles.append(Street("Saint Charles Place",
            violet, 140, [10, 50, 150, 450, 625, 750]))
        self.tiles.append(Utility("Electric Company"))
        self.tiles.append(Street("States Avenue",
            violet, 140, [10, 50, 150, 450, 625, 750]))
        self.tiles.append(Street("Virginia Avenue",
            violet, 160, [12, 60, 180, 500, 700, 900]))
        self.tiles.append(Railroad("Pennsylvania"))
        self.tiles.append(Street("Saint James Place",
            orange, 180, [14, 70, 200, 550, 750, 950]))
        self.tiles.append(CommunityChest(2))
        self.tiles.append(Street("Tennessee Avenue",
            orange, 180, [14, 70, 200, 550, 750, 950]))
        self.tiles.append(Street("New York Avenue",
            orange, 200, [16, 80, 220, 600, 800, 1000]))
        self.tiles.append(FreeParking())
        self.tiles.append(Street("Kentucky Avenue",
            red, 220, [18, 90, 250, 700, 875, 1050]))
        self.tiles.append(Chance(2))
        self.tiles.append(Street("Indiana Avenue",
            red, 220, [18, 90, 250, 700, 875, 1050]))
        self.tiles.append(Street("Illinois Avenue",
            red, 240, [20, 100, 300, 750, 925, 1100]))
        self.tiles.append(Railroad("B & O"))
        self.tiles.append(Street("Atlantic Avenue",
            yellow, 260, [22, 110, 330, 800, 975, 1150]))
        self.tiles.append(Street("Ventnor Avenue",
            yellow, 260, [22, 110, 330, 800, 975, 1150]))
        self.tiles.append(Utility("Water Works"))
        self.tiles.append(Street("Marvin Gardens",
            yellow, 280, [24, 120, 360, 850, 1025, 1200]))
        self.tiles.append(GoToJail())
        self.tiles.append(Street("Pacific Avenue",
            green, 300, [26, 130, 390, 900, 1100, 1275]))
        self.tiles.append(Street("North Carolina Avenue",
            green, 300, [26, 130, 390, 900, 1100, 1275]))
        self.tiles.append(CommunityChest(3))
        self.tiles.append(Street("Pennsylvania Avenue",
            green, 320, [28, 150, 450, 1000, 1200, 1400]))
        self.tiles.append(Railroad("Short Line"))
        self.tiles.append(Chance(3))
        self.tiles.append(Street("Park Place",
            dark_blue, 350, [35, 175, 500, 1100, 1300, 1500]))
        self.tiles.append(LuxuryTax())
        self.tiles.append(Street("Board Walk",
            dark_blue, 400, [50, 200, 600, 1400, 1700, 2000]))
