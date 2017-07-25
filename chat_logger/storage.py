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
        self.chat_collection = self.db.logs
        self.mod_log_collection = self.db.ban_log

        self.chat_collection.create_index([("display-name", pymongo.ASCENDING)])
        self.chat_collection.create_index([("datetime", pymongo.DESCENDING)])
        self.chat_collection.create_index([
            ("display-name", pymongo.ASCENDING),
            ("datetime", pymongo.DESCENDING)
        ])

    def store(self, data, collection):
        if not data:
            return

        del data['collection'] # we do not need this here

        if collection == 'chat':
            self.chat_collection.insert(data)
            data['date'] = data['datetime'].strftime("%d.%m.%Y %H:%M:%S")
            json_data = json.dumps(data, default=json_util.default)
            for queue in self.chat_logger.websocket.queues:
                self.chat_logger.websocket.loop.call_soon_threadsafe(queue.put_nowait, json_data)
        if collection == 'mod_log':
            self.mod_log_collection.insert(data)
