from TelegramBot import bot
from TelegramBot.logging import log

log(__name__).info("client successfully initiated....")
if __name__ == "__main__":
    bot.run()
