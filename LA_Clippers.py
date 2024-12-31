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


# Finds the next clippers game webscraping through the cbs sports website
# THIS FUNCTION IS LESS EFFICIENT
def next_clippers_home_game():
    # URL of the Clippers schedule page on CBS Sports
    url = "https://www.cbssports.com/nba/teams/LAC/los-angeles-clippers/schedule/regular/"

    # Set up headers to mimic a browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/92.0.4515.107 Safari/537.36",
        "Referer": "https://www.cbssports.com/",
        "Accept-Language": "en-US,en;q=0.9",
    }

    # Create a session and send a GET request to the URL
    session = requests.Session()
    response = session.get(url, headers=headers)

    # Check if the response is successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

    # Find all <script> tags with type "application/ld+json"
    script_tags = soup.find_all('script', type='application/ld+json')

    # this is today's date used to compare game dates
    today_date = datetime.now().date()

    # Iterate over all <script> tags found
    for script in script_tags:
        try:
            # Attempt to load the JSON content, stripping problematic characters
            json_data = json.loads(script.string.replace('\n', '').replace('\r', '').replace('\t', ''))

            # Checking if the game is a home game
            if json_data.get('location')['name'] == "Intuit Dome":
                teams = json_data.get('competitor', [])

                # Extract relevant information
                game_date_str = json_data.get('startDate').strip()
                game_date = datetime.strptime(game_date_str, "%b %d, %Y")

                # Format the date as %Y-%m-%d
                formatted_game_date = game_date.strftime("%Y-%m-%d")

                # Compare game date with today's date
                if game_date.date() >= today_date:
                    return formatted_game_date, teams[0]['name'] if 'Clippers' not in teams[0]['name'] else \
                        teams[1]['name']

        except json.JSONDecodeError:
            # Handle JSON parsing errors
            print("Failed to parse JSON data.")
        except Exception as e:
            # Catch-all for any other errors
            print(f"An error occurred: {e}")

    return "No upcoming Clippers home games found."


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
                        and game_date_only >= datetime.now().date()):
                    home_team = game['homeTeam']['teamName']
                    away_team = game['awayTeam']['teamCity'] + " " + game['awayTeam']['teamName']
                    formatted_date = datetime.strptime(original_date, '%m/%d/%Y %H:%M:%S').strftime('%Y-%m-%d')
                    print(f"Date: {formatted_date}")
                    print(f"  - {away_team} at {home_team}")
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


# this function is made so that I can check whether the function handles arguments properly
# It will send a message if the opponents of the clippers made at least 1 free throw in the 1st quarter.
def check_opponent_made_one_ft_in_1st_quarter(game_id):
    # receive the game play by plays by dict
    pbp = playbyplay.PlayByPlay(game_id=game_id).get_dict()
    events = pbp['game']['actions']

    # loop through the play by plays to check if a free throw was made.
    for event in events:
        period = event.get('period', 0)
        description = event.get('description', '')
        team_abbreviation = event.get('teamTricode', '')

        if period == 1:
            # Check if the description matches a made FT
            # if "1 of 2" in description or "1 of 3" in description:
            if ("Free Throw" in description
                    and ("1 of 2" in description or "1 of 3" in description or "2 of 3" in description)):
                # Ensure it's the opponent's FT (not Clippers)
                if team_abbreviation != 'LAC':  # Assuming Clippers' abbreviation is LAC
                    print(description)

    return False


# prints the most current score
def check_score(game_id):
    pbp = playbyplay.PlayByPlay(game_id=game_id).get_dict()
    events = pbp['game']['actions']
    last_play = events[-1]

    period = last_play.get('period', 0)
    clock = last_play.get('clock', '')
    minutes = int(clock[2:4])  # Characters at index 2 and 3
    seconds = int(clock[5:7])
    description = last_play.get('description', '')
    home_score = last_play.get('scoreHome', '')
    away_score = last_play.get('scoreAway', '')

    print(f"Current Score: \n\tClock: {minutes}:{seconds}\n\tPeriod: {period}\n\tDescription: {description}\n\t"
          f"Score: (OPP) {away_score} - {home_score} (LAC)")


def get_most_recent_clippers_home_game_vs_rockets():
    # Find the most recent game between the Clippers and the Rockets where the Clippers were the home team
    gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=1610612746)  # Clippers team ID
    games = gamefinder.get_data_frames()[0]

    # Filter the games for home games against the Rockets (HOU)
    clippers_home_games_vs_rockets = games[(games['MATCHUP'].str.contains('vs. HOU'))]

    if not clippers_home_games_vs_rockets.empty:
        # Get the most recent home game
        most_recent_game = clippers_home_games_vs_rockets.iloc[0]  # First row is the most recent
        game_id = most_recent_game['GAME_ID']
        return game_id
    else:
        return None


def send_notification(message):
    print("Notification:", message)
    # Here you can implement the code to send notifications via email, SMS, etc.


# Run the asynchronous function using an event loop
async def main():
    print(await check_game_finish())
    print(get_next_clippers_home_game())
    print(next_clippers_home_game())
    game_id = await get_game_id_today()
    check_score(game_id)


# Run the async function
if __name__ == "__main__":
    asyncio.run(main())

# # Main logic to check and notify
# print(get_next_clippers_home_game())
#
# print(check_opponent_missed_two_ft_in_4th_quarter(get_most_recent_clippers_home_game_vs_rockets()))

# game_id = get_games_schedule()
#
# next_clippers_game()

# # Test the function
# if game_id:
#     if check_opponent_missed_two_ft_in_4th_quarter(game_id):
#         send_notification(
#             "Opponent missed two consecutive free throws in the 4th quarter of the most recent Clippers home game!")
#     else:
#         print("The condition was not met in this game.")
# else:
#     print("There is not a Clippers home game today.")
