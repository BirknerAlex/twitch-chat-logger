import threading

import asyncio
import websockets.client
import datetime
import re
import sys

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
                content = yield from websocket.recv()
                data = self.parse_message(content)
                if data:
                    self.storage.store(data=data, collection=data['collection'])
        except websockets.exceptions.ConnectionClosed:
            self.chat_logger.logger.error("Connection from Twitch closed - exiting")
            sys.exit(1)
        finally:
            yield from websocket.close()

    def parse_message(self, streamed_message):
        parts = streamed_message.split(";")
        message = {}

        if len(parts) <= 1:
            return

        for part in parts:
            keyvalue = part.split("=")
            if len(keyvalue) != 2:
                continue

            message[keyvalue[0].replace('@', '')] = keyvalue[1]

        # Chat messages
        if "PRIVMSG" in streamed_message:
            message['collection'] = 'chat'

            matches = re.match(".*PRIVMSG #"+ self.chat_logger.args.channel +" :(.*)\r\n$", message['user-type'])
            if matches:
                message['message'] = matches[1]

            if 'message' not in message:
                self.chat_logger.logger.error("Chat message received without message body.")
                return

            message['datetime'] = datetime.datetime.now()
            message['mod'] = int(message['mod']) == 1
            message['broadcaster'] = message['display-name'] == self.chat_logger.args.channel
            message['turbo'] = int(message['turbo']) == 1
            message['subscriber'] = int(message['subscriber']) == 1
            del message['user-id']

        # Ban messages
        elif 'ban-reason' in streamed_message:

            matches = re.match(".*CLEARCHAT #"+ self.chat_logger.args.channel +" :(.*)\r\n$", message['target-user-id'])
            print(message)
            if matches:
                message['collection'] = 'mod_log'
                message['ban-duration'] = int(message['ban-duration'])
                message['target'] = matches[1]

            del message['target-user-id']

        if 'collection' in message:
            del message['room-id']
            return message