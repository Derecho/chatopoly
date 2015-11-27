import logging

class ChatopolyPlugin(object):
    logger = None

    def __init__(self, cardinal, config):
        self.logger = logging.getLogger(__name__)
        self._connect_or_create_db(cardinal)
        self.logger.info("Chatopoly started")

    def _connect_or_create_db(self, cardinal):
        # TODO
        pass

    def roll(self, cardinal, user, channel, msg):
        # TODO Replace stub
        nick, ident, vhost = user.group(1), user.group(2), user.group(3)
        cardinal.sendMsg(channel, "user: {}, channel: {}, message {}".format(nick, channel, msg))

    roll.commands = ['roll', 'r']
    roll.help = ["Roll the dice"]

def setup(cardinal, config):
    return ChatopolyPlugin(cardinal, config)
