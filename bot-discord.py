import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import asyncio

# Set the bot token
TOKEN = "" ## replace it with the bot token

# Initialize intents
intents = discord.Intents.default()
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.command_timers = {
            'Yalahar': None,
            'Goroma': None,
            'Hellgate': None,
            'Kazordoon': None,
            'Plains': None,
            'Drefia': None,
            'Ankrahmun': None,
            'Forbidden': None,
            'Svargrond': None,
            'Edron': None,
        }
        self.cooldown_notified = {key: {'end': False, '1h': False, '30m': False, '15m': False, '5m': False} for key in self.command_timers}
        self.cooldown_duration = timedelta(hours=3)
        self.channel_id = ''  # Replace with the correct channel ID
        self.status_channel_id = ''  # Replace with the status update channel ID
        self.cooldown_messages = {}

    async def setup_hook(self):
        await self.add_cog(LightbearerCog(self))
        await self.tree.sync()
        print("Slash commands have been synced.")
        self.loop.create_task(self.check_cooldowns())

    def is_on_cooldown(self, command_name):
        last_used = self.command_timers.get(command_name)
        if last_used is None:
            return False
        return datetime.now() < last_used + self.cooldown_duration

    def get_remaining_time(self, command_name):
        last_used = self.command_timers.get(command_name)
        if last_used is None:
            return None
        return (last_used + self.cooldown_duration) - datetime.now()

    def format_remaining_time(self, remaining_time):
        total_seconds = int(remaining_time.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}:{minutes:02}:{seconds:02}"

    async def check_cooldowns(self):
        await self.wait_until_ready()
        notify_channel = self.get_channel(self.channel_id)
        status_channel = self.get_channel(self.status_channel_id)

        if not notify_channel or not status_channel:
            print("One or more channels could not be found.")
            return

        while not self.is_closed():
            for name, last_used in self.command_timers.items():
                if last_used:
                    remaining_time = self.get_remaining_time(name)
                    if remaining_time is None:
                        continue

                    # Check remaining time for notifications
                    if remaining_time <= timedelta(hours=1) and not self.cooldown_notified[name]['1h']:
                        await notify_channel.send(f"@everyone The cooldown for `{name}` will end in 1 hour!")
                        self.cooldown_notified[name]['1h'] = True
                    elif remaining_time <= timedelta(minutes=30) and not self.cooldown_notified[name]['30m']:
                        await notify_channel.send(f"@everyone The cooldown for `{name}` will end in 30 minutes!")
                        self.cooldown_notified[name]['30m'] = True
                    elif remaining_time <= timedelta(minutes=15) and not self.cooldown_notified[name]['15m']:
                        await notify_channel.send(f"@everyone The cooldown for `{name}` will end in 15 minutes!")
                        self.cooldown_notified[name]['15m'] = True
                    elif remaining_time <= timedelta(minutes=5) and not self.cooldown_notified[name]['5m']:
                        await notify_channel.send(f"@everyone The cooldown for `{name}` will end in 5 minutes!")
                        self.cooldown_notified[name]['5m'] = True
                    elif remaining_time <= timedelta(0) and not self.cooldown_notified[name]['end']:
                        await notify_channel.send(f"@everyone The cooldown for `{name}` has ended!")
                        self.cooldown_notified[name] = {key: False for key in self.cooldown_notified[name]}
                        self.command_timers[name] = None
                        if name in self.cooldown_messages:
                            await self.cooldown_messages[name].delete()
                            del self.cooldown_messages[name]

                    # Update status message and log
                    formatted_time = self.format_remaining_time(remaining_time)
                    if name not in self.cooldown_messages:
                        message = await status_channel.send(f"{name} cooldown remaining: `{formatted_time}`")
                        self.cooldown_messages[name] = message
                    else:
                        await self.cooldown_messages[name].edit(content=f"{name} cooldown remaining: `{formatted_time}`")
                    
                    # Log update to console
                    print(f"Updated time for {name} with remaining time: {formatted_time}")

            await asyncio.sleep(15)


class LightbearerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name='settime', description='Sets the remaining time for a specific basin')
    @app_commands.describe(name="Specify the Lightbearer", hours="Hours to set", minutes="Minutes to set")
    async def set_time(self, interaction: discord.Interaction, name: str, hours: float, minutes: float = 0.0):
        await interaction.response.defer(ephemeral=True)
        name_value = name.replace(" ", "_").capitalize()

        if name_value not in self.bot.command_timers:
            await interaction.followup.send(f"No Lightbearer found with the name `{name_value}`.", ephemeral=True)
            return

        total_minutes = hours * 60 + minutes
        new_duration = timedelta(minutes=total_minutes)
        self.bot.command_timers[name_value] = datetime.now() - (self.bot.cooldown_duration - new_duration)

        self.bot.cooldown_notified[name_value] = {key: False for key in self.bot.cooldown_notified[name_value]}
        formatted_time = f"{int(hours)}h {int(minutes)}m" if minutes > 0 else f"{int(hours)}h"
        await interaction.followup.send(f"The {name_value} Lightbearer is now set to burn for {formatted_time}.", ephemeral=True)

    @set_time.autocomplete("name")
    async def set_time_name_autocomplete(self, interaction: discord.Interaction, current: str):
        names = list(self.bot.command_timers.keys())
        return [
            app_commands.Choice(name=name, value=name)
            for name in names if current.lower() in name.lower()
        ]

    @app_commands.command(name='lit', description='Controls Lightbearer commands')
    @app_commands.describe(action="Choose the action to perform", name="Specify the Lightbearer")
    async def lit(self, interaction: discord.Interaction, action: str, name: str = None):
        await interaction.response.defer(ephemeral=True)
        action_value = action.lower()
        name_value = name.replace(" ", "_").capitalize() if name else None

        if action_value == "info" and name_value:
            if name_value not in self.bot.command_timers:
                await interaction.followup.send(f"No Lightbearer found with the name `{name_value}`.", ephemeral=True)
                return

            remaining_time = self.bot.get_remaining_time(name_value)
            if remaining_time and remaining_time > timedelta(0):
                formatted_time = self.bot.format_remaining_time(remaining_time)
                await interaction.followup.send(f"The {name_value} Lightbearer is still on fire for {formatted_time}.", ephemeral=True)
            else:
                await interaction.followup.send(f"The {name_value} Lightbearer fire went off! Hurry up!", ephemeral=True)

        elif action_value == "basin" and name_value:
            if name_value not in self.bot.command_timers:
                await interaction.followup.send(f"No Lightbearer found with the name `{name_value}`.", ephemeral=True)
                return

            self.bot.command_timers[name_value] = datetime.now()
            self.bot.cooldown_notified[name_value] = {key: False for key in self.bot.cooldown_notified[name_value]}
            await interaction.followup.send(f"The lightbearer on {name_value} is set on fire for 3h!", ephemeral=True)

    @lit.autocomplete("action")
    async def action_autocomplete(self, interaction: discord.Interaction, current: str):
        actions = ["info", "basin"]
        return [
            app_commands.Choice(name=action, value=action)
            for action in actions if current.lower() in action.lower()
        ]

    @lit.autocomplete("name")
    async def name_autocomplete(self, interaction: discord.Interaction, current: str):
        names = list(self.bot.command_timers.keys())
        return [
            app_commands.Choice(name=name, value=name)
            for name in names if current.lower() in name.lower()
        ]

    @app_commands.command(name='reset', description='Resets the cooldown for a specific Lightbearer.')
    async def reset(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer(ephemeral=True)
        name_value = name.replace(" ", "_").capitalize()
        if name_value in self.bot.command_timers:
            self.bot.command_timers[name_value] = None
            self.bot.cooldown_notified[name_value] = {key: False for key in self.bot.cooldown_notified[name_value]}
            await interaction.followup.send(f"Cooldown for `{name_value}` has been reset!", ephemeral=True)
        else:
            await interaction.followup.send(f"No Lightbearer found with the name `{name_value}`.", ephemeral=True)

    @reset.autocomplete("name")
    async def reset_name_autocomplete(self, interaction: discord.Interaction, current: str):
        names = list(self.bot.command_timers.keys())
        return [
            app_commands.Choice(name=name, value=name)
            for name in names if current.lower() in name.lower()
        ]

    @app_commands.command(name='resetall', description='Resets cooldowns for all Lightbearers.')
    @app_commands.checks.has_permissions(administrator=True)
    async def reset_all(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        for key in self.bot.command_timers:
            self.bot.command_timers[key] = None
            self.bot.cooldown_notified[key] = {subkey: False for subkey in self.bot.cooldown_notified[key]}
        await interaction.followup.send("Cooldowns for all Lightbearers have been reset!", ephemeral=True)

    @app_commands.command(name='showall', description='Shows all current cooldowns for Lightbearers.')
    async def show_all(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        messages = []
        for name, last_used in self.bot.command_timers.items():
            if last_used is not None:
                remaining_time = (last_used + self.bot.cooldown_duration) - datetime.now()
                if remaining_time.total_seconds() > 0:
                    formatted_time = self.bot.format_remaining_time(remaining_time)
                    messages.append(f"The `{name}` Lightbearer is still on fire for `{formatted_time}`.")
                else:
                    messages.append(f"The `{name}` Lightbearer fire went off! Hurry up!")
            else:
                messages.append(f"The `{name}` Lightbearer is ready to be set on fire.")
        response = '\n'.join(messages)
        await interaction.followup.send(response, ephemeral=True)

# Initialize bot
bot = MyBot(command_prefix='/', intents=intents)
bot.run(TOKEN)