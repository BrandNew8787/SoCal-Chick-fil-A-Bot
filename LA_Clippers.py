import asyncio
import json
from datetime import datetime, timezone
from dateutil import parser
import requests
from bs4 import BeautifulSoup
from nba_api.stats.endpoints import leaguegamefinder, playbyplayv2
from nba_api.live.nba.endpoints import playbyplay


# once the game is over, this function works!
async def check_game_finish():
    # Get today's date in the correct format
    today_date = datetime.today().strftime('%m/%d/%Y')

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
    today_date = datetime.today().strftime('%m/%d/%Y')

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
async def get_game_id_today():
    # Fetch the JSON data from the API
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/91.0.4472.124 Safari/537.36"
    }

    today = datetime.today().strftime("%m/%d/%Y")
    season = datetime.today().strftime("%Y")

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

    # Format and print the games
    print("NBA Games for 11/20/2024:")
    game_format = "{gameID}: {awayTeam} vs. {homeTeam} @ {gameTime} ({broadcaster})"

    for game in future_games:
        if game['htNickName'] == 'Clippers' and datetime.today().strftime("%m/%d/%Y") == game['date']:
            print(
                game_format.format(
                    gameID=game["gameID"],
                    awayTeam=f"{game['vtCity']} {game['vtNickName']}",
                    homeTeam=f"{game['htCity']} {game['htNickName']}",
                    gameTime=game["time"],
                    broadcaster=", ".join([b["broadcasterName"] for b in game["broadcasters"]])
                )
            )
            return game["gameID"]

    # Checks if there are any games playing live or if they are completed.
    for game in ongoing_finished_games:
        if game['htNickName'] == 'Clippers' and today == game['date']:
            print(
                game_format.format(
                    gameID=game["gameID"],
                    awayTeam=f"{game['vtCity']} {game['vtNickName']}",
                    homeTeam=f"{game['htCity']} {game['htNickName']}",
                    gameTime=game["time"],
                    broadcaster=f", {game['broadcasterName']}"
                )
            )
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
        games = data.get('leagueSchedule', {}).get('gameDates', [])

        for game_date in games:
            # Parse and reformat the date
            original_date = game_date.get('gameDate')  # e.g., '10/05/2024 00:00:00'
            game_datetime = datetime.strptime(original_date, '%m/%d/%Y %H:%M:%S')  # Convert to datetime object

            # Get the date part only
            game_date_only = game_datetime.date()

            for game in game_date.get('games', []):
                if (game.get('homeTeam', {}).get('teamName', 'N/A') == "Clippers"
                        and game_date_only >= datetime.now().date()):
                    home_team = game.get('homeTeam', {}).get('teamName', 'N/A')
                    away_team = game.get('awayTeam', {}).get('teamName', 'N/A')
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
