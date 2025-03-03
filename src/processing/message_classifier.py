"""
Message classifier for identifying message intents.
"""
import logging
import re
from typing import Dict, Any, List, Optional
from src.processing.nlp_processor import NLPProcessor

logger = logging.getLogger(__name__)

class MessageClassifier:
    """Classifier for determining message intents."""
    
    def __init__(self, nlp_processor: NLPProcessor) -> None:
        """
        Initialize the message classifier.
        
        Args:
            nlp_processor: NLP processor instance
        """
        self.nlp = nlp_processor
        
        # Regex patterns for intent detection
        self.patterns = {
            'interview_request': [
                r'interview',
                r'meet(ing)?(\s|to\s|for\s)',
                r'schedule(\sa)?(\s|call|chat|meeting)',
                r'available(\s|for|to)',
                r'speak(\s|with|to)',
                r'discuss(\s|your|the)',
                r'call(\s|with|to)',
                r'time(\s|for|to)',
                r'talk(\s|about|with)'
            ],
            'follow_up': [
                r'follow(ing)?(\s|-)?up',
                r'checking(\s|in)',
                r'status',
                r'update',
                r'progress',
                r'hear(ing)?(\s|back|from)'
            ],
            'job_offer': [
                r'offer',
                r'position',
                r'role',
                r'salary',
                r'compensation',
                r'package',
                r'accept',
                r'join(\s|our|the)',
                r'welcome(\s|to|aboard)',
            ],
            'networking': [
                r'connect',
                r'network',
                r'introduction',
                r'contact',
                r'recommendation',
                r'refer',
                r'introduction',
                r'community'
            ]
        }
    
    def classify(self, text: str) -> str:
        """
        Classify the intent of a message.
        
        Args:
            text: Message text to classify
            
        Returns:
            Intent classification (interview_request, follow_up, job_offer, networking, other)
        """
        if not text:
            return 'unknown'
        
        try:
            # Use LLM classification if available
            if self.nlp.llm_enabled and self.nlp.llm_nlp:
                return self._classify_with_llm(text)
            
            # Fall back to rule-based classification
            return self._classify_with_rules(text)
            
        except Exception as e:
            logger.error(f"Error classifying message: {str(e)}", exc_info=True)
            return 'unknown'
    
    def _classify_with_llm(self, text: str) -> str:
        """
        Classify message using LLM.
        
        Args:
            text: Message text
            
        Returns:
            Intent classification
        """
        analysis = self.nlp.analyze_text(text)
        
        if 'llm_classification' in analysis and analysis['llm_classification']:
            # Get the highest scoring category
            cats = analysis['llm_classification']
            top_cat = max(cats.items(), key=lambda x: x[1])
            
            logger.info(f"LLM classified as: {top_cat[0]} with score {top_cat[1]}")
            return top_cat[0]
        
        # Fallback to rule-based
        return self._classify_with_rules(text)
    
    def _classify_with_rules(self, text: str) -> str:
        """
        Classify message using regex pattern matching.
        
        Args:
            text: Message text
            
        Returns:
            Intent classification
        """
        text = text.lower()
        scores = {intent: 0 for intent in self.patterns.keys()}
        
        # Check each pattern
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    scores[intent] += 1
        
        # Get intent with highest score
        max_score = max(scores.values())
        
        if max_score == 0:
            return 'other'
        
        # Get all intents with the max score
        top_intents = [intent for intent, score in scores.items() if score == max_score]
        
        # If only one top intent, return it
        if len(top_intents) == 1:
            return top_intents[0]
        
        # If tie between interview_request and others, prioritize interview_request
        if 'interview_request' in top_intents:
            return 'interview_request'
        
        # Otherwise return the first top intent
        return top_intents[0] 