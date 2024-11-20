import json
from datetime import datetime, timezone
from dateutil import parser
import requests
from bs4 import BeautifulSoup
from nba_api.stats.endpoints import leaguegamefinder, playbyplayv2
from nba_api.live.nba.endpoints import scoreboard


def check_game_finish():
    # Get today's date in the correct format
    today_date = datetime.today().strftime('%m/%d/%Y')
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


# This is the new function that returns the id if there is a clippers home game today
async def get_games_schedule():
    # Fetch the JSON data from the API
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/91.0.4472.124 Safari/537.36"
    }

    today = datetime.today().strftime("%m/%d/%Y")
    season = datetime.today().strftime("%Y")

    # URL to fetch the JSON data
    url = f"https://stats.nba.com/stats/internationalbroadcasterschedule?LeagueID=00&Season={season}&RegionID=1&Date={today}&EST=Y"

    response = requests.get(url, headers=headers)
    data = response.json()

    # Extract the games from the NextGameList
    games = data["resultSets"][0]["NextGameList"]

    # Format and print the games
    print("NBA Games for 11/20/2024:")
    game_format = "{gameID}: {awayTeam} vs. {homeTeam} @ {gameTime} ({broadcaster})"

    for game in games:
        if game['htNickName'] == 'Clippers':
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
    return None


# finds the next clippers game webscraping through the cbs sports website
def get_next_clippers_home_game():
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

    # Iterate over all <script> tags found
    for script in script_tags:
        try:
            # Attempt to load the JSON content, stripping problematic characters
            json_data = json.loads(script.string.replace('\n', '').replace('\r', '').replace('\t', ''))

            # Check if the JSON data is a SportsEvent and if it involves the Clippers
            if json_data.get('@type') == 'SportsEvent':
                teams = json_data.get('competitor', [])
                for team in teams:
                    if 'Clippers' in team.get('name', ''):
                        # Extract relevant information
                        game_date_str = json_data.get('startDate').strip()
                        game_date = datetime.strptime(game_date_str, "%b %d, %Y")

                        # Format the date as %Y-%m-%d
                        formatted_game_date = game_date.strftime("%Y-%m-%d")

                        # Compare game date with today's date
                        if game_date.date() >= datetime.now().date():
                            return formatted_game_date, teams[0]['name'] if 'Clippers' not in teams[0]['name'] else \
                                teams[1]['name']

                        break
        except json.JSONDecodeError:
            # Handle JSON parsing errors
            print("Failed to parse JSON data.")
        except Exception as e:
            # Catch-all for any other errors
            print(f"An error occurred: {e}")

    return "No upcoming Clippers home games found."


# finds the next clippers home game parsing through a json file
def next_clippers_game():
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
                    print(f"Date: {formatted_date}")
                    print(f"  - {away_team} at {home_team}")
                    return formatted_date, away_team

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")


def check_opponent_missed_two_ft_in_4th_quarter(game_id):
    # Get the play-by-play data for the game
    play_by_play = playbyplayv2.PlayByPlayV2(game_id=game_id).get_data_frames()[0]

    for index, row in play_by_play.iterrows():
        event_msg_type = row['EVENTMSGTYPE']
        period = row['PERIOD']
        description = row['HOMEDESCRIPTION'] or row['VISITORDESCRIPTION'] or ''
        team_name = 'Clippers' if row['PLAYER1_TEAM_ID'] == 1610612746 else 'Opponent'

        # We are only interested in the 4th quarter (period 4)
        if period == 4:
            # Check for missed free throw events by the opponent
            if event_msg_type == 3 and 'MISS' in description and '2 of 2' in description:
                if team_name == 'Opponent':
                    return True

    return False


def check_opponent_made_one_ft_in_4th_quarter(game_id):
    # Get the play-by-play data for the game
    play_by_play = playbyplayv2.PlayByPlayV2(game_id=game_id).get_data_frames()[0]

    for index, row in play_by_play.iterrows():
        event_msg_type = row['EVENTMSGTYPE']
        period = row['PERIOD']
        description = row['HOMEDESCRIPTION'] or row['VISITORDESCRIPTION'] or ''
        team_name = 'Clippers' if row['PLAYER1_TEAM_ID'] == 1610612746 else 'Opponent'

        # We are only interested in the 4th quarter (period 4)
        if period == 4:
            # Check for missed free throw events by the opponent
            if event_msg_type == 3 and ("1 of 2" in description or "1 of 3" in description):
                if team_name == 'Opponent':
                    return True

    return False


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


# # Main logic to check and notify
# print(get_next_clippers_home_game())
#
print(check_opponent_missed_two_ft_in_4th_quarter(get_most_recent_clippers_home_game_vs_rockets()))

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
