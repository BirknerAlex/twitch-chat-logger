import threading

import asyncio
import websockets.server

class WebsocketServer(threading.Thread):

    def __init__(self, chat_logger):
        super(WebsocketServer, self).__init__()
        self.chat_logger = chat_logger
        self.queues = list()

        self.loop = asyncio.new_event_loop()

    def run(self):
        asyncio.set_event_loop(self.loop)

        start_server = websockets.serve(self.websocket_handler, '0.0.0.0', 8765)

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    @asyncio.coroutine
    def websocket_handler(self, websocket, path):
        queue = asyncio.Queue()
        self.queues.append(queue)
        self.chat_logger.logger.info("Websocket Client connected")

        try:
            while True:
                data = yield from queue.get()
                yield from websocket.send(data)
        except websockets.exceptions.ConnectionClosed:
            self.chat_logger.logger.info("Websocket Client disconnected")
        finally:
            self.queues.remove(queue)