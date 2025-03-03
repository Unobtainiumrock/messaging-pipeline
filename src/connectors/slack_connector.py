"""
Slack connector for fetching messages from Slack channels and DMs.
"""
import os
import logging
from typing import List, Dict, Any
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)

class SlackConnector:
    """Connector for Slack using official Slack API."""
    
    def __init__(self) -> None:
        """Initialize the Slack connector with Bot token."""
        self.token = os.getenv('SLACK_BOT_TOKEN')
        if not self.token:
            logger.warning("Slack Bot token not found in environment variables")
            self.client = None
        else:
            self.client = WebClient(token=self.token)
    
    def fetch_messages(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Fetch recent DMs from Slack.
        
        Args:
            days_back: Number of days to look back for messages
            
        Returns:
            List of message dictionaries with standardized format
        """
        if not self.client:
            logger.error("Slack client not initialized")
            return []
        
        try:
            # Calculate timestamp for filtering (days_back days ago)
            oldest_timestamp = time.time() - (days_back * 24 * 60 * 60)
            
            # Fetch conversations (channels and DMs)
            logger.info("Fetching Slack conversations")
            conversations = self._get_dm_channels()
            
            all_messages = []
            
            # Process each DM channel
            for conversation in conversations:
                channel_id = conversation['id']
                channel_name = conversation.get('name', 'Direct Message')
                
                # Fetch messages for this channel
                logger.info(f"Fetching messages from Slack channel: {channel_id}")
                messages = self._get_channel_messages(channel_id, oldest_timestamp)
                
                # Process messages
                for msg in messages:
                    # Skip non-user messages and bot messages
                    if 'user' not in msg or msg.get('subtype') == 'bot_message':
                        continue
                    
                    # Get user info
                    user_info = self._get_user_info(msg['user'])
                    
                    # Standardize format
                    processed_message = {
                        'id': msg['ts'],
                        'source': 'slack',
                        'sender_name': user_info.get('real_name', 'Unknown User'),
                        'sender_email': user_info.get('profile', {}).get('email', ''),
                        'timestamp': float(msg['ts']),
                        'subject': f"Message in {channel_name}",
                        'content': msg.get('text', ''),
                        'raw_data': {
                            'channel': channel_id,
                            'user': msg['user'],
                            'ts': msg['ts'],
                            'text': msg.get('text', '')
                        }
                    }
                    
                    all_messages.append(processed_message)
            
            logger.info(f"Fetched {len(all_messages)} messages from Slack")
            return all_messages
            
        except SlackApiError as e:
            logger.error(f"Slack API error: {str(e)}", exc_info=True)
            return []
        except Exception as e:
            logger.error(f"Error fetching Slack messages: {str(e)}", exc_info=True)
            return []
    
    def _get_dm_channels(self) -> List[Dict[str, Any]]:
        """
        Get DM channels for the bot.
        
        Returns:
            List of DM channel objects
        """
        result = self.client.conversations_list(
            types="im",
            limit=100
        )
        
        return result.get('channels', [])
    
    def _get_channel_messages(self, channel_id: str, oldest: float) -> List[Dict[str, Any]]:
        """
        Get messages from a specific channel.
        
        Args:
            channel_id: ID of the channel
            oldest: Oldest timestamp to include
            
        Returns:
            List of message objects
        """
        result = self.client.conversations_history(
            channel=channel_id,
            oldest=str(oldest),
            limit=100
        )
        
        return result.get('messages', [])
    
    def _get_user_info(self, user_id: str) -> Dict[str, Any]:
        """
        Get user information from user ID.
        
        Args:
            user_id: ID of the user
            
        Returns:
            User information object
        """
        try:
            result = self.client.users_info(user=user_id)
            return result.get('user', {})
        except SlackApiError:
            logger.warning(f"Could not get info for Slack user: {user_id}")
            return {}
    
    def send_message(self, channel_id: str, message: str) -> bool:
        """
        Send a message to a Slack channel.
        
        Args:
            channel_id: ID of the channel to send to
            message: Message text to send
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.error("Slack client not initialized")
            return False
        
        try:
            self.client.chat_postMessage(
                channel=channel_id,
                text=message
            )
            logger.info(f"Sent message to Slack channel: {channel_id}")
            return True
        except SlackApiError as e:
            logger.error(f"Error sending Slack message: {str(e)}", exc_info=True)
            return False 