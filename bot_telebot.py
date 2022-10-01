import os
from random import randint

import requests
import telebot
from dotenv import load_dotenv
from telebot import types

load_dotenv()
#   Украсить кнопки, добавить везде "в начало"
#   Добавить смайлики в тексты
telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
kinopoisk_token = os.getenv('KINOPOISK_TOKEN')
bot = telebot.TeleBot(telegram_bot_token)

URL = ('https://api.kinopoisk.dev/{type_of_request}?token={token}'
       '&isStrict=false&limit=1&page={page}&search=500-99999999&field=votes.kp'
       '&search=500-99999999&field=votes.imdb')
REQUEST_URL = URL
ADD_PARAM = '&search={}&field={}'

main_keyboard = types.InlineKeyboardMarkup(row_width=3)
movie_keyboard = types.InlineKeyboardMarkup(row_width=3)
type_of_movie_keyboard = types.InlineKeyboardMarkup(row_width=3)
after_search_keyboard = types.InlineKeyboardMarkup(row_width=3)
rate_services_keyboard = types.InlineKeyboardMarkup(row_width=3)

search_button = types.InlineKeyboardButton('Найти', callback_data='search')
new_search_button = types.InlineKeyboardButton(
    'Новый поиск',
    callback_data='new_search'
)
movie_button = types.InlineKeyboardButton('Кино', callback_data='movie_button')
type_of_movie_button = types.InlineKeyboardButton(
    'Выбрать тип кино',
    callback_data='type_of_movie'
)
genre_button = types.InlineKeyboardButton(
    'Добавить жанр',
    callback_data='genre'
)
rating_button = types.InlineKeyboardButton(
    'Добавить рейтинг',
    callback_data='rating'
)
year_button = types.InlineKeyboardButton('Добавить год', callback_data='year')
imdb_buton = types.InlineKeyboardButton('IMDb', callback_data='imdb')
kp_buton = types.InlineKeyboardButton('Kinopoisk', callback_data='kp')
back_buton = types.InlineKeyboardButton('Назад', callback_data='back')
film = types.InlineKeyboardButton('Фильм', callback_data='movie')
tv_series = types.InlineKeyboardButton('Сериал', callback_data='tv-series')
cartoon = types.InlineKeyboardButton('Мультфильм', callback_data='cartoon')
anime = types.InlineKeyboardButton('Аниме', callback_data='anime')
animated_series = types.InlineKeyboardButton(
    'Аниме-сериал',
    callback_data='animated-series'
)
tv_show = types.InlineKeyboardButton('ТВ-шоу', callback_data='tv-show')

main_keyboard.add(movie_button)
movie_keyboard.add(
    new_search_button,
    genre_button,
    rating_button,
    year_button,
    search_button
)
type_of_movie_keyboard.add(
    film, tv_series, cartoon, anime, animated_series, tv_show
)
after_search_keyboard.add(new_search_button, search_button)
rate_services_keyboard.add(imdb_buton, kp_buton)


@bot.message_handler(commands=[
    'start',
    'help'
])
def send_welcome(message):
    FIRST_TEXT = ('Приветик, {}! Я ботик Кеша, и я знаю всё о мире кино! '
                  'Что будем искать? с:')
    bot.reply_to(
        message,
        FIRST_TEXT.format(message.from_user.first_name),
        reply_markup=main_keyboard
    )


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    CHOOSE_PARAMS = 'Выбери желамый параметр поиска!'
    CHOOSE_RATING = ('Напиши, пожалуйста, желаемый диапазон оценки (например'
                     ': 6-8)')
    PRINT_PARAM = 'Напиши значение или диапазон выбранного параметра!'
    NEW_SEARCH = 'Давай ещё что-нибудь найдём!'
    message = call.message
    try:
        if message:
            chat_id = message.chat.id
            message_id = message.id
            global REQUEST_URL
            if call.data == 'search':
                bot.edit_message_reply_markup(chat_id, message_id)
                search(message)
            if call.data == 'new_search':
                REQUEST_URL = URL
                bot.edit_message_reply_markup(chat_id, message_id)
                bot.send_message(
                    chat_id, NEW_SEARCH, reply_markup=main_keyboard
                )
            if call.data == 'movie_button':
                bot.edit_message_reply_markup(
                    chat_id,
                    message_id,
                    reply_markup=type_of_movie_keyboard
                )
                REQUEST_URL = REQUEST_URL.format(
                    type_of_request='movie', token='{token}', page='{page}'
                )
            if (
                call.data == 'movie'
                or call.data == 'tv-series'
                or call.data == 'cartoon'
                or call.data == 'anime'
                or call.data == 'animated-series'
                or call.data == 'tv-show'
            ):
                REQUEST_URL += ADD_PARAM.format(call.data, 'type')
                bot.edit_message_reply_markup(
                    chat_id,
                    message_id,
                    CHOOSE_RATING,
                    reply_markup=movie_keyboard
                )
            if (
                call.data == 'genre'
                or call.data == 'year'
            ):
                bot.edit_message_reply_markup(chat_id, message_id)
                response = bot.send_message(chat_id, PRINT_PARAM)
                bot.register_next_step_handler(response, add_params, call.data)
            if call.data == 'rating':
                bot.edit_message_reply_markup(
                    chat_id,
                    message_id,
                    CHOOSE_PARAMS,
                    reply_markup=rate_services_keyboard
                )
            if (
                call.data == 'imdb'
                or call.data == 'kp'
            ):
                bot.edit_message_reply_markup(chat_id, message_id)
                response = bot.send_message(chat_id, CHOOSE_RATING)
                bot.register_next_step_handler(response, add_params, call.data)
    except Exception as e:
        bot.send_message(chat_id, repr(e))
        print(repr(e))


def add_params(message, field):
    PARAM_ADDED = 'Параметр добавлен! Выбери следующее дейтсвие:'
    global REQUEST_URL
    if field == 'genre':
        field = 'genres.name'
    if (field == 'imdb'
       or field == 'kp'):
        field = 'rating.{}'.format(field)
    REQUEST_URL += ADD_PARAM.format(message.text.lower(), field)
    bot.send_message(message.chat.id, PARAM_ADDED, reply_markup=movie_keyboard)


def search(message):
    NOTHING_FOUND = ('По Вашему запросу ничего не найдено. Попробуйте изменить'
                     ' параметры поиска. Что будем искать?')
    UNKNOWN_ERROR = 'Неизвестная ошибка. Попробуйте ещё раз.'
    SEARCH_RESULT = ('{name}\nГод: {year}\nKinopoisk: {kinopoisk} ({votes_kp} '
                     'чел.)\nIMDb: {imdb} ({votes_imdb} '
                     'чел.)\nОписание: {description}')
    chat_id = message.chat.id
    global REQUEST_URL
    try:
        response = requests.get(
            REQUEST_URL.format(token=kinopoisk_token, page='{page}')
        ).json()
        film = requests.get(REQUEST_URL.format(
            token=kinopoisk_token,
            page=randint(0, response['pages']) - 1
        )).json()
        bot.send_photo(
            chat_id,
            film['docs'][0]['poster']['url'],
            caption=SEARCH_RESULT.format(
                name=film['docs'][0]['name'],
                year=film['docs'][0]['year'],
                kinopoisk=film['docs'][0]['rating']['kp'],
                imdb=film['docs'][0]['rating']['imdb'],
                description=film['docs'][0]['description'],
                votes_kp=film['docs'][0]['votes']['kp'],
                votes_imdb=film['docs'][0]['votes']['imdb']
            ),
            reply_markup=after_search_keyboard
        )
    except IndexError:
        bot.send_message(chat_id, NOTHING_FOUND, reply_markup=main_keyboard)
        REQUEST_URL = URL
    except Exception as e:
        bot.send_message(chat_id, UNKNOWN_ERROR, reply_markup=main_keyboard)
        REQUEST_URL = URL
        print(repr(e))


def main():
    bot.infinity_polling()


if __name__ == '__main__':
    main()
