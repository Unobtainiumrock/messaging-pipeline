"""Discord connector for fetching messages from Discord channels and DMs."""
import os
import logging
import asyncio
from typing import List, Dict, Any
import discord
from discord.ext import commands
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DiscordConnector:
    """Connector for Discord using Discord.py."""

    def __init__(self) -> None:
        """Initialize the Discord connector with Bot token."""
        self.token = os.getenv("DISCORD_BOT_TOKEN")
        if not self.token:
            logger.warning("Discord Bot token not found in environment variables")

        # Initialize but don't connect - we'll do that when fetching
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True

        self.bot = commands.Bot(command_prefix="!", intents=intents)
        self.messages: List[Dict[str, Any]] = []

    async def _fetch_messages_async(self, days_back: int = 7) -> None:
        """
        Asynchronously fetch Discord messages.

        Args:
            days_back: Number of days to look back for messages
        """
        logger.info("Starting async Discord message fetch")

        await self.bot.wait_until_ready()
        logger.info(f"Discord bot logged in as {self.bot.user}")

        # Calculate the cutoff time
        cutoff_time = datetime.now() - timedelta(days=days_back)

        # Clear previous messages
        self.messages = []

        # Fetch messages from DMs
        for dm_channel in self.bot.private_channels:
            if isinstance(dm_channel, discord.DMChannel):
                logger.info(f"Fetching messages from Discord DM with {dm_channel.recipient}")

                async for message in dm_channel.history(limit=100, after=cutoff_time):
                    # Skip messages from the bot itself
                    if message.author == self.bot.user:
                        continue

                    # Standardize format
                    processed_message = {
                        "id": str(message.id),
                        "source": "discord",
                        "sender_name": message.author.name,
                        "sender_email": "",  # Discord doesn't expose email
                        "timestamp": message.created_at.timestamp(),
                        "subject": f"DM from {message.author.name}",
                        "content": message.content,
                        "raw_data": {
                            "author_id": message.author.id,
                            "channel_id": dm_channel.id,
                            "message_id": message.id,
                            "created_at": message.created_at.isoformat(),
                        },
                    }

                    self.messages.append(processed_message)

        logger.info(f"Fetched {len(self.messages)} messages from Discord")

    def fetch_messages(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Fetch recent DMs from Discord.

        Args:
            days_back: Number of days to look back for messages

        Returns:
            List of message dictionaries with standardized format
        """
        if not self.token:
            logger.error("Discord token not available")
            return []

        try:
            # Set up event to collect messages
            @self.bot.event
            async def on_ready():
                await self._fetch_messages_async(days_back)
                await self.bot.close()

            # Run the bot to collect messages
            asyncio.run(self.bot.start(self.token))

            return self.messages

        except Exception as e:
            logger.error(f"Error fetching Discord messages: {str(e)}", exc_info=True)
            return []

    async def send_message_async(self, user_id: int, content: str) -> bool:
        """
        Send a DM to a Discord user asynchronously.

        Args:
            user_id: Discord user ID to send message to
            content: Message content to send

        Returns:
            True if successful, False otherwise
        """
        try:
            user = await self.bot.fetch_user(user_id)
            dm_channel = await user.create_dm()
            await dm_channel.send(content)
            logger.info(f"Sent Discord DM to user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error sending Discord DM: {str(e)}", exc_info=True)
            return False

    def send_message(self, user_id: int, content: str) -> bool:
        """
        Send a DM to a Discord user.

        Args:
            user_id: Discord user ID to send message to
            content: Message content to send

        Returns:
            True if successful, False otherwise
        """
        if not self.token:
            logger.error("Discord token not available")
            return False

        try:
            # Create a simple bot just for sending this message
            intents = discord.Intents.default()
            bot = commands.Bot(command_prefix="!", intents=intents)

            @bot.event
            async def on_ready():
                result = await self.send_message_async(user_id, content)
                await bot.close()
                return result

            return asyncio.run(bot.start(self.token))

        except Exception as e:
            logger.error(f"Error in Discord send message: {str(e)}", exc_info=True)
            return False

    def process_messages(self, raw_messages: List[Any]) -> List[Dict[str, Any]]:
        """Process raw Discord messages into a standard format."""
        messages: List[Dict[str, Any]] = []
        # ... existing code ...
        return messages
