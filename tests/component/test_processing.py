"""Tests for processing modules."""

import pytest
from unittest.mock import MagicMock, patch

from src.processing.nlp_processor import NLPProcessor
from src.processing.message_classifier import MessageClassifier


class TestNLPProcessor:
    """Tests for NLPProcessor class."""

    @pytest.fixture
    def nlp_processor(self):
        """Create a NLP processor for testing with mocked spaCy."""
        with patch("spacy.load") as mock_load:
            # Create a simple mock for the spaCy model
            mock_nlp = MagicMock()
            mock_doc = MagicMock()
            mock_nlp.return_value = mock_doc
            mock_load.return_value = mock_nlp

            # Disable LLM for testing
            with patch.dict("os.environ", {"ENABLE_LLM": "false"}):
                processor = NLPProcessor()
                return processor

    def test_initialization(self, nlp_processor):
        """Test initialization of NLP processor."""
        assert nlp_processor.basic_nlp is not None
        assert nlp_processor.llm_enabled is False

    def test_extract_entities(self, nlp_processor):
        """Test entity extraction."""
        # Mock the behavior of extract_entities
        mock_doc = MagicMock()
        mock_ent1 = MagicMock()
        mock_ent1.text = "Google"
        mock_ent1.label_ = "ORG"
        mock_ent2 = MagicMock()
        mock_ent2.text = "John Smith"
        mock_ent2.label_ = "PERSON"

        mock_doc.ents = [mock_ent1, mock_ent2]
        nlp_processor.basic_nlp.return_value = mock_doc

        # Test
        entities = nlp_processor.extract_entities("Google is hiring John Smith.")

        # Assertions
        assert len(entities) == 2
        assert entities["ORG"] == ["Google"]
        assert entities["PERSON"] == ["John Smith"]

    def test_analyze_sentiment(self, nlp_processor):
        """Test sentiment analysis."""
        # Mock the sentiment analysis
        mock_doc = MagicMock()
        mock_doc._.polarity = 0.8
        nlp_processor.basic_nlp.return_value = mock_doc

        # Test
        sentiment = nlp_processor.analyze_sentiment("I am very happy about this opportunity!")

        # Assertions
        assert isinstance(sentiment, dict)
        assert "polarity" in sentiment
        assert sentiment["polarity"] == 0.8


class TestMessageClassifier:
    """Tests for MessageClassifier class."""

    @pytest.fixture
    def message_classifier(self):
        """Create a message classifier for testing."""
        nlp_processor = MagicMock()
        return MessageClassifier(nlp_processor)

    def test_classify_interview_request(self, message_classifier):
        """Test classification of interview request messages."""
        # Test various interview request messages
        texts = [
            "Would you be available for an interview next week?",
            "I'd like to schedule a call to discuss this role further.",
            "Let's set up a meeting to talk about your application.",
            "Are you available for a chat about the position?",
            "Can we arrange an interview for the software engineer role?",
        ]

        for text in texts:
            # Mock the NLP processor
            message_classifier.nlp.analyze_message.return_value = {
                "intent": "interview_request",
                "confidence": 0.9,
            }

            # Test
            intent = message_classifier.classify(text)

            # Assertions
            assert intent == "interview_request"

    def test_classify_follow_up(self, message_classifier):
        """Test classification of follow-up messages."""
        # Test follow-up messages
        texts = [
            "Just following up on my application.",
            "I'm checking in about the status of my application.",
            "Any updates on the position I applied for?",
            "Just wanted to follow up on our conversation last week.",
        ]

        for text in texts:
            # Mock the NLP processor
            message_classifier.nlp.analyze_message.return_value = {
                "intent": "follow_up",
                "confidence": 0.85,
            }

            # Test
            intent = message_classifier.classify(text)

            # Assertions
            assert intent == "follow_up"

    def test_classify_job_offer(self, message_classifier):
        """Test classification of job offer messages."""
        # Test job offer messages
        texts = [
            "We are pleased to offer you the position.",
            "I'm happy to extend an offer for the role.",
            "We would like to offer you the job at our company.",
            "Congratulations! We're offering you the position.",
        ]

        for text in texts:
            # Mock the NLP processor
            message_classifier.nlp.analyze_message.return_value = {
                "intent": "job_offer",
                "confidence": 0.95,
            }

            # Test
            intent = message_classifier.classify(text)

            # Assertions
            assert intent == "job_offer"
