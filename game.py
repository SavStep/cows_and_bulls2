# блок импортов
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler
from config import TOKEN
from telegram.ext.filters import Filters
from functions import *


# блок хендлеров
game_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        LEVEL: [MessageHandler(Filters.regex(f"^({GO})$"), chose_level)],
        BEGIN: [MessageHandler(Filters.regex(f"^({EASY}|{MEDIUM}|{HARD})$"), begin)],
        GAME: [MessageHandler(Filters.text & ~Filters.command, game)],

    },
    fallbacks=[CommandHandler("cancel", end), CommandHandler("stop", end)]


)


# сам бот и его зам
updater = Updater(TOKEN)
dispatcher = updater.dispatcher

# работники диспечера
dispatcher.add_handler(game_handler)


print("бот запущен")
updater.start_polling()
updater.idle()
