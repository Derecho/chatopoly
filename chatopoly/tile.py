# -*- coding: utf-8 -*-
from functools import partial

RR_PRICE = 200
RR_BASE_RENT = 25
UTIL_PRICE = 150
UTIL_MUL_SOLO = 4
UTIL_MUL_DUO = 10
MORT_MUL = 0.5
MORT_LOSS = 0.1
INC_TAX_PRCT = 10
INC_TAX_FLAT = 200
LUX_TAX = 75

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

    def rent(self, dice):
        raise NotImplementedError

    def mortgage_value(self):
        """Returns mortgage value, or 0 if already mortgaged."""
        if self.mortgaged:
            return 0
        else:
            return int(MORT_MUL * self.price)

    def unmortgage_cost(self):
        """Returns unmortgage cost, or 0 if not mortgaged"""
        if not self.mortgaged:
            return 0
        else:
            return int((MORT_MUL * self.price) * (1 + MORT_LOSS))

    def mortgage(self):
        """Attempts to mortgage the property"""
        if self.mortgaged:
            return False
        else:
            self.owner.balance += self.mortgage_value()
            self.mortgaged = True
            return True

    def unmortgage(self):
        """Attempts to unmortgage the property"""
        if not self.mortgaged:
            return False

        if self.owner.balance < self.unmortgage_cost():
            return False

        self.owner.balance -= self.unmortgage_cost()
        self.mortgaged = False
        return True

# TODO Building/removing houses, check monopoly + distribution
class Street(Property):
    """The most common property, streets can form monopolies and subsequently
    allow houses and hotels to be built. Rentprices is a list of successive
    prices for the corresponding amount of houses built."""
    def __init__(self, name, monopoly, price, rentprices):
        super(Street, self).__init__("{} ({})".format(name, monopoly.colour),
                price)
        self.monopoly = monopoly
        self.rentprices = rentprices
        self.buildlevel = 0
        monopoly.streets.append(self)

    def rent(self, dice):
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

    def rent(self, dice):
        total_rr = 0
        for prop in self.owner.properties:
            if isinstance(prop, Railroad):
                total_rr += 1

        return (RR_BASE_RENT * (2 ** (total_rr - 1)))

class Utility(Property):
    """Utilities are simple properties that base their rent on dice throw and
    amount of other possessed utilities by the owner"""
    def __init__(self, name):
        super(Utility, self).__init__(name, UTIL_PRICE)

    def rent(self, dice):
        total_util = 0
        for prop in self.owner.properties:
            if isinstance(prop, Utility):
                total_util += 1

        multiplier = UTIL_MUL_DUO if (total_util == 2) else UTIL_MUL_SOLO
        return (multiplier * dice)

class Special(Tile):
    """(Abstract) Special tiles are tiles with customisable behaviour"""
    def __init__(self, name):
        super(Special, self).__init__(name)

    def on_entry(self, game):
        pass

    def on_turn(self, game):
        pass

class Go(Special):
    def __init__(self):
        super(Go, self).__init__("Go")

class Jail(Special):
    def __init__(self):
        super(Jail, self).__init__("Jail")

    def on_turn(self, game):
        # TODO Visting/Jailed logic
        pass

class FreeParking(Special):
    def __init__(self):
        super(FreeParking, self).__init__("Free Parking")

class GoToJail(Special):
    def __init__(self):
        super(Special, self).__init__("Go To Jail")

    def on_entry(self, game):
        # TODO Put player in jail
        pass

class CommunityChest(Special):
    def __init__(self, number):
        super(CommunityChest, self).__init__("Community Chest {}".format(number))

    def on_entry(self, game):
        # TODO Pick card and process effect
        pass

class Chance(Special):
    def __init__(self, number):
        super(Chance, self).__init__("Chance {}".format(number))

    def on_entry(self, game):
        # TODO Pick card and process effect
        pass
class LuxuryTax(Special):
    """Player arrived on Luxury Tax, flat fee"""
    def __init__(self):
        super(LuxuryTax, self).__init__("Luxury Tax")

    def on_entry(self, game):
        game.get_current_player().balance -= LUX_TAX
        return ["You pay {}{}.".format(
            game.board.cursymbol,
            LUX_TAX)]

class IncomeTax(Special):
    def __init__(self):
        super(IncomeTax, self).__init__("Income Tax")

    def on_entry(self, game):
        """Player arrived at Income Tax, prepare interactive session"""
        msg = []
        game.interactive_cb = partial(self._choice_cb, game=game)

        msg =  ["Pay up, {}% of your total worth or {}{}?".format(
            INC_TAX_PRCT,
            game.board.cursymbol,
            INC_TAX_FLAT)]
        msg += ["(Enter 'pay {}%' or 'pay {}' command)".format(
            INC_TAX_PRCT,
            INC_TAX_FLAT)]

        return msg

    def _choice_cb(self, cmd, args, game):
        """Callback handling payment of income tax"""
        msg = []

        if (cmd == 'pay') & (len(args) == 2):
            if args[1] == "{}%".format(INC_TAX_PRCT):
                current_player = game.get_current_player()
                total = current_player.balance

                for prop in current_player.properties:
                    total += (prop.price - prop.unmortgage_cost())
                # TODO Get out of jail free card?
                # TODO Houses
                tax = int((INC_TAX_PRCT/100.0) * total)
                current_player.balance -= tax
                msg += ["You pay: {}{} (UNFINISHED)".format(
                    game.board.cursymbol,
                    tax)]

                game.interactive_cb = None

            elif args[1] == "{}".format(INC_TAX_FLAT):
                game.get_current_player().balance -= INC_TAX_FLAT
                game.interactive_cb = None

        if game.interactive_cb == None:
            msg += [game._end_turn()]
        else:
            msg += ["Not a valid command. Your options are: 'pay {}%' and "
                    "'pay {}'.".format(
                INC_TAX_PRCT,
                INC_TAX_FLAT)]

        return msg
