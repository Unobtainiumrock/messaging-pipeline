#!/usr/bin/env python3
"""
Test script to verify Discord Bot credentials.
"""
import os
import asyncio
import discord
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_discord_bot():
    """Async function to test Discord bot token."""
    print("Connecting to Discord...")
    
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        print(f"✅ Connected to Discord as {client.user} (ID: {client.user.id})")
        print(f"  - Bot is in {len(client.guilds)} servers")
        
        if client.guilds:
            guild = client.guilds[0]
            print(f"\nFirst server details:")
            print(f"  - Name: {guild.name}")
            print(f"  - ID: {guild.id}")
            print(f"  - Member count: {guild.member_count}")
            
            # List some channels
            text_channels = [channel for channel in guild.channels if isinstance(channel, discord.TextChannel)]
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
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False
    
    return True

def test_discord_credentials():
    """Test Discord Bot Token."""
    print("Testing Discord credentials...")
    
    global bot_token
    # Check environment variables
    bot_token = os.getenv('DISCORD_BOT_TOKEN')
    
    print(f"- Bot Token: {'✓ Found' if bot_token else '✗ MISSING'}")
    
    if not bot_token:
        print("❌ ERROR: Discord Bot Token missing")
        return False
    
    # Discord API requires asyncio
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(test_discord_bot())
    except Exception as e:
        print(f"❌ Error running asyncio event loop: {str(e)}")
        return False

if __name__ == "__main__":
    test_discord_credentials() 