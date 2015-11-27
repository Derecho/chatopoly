from tile import *

class Board(object):
    def __init__(self):
        self.tiles = []

class UKBoard(Board):
    def __init__(self):
        super(UKBoard, self).__init__()
        self.tiles.append(Go())
        self.tiles.append(Street("Mediteranean Avenue (P)",
            60, [2, 10, 30, 90, 160, 250]))
        self.tiles.append(CommunityChest(1))
        self.tiles.append(Street("Baltic Avenue (P)",
            60, [4, 20, 60, 180, 320, 450]))
        self.tiles.append(IncomeTax())
        self.tiles.append(Railroad("Reading"))
        self.tiles.append(Street("Oriental Avenue (L)",
            100, [6, 30, 90, 270, 400, 550]))
        self.tiles.append(Chance(1))
        self.tiles.append(Street("Vermont Avenue (L)",
            100, [6, 30, 90, 270, 400, 550]))
        self.tiles.append(Street("Connecticut Avenue (L)",
            120, [8, 40,100, 300, 450, 600]))
        self.tiles.append(Jail())
