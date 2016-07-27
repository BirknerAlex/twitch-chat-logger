import pymongo

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

        self.chat_logger.logger.info(data)
        self.collection.insert(data)