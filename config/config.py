"""Configuration module for the Communication Centralizer."""

import os
from typing import Dict, Any


class Config:
    """Configuration class for application settings."""

    @staticmethod
    def get_conn_settings(connector_type: str) -> Dict[str, Any]:
        """
        Get settings for a specific connector type.

        Args:
            connector_type: Type of connector (gmail, outlook, linkedin, etc.)

        Returns:
            Dictionary of settings for the connector
        """
        settings = {
            "gmail": {
                "credentials_path": os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
                "username": os.getenv("EMAIL_USERNAME"),
                "password": os.getenv("EMAIL_PASSWORD"),
                "scopes": ["https://www.googleapis.com/auth/gmail.modify"],
            },
            "outlook": {
                "client_id": os.getenv("OUTLOOK_CLIENT_ID"),
                "client_secret": os.getenv("OUTLOOK_CLIENT_SECRET"),
                "username": os.getenv("EMAIL_USERNAME"),
                "password": os.getenv("EMAIL_PASSWORD"),
                "scopes": ["Mail.Read", "Mail.Send"],
            },
            "linkedin": {
                "api_key": os.getenv("PHANTOMBUSTER_API_KEY"),
                "agent_id": os.getenv("PHANTOMBUSTER_MESSAGE_AGENT_ID"),
            },
            "handshake": {
                "username": os.getenv("HANDSHAKE_USERNAME"),
                "password": os.getenv("HANDSHAKE_PASSWORD"),
                "automation_type": os.getenv("HANDSHAKE_AUTOMATION", "selenium"),
            },
            "slack": {"bot_token": os.getenv("SLACK_BOT_TOKEN")},
            "discord": {"bot_token": os.getenv("DISCORD_BOT_TOKEN")},
            "google_sheets": {
                "sheet_id": os.getenv("GOOGLE_SHEET_ID"),
                "credentials_path": os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            },
            "calendly": {
                "api_key": os.getenv("CALENDLY_API_KEY"),
                "user": os.getenv("CALENDLY_USER"),
            },
            "google_calendar": {"credentials_path": os.getenv("GOOGLE_APPLICATION_CREDENTIALS")},
        }

        return settings.get(connector_type, {})

    @staticmethod
    def get_nlp_settings() -> Dict[str, Any]:
        """
        Get settings for NLP processing.

        Returns:
            Dictionary of NLP settings
        """
        result: Dict[str, Any] = {
            "enable_llm": os.getenv("ENABLE_LLM", "true").lower() == "true",
            "llm_model": os.getenv("SPACY_LLM_MODEL", "gpt-3.5-turbo"),
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "spacy_model": os.getenv("SPACY_MODEL", "en_core_web_sm"),
        }
        return result
