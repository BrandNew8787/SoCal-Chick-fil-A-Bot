import asyncio
from datetime import datetime

import aiohttp  # For asynchronous HTTP requests

today = datetime.today().strftime('%Y-%m-%d')
NHL_API_URL: [str] = f"https://api-web.nhle.com/v1/score/{today}"
# NHL_API_URL: [str] = f"https://api-web.nhle.com/v1/score/2024-04-18"
# NHL_API_URL: [str] = f"https://api-web.nhle.com/v1/score/2024-11-25"


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

    # Check if it was a Ducks home game and they scored 5 points
    daily_games = data_nhl['games']
    for i in daily_games:
        if i['awayTeam']['id'] == 24:
            return True
    return False


# If there is a home game, checks if the ducks scored 5 points
async def check_ducks_score():
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


# For testing the ducks games, checks if the ducks scored 2 points at an away game
async def check_ducks_away_score():
    async with aiohttp.ClientSession() as session:
        async with session.get(NHL_API_URL) as response:
            data_nhl = await response.json()

    # Check if it was a Ducks home game and they scored 5 points
    daily_games = data_nhl['games']
    for i in daily_games:
        if i['awayTeam']['id'] == 24:
            if 'scores' in i['awayTeam'] and 'gameOutcome' in i:
                if i['awayTeam']['scores'] >= 2:
                    return True
                else:
                    return False
    return "The game hasn't finished yet!"


# async def main():
#     result = await get_ducks_next_home_game()
#     print(result)
#     # Uncomment if you want to run the check_ducks_score function
#     score_result = await check_ducks_score()
#     if score_result:
#         print("Ducks scored 5 points!")
#     else:
#         print("The game hasn't finished, or they haven't scored 5 points yet.")
#
#
# # Run the async function
# if __name__ == "__main__":
#     asyncio.run(main())
