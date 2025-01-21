from datetime import datetime
import pytz
import aiohttp
import requests
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.live.nba.endpoints import playbyplay

pacific_tz = pytz.timezone("America/Los_Angeles")


# use only if the game is finished
def check_game_finish():
    # Get today's date in the correct format
    today_date = datetime.now(pacific_tz).strftime('%m/%d/%Y')

    # this is a date where the opponent of the clippers missed 2 free throws
    # other_date = "11/18/2024"

    try:
        # Simple test request to see if the API is reachable
        gamefinder = leaguegamefinder.LeagueGameFinder(
            team_id_nullable=1610612746,  # Clippers team ID
            date_from_nullable=today_date,
            date_to_nullable=today_date
        )
        games = gamefinder.get_data_frames()[0]

        # Filter the games to find a home game (indicated by 'vs.' in the MATCHUP field)
        clippers_home_game_today = games[games['MATCHUP'].str.contains('vs.')]

        if not clippers_home_game_today.empty:
            game_result = clippers_home_game_today.iloc[0]['WL']
            return game_result
        else:
            return None

    except Exception as e:
        print("An error occurred:", e)
        return None


# This function can be used to check if there are any live games going on right now.
def check_live_game():
    # Get today's date in the correct format
    today_date = datetime.now(pacific_tz).strftime('%m/%d/%Y')

    try:
        # Simple test request to see if the API is reachable
        games = playbyplay.PlayByPlay(game_id=get_game_id_today()).get_dict()

        # Filter the games to find a home game (indicated by 'vs.' in the MATCHUP field)
        clippers_home_game_today = games[games['MATCHUP'].str.contains('vs.')]

        if not clippers_home_game_today.empty:
            game_result = clippers_home_game_today.iloc[0]['WL']
            return game_result
        else:
            return None

    except Exception as e:
        print("An error occurred:", e)
        return None


# This is the new function that returns the id if there is a clippers home game today
def get_game_id_today():
    # Fetch the JSON data from the API
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/91.0.4472.124 Safari/537.36"
    }

    today = datetime.now(pacific_tz).strftime("%m/%d/%Y")
    season = datetime.now(pacific_tz).strftime("%Y")
    if datetime.now(pacific_tz).month < 6:
        season = str(int(season) - 1)

    # this is a date where the opponent of the clippers missed 2 free throws
    # today = "11/18/2024"

    # URL to fetch the JSON data
    url = f"https://stats.nba.com/stats/internationalbroadcasterschedule?LeagueID=00&Season={season}&RegionID=1&Date={today}&EST=Y"

    response = requests.get(url, headers=headers)
    data = response.json()

    # Extract the upcoming games
    future_games = data["resultSets"][0]["NextGameList"]

    # Extract either live or finished games
    ongoing_finished_games = data["resultSets"][1]["CompleteGameList"]

    for game in future_games:
        if game['htNickName'] == 'Clippers' and datetime.now(pacific_tz).strftime("%m/%d/%Y") == game['date']:
            return game["gameID"]

    # Checks if there are any games playing live or if they are completed.
    for game in ongoing_finished_games:
        if game['htNickName'] == 'Clippers' and today == game['date']:
            return game["gameID"]
    return None


# finds the next clippers home game parsing through a json file
def get_next_clippers_home_game():
    # URL for the NBA schedule JSON data
    url = "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json"

    try:
        # Fetch the JSON data
        response = requests.get(url)
        response.raise_for_status()  # Ensure the request was successful

        # Parse the JSON content
        data = response.json()

        # Example: Extracting all games
        games = data['leagueSchedule']['gameDates']

        for game_date in games:
            # Parse and reformat the date
            original_date = game_date.get('gameDate')  # e.g., '10/05/2024 00:00:00'
            game_datetime = datetime.strptime(original_date, '%m/%d/%Y %H:%M:%S')  # Convert to datetime object

            # Get the date part only
            game_date_only = game_datetime.date()

            for game in game_date['games']:
                if (game['homeTeam']['teamName'] == "Clippers"
                        and game_date_only >= datetime.now(pacific_tz).date()):
                    home_team = game['homeTeam']['teamName']
                    away_team = game['awayTeam']['teamCity'] + " " + game['awayTeam']['teamName']
                    formatted_date = datetime.strptime(original_date, '%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d')
                    return formatted_date, away_team

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")


# This function displays the current games that are going on right now with live updates.
# It will send a message if the opponents of the opponents missed 2 free throws in a row in the 4th quarter.
def check_opponent_missed_two_ft_in_4th_quarter(game_id):
    pbp = playbyplay.PlayByPlay(game_id=game_id).get_dict()
    events = pbp['game']['actions']

    for event in events:
        period = event.get('period', 0)
        description = event.get('description', '')
        team_abbreviation = event.get('teamTricode', '')

        # We are only interested in the 4th quarter (period 4)
        if period == 4:
            # Check for missed free throw events by the opponent
            if ('MISS' in description and 'Free Throw' in description
                    and ('2 of 2' in description or '2 of 3' in description or '3 of 3' in description)):
                if team_abbreviation != 'LAC':
                    return True
    return False
