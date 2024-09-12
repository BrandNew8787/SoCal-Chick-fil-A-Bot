# Chick-fil-A Notification Discord Bot

This bot is designed to notify users on a Discord server when certain game conditions are met during Los Angeles sports team games. When a condition is fulfilled, such as a team winning or scoring a certain number of points/goals, the bot will send a notification for users to claim a free Chick-fil-A sandwich.

## Features

- **Teams Covered**: LAFC, Anaheim Ducks, LA Clippers, LA Angels.
- **Trigger Conditions**:
  - LAFC wins their home game.
  - Anaheim Ducks score 5 or more goals in a home game.
  - LA Clippers' opponent misses two free throws in a row during the 4th quarter of a home game.
  - LA Angels score 7 or more points in a home game.
- **Automated checks**: The bot periodically checks for ongoing games and updates users when game conditions are met.
- **User interaction**: Users can query the bot for upcoming games and conditions.

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- Discord bot token
- Required libraries: `discord.py`, `python-dotenv`, `requests`, `asyncio`
- `.env` file containing:
  ```bash
  DISCORD_TOKEN=your_token_here
  DISCORD_CHANNEL_ID=your_channel_id_here


### Step 2: Install Dependencies

Install the required dependencies using pip:

  ```bash
  pip install discord.py python-dotenv asyncio
```

### Step 3
Start the bot by running the main Python script:
```bash
  python bot.py
```

### Step 4: Bot Commands
The bot responds to the following commands when mentioned in a message:

- `hello`: Responds with a greeting.
- `how are you`: Replies with a status message.
- `bye`: Says goodbye.
- `roll dice`: Simulates rolling a 6-sided die and returns a number between 1 and 6.
- `next chance`: Provides the next opportunity to claim a free Chick-fil-A sandwich by checking upcoming games.
- `next clippers game`: Returns the next Clippers home game date and opponent.
- `next ducks game`: Returns the next Anaheim Ducks home game date and opponent.
- `next lafc game`: Returns the next LAFC home game date and opponent.
- `next angels game`: Returns the next LA Angels home game date and opponent.


## How It Works

### Step 1: Bot Setup
The bot is initialized with the necessary intents to handle message content. The `TOKEN` and `CHANNEL_ID` are retrieved from the environment variables:
```python
intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
CHANNEL_ID: Final[int] = int(os.getenv('DISCORD_CHANNEL_ID'))
```

### Step 2: Checking for Games Today
The bot checks if any games are scheduled for today across the four covered teams. Each team’s game-checking function is called asynchronously:
```python
async def check_for_games():
    global LAFC_game, ANA_Ducks_game, LA_Angels_game, LA_Clippers_game, clippers_game_id, clippers_result

    try:
        LAFC_game = LAFC.game_today()
    except Exception as e:
        print(f"Error checking LAFC game: {e}")
        LAFC_game = False

    try:
        ANA_Ducks_game = await Anaheim_Ducks.ducks_home_game_today()
    except Exception as e:
        print(f"Error checking Ducks game: {e}")
        ANA_Ducks_game = False

    try:
        LA_Angels_game = await LA_Angels.get_today_angels_home_game()
    except Exception as e:
        print(f"Error checking Angels game: {e}")
        LA_Angels_game = False

    try:
        result = LA_Clippers.get_today_clippers_home_game_id()
        if result:
            clippers_game_id, clippers_result = result
            LA_Clippers_game = clippers_game_id is not None
        else:
            LA_Clippers_game = False
    except Exception as e:
        print(f"Error checking Clippers game: {e}")
        LA_Clippers_game = False
```

### Step 3: Periodic Game Check
The bot continuously checks if game conditions have been met, using asynchronous functions to handle real-time updates. If a condition is met, the bot sends a message to the designated channel:
```python
async def periodic_check():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    while not client.is_closed():
        await check_for_games()

        ongoing_games = False

        if LAFC_game:
            lafc_results = await LAFC.get_match_results()
            if lafc_results != "The game has not finished yet!":
                if lafc_results['outcome'] == "Win":
                    await channel.send("LAFC has won their home game! Free Chick-fil-A sandwich!")
                LAFC_game = False
            else:
                ongoing_games = True

        if ANA_Ducks_game:
            ducks_results = await Anaheim_Ducks.check_ducks_score()
            if ducks_results != "The game hasn't finished yet!":
                if ducks_results:
                    await channel.send("The Anaheim Ducks have scored 5 or more goals at a home game! Free Chick-fil-A sandwich!")
                ANA_Ducks_game = False
            else:
                ongoing_games = True

        if LA_Clippers_game:
            if clippers_result == "W" or clippers_result == "L":
                clippers_4th_quarter = await LA_Clippers.check_opponent_missed_two_ft_in_4th_quarter(clippers_game_id)
                if clippers_4th_quarter:
                    await channel.send("The opponents of the Los Angeles Clippers missed two free throws in a row at a home game! Free Chick-fil-A sandwich!")
                LA_Clippers_game = False
            else:
                ongoing_games = True

        if LA_Angels_game:
            angels_result = await LA_Angels.check_angels_score()
            if angels_result != "The game has not finished yet!":
                if angels_result:
                    await channel.send("The Los Angeles Angels have scored 7 points! Free Chick-fil-A sandwich!")
                LA_Angels_game = False
            else:
                ongoing_games = True

        # Wait for 10 minutes if there are ongoing games, or 12 hours if no games are ongoing
        await asyncio.sleep(600 if ongoing_games else 43200)
```

### Step 4: Message Handling
The bot can respond to user messages, either privately or publicly, depending on the message's prefix:
```python
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        return

    is_private = user_message[0] == '?'
    user_message = user_message[1:] if is_private else user_message

    bot_mention = f'<@{client.user.id}>'

    try:
        response = await get_response(user_message, bot_mention)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)
```

## Licencse
This project is licensed under the MIT License. See the LICENSE file for details.

```vbnet
This is the complete markdown structure for all steps needed to set up and understand the Chick-fil-A bot project. It can be copied and pasted into a README.md file on GitHub.
```
