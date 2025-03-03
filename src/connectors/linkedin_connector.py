"""
LinkedIn connector using PhantomBuster for fetching LinkedIn messages.
"""
import os
import time
import logging
import requests
from typing import List, Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

class LinkedInConnector:
    """Connector for LinkedIn using PhantomBuster API."""
    
    def __init__(self) -> None:
        """Initialize the LinkedIn connector with PhantomBuster API."""
        self.api_key = os.getenv('PHANTOMBUSTER_API_KEY')
        if not self.api_key:
            logger.warning("PhantomBuster API key not found in environment variables")
        
        # PhantomBuster container/agent IDs for different functionalities
        self.message_agent_id = os.getenv('PHANTOMBUSTER_MESSAGE_AGENT_ID')
        self.base_url = "https://api.phantombuster.com/api/v2"
    
    def fetch_messages(self) -> List[Dict[str, Any]]:
        """
        Fetch recent LinkedIn messages using PhantomBuster.
        
        Returns:
            List of message dictionaries with standardized format
        """
        if not self.api_key or not self.message_agent_id:
            logger.error("Missing PhantomBuster credentials")
            return []
        
        try:
            # Launch the PhantomBuster agent to fetch LinkedIn messages
            logger.info("Launching PhantomBuster agent to fetch LinkedIn messages")
            
            # Launch the agent
            launch_response = self._launch_agent(self.message_agent_id)
            if not launch_response.get('success'):
                logger.error(f"Failed to launch PhantomBuster agent: {launch_response}")
                return []
            
            container_id = launch_response.get('containerId')
            
            # Wait for agent to complete
            status = self._wait_for_agent_completion(container_id)
            if status != 'finished':
                logger.error(f"PhantomBuster agent did not complete successfully: {status}")
                return []
            
            # Fetch the result
            result = self._fetch_agent_output(container_id)
            if not result:
                logger.error("No output from PhantomBuster agent")
                return []
            
            # Process the messages into standardized format
            processed_messages = self._process_linkedin_messages(result)
            logger.info(f"Fetched {len(processed_messages)} messages from LinkedIn")
            
            return processed_messages
            
        except Exception as e:
            logger.error(f"Error fetching LinkedIn messages: {str(e)}", exc_info=True)
            return []
    
    def _launch_agent(self, agent_id: str) -> Dict[str, Any]:
        """Launch a PhantomBuster agent by ID."""
        url = f"{self.base_url}/container/launch"
        headers = {
            "X-Phantombuster-Key": self.api_key,
            "Content-Type": "application/json"
        }
        data = {
            "id": agent_id,
            "arguments": {}
        }
        
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    
    def _wait_for_agent_completion(self, container_id: str, max_wait_time: int = 300) -> str:
        """
        Wait for PhantomBuster agent to complete.
        
        Args:
            container_id: The container ID of the running agent
            max_wait_time: Maximum time to wait in seconds
            
        Returns:
            Status of the agent (finished, error, etc.)
        """
        url = f"{self.base_url}/container/status"
        headers = {"X-Phantombuster-Key": self.api_key}
        params = {"id": container_id}
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            
            status = data.get('status')
            if status in ['finished', 'failed', 'stopped']:
                return status
            
            # Wait before checking again
            time.sleep(10)
        
        return "timeout"
    
    def _fetch_agent_output(self, container_id: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch the output from a completed PhantomBuster agent."""
        url = f"{self.base_url}/container/output"
        headers = {"X-Phantombuster-Key": self.api_key}
        params = {"id": container_id}
        
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        if data.get('status') == 'success' and 'output' in data:
            try:
                # PhantomBuster typically returns JSON string output
                return json.loads(data['output'])
            except json.JSONDecodeError:
                logger.error("Failed to decode JSON from PhantomBuster output")
                return None
        
        return None
    
    def _process_linkedin_messages(self, raw_messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process raw LinkedIn message data into standardized format.
        
        Args:
            raw_messages: Raw message data from PhantomBuster
            
        Returns:
            Standardized message dictionaries
        """
        processed_messages = []
        
        for msg in raw_messages:
            # The exact format depends on PhantomBuster output
            # This is a placeholder mapping
            processed_message = {
                'id': msg.get('id', f"linkedin_{len(processed_messages)}"),
                'source': 'linkedin',
                'sender_name': msg.get('senderName', ''),
                'sender_email': msg.get('senderEmail', ''),  # LinkedIn might not provide email
                'timestamp': msg.get('timestamp', ''),
                'subject': '',  # LinkedIn messages don't have subjects
                'content': msg.get('messageContent', ''),
                'raw_data': msg
            }
            
            processed_messages.append(processed_message)
        
        return processed_messages 