#!/usr/bin/env python3
"""
Main entry point for the Communication Centralizer application.
"""
import logging
import os
import sys
import time
from typing import Dict, List, Any
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.connectors.email_connector import EmailConnector
from src.connectors.linkedin_connector import LinkedInConnector
from src.connectors.handshake_connector import HandshakeConnector
from src.connectors.slack_connector import SlackConnector
from src.connectors.discord_connector import DiscordConnector
from src.storage.google_sheets import GoogleSheetsStorage
from src.processing.nlp_processor import NLPProcessor
from src.processing.message_classifier import MessageClassifier
from src.scheduling.calendly import CalendlyScheduler
from src.scheduling.google_calendar import GoogleCalendarScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("comm_centralizer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main() -> None:
    """Main function to run the communication centralizer pipeline."""
    # Load environment variables
    load_dotenv()
    
    try:
        # Initialize components
        logger.info("Initializing components...")
        storage = GoogleSheetsStorage()
        nlp_processor = NLPProcessor()
        message_classifier = MessageClassifier(nlp_processor)
        calendly_scheduler = CalendlyScheduler()
        google_calendar = GoogleCalendarScheduler()
        
        # Initialize connectors
        email_connector = EmailConnector()
        linkedin_connector = LinkedInConnector()
        handshake_connector = HandshakeConnector()
        slack_connector = SlackConnector()
        discord_connector = DiscordConnector()
        
        # Fetch messages from all sources
        logger.info("Fetching messages from all sources...")
        email_messages = email_connector.fetch_messages()
        linkedin_messages = linkedin_connector.fetch_messages()
        handshake_messages = handshake_connector.fetch_messages()
        slack_messages = slack_connector.fetch_messages()
        discord_messages = discord_connector.fetch_messages()
        
        # Combine all messages
        all_messages = (
            email_messages + 
            linkedin_messages + 
            handshake_messages + 
            slack_messages + 
            discord_messages
        )
        
        # Process messages
        logger.info(f"Processing {len(all_messages)} messages...")
        for message in all_messages:
            # Classify message intent
            intent = message_classifier.classify(message['content'])
            message['intent'] = intent
            
            # Store in Google Sheets
            storage.store_message(message)
            
            # If interview request, schedule it
            if intent == 'interview_request':
                logger.info(f"Scheduling interview for message: {message['id']}")
                calendly_link = calendly_scheduler.get_scheduling_link()
                email_connector.send_reply(
                    message['sender_email'],
                    "Interview Scheduling",
                    f"Thank you for your interest! Please schedule a time using this link: {calendly_link}"
                )
        
        logger.info("Communication processing completed successfully")
        
    except Exception as e:
        logger.error(f"Error in main processing: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 