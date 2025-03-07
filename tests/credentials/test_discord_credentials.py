#!/usr/bin/env python3
"""Test script to verify Discord Bot credentials."""
import os
import asyncio
import discord
import pytest
import warnings
import sys
from typing import Optional, List

# Before importing discord
warnings.filterwarnings("ignore", message="'audioop' is deprecated")

# Global variable for token
bot_token: Optional[str] = None


@pytest.mark.asyncio
async def test_discord_bot() -> None:
    """Async function to test Discord bot token."""
    print("Connecting to Discord...")

    intents: discord.Intents = discord.Intents.default()
    intents.message_content = True
    client: discord.Client = discord.Client(intents=intents)

    @client.event
    async def on_ready() -> None:
        print(f"✅ Connected to Discord as {client.user} (ID: {client.user.id})")
        print(f"  - Bot is in {len(client.guilds)} servers")

        if client.guilds:
            guild: discord.Guild = client.guilds[0]
            print("\nFirst server details:")
            print(f"  - Name: {guild.name}")
            print(f"  - ID: {guild.id}")
            print(f"  - Member count: {guild.member_count}")

            # List some channels
            text_channels: List[discord.TextChannel] = [
                channel for channel in guild.channels if isinstance(channel, discord.TextChannel)
            ]
            if text_channels:
                print("\nText channels:")
                for i, channel in enumerate(text_channels[:5]):
                    print(f"  - #{channel.name}")
                    if i >= 4:
                        break

        print("\n✅ SUCCESS: Discord bot token is working correctly!")
        await client.close()

    try:
        await client.start(bot_token)
    except discord.errors.LoginFailure:
        print("❌ ERROR: Discord login failed. Invalid bot token.")
        print("\nTroubleshooting tips:")
        print("1. Check your bot token in the .env file")
        print("2. Ensure your bot token is from a bot application, not a user token")
        print("3. Verify that your bot is not disabled")
        pytest.fail("Discord login failed. Invalid bot token.")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        pytest.fail(f"Test failed with exception: {str(e)}")


def test_discord_credentials() -> None:
    """Test Discord Bot Token."""
    print("Testing Discord credentials...")

    global bot_token
    # Check environment variables
    bot_token = os.getenv("DISCORD_BOT_TOKEN")

    print(f"- Bot Token: {'✓ Found' if bot_token else '✗ MISSING'}")

    if not bot_token:
        print("❌ ERROR: Discord Bot Token missing")
        pytest.skip("Discord Bot Token not found in environment variables")

    # Discord API requires asyncio
    try:
        loop: asyncio.AbstractEventLoop
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(test_discord_bot())
    except Exception as e:
        print(f"❌ Error running asyncio event loop: {str(e)}")
        pytest.fail(f"Error running asyncio event loop: {str(e)}")


def run_test() -> bool:
    """Run the test and return boolean result for command line usage."""
    try:
        global bot_token
        # Check environment variables
        bot_token = os.getenv("DISCORD_BOT_TOKEN")

        print(f"- Bot Token: {'✓ Found' if bot_token else '✗ MISSING'}")

        if not bot_token:
            print("❌ ERROR: Discord Bot Token missing")
            return False

        # Discord API requires asyncio
        loop: asyncio.AbstractEventLoop
        try:
            loop = asyncio.get_running_loop()
            return loop.run_until_complete(async_run_test())
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(async_run_test())
    except Exception as e:
        print(f"❌ Error running asyncio event loop: {str(e)}")
        return False


async def async_run_test() -> bool:
    """Async wrapper for running the test from command line."""
    try:
        await test_discord_bot()
        return True
    except Exception:
        return False


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
