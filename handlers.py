from datetime import datetime
from pytz import timezone

from telegram.ext import CallbackContext, ConversationHandler
from telegram import Update, ReplyKeyboardRemove

from models import Club, Shedule, League, User
from utils import get_kb, get_names_kb
from db import db_session


def greet_user(update: Update, context: CallbackContext):
    username = update.message.chat.username
    update.message.reply_text(
        f'Привет, {username.capitalize()}!',
        reply_markup=get_kb()
    )


def choose_league(update: Update, context: CallbackContext):
    all_leagues = League.query.all()
    names = [league.name for league in all_leagues]
    update.message.reply_text(
        'Выберите чемпионат',
        reply_markup=get_names_kb(names)
    )
    return 'choose_team'


def choose_team(update: Update, context: CallbackContext):
    user_league = update.message.text
    # проверка на чемпионат, существует или нет
    league = League.query.filter_by(name=user_league).first()
    if not league:
        update.message.reply_text('Ошибка: выберите лигу из списка.', reply_markup=get_kb())
        return ConversationHandler.END
    all_clubs = Club.query.filter_by(league=league.id)
    print(all_clubs)
    print(all_clubs.count())
    # если all_clubs нечетное, то что-то делаем

    names = [club.club for club in all_clubs.all()]

    update.message.reply_text(
        'Укажите Вашу любимую команду',
        reply_markup=get_names_kb(names)
    )
    return 'show_shedule'


def show_shedule(update: Update, context: CallbackContext):
    user_team = update.message.text
    # а что делает пользователь? если регистрируется, то расписание ему не нужно!
    # проверка через context.user_data - туда можно сохранять абсолютно все
    check_club = Club.query.filter(Club.club == user_team).first()
    if not check_club:
        update.message.reply_text('Error, выберите клуб из указанных ниже')
        return 'show_shedule'

    context.user_data['favorite_club_id'] = check_club.id
    matches = Shedule.query.filter(
        (Shedule.home_team == check_club.id) | (Shedule.away_team == check_club.id)
    ).order_by(Shedule.match_date).all()

    now = datetime.now()
    nearest = None
    for match in matches:
        if match.match_date >= now:
            nearest = match
            break

    if matches and nearest is not None:
        home_club = Club.query.get(nearest.home_team)
        away_club = Club.query.get(nearest.away_team)
        if check_club.id == home_club.id:
            opponent = away_club.club
            location = "дома"
        else:
            opponent = home_club.club
            location = "в гостях"
        date_str = nearest.match_date.strftime("%d.%m.%Y в %H:%M")
        message = (
            f"Ваша любимая команда: {check_club.club}\n"
            f"Ближайший матч: {date_str} против {opponent} ({location})"
        )
    else:
        message = f"Отлично! Ваша любимая команда: {check_club.club}\nБлижайших матчей пока нет."

    update.message.reply_text(message, reply_markup=get_kb())
    return ConversationHandler.END

def start_subscription(update: Update, context: CallbackContext):
    all_leagues = League.query.all()
    names = [league.name for league in all_leagues]
    update.message.reply_text(
        'Выберите чемпионат для подписки:',
        reply_markup=get_names_kb(names)
    )
    return 'choose_league_sub'

def choose_league_sub(update: Update, context: CallbackContext):
    user_league = update.message.text
    league = League.query.filter_by(name=user_league).first()
    clubs = Club.query.filter_by(league=league.id).all()
    names = [club.club for club in clubs]
    context.user_data['sub_league_id'] = league.id
    update.message.reply_text(
        'Выберите вашу любимую команду:',
        reply_markup=get_names_kb(names)
    )
    return 'choose_team_sub'
def choose_team_sub(update: Update, context: CallbackContext):
    team_name = update.message.text
    club = Club.query.filter_by(club=team_name).first()
    user_id = update.message.chat.id
    existing = User.query.filter_by(telegram_id=user_id).first()
    if existing:
        existing.club_id = club.id
    else:
        new_user = User(telegram_id=user_id, club_id=club.id)
        db_session.add(new_user)
    db_session.commit()

    update.message.reply_text(
        f'Вы подписались на рассылку матчей команды "{club.club}". ',
        reply_markup=get_kb()
    )
    return ConversationHandler.END
