# Discord Lightbearer Bot ![Lightbearer Logo](./assets/basin.gif)

A Discord bot designed to track cooldowns for Lightbearer events in the game. The bot notifies users in specific channels when cooldowns are nearing their end and provides commands to manage Lightbearers' status.

## Features

- Tracks cooldowns for multiple Lightbearers.
- Sends notifications at **1 hour**, **30 minutes**, **15 minutes**, and **5 minutes** before cooldown ends.
- Provides slash commands to interact with the cooldowns.
- Updates status messages in a dedicated status channel.
- Allows setting, resetting, and displaying Lightbearer cooldowns.

## Installation

### Requirements

- Python 3.8+
- `discord.py` library

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/Boar-ingCode/Discord-Reminder.git
   cd your-repo-name
   ```
2. Install dependencies:
   Python installed (version 3.8 or higher is recommended for compatibility with discord.py).
    ```bash
   pip install discord.py
   ```
3. Set up your bot by replacing the placeholder token in the script:
   ```bash
   TOKEN = "YOUR_BOT_TOKEN_HERE"
   ```
4. Replace the channel IDs in the script with your actual Discord channel IDs:
   ```bash
   self.channel_id = YOUR_NOTIFY_CHANNEL_ID
   self.status_channel_id = YOUR_STATUS_CHANNEL_ID
   ```
5. Run the bot:
   ```bash
   python bot_discord.py
   ```

### Commands

#### /settime name hours minutes

Set the cooldown time for a specific Lightbearer:

- name: The Lightbearer name.
- hours: The number of hours.
- minutes (optional): The number of minutes.

#### /lit action name

Interact with a Lightbearer cooldown:

- action: Either info (to check status) or basin (to start cooldown).
- name: The Lightbearer name.

#### /reset name

Reset the cooldown for a specific Lightbearer.

#### /resetall

Reset all Lightbearer cooldowns (Admin only).

#### /showall

Show all current Lightbearer cooldowns.

### Configuration

- The bot automatically updates cooldowns and sends notifications.
- Ensure the bot has the necessary permissions to send messages in the specified channels.

### License

This project is licensed under the MIT License. Feel free to modify and distribute it.

### Author

Dariusz Pazdur
Contact: dzikuudev@gmail.com
