"""
Configuration file for ClauseWise Legal Document Analyzer
"""

import os
from typing import Dict, Any

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clausewise-hackathon-2024'
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # IBM Watson NLU Configuration
    WATSON_NLU_APIKEY = os.environ.get('WATSON_NLU_APIKEY') or 'your-watson-api-key'
    WATSON_NLU_URL = os.environ.get('WATSON_NLU_URL') or 'https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/your-instance-id'

    # AI Model Configuration
    SPACY_MODEL = 'en_core_web_sm'
    TRANSFORMERS_CACHE_DIR = './models_cache'

    # Risk Assessment Thresholds
    RISK_THRESHOLDS = {
        'high_risk_score': 8,
        'medium_risk_score': 5,
        'importance_threshold': 7
    }

    # Clause Classification Patterns
    CLAUSE_PATTERNS = {
        'payment': [r'payment', r'fee', r'cost', r'price', r'remuneration', r'compensation'],
        'termination': [r'terminate', r'end', r'expire', r'cancel', r'dissolution'],
        'liability': [r'liable', r'liability', r'responsible', r'damages', r'loss'],
        'confidentiality': [r'confidential', r'non-disclosure', r'proprietary', r'trade secret'],
        'intellectual_property': [r'copyright', r'patent', r'trademark', r'intellectual property', r'IP'],
        'warranty': [r'warrant', r'guarantee', r'representation', r'condition'],
        'dispute_resolution': [r'dispute', r'arbitration', r'mediation', r'court', r'jurisdiction'],
        'force_majeure': [r'force majeure', r'act of god', r'unforeseeable', r'beyond control'],
        'governing_law': [r'governing law', r'applicable law', r'jurisdiction', r'venue'],
        'amendment': [r'amend', r'modify', r'change', r'alter', r'update']
    }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
