from datetime import datetime, timedelta
import pytz
import aiohttp  # For asynchronous HTTP requests
import requests

pacific_tz = pytz.timezone("America/Los_Angeles")

# returns the date and opponent of the next angels game
def get_next_angels_game():
    # Set up the API URL with the necessary parameters
    team_id = 108  # Los Angeles Angels team ID
    today = datetime.now(pacific_tz)
    next_year = today + timedelta(days=365)
    url = (f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId={team_id}"
           f"&startDate={today.strftime('%Y-%m-%d')}&endDate={next_year.strftime('%Y-%m-%d')}")
    "2024-09-29"

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
                    return game_date, opponent_team

        return "No upcoming games found for the Angels."
    else:
        return f"Failed to retrieve data. Status code: {response.status_code}"


# returns a boolean whether there is an angels game today or not
async def get_today_angels_home_game():
    # Set up the API URL with the necessary parameters
    team_id = 108  # Los Angeles Angels team ID
    today = datetime.now(pacific_tz).strftime('%Y-%m-%d')
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId={team_id}&startDate={today}&endDate={today}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data_mlb = await response.json()

    # checks if any games exists today
    if len(data_mlb['dates']) != 0:
        games = data_mlb.get('dates', [])[0].get('games', [])

        for game in games:
            # Check if the Angels are playing at home
            if game['teams']['home']['team']['name'] == "Los Angeles Angels":
                return True
        return False
    else:
        return False


# returns a boolean if the game is finished and if the angels scored 7 or more at a home game
async def check_angels_score():
    # Set up the API URL with the necessary parameters
    team_id = 108  # Los Angeles Angels team ID
    today = datetime.now(pacific_tz).strftime('%Y-%m-%d')
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


# Returns today's game ID
async def get_game_id():
    # Set up the API URL with the necessary parameters
    team_id = 108  # Los Angeles Angels team ID
    today = datetime.now(pacific_tz).strftime('%Y-%m-%d')
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId={team_id}&startDate={today}&endDate={today}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data_mlb = await response.json()

    return data_mlb['dates'][0]['games'][0]['gamePk']
