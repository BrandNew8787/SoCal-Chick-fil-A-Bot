import asyncio
import aiohttp  # For asynchronous HTTP requests
import requests
from datetime import datetime


def get_next_angels_game():
    # Set up the API URL with the necessary parameters
    team_id = 108  # Los Angeles Angels team ID
    today = datetime.today().strftime('%Y-%m-%d')
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId={team_id}&startDate={today}&endDate=2024-12-31"

    # Send a GET request to the API
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        # Iterate through the dates and find the first game that is scheduled
        for date_info in data.get('dates', []):
            for game in date_info.get('games', []):
                if (game['status']['detailedState'] == 'Scheduled'
                        and game['teams']['home']['team']['name'] == 'Los Angeles Angels'):
                    game_date = game['officialDate']
                    opponent_team = game['teams']['away']['team']['name'] if game['teams']['home']['team'][
                                                                                 'id'] == team_id else \
                        game['teams']['home']['team']['name']
                    venue = game['venue']['name']
                    return f"Next Angels Home game is on {game_date} against {opponent_team} at {venue}."

        return "No upcoming games found for the Angels."
    else:
        return f"Failed to retrieve data. Status code: {response.status_code}"


async def get_today_angels_home_game():
    # Set up the API URL with the necessary parameters
    team_id = 108  # Los Angeles Angels team ID
    today = datetime.today().strftime('%Y-%m-%d')
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId={team_id}&startDate={today}&endDate={today}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data_mlb = await response.json()

    games = data_mlb.get('dates', [])[0].get('games', [])

    for game in games:
        # Check if the Angels are playing at home
        if game['teams']['home']['team']['name'] == "Los Angeles Angels":
            return True
    return False


async def check_angels_score():
    # Set up the API URL with the necessary parameters
    team_id = 108  # Los Angeles Angels team ID
    today = datetime.today().strftime('%Y-%m-%d')
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId={team_id}&startDate={today}&endDate={today}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data_mlb = await response.json()

    # Extract games from today's schedule
    games = data_mlb.get('dates', [])[0].get('games', [])

    for game in games:
        # Check if the Angels are playing at home
        if game['teams']['home']['team']['name'] == "Los Angeles Angels":
            # Ensure 'score' key exists before accessing it
            if game['status']['detailedState'] != "Final" and game['status']['abstractGameCode'] != 'F':
                return "The game has not finished yet!"
            if 'score' in game['teams']['home']:
                # Check if the Angels have scored 7 or more runs
                if game['teams']['home']['score'] >= 7:
                    return True
    return False

# Run the asynchronous function using an event loop
async def main():
    result = await check_angels_score()
    print(result)

# Run the async function
if __name__ == "__main__":
    asyncio.run(main())