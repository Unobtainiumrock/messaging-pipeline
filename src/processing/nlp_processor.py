"""NLP processor using spaCy with LLM integration for message analysis."""
import os
import logging
from typing import Dict, List, Any
import spacy
from spacy.tokens import Doc

# For LLM integration
try:
    from spacy_llm.util import assemble
except ImportError:
    logging.warning("spacy_llm not found, LLM functionality will be limited")

logger = logging.getLogger(__name__)


class NLPProcessor:
    """Processor for NLP tasks using spaCy with LLM integration."""

    def __init__(self) -> None:
        """Initialize spaCy NLP pipeline with LLM integration."""
        try:
            # Initialize basic spaCy model
            self.basic_nlp = spacy.load("en_core_web_sm")

            # Initialize LLM-enhanced model if available
            self.llm_enabled = os.getenv("ENABLE_LLM", "true").lower() == "true"

            if self.llm_enabled:
                self._init_llm_pipeline()
                logger.info("NLP processor initialized with LLM integration")
            else:
                self.llm_nlp = None
                logger.info("NLP processor initialized with basic spaCy (LLM disabled)")

            self.client = None  # Initialize the attribute

        except Exception as e:
            logger.error(f"Error initializing NLP processor: {str(e)}", exc_info=True)
            self.basic_nlp = None
            self.llm_nlp = None

    def _init_llm_pipeline(self) -> None:
        """Initialize spaCy pipeline with LLM integration."""
        try:
            # Set OpenAI API key for spaCy LLM
            os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

            # Configure LLM pipeline
            llm_model = os.getenv("SPACY_LLM_MODEL", "gpt-3.5-turbo")

            # Define a custom pipeline with text classification component
            config = {
                "nlp": {"lang": "en", "pipeline": ["llm"]},
                "components": {
                    "llm": {
                        "factory": "llm",
                        "model": llm_model,
                        "config": {
                            "task": {
                                "@llm_tasks": "spacy.TextCat.v2",
                                "labels": [
                                    "interview_request",
                                    "follow_up",
                                    "job_offer",
                                    "networking",
                                    "other",
                                ],
                            }
                        },
                    }
                },
            }

            # Assemble the pipeline from config
            self.llm_nlp = assemble(config)

        except Exception as e:
            logger.error(f"Error initializing LLM pipeline: {str(e)}", exc_info=True)
            self.llm_nlp = None

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze text with NLP pipeline.

        Args:
            text: The text to analyze

        Returns:
            Dictionary with analysis results
        """
        if not self.basic_nlp:
            logger.error("NLP processor not initialized")
            return {"error": "NLP processor not initialized"}

        try:
            # Process with basic spaCy
            doc = self.basic_nlp(text)

            # Extract basic entities and keywords
            entities = [
                {
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                }
                for ent in doc.ents
            ]

            keywords = [
                token.text
                for token in doc
                if not token.is_stop and not token.is_punct and token.is_alpha
            ]

            result = {
                "entities": entities,
                "keywords": keywords[:10],  # Top 10 keywords
                "sentiment": self._get_sentiment(doc),
                "subject": self._extract_subject(doc),
            }

            # Add LLM classification if available
            if self.llm_enabled and self.llm_nlp:
                result["llm_classification"] = self._classify_with_llm(text)

            return result

        except Exception as e:
            logger.error(f"Error analyzing text: {str(e)}", exc_info=True)
            return {"error": str(e)}

    def _get_sentiment(self, doc: Doc) -> Dict[str, float]:
        """
        Get sentiment scores from spaCy document.

        Args:
            doc: spaCy document

        Returns:
            Dictionary with sentiment scores
        """
        # Simple rule-based sentiment
        positive_words = 0
        negative_words = 0

        for token in doc:
            if token.pos_ in ["ADJ", "VERB", "ADV"]:
                # This is a simple approach - a real implementation would use
                # a more sophisticated sentiment lexicon
                if token.text.lower() in [
                    "good",
                    "great",
                    "excellent",
                    "happy",
                    "interested",
                ]:
                    positive_words += 1
                elif token.text.lower() in ["bad", "poor", "unhappy", "disappointed"]:
                    negative_words += 1

        total = max(1, positive_words + negative_words)
        positive_score = positive_words / total
        negative_score = negative_words / total

        return {
            "positive": positive_score,
            "negative": negative_score,
            "neutral": 1.0 - (positive_score + negative_score),
        }

    def _extract_subject(self, doc: Doc) -> str:
        """
        Extract the subject of the message.

        Args:
            doc: spaCy document

        Returns:
            Extracted subject or empty string
        """
        # Simple subject extraction - find the first noun chunk
        for chunk in doc.noun_chunks:
            if chunk.root.dep_ in ["nsubj", "nsubjpass"]:
                return chunk.text

        # Fallback to first noun chunk
        for chunk in doc.noun_chunks:
            return chunk.text

        return ""

    def _classify_with_llm(self, text: str) -> Dict[str, float]:
        """
        Classify text using LLM integration.

        Args:
            text: The text to classify

        Returns:
            Dictionary with classification scores
        """
        try:
            # Check if llm_nlp is None before calling it
            if self.llm_nlp is None:
                logger.warning("LLM NLP model not initialized")
                return {}

            doc = self.llm_nlp(text)

            # Extract classification scores
            cats = doc.cats

            return cats

        except Exception as e:
            logger.error(f"Error classifying with LLM: {str(e)}", exc_info=True)
            return {}

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from text.

        Args:
            text: Input text to analyze

        Returns:
            Dictionary of entity types and their values
        """
        try:
            doc = self.basic_nlp(text)
            entities: Dict[str, Any] = {}

            for ent in doc.ents:
                if ent.label_ not in entities:
                    entities[ent.label_] = []

                entities[ent.label_].append(ent.text)

            return entities

        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}", exc_info=True)
            return {}

    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of text.

        Args:
            text: Input text to analyze

        Returns:
            Dictionary with sentiment metrics
        """
        try:
            doc = self.basic_nlp(text)

            # Note: Basic spaCy models don't include sentiment
            # This requires the TextBlob extension or custom logic
            # For this example, we'll assume the doc has a polarity score
            polarity = getattr(doc._, "polarity", 0.0)

            return {
                "polarity": polarity,
                "is_positive": polarity > 0.1,
                "is_negative": polarity < -0.1,
            }

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}", exc_info=True)
            return {"polarity": 0.0, "is_positive": False, "is_negative": False}

    def analyze_message(self, text: str) -> Dict[str, Any]:
        """
        Perform comprehensive analysis on a message.

        Args:
            text: Input text to analyze

        Returns:
            Dictionary with analysis results
        """
        results = {
            "entities": self.extract_entities(text),
            "sentiment": self.analyze_sentiment(text),
            "intent": "unknown",
            "confidence": 0.0,
        }

        # Use LLM for intent classification if enabled
        if self.llm_enabled:
            # Implement LLM-based intent classification
            pass
        else:
            # Simple rule-based intent classification
            results.update(self._rule_based_intent(text))

        return results

    def _rule_based_intent(self, text: str) -> Dict[str, Any]:
        """Classify intent, based on rules."""
        text_lower = text.lower()

        # Interview request patterns
        interview_patterns = [
            "interview",
            "schedule",
            "meet",
            "meeting",
            "call",
            "chat",
            "availability",
            "available",
            "discuss",
        ]

        # Follow-up patterns
        follow_up_patterns = [
            "follow up",
            "following up",
            "checking in",
            "status",
            "update",
        ]

        # Job offer patterns
        offer_patterns = ["offer", "pleased to", "happy to", "position", "job", "role"]

        # Count matches for each intent
        interview_matches = sum(1 for p in interview_patterns if p in text_lower)
        follow_up_matches = sum(1 for p in follow_up_patterns if p in text_lower)
        offer_matches = sum(1 for p in offer_patterns if p in text_lower)

        # Determine the most likely intent
        max_matches = max(interview_matches, follow_up_matches, offer_matches)
        confidence = min(max_matches * 0.2, 0.9)  # Scale confidence, max 0.9

        if max_matches == 0:
            return {"intent": "unknown", "confidence": 0.0}
        elif interview_matches == max_matches:
            return {"intent": "interview_request", "confidence": confidence}
        elif follow_up_matches == max_matches:
            return {"intent": "follow_up", "confidence": confidence}
        elif offer_matches == max_matches:
            return {"intent": "job_offer", "confidence": confidence}
        else:
            return {"intent": "unknown", "confidence": 0.0}

    def process_text(self, text: str) -> Dict[str, Any]:
        """
        Process text with NLP pipeline.

        Args:
            text: The text to process

        Returns:
            Dictionary with analysis results
        """
        if self.client is None:
            logger.warning("NLP client is not initialized")
            return {"error": "NLP client not initialized"}

        try:
            response = self.client.some_method(text)  # Replace with actual method call
            return response
        except Exception as e:
            logger.error(f"Error processing text: {str(e)}", exc_info=True)
            return {"error": str(e)}
