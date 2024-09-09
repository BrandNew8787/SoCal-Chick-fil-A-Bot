import asyncio
import os
from typing import Final

from discord import Intents, Client, Message
from dotenv import load_dotenv

import Anaheim_Ducks
import LAFC
import LA_Angels
import LA_Clippers
import webserver
from responses import get_response

# STEP 0: LOAD OUR TOKEN FROM SOMEWHERE SAFE AND CREATE OUR GAME VARIABLES
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
MLB_API_URL: Final[str] = "https://statsapi.mlb.com/api/v1/schedule?sportId=1"
NHL_API_URL: Final[str] = "https://api-web.nhle.com/v1/score/now"
LAFC_API_URL: Final[str] = "https://api.football-data.org/v4/teams/740/matches?status=FINISHED"

LAFC_game = False
LA_Clippers_game = False
ANA_Ducks_game = False
LA_Angels_game = False
clippers_game_id = None
clippers_result = None

# STEP 1: BOT SETUP
intents: Intents = Intents.default()
intents.message_content = True  # NOQA
client: Client = Client(intents=intents)
CHANNEL_ID: Final[int] = int(os.getenv('DISCORD_CHANNEL_ID'))


# STEP 2: CHECK FOR GAMES TODAY
async def check_for_games():
    global LAFC_game, ANA_Ducks_game, LA_Angels_game, LA_Clippers_game, clippers_game_id, clippers_result

    try:
        LAFC_game = LAFC.game_today()
    except Exception as e:
        print(f"Error checking LAFC game: {e}")
        LAFC_game = False

    try:
        ANA_Ducks_game = await Anaheim_Ducks.ducks_home_game_today()  # Await the asynchronous function
    except Exception as e:
        print(f"Error checking Ducks game: {e}")
        ANA_Ducks_game = False

    try:
        LA_Angels_game = await LA_Angels.get_today_angels_home_game()  # Await the asynchronous function
    except Exception as e:
        print(f"Error checking Angels game: {e}")
        LA_Angels_game = False

    try:
        result = LA_Clippers.get_today_clippers_home_game_id()  # Await the asynchronous function
        if result:
            clippers_game_id, clippers_result = result
            LA_Clippers_game = clippers_game_id is not None
        else:
            LA_Clippers_game = False
    except Exception as e:
        print(f"Error checking Clippers game: {e}")
        LA_Clippers_game = False


# STEP 4: PERIODIC CHECK FUNCTION
async def periodic_check():
    global LAFC_game, ANA_Ducks_game, LA_Angels_game, LA_Clippers_game, clippers_game_id, clippers_result
    await client.wait_until_ready()  # Wait until the bot is ready
    channel = client.get_channel(CHANNEL_ID)  # Get the channel to send messages

    while not client.is_closed():
        await check_for_games()  # Refresh the state of game variables

        ongoing_games = False

        if LAFC_game:
            lafc_results = await LAFC.get_match_results()
            if lafc_results != "The game has not finished yet!":
                if lafc_results['outcome'] == "Win":
                    await channel.send(
                        "LAFC has won their home game! Free Chick-fil-A sandwich! Open "
                        "[here](https://apps.apple.com/us/app/chick-fil-a/id488818252) to claim your sandwich!"
                    )
                LAFC_game = False  # Game is over, reset the state
            else:
                ongoing_games = True  # Game is still ongoing, continue checking

        if ANA_Ducks_game:
            ducks_results = await Anaheim_Ducks.check_ducks_score()
            if ducks_results != "The game hasn't finished yet!":
                if ducks_results:
                    await channel.send(
                        "The Anaheim Ducks have scored 5 or more goals at a home game! Free Chick-fil-A sandwich! Open "
                        "[here](https://apps.apple.com/us/app/chick-fil-a/id488818252) to claim your sandwich!"
                    )
                ANA_Ducks_game = False  # Game is over, reset the state
            else:
                ongoing_games = True  # Game is still ongoing, continue checking

        if LA_Clippers_game:
            if clippers_result == "W" or clippers_result == "L":
                clippers_4th_quarter = await LA_Clippers.check_opponent_missed_two_ft_in_4th_quarter(clippers_game_id)
                if clippers_4th_quarter:
                    await channel.send(
                        "The opponents of the Los Angeles Clippers missed two free throws in a row at a home game! Free"
                        "Chick-fil-A sandwich! Open [here](https://apps.apple.com/us/app/chick-fil-a/id488818252) to "
                        "claim your sandwich!"
                    )
                LA_Clippers_game = False  # Game is over, reset the state
            else:
                ongoing_games = True  # Game is still ongoing, continue checking

        if LA_Angels_game:
            angels_result = await LA_Angels.check_angels_score()
            if angels_result != "The game has not finished yet!":
                if angels_result:
                    await channel.send(
                        "The Los Angeles Angels have scored 7 points! Free Chick-fil-A sandwich!"
                        " Open [here](https://apps.apple.com/us/app/chick-fil-a/id488818252) to claim your sandwich!"
                    )
                LA_Angels_game = False  # Game is over, reset the state
            else:
                ongoing_games = True  # Game is still ongoing, continue checking

        # If there are still ongoing games, wait for 10 minutes before checking again
        if ongoing_games:
            await asyncio.sleep(600)  # Wait for 10 minutes before checking again
        else:
            # No ongoing games, check for the next day's games immediately
            await asyncio.sleep(43200)  # Wait for 12 hours before checking for new games


# STEP 5: MESSAGE FUNCTIONALITY
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('(Message was empty because intents were not enabled probably)')
        return

    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    try:
        response: str = await get_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


# STEP 6: HANDLING THE STARTUP FOR OUR BOT
@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running!')
    await client.loop.create_task(periodic_check())  # Start the periodic check loop


# STEP 7: HANDLING INCOMING MESSAGES
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'[{channel}] {username}: "{message}"')
    await send_message(message, user_message)


# STEP 8: MAIN ENTRY POINT
def main() -> None:
    webserver.keep_alive()
    client.run(TOKEN)


if __name__ == '__main__':
    main()
