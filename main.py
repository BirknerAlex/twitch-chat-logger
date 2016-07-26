import argparse
import chat_logger

def main() -> None:
    parser = argparse.ArgumentParser(description='Twitch Chat Logger - Logs your chat into MongoDB')
    parser.add_argument('--channel', help='Twitch Channel Name', required=True)
    parser.add_argument('--username', help='Twitch Chat Username', required=True)
    parser.add_argument('--token', help='Twtich Chat oAuth Token', required=True)
    parser.add_argument('--host', help='MongoDB Hostname', default='localhost')
    parser.add_argument('--port', help='MongoDB Port', default=27017)
    args = parser.parse_args()

    logger = chat_logger.TwitchChatLogger(args)
    try:
        logger.start()
    except KeyboardInterrupt:
        logger.stop()

if __name__ == '__main__':
    main()
