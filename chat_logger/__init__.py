import logging
import sys

from chat_logger.bot import Bot
from chat_logger.websocket_server import WebsocketServer


class TwitchChatLogger:
    """
    Twitch Chat Logger
        - A Twitch Chat MongoDB logging tool

    (C) Alexander Birkner 2016
    """

    def __init__(self, args):
        logging.basicConfig(
            stream=sys.stdout,
            format="%(levelname)s - %(name)s -> %(message)s",
            level=logging.INFO)

        self.queues = []
        self.running = True
        self.args = args
        self.logger = logging.getLogger("Twitch Chat Logger")

    def start(self):
        self.logger.info("Starting Up")

        self.websocket = WebsocketServer(self)
        self.websocket.start()

        self.bot = Bot(self)
        self.bot.start()


    def stop(self):
        self.logger("Shutting down")
        self.running = False
