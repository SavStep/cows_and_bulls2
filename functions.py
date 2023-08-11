from telegram.ext import CallbackContext, ConversationHandler
import random
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from constans import *
from stikers import *
import rsa

def start(update: Update, context: CallbackContext):
    keyboard = [[GO]]
    marcup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_sticker(random.choice(HELLO_STIK))
    update.message.reply_text(
        f"есть  загаданное слово если вы угадали букву,но она не в том месте это корова,если вы угадали букву и она в том месте это бык (в любое вряме вы можете написать /cancel и закончить игру)",
        reply_markup=marcup)
    return LEVEL


def begin(update: Update, context: CallbackContext):
    difficulty = update.message.text
    money = context.user_data["coins"]
    if money < MEDIUM_PRICE and difficulty == MEDIUM:
        difficulty = EASY
        update.message.reply_sticker(MONEY_STIK)
        update.message.reply_text(
            "У вас недостаточно средств,к сожалению или к счастью мы вас переносим на уровень 'easy'")
    elif money < HARD_PRICE and difficulty == HARD:
        difficulty = EASY
        update.message.reply_sticker(MONEY_STIK)
        update.message.reply_text(
            "У вас недостаточно средств,к сожалению или к счастью мы вас переносим на уровень 'easy'")
    elif difficulty == MEDIUM:
        money -= MEDIUM_PRICE
        update.message.reply_sticker(LEVEL_STIK)
        update.message.reply_text(f"вы преобрели медиум")
    elif difficulty == HARD:
        money -= HARD_PRICE
        update.message.reply_sticker(LEVEL_STIK)
        update.message.reply_text(f"вы преобрели хард")
    count = LEVELS[difficulty]
    context.user_data["difficulty"] = count

    with open(f"cows_and_buls2/{difficulty}_{count}.txt", encoding="utf-8") as file:
        words = file.read().split("\n")
    secret_word = random.choice(words).strip()
    context.user_data["секрет"] = secret_word  # записыва
    update.message.reply_text(
        f"введите слово из {count} букв")
    return GAME


def chose_level(update: Update, context: CallbackContext):
    with open(f"cows_and_buls2/ssh/key",encoding="utf-8") as file:
        private_key = file.read().split(", ")
        private_key = [int(number) for number in private_key]
        private_key = rsa.PrivateKey(*private_key)
    with open(f"cows_and_buls2/coins.txt", "rb") as file:
        coins = file.read()
        message = rsa.decrypt(coins, private_key)
        coins = message.decode("utf8")
    context.user_data["coins"] = int(coins)
    context.user_data["attemps"] = 0
    update.message.reply_text(
        f'у вас {coins} монет. слово уровня easy: бесплатно ,medium: 5 монет hard:15 монет,на изи уровне дают две монеты,на медиуме 4,а на харде 6')
    keyboard = [[EASY], [MEDIUM], [HARD]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True,
                                 input_field_placeholder="Выбери что тебе по силам")
    update.message.reply_text("Выбери уровень сложности",
                              reply_markup=markup)
    
    return BEGIN


def game(update: Update, context: CallbackContext):
    user_name = update.effective_user.first_name
    my_word = update.message.text.lower()
    secret_word = context.user_data["секрет"]  # достаю
    if len(secret_word) != len(my_word):
        update.message.reply_sticker(ANGRY_STIK)
        update.message.reply_text(f"Количество букв должно быть {len (my_word)}.")
        return None
    bulls = 0
    cows = 0
    for index, letter in enumerate(my_word):
        if letter in secret_word:
            if secret_word[index] == my_word[index]:
                bulls += 1
            else:
                cows += 1
    word_cow = incline_words(COW, cows)
    word_bull = incline_words(BULL, bulls)
    update.message.reply_text(
        f"в вашем слове {bulls} {word_bull} и {cows} {word_cow}", reply_markup=ReplyKeyboardRemove())
    # update.message.reply_text(f"{bulls}  и {len(secret_word)} ")
    if bulls == len(secret_word):
        update.message.reply_sticker(VICTORY_STIK)
        update.message.reply_text(
            f"Поздравляем! Вы победили. Чтобы сыграть еще раз, нажмите /start", reply_markup=ReplyKeyboardRemove())
        change_money(context, plus=True)
        del context.user_data["секрет"]
        return ConversationHandler.END


def end(update: Update, context: CallbackContext):
    if "секрет" in context.user_data:
        secret_word = context.user_data["секрет"]
        update.message.reply_sticker(END_STIK)
        update.message.reply_text(f"Загаданное слово было {secret_word}")
        change_money(context, plus=False)
    else:
        update.message.reply_sticker(END_STIK)
        update.message.reply_text(
            f"ты выбрал конец,амням грустит", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


# если выклюатель включен, то прибавляет,выключен - отнимаем
def change_money(context, plus=False):
    difficulty = context.user_data["difficulty"]
    money = context.user_data["coins"]
    if plus == False:  # если мы вичитаем
        money *= -1  # делаем число отрицательным
    money += int (difficulty)  # прибавляем или отнимаем монеты
    with open(f"cows_and_buls2/ssh/key.pub",encoding="utf-8") as file:
        public_key = file.read().split(", ")
        public_key = [int(number) for number in public_key]
        public_key = rsa.PublicKey(*public_key)
    with open(f"cows_and_buls2/coins.txt", "wb") as file:
        message = f"{money}".encode('utf8')
        crypto = rsa.encrypt(message, public_key)
        file.write(crypto)


def incline_words(animal: pymorphy2.analyzer.Parse, count: int):
    if count == 1:
        animal = animal.inflect({"nomn"}).word  # бык корова
    elif count in [2, 3, 4]:
        animal = animal.inflect({"gent"}).word  # быка коровы
    else:
        animal = animal.inflect({"gent", "plur"}).word  # быков коров
    return animal

