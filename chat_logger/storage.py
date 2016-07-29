import pymongo
from bson import json_util
import json

class Storage:

    """
    MongoDB Storage Class
    """
    def __init__(self, chat_logger):
        self.chat_logger = chat_logger
        self.client = pymongo.MongoClient(host=self.chat_logger.args.host, port=self.chat_logger.args.port)

        self.db = self.client.twitch_db
        self.collection = self.db.logs

        self.collection.create_index([("display-name", pymongo.ASCENDING)])
        self.collection.create_index([("datetime", pymongo.DESCENDING)])
        self.collection.create_index([
            ("display-name", pymongo.ASCENDING),
            ("datetime", pymongo.DESCENDING)
        ])

    def store(self, data):
        if not data:
            return

        self.chat_logger.logger.debug(data)
        self.collection.insert(data)
        data['date'] = data['datetime'].strftime("%d.%m.%Y %H:%M:%S")
        json_data = json.dumps(data, default=json_util.default)
        for queue in self.chat_logger.websocket.queues:
            self.chat_logger.websocket.loop.call_soon_threadsafe(queue.put_nowait, json_data)