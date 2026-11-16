from telegram import ReplyKeyboardMarkup
import requests


def get_kb():
    btns = [
        ['Подписаться на рассылку'],
        ['Ближайшая дата матча'],
        ['Связаться с админом']
    ]
    return ReplyKeyboardMarkup(btns, resize_keyboard=True)


def get_names_kb(names):
    btns = []
    # clubs = map(lambda club: club.club, clubs)
    names = sorted(names)
    for i in range(0, len(names), 2):
        if i + 1 < len(names):
            btns.append([names[i], names[i + 1]])
        else:
            btns.append([names[i]])
    return ReplyKeyboardMarkup(btns, resize_keyboard=True)


def get_response(url, params=None, headers=None):
    response = requests.get(url, params=params, headers=headers)
    try:
        response.raise_for_status()
        return response
    except requests.RequestException:
        print('api сломался')
        return False
