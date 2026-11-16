from datetime import datetime, date

from bs4 import BeautifulSoup
from fake_headers import Headers

from db import db_session
from models import League, Club, Shedule
from utils import get_response


def get_data():
    urls = [
        ('https://soccer365.ru/competitions/16/2025-2026/shedule/', 'Испания', 'La Liga'),
        ('https://soccer365.ru/competitions/12/2025-2026/shedule/', 'Англия', 'EPL'),
    ]
    for url, country, league in urls:
        # проверяем, есть ли у нас вообще расписание
        # если нет, то идет код как обычно
        # если есть, то забираем матчи на ближайшие 3 недели и сравниваем даты
        # если расхождение, то меняем дату и commit

        headers = Headers(headers=True).generate()
        response = get_response(url, headers=headers)
        if response:
            html = response.text

            soup = BeautifulSoup(html, 'html.parser')
            games = soup.find_all('div', class_='game_block')
            breadcrumb_h1 = soup.find('h1', class_='breadcrumb')
            # вычленить в маленькую функцию
            start_year, end_year = 2025, 2026
            if breadcrumb_h1:
                season_text = breadcrumb_h1.text
                years = season_text.split('/')
                if len(years) > 1:
                    start_year, end_year = map(int, years)
                else:
                    start_year, end_year = int(years), int(years)

            today = date.today().strftime('%d.%m')

            clubs = set()
            shedule = []

            for game in games:
                game_info = {}
                game_date = game.find('div', class_='status').text
                if ',' not in game_date:
                    game_date = f'{today}, {game_date}'

                date_part = game_date.split(',')[0]
                month = int(date_part.split('.')[1])
                year = start_year if month >= 7 else end_year

                try:
                    game_date = datetime.strptime(f'{year} {game_date}', '%Y %d.%m, %H:%M')
                except ValueError:
                    continue  # пропускаем матч с некорректной датой (например, "Непрерыв")
                game_info['date'] = game_date
                teams = game.find('div', class_='result')
                game_info['home_team'] = teams.find('div', class_='ht').text.strip('\n-')
                game_info['away_team'] = teams.find('div', class_='at').text.strip('\n-')
                print(game_info)
                shedule.append(game_info)
                clubs.add(game_info['home_team'])
            save_data(clubs, shedule, league_name=league, country=country)

    return False


def save_data(clubs, shedule, league_name, country):
    league = League.query.filter(League.name == league_name).first()
    if not league:
        league = League(name=league_name, country=country)
        db_session.add(league)
        db_session.commit()

    club_id = {}
    for club in clubs:
        exist_club = Club.query.filter(Club.club == club).first()
        if exist_club:
            club_id[club] = exist_club.id
        else:
            new_club = Club(club=club, league=league.id)
            db_session.add(new_club)
            db_session.commit()
            club_id[club] = new_club.id

    for match in shedule:
        match_date = match['date']
        home_team = match['home_team']
        away_team = match['away_team']
        home_id = club_id[home_team]
        away_id = club_id[away_team]
        exists = Shedule.query.filter(
            Shedule.home_team == home_id,
            Shedule.away_team == away_id,
            Shedule.match_date == match_date
        ).first()
        if not exists:
            new_match = Shedule(home_team=home_id, away_team=away_id, match_date=match_date)
            db_session.add(new_match)
    db_session.commit()


if __name__ == '__main__':
    get_data()
