import asyncio
import datetime
import pytz
import os
import logging
from typing import Final

from discord import Intents, Client, Message
from dotenv import load_dotenv

import Anaheim_Ducks
import LAFC
import LA_Angels
import LA_Clippers
import webserver
from responses import get_response

# Define the timezone (Pacific Time Zone)
pacific_tz = pytz.timezone("America/Los_Angeles")

# Set up logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

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
current_date = datetime.datetime.now(pacific_tz).date()

# Lock for shared state
state_lock = asyncio.Lock()

# STEP 1: BOT SETUP
intents: Intents = Intents.default()
intents.message_content = True  # NOQA
client: Client = Client(intents=intents)
CHANNEL_ID: Final[int] = int(os.getenv('DISCORD_CHANNEL_ID'))


# STEP 2: CHECK FOR GAMES TODAY
async def check_for_games():
    global LAFC_game, ANA_Ducks_game, LA_Angels_game, LA_Clippers_game, clippers_game_id, clippers_result

    async with state_lock:
        try:
            logger.debug("Checking for LAFC game")
            LAFC_game = LAFC.game_today()
            logger.debug(LAFC_game)
        except Exception as e:
            logger.error(f"Error checking LAFC game: {e}")
            LAFC_game = False

        try:
            logger.debug("Checking for Ducks game")
            ANA_Ducks_game = await Anaheim_Ducks.ducks_home_game_today()  # Await the asynchronous function
            logger.debug(ANA_Ducks_game)
        except Exception as e:
            logger.error(f"Error checking Ducks game: {e}")
            ANA_Ducks_game = False

        try:
            logger.debug("Checking for Angels game")
            LA_Angels_game = await LA_Angels.get_today_angels_home_game()  # Await the asynchronous function
            logger.debug(LA_Angels_game)
        except Exception as e:
            logger.error(f"Error checking Angels game: {e}")
            LA_Angels_game = False

        try:
            logger.debug("Checking for Clippers game")
            clippers_game_id = await LA_Clippers.get_game_id_today()  # Await the asynchronous function
            logger.debug(clippers_game_id)
            if clippers_game_id:
                LA_Clippers_game = clippers_game_id is not None
                logger.debug(LA_Clippers_game)
            else:
                LA_Clippers_game = False
        except Exception as e:
            logger.error(f"Error checking Clippers game: {e}")
            LA_Clippers_game = False


# STEP 4: PERIODIC CHECK FUNCTION
async def periodic_check():
    global LAFC_game, ANA_Ducks_game, LA_Angels_game, LA_Clippers_game, clippers_game_id, clippers_result, current_date
    await client.wait_until_ready()  # Wait until the bot is ready
    channel = client.get_channel(CHANNEL_ID)  # Get the channel to send messages

    while not client.is_closed():
        logger.info("Starting periodic check for games.")
        await check_for_games()  # Refresh the state of game variables
        ongoing_games = False

        async with state_lock:
            now = datetime.datetime.now(pacific_tz)
            tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
            seconds_left = (tomorrow - now).seconds
            today_date = now.date()
            if LAFC_game:
                if today_date > current_date:
                    current_date = today_date
                    await channel.send("LAFC has a home game today! Be on the lookout for a free sandwich "
                                       ":chicken::sandwich:", delete_after=seconds_left)
                logger.info("there is an lafc game today!")
                lafc_results = await LAFC.get_match_results()
                if lafc_results != "The game has not finished yet!":
                    logger.info("The game has finished!")
                    await channel.send("The LAFC Game has finished!", delete_after=seconds_left)
                    if lafc_results['outcome'] == "Win":
                        logger.info("Conditions are met for LAFC game.")
                        await channel.send(
                            "@everyone LAFC has won their home game! Free Chick-fil-A sandwich! Open "
                            "[here](https://apps.apple.com/us/app/chick-fil-a/id488818252) to claim your sandwich!",
                            delete_after=seconds_left
                        )
                    else:
                        logger.info("Conditions are met for LAFC games.")
                        await channel.send(
                            "LAFC did not win... no free sandwich today..."
                        )
                    # Game is over, reset the state
                    LAFC_game = False
                    ongoing_games = False

                else:
                    logger.info("The LAFC game hasn't finished yet.")
                    ongoing_games = True  # Game is still ongoing, continue checking

            if ANA_Ducks_game:
                if today_date > current_date:
                    current_date = today_date
                    await channel.send("The Anaheim Ducks has a home game today! Be on the lookout for a free sandwich "
                                       ":chicken::sandwich:", delete_after=seconds_left)
                logger.info("There is a ducks game today!")
                # find the game ID for today
                today_ducks_game = await Anaheim_Ducks.get_game_id()
                ducks_results = await Anaheim_Ducks.check_ducks_score(today_ducks_game)
                if ducks_results != "The game hasn't finished yet!":
                    logger.info("The game has finished!")
                    await channel.send("The Ducks Game has finished!", delete_after=seconds_left)
                    if ducks_results:
                        logger.info("Conditions are met for Ducks games.")
                        now = datetime.datetime.now(pacific_tz)
                        tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
                        seconds_left = (tomorrow - now).seconds
                        await channel.send(
                            "@everyone The Anaheim Ducks have scored 5 or more goals at a home game! Free Chick-fil-A "
                            "sandwich! Open [here](https://apps.apple.com/us/app/chick-fil-a/id488818252) to claim your"
                            "sandwich!",
                            delete_after=seconds_left
                        )
                    else:
                        logger.info("Conditions are not met for Ducks game.")
                        await channel.send(
                            "The Anaheim Ducks did not score 5 points... no free sandwich today..."
                        )
                    # Game is over, reset the state
                    ANA_Ducks_game = False
                    ongoing_games = False

                else:
                    logger.info("The Ducks game hasn't finished yet.")
                    ongoing_games = True  # Game is still ongoing, continue checking

            if LA_Clippers_game:
                if today_date > current_date:
                    current_date = today_date
                    await channel.send("The LA Clippers has a home game today! Be on the lookout for a free sandwich "
                                       ":chicken::sandwich:", delete_after=seconds_left)
                logger.info("There is a clippers game today!")
                clippers_result = await LA_Clippers.check_game_finish_v2(clippers_game_id)
                if clippers_result:
                    logger.info("The clipper game has finished!")
                    await channel.send("The Clippers Game has finished!", delete_after=seconds_left)
                    clippers_4th_quarter = await LA_Clippers.check_missed_ft_in_4th_quarter_v2(clippers_game_id)
                    if clippers_4th_quarter:
                        logger.info("Conditions are met for Clippers game.")
                        now = datetime.datetime.now(pacific_tz)
                        tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
                        seconds_left = (tomorrow - now).seconds
                        # changed this so that it checks if the opponent made one basket or not
                        await channel.send(
                            "@everyone The opponents of the Los Angeles Clippers missed 2 free throw at a home game! "
                            "Free Chick-fil-A sandwich! Open [here]("
                            "https://apps.apple.com/us/app/chick-fil-a/id488818252) to claim your sandwich!",
                            delete_after=seconds_left
                        )
                    else:
                        logger.info("Conditions are not met for clippers game.")
                        await channel.send(
                            "The Clippers opponents did miss 2 free throws in the 4th quarter... no free sandwich "
                            "today..."
                        )
                    # Game is over, reset the state
                    LA_Clippers_game = False
                    ongoing_games = False

                else:
                    logger.info("The Clippers game hasn't finished yet.")
                    ongoing_games = True  # Game is still ongoing, continue checking

            if LA_Angels_game:
                if today_date > current_date:
                    current_date = today_date
                    await channel.send("The Los Angeles Clippers has a home game today! Be on the lookout for a free "
                                       "sandwich :chicken::sandwich:", delete_after=seconds_left)
                logger.info("There is an Angels game today!")
                angels_result = await LA_Angels.check_angels_score()
                if angels_result != "The game has not finished yet!":
                    logger.info("The Angels game has finished!")
                    await channel.send("The Angels Game has finished!", delete_after=seconds_left)
                    if angels_result:
                        logger.info("Conditions are met for Angels game.")
                        now = datetime.datetime.now(pacific_tz)
                        tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
                        seconds_left = (tomorrow - now).seconds
                        await channel.send(
                            "@everyone The Los Angeles Angels have scored 7 points! Free Chick-fil-A sandwich! Open ["
                            "here](https://apps.apple.com/us/app/chick-fil-a/id488818252) to claim your sandwich!",
                            delete_after=seconds_left
                        )
                    else:
                        logger.info("Conditions are not met for Angels game.")
                        await channel.send(
                            "The Angels did not score 7 points... no free sandwich today..."
                        )
                    # Game is over, reset the state
                    LA_Angels_game = False
                    ongoing_games = False
                else:
                    logger.info("The Angels game hasn't finished yet.")
                    ongoing_games = True
        # If there are still ongoing games, wait for 10 minutes before checking again
        if ongoing_games:
            logger.info("There is still an ongoing game today! This will check every 10 minutes")
            await asyncio.sleep(600)  # Wait for 10 minutes before checking again
        else:
            logger.info("There are no ongoing games today or the games have finished. Wait 6 hours for the next check.")
            await asyncio.sleep(21600)  # Wait for 6 hours before checking for new games


# STEP 5: MESSAGE FUNCTIONALITY
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        logger.info('(Message was empty because intents were not enabled probably)')
        return

    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    # Extract the bot's mention in the form <@bot_id>
    bot_mention = f'<@{client.user.id}>'

    try:
        response: str = await get_response(user_message, bot_mention)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        logger.info(e)


# STEP 6: HANDLING THE STARTUP FOR OUR BOT
@client.event
async def on_ready() -> None:
    logger.info(f'{client.user} is now running!')
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
    logger.info(f'[{channel}] {username}: "{message.content}"')

    # Check if the bot is mentioned
    bot_mention = f'<@{client.user.id}>'
    if bot_mention in user_message:
        # Remove the mention from the message to process only the actual text
        cleaned_message = user_message.replace(bot_mention, "").strip()

        # Generate a response and send it
        response = await get_response(cleaned_message, bot_mention)
        await message.channel.send(response, delete_after=4320)
        return


# STEP 8: MAIN ENTRY POINT
def main() -> None:
    webserver.keep_alive()
    client.run(TOKEN)


if __name__ == '__main__':
    main()
