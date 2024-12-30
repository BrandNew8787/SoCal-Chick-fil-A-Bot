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

        # using an away game function instead of a home
        # ANA_Ducks_game = await Anaheim_Ducks.ducks_away_game_today()
    except Exception as e:
        print(f"Error checking Ducks game: {e}")
        ANA_Ducks_game = False

    try:
        LA_Angels_game = await LA_Angels.get_today_angels_home_game()  # Await the asynchronous function
    except Exception as e:
        print(f"Error checking Angels game: {e}")
        LA_Angels_game = False

    try:
        clippers_game_id = await LA_Clippers.get_game_id_today()  # Await the asynchronous function
        if clippers_game_id:
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
                        "@everyone LAFC has won their home game! Free Chick-fil-A sandwich! Open "
                        "[here](https://apps.apple.com/us/app/chick-fil-a/id488818252) to claim your sandwich!"
                    )
                else:
                    await channel.send(
                        "LAFC did not win... no free sandwich today..."
                    )

                # Game is over, reset the state
                LAFC_game = False
                ongoing_games = False

            else:
                ongoing_games = True  # Game is still ongoing, continue checking

        if ANA_Ducks_game:
            # FOR MAIN FUNCTION
            today_ducks_game = Anaheim_Ducks.get_game_id()
            ducks_results = await Anaheim_Ducks.check_ducks_score(today_ducks_game)

            # added a function to check the away score to make sure this is working
            # ducks_away_results = await Anaheim_Ducks.check_ducks_away_score()
            if ducks_results != "The game hasn't finished yet!":
                if ducks_results:

                    # changed the message to state and away game had happened
                    await channel.send(
                        "@everyone The Anaheim Ducks have scored 5 or more goals at a home game! Free Chick-fil-A "
                        "sandwich! Open [here](https://apps.apple.com/us/app/chick-fil-a/id488818252) to claim your "
                        "sandwich!"
                    )
                else:
                    await channel.send(
                        "The Anaheim Ducks did not score 5 points... no free sandwich today..."
                    )

                # Game is over, reset the state
                ANA_Ducks_game = False
                ongoing_games = False

            else:
                ongoing_games = True  # Game is still ongoing, continue checking

        if LA_Clippers_game:
            # This is to ensure that the game is over before checking if the conditions were met
            clippers_result = await LA_Clippers.check_game_finish()
            if clippers_result == "W" or clippers_result == "L":
                clippers_4th_quarter = LA_Clippers.check_opponent_missed_two_ft_in_4th_quarter(clippers_game_id)
                if clippers_4th_quarter:

                    # changed this so that it checks if the opponent made one basket or not
                    await channel.send(
                        "@everyone The opponents of the Los Angeles Clippers missed 2 free throw at a home game! Free"
                        "Chick-fil-A sandwich! Open [here](https://apps.apple.com/us/app/chick-fil-a/id488818252) to "
                        "claim your sandwich!"
                    )
                else:
                    await channel.send(
                        "The Clippers opponents did miss 2 free throws in the 4th quarter... no free sandwich today..."
                    )

                # Game is over, reset the state
                LA_Clippers_game = False
                ongoing_games = False

            else:
                ongoing_games = True  # Game is still ongoing, continue checking

            '''
            
            This part is to check if the periodic check is working. Uncommenting this checks if the clippers 
            opponents made a free throw in the 4th quarter regardless if the game is over or not. To use this, uncomment
            this code to allow it to function.
            
            '''
            # clippers_result = LA_Clippers.check_game_finish()
            # clippers_4th_quarter = LA_Clippers.check_opponent_missed_two_ft_in_4th_quarter(clippers_game_id)
            # if clippers_4th_quarter:
            #     # changed this so that it checks if the opponent made one basket or not
            #     await channel.send(
            #         "The opponents of the Los Angeles Clippers made 1 free throw at a home game! Free"
            #         "Chick-fil-A sandwich! Open [here](https://apps.apple.com/us/app/chick-fil-a/id488818252) to "
            #         "claim your sandwich!"
            #     )
            #     LA_Clippers_game = False
            #     ongoing_games = False

        if LA_Angels_game:
            angels_result = await LA_Angels.check_angels_score()
            if angels_result != "The game has not finished yet!":
                if angels_result:
                    await channel.send(
                        "@everyone The Los Angeles Angels have scored 7 points! Free Chick-fil-A sandwich!"
                        " Open [here](https://apps.apple.com/us/app/chick-fil-a/id488818252) to claim your sandwich!"
                    )
                else:
                    await channel.send(
                        "The Angels did not score 7 points... no free sandwich today..."
                    )

                # Game is over, reset the state
                LA_Angels_game = False
                ongoing_games = False

            else:
                ongoing_games = True  # Game is still ongoing, continue checking

        # If there are still ongoing games, wait for 10 minutes before checking again
        if ongoing_games:
            await asyncio.sleep(600)  # Wait for 10 minutes before checking again
        else:
            await asyncio.sleep(21600)  # Wait for 6 hours before checking for new games


# STEP 5: MESSAGE FUNCTIONALITY
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('(Message was empty because intents were not enabled probably)')
        return

    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    # Extract the bot's mention in the form <@bot_id>
    bot_mention = f'<@{client.user.id}>'

    try:
        response: str = await get_response(user_message, bot_mention)
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
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # Extract username, message content, and channel for logging
    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    # Log the message
    print(f'[{channel}] {username}: "{message.content}"')

    # Check if the bot is mentioned
    bot_mention = f'<@{client.user.id}>'
    if bot_mention in user_message:
        # Remove the mention from the message to process only the actual text
        cleaned_message = user_message.replace(bot_mention, "").strip()

        # Generate a response and send it
        response = await get_response(cleaned_message, bot_mention)
        await message.channel.send(response)
        return


# STEP 8: MAIN ENTRY POINT
def main() -> None:
    webserver.keep_alive()
    client.run(TOKEN)


if __name__ == '__main__':
    main()
