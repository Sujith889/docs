"""
IBM Watson NLU Integration Module for ClauseWise
"""

import os
import json
from typing import Dict, List, Any, Optional
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions, SentimentOptions, EmotionOptions
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core import ApiException

class WatsonNLUAnalyzer:
    """IBM Watson Natural Language Understanding integration"""

    def __init__(self, api_key: str, url: str):
        """Initialize Watson NLU service"""
        self.api_key = api_key
        self.url = url
        self.service = None
        self._initialize_service()

    def _initialize_service(self):
        """Initialize the Watson NLU service"""
        try:
            if self.api_key and self.api_key != 'your-watson-api-key':
                authenticator = IAMAuthenticator(self.api_key)
                self.service = NaturalLanguageUnderstandingV1(
                    version='2022-04-07',
                    authenticator=authenticator
                )
                self.service.set_service_url(self.url)
                print("✅ Watson NLU service initialized successfully")
            else:
                print("⚠️ Watson NLU API key not configured, using mock responses")
        except Exception as e:
            print(f"❌ Error initializing Watson NLU: {e}")
            self.service = None

    def analyze_legal_document(self, text: str) -> Dict[str, Any]:
        """Comprehensive analysis of legal document using Watson NLU"""
        if not self.service:
            return self._mock_analysis(text)

        try:
            # Truncate text if too long (Watson NLU has limits)
            if len(text) > 50000:
                text = text[:50000] + "..."

            response = self.service.analyze(
                text=text,
                features=Features(
                    entities=EntitiesOptions(limit=20, sentiment=True),
                    keywords=KeywordsOptions(limit=20, sentiment=True),
                    sentiment=SentimentOptions(document=True),
                    emotion=EmotionOptions(document=True)
                )
            ).get_result()

            return self._process_watson_response(response)

        except ApiException as e:
            print(f"Watson NLU API Error: {e}")
            return self._mock_analysis(text)
        except Exception as e:
            print(f"Error in Watson NLU analysis: {e}")
            return self._mock_analysis(text)

    def _process_watson_response(self, response: Dict) -> Dict[str, Any]:
        """Process Watson NLU response into legal-specific insights"""

        # Extract legal entities
        legal_entities = []
        if 'entities' in response:
            for entity in response['entities']:
                legal_entity = {
                    'text': entity['text'],
                    'type': entity['type'],
                    'confidence': entity['confidence'],
                    'sentiment': entity.get('sentiment', {}).get('label', 'neutral'),
                    'legal_relevance': self._assess_legal_relevance(entity['text'], entity['type'])
                }
                legal_entities.append(legal_entity)

        # Extract and categorize keywords
        legal_keywords = []
        if 'keywords' in response:
            for keyword in response['keywords']:
                legal_keyword = {
                    'text': keyword['text'],
                    'relevance': keyword['relevance'],
                    'sentiment': keyword.get('sentiment', {}).get('label', 'neutral'),
                    'legal_category': self._categorize_legal_keyword(keyword['text'])
                }
                legal_keywords.append(legal_keyword)

        # Document-level sentiment and emotion
        document_sentiment = response.get('sentiment', {}).get('document', {})
        document_emotion = response.get('emotion', {}).get('document', {}).get('emotion', {})

        # Generate legal-specific summary
        summary = self._generate_legal_summary(legal_entities, legal_keywords, document_sentiment)

        return {
            'entities': legal_entities,
            'keywords': legal_keywords,
            'sentiment': {
                'score': document_sentiment.get('score', 0),
                'label': document_sentiment.get('label', 'neutral'),
                'legal_tone_assessment': self._assess_legal_tone(document_sentiment)
            },
            'emotion': document_emotion,
            'summary': summary,
            'risk_indicators': self._identify_risk_indicators(legal_entities, legal_keywords),
            'compliance_flags': self._identify_compliance_flags(legal_entities, legal_keywords)
        }

    def _assess_legal_relevance(self, text: str, entity_type: str) -> str:
        """Assess legal relevance of an entity"""
        legal_entity_types = ['Person', 'Organization', 'Location', 'Money', 'Date']
        legal_terms = ['contract', 'agreement', 'liability', 'damages', 'breach', 'termination']

        if entity_type in legal_entity_types:
            return 'high'
        elif any(term in text.lower() for term in legal_terms):
            return 'high'
        else:
            return 'medium'

    def _categorize_legal_keyword(self, keyword: str) -> str:
        """Categorize keywords into legal categories"""
        categories = {
            'risk': ['risk', 'liability', 'damages', 'penalty', 'breach', 'default'],
            'obligations': ['shall', 'must', 'required', 'obligation', 'duty', 'responsibility'],
            'financial': ['payment', 'fee', 'cost', 'price', 'compensation', 'remuneration'],
            'temporal': ['term', 'duration', 'deadline', 'expiry', 'termination'],
            'legal_process': ['court', 'arbitration', 'mediation', 'jurisdiction', 'governing law']
        }

        keyword_lower = keyword.lower()
        for category, terms in categories.items():
            if any(term in keyword_lower for term in terms):
                return category

        return 'general'

    def _assess_legal_tone(self, sentiment: Dict) -> str:
        """Assess legal tone based on sentiment"""
        score = sentiment.get('score', 0)
        label = sentiment.get('label', 'neutral')

        if label == 'positive' and score > 0.5:
            return 'collaborative'
        elif label == 'negative' and score < -0.5:
            return 'adversarial'
        else:
            return 'formal_neutral'

    def _identify_risk_indicators(self, entities: List[Dict], keywords: List[Dict]) -> List[str]:
        """Identify potential risk indicators"""
        risk_indicators = []

        # Check for high-risk keywords
        high_risk_terms = ['penalty', 'liquidated damages', 'breach', 'default', 'termination', 'void']
        for keyword in keywords:
            if any(term in keyword['text'].lower() for term in high_risk_terms):
                risk_indicators.append(f"High-risk term detected: {keyword['text']}")

        # Check for negative sentiment entities
        for entity in entities:
            if entity.get('sentiment') == 'negative' and entity.get('legal_relevance') == 'high':
                risk_indicators.append(f"Negative sentiment on legal entity: {entity['text']}")

        return risk_indicators

    def _identify_compliance_flags(self, entities: List[Dict], keywords: List[Dict]) -> List[str]:
        """Identify potential compliance issues"""
        compliance_flags = []

        # Check for regulatory terms
        regulatory_terms = ['regulation', 'compliance', 'gdpr', 'privacy', 'data protection']
        for keyword in keywords:
            if any(term in keyword['text'].lower() for term in regulatory_terms):
                compliance_flags.append(f"Regulatory term detected: {keyword['text']}")

        return compliance_flags

    def _generate_legal_summary(self, entities: List[Dict], keywords: List[Dict], sentiment: Dict) -> str:
        """Generate a legal-focused summary"""
        high_relevance_entities = [e for e in entities if e.get('legal_relevance') == 'high']
        risk_keywords = [k for k in keywords if k.get('legal_category') == 'risk']

        summary_parts = []

        if high_relevance_entities:
            summary_parts.append(f"Document contains {len(high_relevance_entities)} legally relevant entities")

        if risk_keywords:
            summary_parts.append(f"Identified {len(risk_keywords)} risk-related terms")

        tone = self._assess_legal_tone(sentiment)
        summary_parts.append(f"Overall legal tone is {tone}")

        return ". ".join(summary_parts) + "."

    def _mock_analysis(self, text: str) -> Dict[str, Any]:
        """Provide mock analysis when Watson NLU is not available"""
        return {
            'entities': [
                {'text': 'Contract Agreement', 'type': 'Legal Document', 'confidence': 0.95, 'sentiment': 'neutral', 'legal_relevance': 'high'},
                {'text': 'Payment Terms', 'type': 'Legal Clause', 'confidence': 0.88, 'sentiment': 'neutral', 'legal_relevance': 'high'},
                {'text': 'Liability Clause', 'type': 'Legal Clause', 'confidence': 0.82, 'sentiment': 'negative', 'legal_relevance': 'high'}
            ],
            'keywords': [
                {'text': 'liability', 'relevance': 0.92, 'sentiment': 'negative', 'legal_category': 'risk'},
                {'text': 'payment', 'relevance': 0.85, 'sentiment': 'neutral', 'legal_category': 'financial'},
                {'text': 'termination', 'relevance': 0.78, 'sentiment': 'negative', 'legal_category': 'temporal'},
                {'text': 'obligations', 'relevance': 0.75, 'sentiment': 'neutral', 'legal_category': 'obligations'}
            ],
            'sentiment': {
                'score': 0.1,
                'label': 'neutral',
                'legal_tone_assessment': 'formal_neutral'
            },
            'emotion': {
                'sadness': 0.2,
                'joy': 0.3,
                'fear': 0.4,
                'disgust': 0.1,
                'anger': 0.2
            },
            'summary': 'This legal document contains standard contractual clauses with moderate risk levels and formal neutral tone.',
            'risk_indicators': [
                'High-risk term detected: liability',
                'High-risk term detected: termination'
            ],
            'compliance_flags': []
        }

def create_watson_analyzer(api_key: str = None, url: str = None) -> WatsonNLUAnalyzer:
    """Factory function to create Watson NLU analyzer"""
    from config import Config

    api_key = api_key or Config.WATSON_NLU_APIKEY
    url = url or Config.WATSON_NLU_URL

    return WatsonNLUAnalyzer(api_key, url)
