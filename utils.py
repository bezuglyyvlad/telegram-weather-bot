from datetime import datetime

import telebot

import config
import dbworker
from api import get_city_info, get_weather_from_ow, get_weather_from_sinoptik


def get_weather_string_ow(day_weather, timezone_offset):
    wind_gust = f"Порыв ветра - {day_weather['wind_gust']} метр/сек\n" \
        if 'wind_gust' in day_weather.keys() else ""
    rain = f"Обьем осадков - {day_weather['rain']} мм\n" \
        if 'rain' in day_weather.keys() else ""
    snow = f"Обьем снега - {day_weather['snow']} мм" \
        if 'snow' in day_weather.keys() else ""
    date = datetime.fromtimestamp(day_weather['dt'] +
                                  timezone_offset).strftime(config.DATE_FORMAT)
    weather_string = f"###OpenWeather###\n" \
                     f"{date}\n" \
                     f"{day_weather['weather'][0]['description'].capitalize()}\n" \
                     f"Температура:\n" \
                     f"\t\tутреняя -> {day_weather['temp']['morn']} С " \
                     f"(чуствуется как {day_weather['feels_like']['morn']} С)\n" \
                     f"\t\tдневная -> {day_weather['temp']['day']} С " \
                     f"(чуствуется как {day_weather['feels_like']['day']} С)\n" \
                     f"\t\tвечерняя -> {day_weather['temp']['eve']} С " \
                     f"(чуствуется как {day_weather['feels_like']['eve']} С)\n" \
                     f"\t\tночная -> {day_weather['temp']['night']} С " \
                     f"(чуствуется как {day_weather['feels_like']['night']} С)\n" \
                     f"\t\tминимальная -> {day_weather['temp']['min']} С\n" \
                     f"\t\tмаксимальная -> {day_weather['temp']['max']} С\n" \
                     f"Давление - {day_weather['pressure']} гПа\n" \
                     f"Влажность - {day_weather['humidity']}%\n" \
                     f"Точка росы -> {day_weather['dew_point']} С\n" \
                     f"Скорость ветра - {day_weather['wind_speed']} метр/сек\n" \
                     f"{wind_gust}" \
                     f"Направление ветра (градусы) - {day_weather['wind_deg']}\n" \
                     f"Облачность - {day_weather['clouds']}%\n" \
                     f"Максимальное значение УФ-индекса за день - {day_weather['uvi']}\n" \
                     f"Вероятность выпадения осадков - {day_weather['pop']}\n" \
                     f"{rain}" \
                     f"{snow}"
    return weather_string


def get_weather_string_sinoptik(day_weather):
    weather_string = f"###Sinoptik###\n" \
                     f"{day_weather.select_one('.day-link').text}, " \
                     f"{day_weather.select_one('.date').text} {day_weather.select_one('.month').text}\n" \
                     f"{day_weather.select_one('.weatherIco')['title']}\n" \
                     f"Температура:\n" \
                     f"\t\tмин -> {day_weather.select_one('.temperature .min span').text}\n" \
                     f"\t\tмакс -> {day_weather.select_one('.temperature .max span').text}"
    return weather_string


def send_weather(bot, chat_id, days, data_weather_prefix, city_info=False):
    user_location = dbworker.get_value(config.DB_FILE_LOCATION, chat_id)

    city_info = city_info or get_city_info(user_location)
    open_weather = get_weather_from_ow(city_info['coords'])
    location_name = city_info['location_name']

    sinoptik = get_weather_from_sinoptik(user_location) or get_weather_from_sinoptik(location_name)

    if not open_weather and not sinoptik:
        bot.send_message(chat_id, f"Не могу найти погоду для \"{user_location}\"")
        return False
    else:
        bot.send_message(chat_id, f"Вот погода {data_weather_prefix} для \"{location_name}\":\n")
        ow_daily = open_weather and open_weather['daily']

        for i in days:
            if open_weather:
                elem = ow_daily[i]
                weather_string_ow = get_weather_string_ow(elem, open_weather['timezone_offset'])
                bot.send_photo(chat_id, f"http://openweathermap.org/img/wn/{elem['weather'][0]['icon']}@2x.png")
                bot.send_message(chat_id, weather_string_ow)
            else:
                bot.send_message(chat_id, "Нет данных в OpenWeather")
            if sinoptik:
                elem = sinoptik.select_one(f"#bd{i + 1}")
                weather_string_sinoptik = get_weather_string_sinoptik(elem)
                bot.send_photo(chat_id, f"https:{elem.select_one('.weatherImg')['src']}")
                bot.send_message(chat_id, weather_string_sinoptik)
            else:
                bot.send_message(chat_id, f"Нет данных в Sinoptik")

    return True


def add_keyboard(bot, chat_id, buttons, row_width, resize_keyboard=False, one_time_keyboard=False):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=row_width, resize_keyboard=resize_keyboard,
                                                 one_time_keyboard=one_time_keyboard)
    for title in buttons:
        keyboard.add(title)
    keyboard.add('/reset')
    bot.send_message(chat_id, 'Выберите вариант', reply_markup=keyboard)


def change_weather_mode(text, bot, chat_id, city_info=False):
    if text == config.W_TODAY_TITLE and send_weather(bot, chat_id, [0], config.W_TODAY_TITLE.lower(), city_info):
        add_keyboard(bot, chat_id, [config.W_TOMORROW_TITLE, config.W_5_DAYS_TITLE], 1, True)
        dbworker.set_value(config.DB_FILE_STATE, chat_id, config.States.S_WEATHER_TODAY.value)
    elif text == config.W_TOMORROW_TITLE and send_weather(bot, chat_id, [1], config.W_TOMORROW_TITLE.lower(),
                                                          city_info):
        add_keyboard(bot, chat_id, [config.W_TODAY_TITLE, config.W_5_DAYS_TITLE], 1, True)
        dbworker.set_value(config.DB_FILE_STATE, chat_id, config.States.S_WEATHER_TOMORROW.value)
    elif text == config.W_5_DAYS_TITLE and send_weather(bot, chat_id, range(5), config.W_5_DAYS_TITLE.lower(),
                                                        city_info):
        add_keyboard(bot, chat_id, [config.W_TODAY_TITLE, config.W_TOMORROW_TITLE], 1, True)
        dbworker.set_value(config.DB_FILE_STATE, chat_id, config.States.S_WEATHER_NEXT_5_DAYS.value)
