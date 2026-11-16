from datetime import datetime, timedelta

from pytz import timezone
from telegram.ext import CallbackContext
from telegram import Bot

import config
from football_parser import get_data
from db import db_session
from models import Shedule, User, Club


def delete_old_matches(context: CallbackContext):
    print('задача запущена!')
    now = datetime.now()
    print(now)
    all_matches = Shedule.query.filter(Shedule.match_date < now).all()
    for match in all_matches:
        db_session.delete(match)
    db_session.commit()

def update_schedule(context: CallbackContext):
    print('Запущено обновление расписания')
    get_data()
    print('Расписание успешно обновлено')

def send_matches_reminders(context: CallbackContext):
    bot = Bot(token=config.API_TOKEN_BOT)
    now = datetime.now()
    start_range = datetime(now.year, now.month, now.day) + timedelta(days=1)
    end_range = start_range + timedelta(days=1)

    matches = Shedule.query.filter(
        Shedule.match_date >= start_range,
        Shedule.match_date < end_range
    ).all()

    for match in matches:
        home_club = Club.query.get(match.home_team)
        away_club = Club.query.get(match.away_team)
        match_time = match.match_date.strftime("%H:%M")

        users_home = User.query.filter_by(club_id=home_club.id).all()
        users_away = User.query.filter_by(club_id=away_club.id).all()

        for user in users_home + users_away:
            if user.club_id == home_club.id:
                opponent = away_club.club
                location = "дома"
            else:
                opponent = home_club.club
                location = "в гостях"

            text = (f"Напоминание: завтра в {match_time} матч {home_club.club} vs {away_club.club}\n"
                    f"Ваша команда {home_club.club if user.club_id == home_club.id else away_club.club} играет {location} против {opponent}.")
            try:
                bot.send_message(chat_id=user.telegram_id, text=text)
            except Exception as e:
                print(f"Не удалось отправить сообщение {user.telegram_id}: {e}")

# функция обновления расписания
# вызываем get_data