import threading

import asyncio
import websockets.server

from queue import Queue

class WebsocketServer(threading.Thread):

    def __init__(self, chat_logger):
        super(WebsocketServer, self).__init__()

        self.chat_logger = chat_logger

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        start_server = websockets.serve(self.queue_reader, '0.0.0.0', 8765)

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    @asyncio.coroutine
    def queue_reader(self, websocket, path):

        queue = Queue()
        self.chat_logger.queues.append(queue)

        running = True
        while running:
            try:
                data = queue.get(block=True)
                yield from websocket.send(str(data))
                queue.task_done()
            except websockets.exceptions.ConnectionClosed:
                running = False
                self.chat_logger.queues.remove(queue)