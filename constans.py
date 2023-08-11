from telegram import ReplyKeyboardMarkup
import pymorphy2
GO = "вперёд"
LEVEL, BEGIN, GAME  = range(3)
EASY, MEDIUM, HARD = "izi", "medium", "hard"
morph = pymorphy2.MorphAnalyzer()
COW = morph.parse("корова") [0]
BULL = morph.parse("бык") [0]
#надписи на кнопках
LEVELS ={
    EASY :3, 
    MEDIUM :4,
    HARD : 5
}
CANCEL = "/cancel"
KEYPAD = ReplyKeyboardMarkup([[CANCEL]],
                             resize_keyboard=True,
                             input_field_placeholder="Чтобы сдаться,нажми на /cancel")
MEDIUM_PRICE = 5
HARD_PRICE = 15

