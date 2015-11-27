# -*- coding: utf-8 -*-
RR_PRICE = 200
RR_BASE_RENT = 25
UTIL_PRICE = 150
UTIL_MUL_SOLO = 4
UTIL_MUL_DUO = 10
MORT_MUL = 0.5
MORT_LOSS = 0.1

class Tile(object):
    """(Abstract) Any sort of tile that a player could stand on"""
    def __init__(self, name):
        self.name = name

class Property(Tile):
    """(Abstract) Any sort of tile that can be owned by a player"""
    def __init__(self, name, price):
        super(Property, self).__init__(name)
        self.price = price
        self.owner = None
        self.mortgaged = False

    def rent(self):
        raise NotImplementedError

    def mortgage_value(self):
        """Returns mortgage value, or 0 if already mortgaged."""
        if self.mortgaged == True:
            return 0
        else:
            return (MORT_MUL * self.price)

    def unmortgage_cost(self):
        """Returns unmortgage cost, or 0 if not mortgaged"""
        if self.mortgaged == False:
            return 0
        else:
            return ((MORT_MUL * self.price) * (1 + MORT_LOSS))

    def mortgage(self):
        """Attempts to mortgage the property"""
        if self.mortgaged == True:
            return False
        else:
            self.owner.balance += self.mortgage_value()
            self.mortgaged = True
            return True

    def unmortgage(self):
        """Attempts to unmortgage the property"""
        if self.mortgaged == False:
            return False

        if self.owner.balance < self.unmortgage_cost():
            return False

        self.owner.balance - self.unmortgage_cost()
        self.mortgaged = False
        return True

# TODO Building/removing houses, check monopoly + distribution
class Street(Property):
    """The most common property, streets can form monopolies and subsequently
    allow houses and hotels to be built."""
    def __init__(self, name, price, rentprices):
        super(Street, self).__init__(name, price)
        self.rentprices = rentprices
        # TODO rentprices format {2, 10, 30, 90, 160, 250}
        self.buildlevel = 0

    def rent(self):
        return self.rentprices[self.buildlevel]

    def mortgage(self):
        # Streets cannot be mortgaged with houses on them
        if self.buildlevel > 0:
            return False
        else:
            return super(Street, self).mortgage()

class Railroad(Property):
    """Railroads are simple properties that have deterministic rent based on
    the amount of railroads the owner possesses"""
    def __init__(self, name):
        super(Railroad, self).__init__("{} Railroad".format(name), RR_PRICE)

    def rent(self):
        total_rr = 0
        for prop in self.owner.properties:
            if isinstance(prop, Railroad):
                total_rr += 1

        return (RR_BASE_RENT * (2 ** (total_rr - 1)))

class Utility(Property):
    """Utilities are simple properties that base their rent own dice throw and
    amount of other possessed utilities by the owner"""
    def __init__(self, name):
        super(Utility, self).__init__(name, UTIL_PRICE)

    def rent(self):
        total_util = 0
        for prop in self.owner.properties:
            if isinstance(prop, Utility):
                total_util += 1

        multiplier = UTIL_MUL_DUO if (total_util == 2) else UTIL_MUL_SOLO
        return (multiplier * self.owner.last_roll)

class Special(Tile):
    """(Abstract) Special tiles are tiles with customisable behaviour"""
    def __init__(self, name):
        super(Special, self).__init__(name)

    def on_entry(self, player):
        pass

    def on_turn(self, player):
        pass

class Go(Special):
    def __init__(self):
        super(Go, self).__init__("Go")

class Jail(Special):
    def __init__(self):
        super(Jail, self).__init__("Jail")

    def on_turn(self, player):
        # TODO Visting/Jailed logic
        pass

class FreeParking(Special):
    def __init__(self):
        super(FreeParking, self).__init__("Free Parking")

class GoToJail(Special):
    def __init__(self):
        super(Special, self).__init__("Go To Jail")

    def on_entry(self, player):
        # TODO Put player in jail
        pass

class CommunityChest(Special):
    def __init__(self, number):
        super(CommunityChest, self).__init__("Community Chest {}".format(number))

    def on_entry(self, player):
        # TODO Pick card and process effect
        pass

class Chance(Special):
    def __init__(self, number):
        super(Chance, self).__init__("Chance {}".format(number))

    def on_entry(self, player):
        # TODO Pick card and process effect
        pass

class IncomeTax(Special):
    def __init__(self):
        super(IncomeTax, self).__init__("Income Tax")

    def on_entry(self, player):
        # TODO 10% or $200
        pass
