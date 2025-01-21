import requests
from bs4 import BeautifulSoup
from datetime import datetime


# # returns the date and opponent of the next scheduled lafc game
def get_next_lafc_home_game():
    year = datetime.now().year
    # URL of the page: eventually this website will need to be changed when the new schedule comes out
    url = (
        f"https://fbref.com/en/squads/81d817a3/{year}/matchlogs/c22/schedule/Los-Angeles-FC-Scores-and-Fixtures-Major"
        "-League-Soccer")

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Locate the table with id "matchlogs_for"
        table = soup.find('table', {'id': 'matchlogs_for'})

        # Extract the table rows, skipping the first row (title row)
        rows = table.find_all('tr')[1:]  # Skip the first row

        # Today's date for comparison
        today = datetime.today()

        # Loop through rows and find the next home game
        for row in rows:
            # Extract the date of the match
            date_str = row.find('th', {'data-stat': 'date'}).text.strip()

            # checks if there is a blank row indicating a separation for playoff games
            if date_str != '':
                match_date = datetime.strptime(date_str, "%Y-%m-%d")

                # Check if the match is in the future
                if match_date >= today:
                    # Extract venue and check if it's a home game
                    venue = row.find('td', {'data-stat': 'venue'}).text.strip()
                    if venue.lower() == "home":
                        opponent = row.find('td', {'data-stat': 'opponent'}).text.strip()
                        return match_date.strftime('%Y-%m-%d'), opponent

        return "No upcoming LAFC home games found.", None
    else:
        return f"Failed to retrieve the page. Status code: {response.status_code}"


# returns a boolean if there is a home game today
def game_today():
    year = datetime.now().year
    # URL of the page: eventually this website will need to be changed when the new schedule comes out
    url = (
        f"https://fbref.com/en/squads/81d817a3/{year}/matchlogs/c22/schedule/Los-Angeles-FC-Scores-and-Fixtures-Major"
        "-League-Soccer")

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Locate the table with id "matchlogs_for"
        table = soup.find('table', {'id': 'matchlogs_for'})

        # Extract the table rows, skipping the first row (title row)
        rows = table.find_all('tr')[1:]  # Skip the first row

        # Today's date for comparison
        today = datetime.today()

        # Loop through rows and find the next home game
        for row in rows:
            # Extract the date of the match
            date_str = row.find('th', {'data-stat': 'date'}).text.strip()
            # checks if there is a blank row indicating a separation for playoff games
            if date_str != '':
                match_date = datetime.strptime(date_str, "%Y-%m-%d")

                # Check if the match is in the future
                if match_date == today:
                    # Extract venue and check if it's a home game
                    venue = row.find('td', {'data-stat': 'venue'}).text.strip()
                    if venue.lower() == "home":
                        return True
                elif match_date > today:
                    return False
        return False
    else:
        return f"Failed to retrieve the page. Status code: {response.status_code}"


# returns a string value of the date, time, and opponent of the next lafc home game.
def upcoming_game(game):
    for row in game:
        date = row.find('td', {'data-index': '0'}).get_text(strip=True)
        opponent_info = row.find('td', {'data-index': '1'})
        opponent = opponent_info.find('a', class_='table-entity-name').get_text(strip=True)
        time_info = row.find('td', {'data-index': '2'}).get_text(strip=True)

        venue_info = row.find('td', {'data-index': '3'})
        if venue_info:
            venue_div = venue_info.find('div')
            if venue_div:
                venue = venue_div.get_text(strip=True) if venue_div else "N/A"
                if "(H)" not in opponent and "(A)" not in opponent:
                    if venue == "BMO Stadium,Los Angeles, CA":
                        opponent = opponent + " (H)"
                    else:
                        opponent = opponent + " (A)"
            else:
                "N/A"
        else:
            "N/A"
            "N/A"
        if '(H)' in opponent:
            return f"Next LAFC Home Game:\n\tDate: {date}\n\tOpponent: {opponent}\n\tTime: {time_info}"


# returns the results of a today's game
def get_match_results():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/92.0.4515.107 Safari/537.36",
        "Referer": "https://www.espn.com/",
        "Accept-Language": "en-US,en;q=0.9",
    }

    # Create a session and send a GET request to the URL
    session = requests.Session()
    response = session.get("https://www.espn.com/soccer/team/results/_/id/18966/usa.lafc", headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the table containing the match results
        table = soup.find('div', class_='ResponsiveTable Table__results')

        # Check if the table exists
        if not table:
            return "No table found on the page."

        # Extract all rows in the table
        rows = table.find_all('tr', class_='Table__TR')[1:]

        match_data = []

        # Loop through each row and extract the relevant data
        for row in rows:
            # Extract the date
            date_str = row.find('div', class_='matchTeams').text.strip()

            # Parse the date string into a datetime object (current year)
            match_date = datetime.strptime(date_str, '%a, %b %d').replace(year=datetime.now().year)
            today = datetime.now()

            # Compare the match date with today's date
            if match_date.date() != today.date():
                return "The game has not finished yet!"

            # Extract the team names
            teams = row.find_all('a', class_='AnchorLink Table__Team')
            home_team = teams[0].text.strip()
            away_team = teams[1].text.strip()

            # Extract the result
            result = row.find('span', class_='Table__Team score').text.strip()

            # Determine the winner and the goal difference
            home_score, away_score = map(int, result.split('-'))
            if home_score > away_score:
                outcome = "Win"
            elif home_score < away_score:
                outcome = "Lose"
            else:
                outcome = "The match was a draw"

            # Compile the match data
            match_info = {
                'date': date_str,
                'home_team': home_team,
                'away_team': away_team,
                'result': result,
                'outcome': outcome
            }

            match_data.append(match_info)

        return match_data

    else:
        return f"Failed to retrieve the page. Status code: {response.status_code}"
