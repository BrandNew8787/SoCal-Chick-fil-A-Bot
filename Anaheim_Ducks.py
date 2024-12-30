import asyncio
from datetime import datetime

import aiohttp  # For asynchronous HTTP requests

today = datetime.today().strftime('%Y-%m-%d')
# NHL_API_URL: [str] = f"https://api-web.nhle.com/v1/score/{today}"
# NHL_API_URL: [str] = f"https://api-web.nhle.com/v1/score/2024-04-18"
# NHL_API_URL: [str] = f"https://api-web.nhle.com/v1/score/2024-11-25"

# shootout game id = 2024020392
NHL_API_URL: [str] = f"https://api-web.nhle.com/v1/score/2024-12-01"


async def get_game_id():
    async with aiohttp.ClientSession() as session:
        async with session.get(NHL_API_URL) as response:
            data_nhl = await response.json()

    # Check if it was a Ducks home game and they scored 5 points
    daily_games = data_nhl['games']
    for i in daily_games:
        if i['homeTeam']['id'] == 24:
            return i['id']
    return None


# Receives the next home game
async def get_ducks_next_home_game():
    # Define the endpoint for the Ducks' schedule
    schedule_url = f"https://api-web.nhle.com/v1/club-schedule-season/ANA/now"
    today_home = datetime.today().strftime('%Y-%m-%d')

    async with aiohttp.ClientSession() as session:
        async with session.get(schedule_url) as response:
            schedule_data = await response.json()

    for row in schedule_data['games']:
        if row['homeTeam']['id'] == 24 and row['gameDate'] >= today_home:
            return row['gameDate'], row['awayTeam']['placeName']['default']

    return "No upcoming home games found."


# Checks if there is a ducks home game today
async def ducks_home_game_today():
    async with aiohttp.ClientSession() as session:
        async with session.get(NHL_API_URL) as response:
            data_nhl = await response.json()

    # Check if it was a Ducks home game and they scored 5 points
    daily_games = data_nhl['games']
    for i in daily_games:
        if i['homeTeam']['id'] == 24:
            return True
    return False


# check if there is an away game today
async def ducks_away_game_today():
    async with aiohttp.ClientSession() as session:
        async with session.get(NHL_API_URL) as response:
            data_nhl = await response.json()
    daily_games = data_nhl['games']
    for i in daily_games:
        if i['awayTeam']['id'] == 24:
            return True
    return False


# If there is a home game, checks if the ducks scored 5 points
# THIS DOES NOT ACCOUNT FOR SHOOT OUTS
async def check_ducks_score_non_shootout():
    async with aiohttp.ClientSession() as session:
        async with session.get(NHL_API_URL) as response:
            data_nhl = await response.json()

    # Check if it was a Ducks home game and they scored 5 points
    daily_games = data_nhl['games']
    for i in daily_games:
        if i['homeTeam']['id'] == 24:
            if 'score' in i['homeTeam'] and 'gameOutcome' in i:
                if i['homeTeam']['score'] >= 5:
                    return True
                else:
                    return False
    return "The game hasn't finished yet!"


# returns true if the ducks have scored 5 or more goals including shootouts
async def check_ducks_score(game_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play") as response:
            data_nhl = await response.json()

    result = data_nhl['plays'][-1]['typeDescKey']
    if data_nhl['plays'][-1]['typeDescKey'] == 'game-end':
        # Check if it was a Ducks home game and they scored 5 points
        away_score = int
        if 'score' in data_nhl['awayTeam']:
            away_score = data_nhl['awayTeam']['score']
        else:
            away_score = 0
        away_team = data_nhl['awayTeam']['abbrev']
        home_score = int
        if 'score' in data_nhl['homeTeam']:
            home_score = data_nhl['homeTeam']['score']
        else:
            home_score = 0

        if data_nhl['shootoutInUse']:
            so_score = 0
            for plays in data_nhl['plays']:
                if plays['periodDescriptor']['periodType'] == 'SO':
                    if plays['typeDescKey'] == 'goal' and plays['details']['eventOwnerTeamId'] == 24:
                        so_score += 1
            if home_score > away_score:
                if home_score - 1 + so_score >= 5:
                    return True
            else:
                return False
        else:
            if home_score >= 5:
                return True
            else:
                return False
    else:
        return "The game hasn't finished yet!"


# For testing the ducks games, checks if the ducks scored 2 points at an away game
async def check_ducks_away_score():
    async with aiohttp.ClientSession() as session:
        async with session.get(NHL_API_URL) as response:
            data_nhl = await response.json()

    # Check if it was a Ducks home game and they scored 5 points
    daily_games = data_nhl['games']
    for i in daily_games:
        if i['awayTeam']['id'] == 24:
            # THERE IS A TYPO WITH SCORE!!!! PLEASE FIX TMRW!
            if 'score' in i['awayTeam'] and 'gameOutcome' in i:
                if i['awayTeam']['score'] >= 2:
                    return True
                else:
                    return False
    return "The game hasn't finished yet!"

