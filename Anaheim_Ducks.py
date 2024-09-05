import asyncio
import aiohttp  # For asynchronous HTTP requests
import requests
from datetime import datetime

today = datetime.today().strftime('%Y-%m-%d')
# NHL_API_URL: [str] = f"https://api-web.nhle.com/v1/score/{today}"
NHL_API_URL: [str] = f"https://api-web.nhle.com/v1/score/2024-04-18"


async def get_ducks_next_home_game():
    # Define the endpoint for the Ducks' schedule
    team_id = 24  # Anaheim Ducks' team ID in the NHL API
    schedule_url = f"https://api-web.nhle.com/v1/club-schedule-season/ANA/now"
    today = datetime.today().strftime('%Y-%m-%d')

    async with aiohttp.ClientSession() as session:
        async with session.get(schedule_url) as response:
            schedule_data = await response.json()

    for row in schedule_data['games']:
        if row['homeTeam']['id'] == 24 and row['gameDate'] >= today:
            return f"Next Ducks Home Game: \n\tDate: {row['gameDate']}\n\tOpp: {row['awayTeam']['placeName']['default']}"

    return "No upcoming home games found."
# gameOutcome

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


async def check_ducks_score():
    async with aiohttp.ClientSession() as session:
        async with session.get(NHL_API_URL) as response:
            data_nhl = await response.json()

    # Check if it was a Ducks home game and they scored 5 points
    daily_games = data_nhl['games']
    free_chick_fil_a = False
    for i in daily_games:
        if i['homeTeam']['id'] == 24:
            if 'scores' in i['homeTeam'] and 'gameOutcome' in i:
                if i['homeTeam']['scores'] >= 5:
                    return True
                else:
                    return False
    return "The game hasn't finished yet!"


# async def main():
#     result = await check_ducks_score()
#     if result:
#         print(result)
#
# # Run the async function
# if __name__ == "__main__":
#     asyncio.run(main())