# Chick-fil-A Game Notification Discord Bot

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
