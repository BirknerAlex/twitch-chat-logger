import threading

import asyncio
import websockets.client
import datetime

from chat_logger.storage import Storage

class Bot(threading.Thread):

    def __init__(self, chat_logger):
        super(Bot, self).__init__()

        self.chat_logger = chat_logger
        self.storage = Storage(self.chat_logger)

    def run(self):
        self.chat_logger.logger.info("Bot connecting to Channel \"{channel}\"".format(
            channel=self.chat_logger.args.channel
        ))

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        asyncio.get_event_loop().run_until_complete(self.connect())

    @asyncio.coroutine
    def connect(self):
        websocket = yield from websockets.connect('ws://irc-ws.chat.twitch.tv/')

        try:
            yield from websocket.send("CAP REQ :twitch.tv/tags twitch.tv/commands")
            yield from websocket.send("PASS oauth:{token}".format(token=self.chat_logger.args.token))
            yield from websocket.send("NICK {username}".format(username=self.chat_logger.args.username))
            yield from websocket.send("JOIN #{channel}".format(channel=self.chat_logger.args.channel))

            while self.chat_logger.running:
                data = yield from websocket.recv()
                self.storage.store(data=self.parse_message(data))

        finally:
            yield from websocket.close()

    def parse_message(self, message):
        parts = message.split(";")
        message = {}

        if len(parts) <= 1:
            return

        for part in parts:
            keyvalue = part.split("=")
            if len(keyvalue) != 2:
                continue

            if keyvalue[0] == 'user-type':
                messageParts = part.split("PRIVMSG #"+ self.chat_logger.args.channel +" :")
                if len(messageParts) != 2:
                    continue
                keyvalue[1] = messageParts[0]
                message['message'] = messageParts[1].strip()

            message[keyvalue[0]] = keyvalue[1]

        if 'message' not in message:
            return

        message['datetime'] = datetime.datetime.now()
        message['mod'] = int(message['mod']) == 1
        message['turbo'] = int(message['turbo']) == 1
        message['subscriber'] = int(message['subscriber']) == 1

        return message