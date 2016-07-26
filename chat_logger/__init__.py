import logging
import asyncio
import sys

from chat_logger.bot import Bot


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

        self.queue = asyncio.Queue()
        self.running = True
        self.args = args
        self.logger = logging.getLogger("Twitch Chat Logger")

    def start(self):
        self.logger.info("Starting Up")

        self.bot = Bot(self)
        self.bot.start()


    def stop(self):
        self.logger("Shutting down")
        self.running = False
