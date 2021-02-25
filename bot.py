import telebot
import config
import dbworker
import os

from api import get_city_info
from utils import change_weather_mode
from dotenv import load_dotenv

load_dotenv()

bot = telebot.TeleBot(os.environ['TELEGRAM_TOKEN'])


@bot.message_handler(commands=['start'])
def handle_start_command(message):
    state = dbworker.get_value(config.DB_FILE_STATE, message.chat.id)
    if state == config.States.S_ENTER_LOCATION.value:
        bot.send_message(message.chat.id, "Вы забыли ввести название вашего города. Давайте попробуем еще раз")
    elif state == config.States.S_WEATHER_TODAY.value:
        change_weather_mode(config.W_TODAY_TITLE, bot, message.chat.id)
    elif state == config.States.S_WEATHER_TOMORROW.value:
        change_weather_mode(config.W_TOMORROW_TITLE, bot, message.chat.id)
    elif state == config.States.S_WEATHER_NEXT_5_DAYS.value:
        change_weather_mode(config.W_5_DAYS_TITLE, bot, message.chat.id)
    else:
        bot.send_message(message.chat.id, "Привет, " + message.chat.first_name + ", введите название вашего города")
        dbworker.set_value(config.DB_FILE_STATE, message.chat.id, config.States.S_ENTER_LOCATION.value)


@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    deleted_keyboard = telebot.types.ReplyKeyboardRemove(True)
    bot.send_message(message.chat.id, "Введите новое название вашего города", reply_markup=deleted_keyboard)
    dbworker.set_value(config.DB_FILE_STATE, message.chat.id, config.States.S_ENTER_LOCATION.value)


@bot.message_handler(
    func=lambda message: dbworker.get_value(config.DB_FILE_STATE,
                                            message.chat.id) == config.States.S_ENTER_LOCATION.value)
def user_entering_location(message):
    user_location = message.text

    city_info = get_city_info(user_location)

    if not city_info:
        bot.send_message(message.chat.id, "Некоректный город, попробуйте еще раз")
    else:
        dbworker.set_value(config.DB_FILE_LOCATION, message.chat.id, user_location)
        change_weather_mode(config.W_TODAY_TITLE, bot, message.chat.id, city_info)


@bot.message_handler(
    func=lambda message: dbworker.get_value(config.DB_FILE_STATE,
                                            message.chat.id) in [config.States.S_WEATHER_TODAY.value,
                                                                 config.States.S_WEATHER_TOMORROW.value,
                                                                 config.States.S_WEATHER_NEXT_5_DAYS.value]
)
def weather_mode(message):
    change_weather_mode(message.text, bot, message.chat.id)


if __name__ == "__main__":
    bot.infinity_polling()
