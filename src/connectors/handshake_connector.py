"""
Handshake connector for fetching messages from Handshake platform.
Uses Selenium or Puppeteer for browser automation.
"""

import os
import logging
import json
import subprocess
from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


class HandshakeConnector:
    """Connector for Handshake using browser automation."""

    def __init__(self) -> None:
        """Initialize the Handshake connector."""
        self.username = os.getenv("HANDSHAKE_USERNAME")
        self.password = os.getenv("HANDSHAKE_PASSWORD")
        self.automation_type = os.getenv("HANDSHAKE_AUTOMATION", "selenium")

        if not self.username or not self.password:
            logger.warning("Handshake credentials not found in environment variables")

    def fetch_messages(self) -> List[Dict[str, Any]]:
        """
        Fetch recent messages from Handshake.

        Returns:
            List of message dictionaries with standardized format
        """
        if not self.username or not self.password:
            logger.error("Missing Handshake credentials")
            return []

        if self.automation_type == "puppeteer":
            return self._fetch_with_puppeteer()
        else:
            return self._fetch_with_selenium()

    def _fetch_with_selenium(self) -> List[Dict[str, Any]]:
        """Fetch Handshake messages using Selenium."""
        messages = []
        driver = None

        try:
            logger.info("Setting up Chrome driver for Handshake automation")
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)

            # Log in to Handshake
            logger.info("Logging in to Handshake")
            driver.get("https://app.joinhandshake.com/login")

            # Wait for login form and enter credentials
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))
            driver.find_element(By.ID, "email").send_keys(self.username)
            driver.find_element(By.ID, "password").send_keys(self.password)
            driver.find_element(By.NAME, "commit").click()

            # Navigate to messages
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Messages")))
            driver.find_element(By.LINK_TEXT, "Messages").click()

            # Wait for message list to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".message-thread"))
            )

            # Extract message threads
            message_threads = driver.find_elements(By.CSS_SELECTOR, ".message-thread")
            logger.info(f"Found {len(message_threads)} message threads on Handshake")

            # Process each thread
            for i, thread in enumerate(message_threads[:10]):  # Limit to 10 threads for performance
                thread.click()

                # Wait for message content to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".message-content"))
                )

                # Extract latest message
                latest_message = driver.find_elements(By.CSS_SELECTOR, ".message-content")[-1]
                sender_element = driver.find_elements(By.CSS_SELECTOR, ".message-sender")[-1]
                timestamp_element = driver.find_elements(By.CSS_SELECTOR, ".message-timestamp")[-1]

                sender_name = sender_element.text if sender_element else "Unknown Sender"
                content = latest_message.text if latest_message else ""
                timestamp = timestamp_element.text if timestamp_element else ""

                # Create standardized message object
                message = {
                    "id": f"handshake_{i}_{timestamp.replace(' ', '_')}",
                    "source": "handshake",
                    "sender_name": sender_name,
                    "sender_email": "",  # Handshake doesn't expose email directly
                    "timestamp": timestamp,
                    "subject": "",  # Handshake messages don't have subjects
                    "content": content,
                    "raw_data": {
                        "sender": sender_name,
                        "content": content,
                        "timestamp": timestamp,
                    },
                }

                messages.append(message)

                # Go back to message list for next thread
                driver.find_element(By.LINK_TEXT, "Messages").click()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".message-thread"))
                )

            logger.info(f"Successfully extracted {len(messages)} messages from Handshake")
            return messages

        except Exception as e:
            logger.error(
                f"Error fetching Handshake messages with Selenium: {str(e)}",
                exc_info=True,
            )
            return []

        finally:
            if driver:
                driver.quit()

    def _fetch_with_puppeteer(self) -> List[Dict[str, Any]]:
        """Fetch Handshake messages using Puppeteer (Node.js)."""
        try:
            logger.info("Running Puppeteer script for Handshake automation")
            script_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "src",
                "automation",
                "puppeteer_scripts",
                "handshake.js",
            )

            # Run the Node.js script and capture output
            process = subprocess.run(["node", script_path], capture_output=True, text=True, check=True)

            # Parse JSON output from the script
            output = process.stdout.strip()
            if not output:
                logger.error("Empty output from Puppeteer script")
                return []

            raw_messages = json.loads(output)

            # Process raw messages into standardized format
            messages = []
            for i, msg in enumerate(raw_messages):
                message = {
                    "id": msg.get("id", f"handshake_{i}"),
                    "source": "handshake",
                    "sender_name": msg.get("sender", "Unknown Sender"),
                    "sender_email": "",  # Handshake doesn't expose email directly
                    "timestamp": msg.get("timestamp", ""),
                    "subject": "",  # Handshake messages don't have subjects
                    "content": msg.get("content", ""),
                    "raw_data": msg,
                }

                messages.append(message)

            logger.info(f"Successfully extracted {len(messages)} messages from Handshake with Puppeteer")
            return messages

        except Exception as e:
            logger.error(
                f"Error fetching Handshake messages with Puppeteer: {str(e)}",
                exc_info=True,
            )
            return []
