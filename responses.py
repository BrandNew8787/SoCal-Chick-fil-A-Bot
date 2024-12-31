from datetime import datetime
from random import randint

import Anaheim_Ducks
import LAFC
import LA_Angels
import LA_Clippers


# returns phrases the bot will respond with given a command
async def get_response(user_input: str, bot_mention: str) -> str:
    # Remove bot mention from the user_input to get the actual command
    lowered = user_input.lower().replace(bot_mention, '').strip()

    if lowered == '':
        return 'Well, you\'re awfully silent...'
    elif 'hello' in lowered:
        return 'Hello there!'
    elif 'how are you' in lowered:
        return 'Good, thanks!'
    elif 'bye' in lowered:
        return 'See you!'
    elif 'roll dice' in lowered:
        return f'You rolled: {randint(1, 6)}'
    elif 'next chance' in lowered:
        next_game = await next_chance()
        return next_game
    elif 'next clippers game' in lowered:
        clippers_date, clippers_opp = LA_Clippers.get_next_clippers_home_game()
        clippers_date = datetime.strptime(clippers_date, "%Y-%m-%d") if clippers_date else None
        return (f"The next Clippers Home Game:\n\tGAME: Clippers vs. {clippers_opp}"
                f"\n\tDATE: {clippers_date.strftime('%b %d, %Y')}")
    elif 'next ducks game' in lowered:
        duck_date, duck_opp = await Anaheim_Ducks.get_ducks_next_home_game()  # Await here
        duck_date = datetime.strptime(duck_date, "%Y-%m-%d") if duck_date else None
        return f"The next Ducks Home Game:\n\tGAME: Ducks vs. {duck_opp}\n\tDATE: {duck_date.strftime('%b %d, %Y')}"
    elif 'next lafc game' in lowered:
        lafc_date, lafc_opp = LAFC.get_next_lafc_home_game()
        if lafc_date == "No upcoming LAFC home games found." :
            return "There are no scheduled LAFC Home Games coming up. Try again in January for next years schedule."
        else:
            lafc_date = datetime.strptime(lafc_date, "%Y-%m-%d") if lafc_date else None
            return f"The next LAFC Home Game:\n\tGAME: LAFC vs. {lafc_opp}\n\tDATE: {lafc_date.strftime('%b %d, %Y')}"
    elif 'next angels game' in lowered:
        angels_date, angels_opp = LA_Angels.get_next_angels_game()
        angels_date = datetime.strptime(angels_date, "%Y-%m-%d") if angels_date else None
        return f"The next Angels Home Game:\n\tGAME: LAFC vs. {angels_opp}\n\tDATE: {angels_date.strftime('%b %d, %Y')}"
    else:
        return 'I don\'t understand that command.'


# returns the closest home game between the clippers, ducks, angels, and lafc
async def next_chance():
    # Get upcoming game dates and opponents
    lafc_date, lafc_opp = LAFC.get_next_lafc_home_game()
    duck_date, duck_opp = await Anaheim_Ducks.get_ducks_next_home_game()  # Await here
    angels_date, angels_opp = LA_Angels.get_next_angels_game()
    clippers_date, clippers_opp = LA_Clippers.get_next_clippers_home_game()

    # Convert dates to datetime objects for comparison
    today = datetime.now()

    lafc_date = datetime.strptime(lafc_date, "%Y-%m-%d") if lafc_date != "No upcoming LAFC home games found." else None
    duck_date = datetime.strptime(duck_date, "%Y-%m-%d") if duck_date else None
    angels_date = datetime.strptime(angels_date, "%Y-%m-%d") if angels_date else None
    clippers_date = datetime.strptime(clippers_date, "%Y-%m-%d") if clippers_date else None

    # Create a dictionary to store team and game data
    game_data = {
        "LAFC": {"date": lafc_date, "opponent": lafc_opp},
        "Ducks": {"date": duck_date, "opponent": duck_opp},
        "Angels": {"date": angels_date, "opponent": angels_opp},
        "Clippers": {"date": clippers_date, "opponent": clippers_opp},
    }

    # Find the team with the closest upcoming game
    closest_team = None
    closest_date = None
    closest_opponent = None

    for team, data in game_data.items():
        game_date = data["date"]
        if game_date and (closest_date is None or (game_date - today).days < (closest_date - today).days):
            closest_date = game_date
            closest_team = team
            closest_opponent = data["opponent"]

    if closest_date.strftime("%Y-%m-%d") == today.strftime("%Y-%m-%d"):
        return (f"There's a chance **TODAY** for a free Chick-Fil-A sandwich is for the following game: "
                f"\n\tGAME: {closest_team} vs {closest_opponent} \n\tDATE: {closest_date.strftime('%b %d, %Y')}")
    elif closest_team:
        return (f"The next chance for a free Chick-Fil-A sandwich is for the following game: "
                f"\n\tGAME: {closest_team} vs {closest_opponent} \n\tDATE: {closest_date.strftime('%b %d, %Y')}")
    else:
        return "No upcoming games found."
