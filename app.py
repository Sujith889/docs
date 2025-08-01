
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import json
from datetime import datetime
import re
import PyPDF2
import docx
from werkzeug.utils import secure_filename
import spacy
from transformers import pipeline
import pandas as pd
from collections import Counter
import hashlib

app = Flask(__name__)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure uploads directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize NLP models (you'll need to install these)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Please install spaCy English model: python -m spacy download en_core_web_sm")
    nlp = None

# Initialize sentiment analysis pipeline
try:
    sentiment_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
except Exception as e:
    print(f"Error initializing transformers: {e}")
    sentiment_analyzer = None
    summarizer = None

class LegalDocumentAnalyzer:
    def __init__(self):
        self.clause_patterns = {
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

        self.risk_keywords = {
            'high': ['penalty', 'breach', 'default', 'liquidated damages', 'forfeit', 'void', 'null'],
            'medium': ['may', 'discretion', 'reasonable', 'commercially reasonable', 'best efforts'],
            'low': ['shall', 'will', 'must', 'required', 'mandatory']
        }

        self.boilerplate_patterns = [
            r'this agreement shall be governed by',
            r'entire agreement',
            r'severability',
            r'no waiver',
            r'counterparts',
            r'headings are for convenience only'
        ]

    def extract_text_from_file(self, file_path):
        """Extract text from various file formats"""
        _, ext = os.path.splitext(file_path.lower())

        try:
            if ext == '.pdf':
                return self._extract_pdf_text(file_path)
            elif ext == '.docx':
                return self._extract_docx_text(file_path)
            elif ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return "Unsupported file format"
        except Exception as e:
            return f"Error extracting text: {str(e)}"

    def _extract_pdf_text(self, file_path):
        """Extract text from PDF"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            text = f"Error reading PDF: {str(e)}"
        return text

    def _extract_docx_text(self, file_path):
        """Extract text from DOCX"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            return f"Error reading DOCX: {str(e)}"

    def classify_clauses(self, text):
        """Classify clauses in the document"""
        clauses = []
        sentences = text.split('.')

        for i, sentence in enumerate(sentences):
            if len(sentence.strip()) < 20:  # Skip very short sentences
                continue

            clause_types = []
            sentence_lower = sentence.lower()

            for clause_type, patterns in self.clause_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, sentence_lower):
                        clause_types.append(clause_type)
                        break

            if clause_types:
                risk_level = self._assess_risk_level(sentence)
                importance_score = self._calculate_importance_score(sentence, clause_types)

                clauses.append({
                    'id': i,
                    'text': sentence.strip(),
                    'types': clause_types,
                    'risk_level': risk_level,
                    'importance_score': importance_score,
                    'position': i
                })

        return clauses

    def _assess_risk_level(self, text):
        """Assess risk level of a clause"""
        text_lower = text.lower()

        high_risk_count = sum(1 for keyword in self.risk_keywords['high'] if keyword in text_lower)
        medium_risk_count = sum(1 for keyword in self.risk_keywords['medium'] if keyword in text_lower)
        low_risk_count = sum(1 for keyword in self.risk_keywords['low'] if keyword in text_lower)

        if high_risk_count > 0:
            return 'high'
        elif medium_risk_count > low_risk_count:
            return 'medium'
        else:
            return 'low'

    def _calculate_importance_score(self, text, clause_types):
        """Calculate importance score (1-10)"""
        base_score = 5

        # Adjust based on clause types
        important_types = ['liability', 'payment', 'termination', 'intellectual_property']
        for clause_type in clause_types:
            if clause_type in important_types:
                base_score += 2

        # Adjust based on text length and complexity
        if len(text) > 200:
            base_score += 1

        # Adjust based on legal keywords
        legal_keywords = ['shall', 'liable', 'damages', 'breach', 'default']
        keyword_count = sum(1 for keyword in legal_keywords if keyword.lower() in text.lower())
        base_score += min(keyword_count, 3)

        return min(base_score, 10)

    def extract_timeline_info(self, text):
        """Extract dates, deadlines, and durations"""
        timeline_info = []

        # Date patterns
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            r'\b\d{1,2}-\d{1,2}-\d{4}\b',
            r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            r'\b\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b'
        ]

        # Duration patterns
        duration_patterns = [
            r'\b\d+\s+(days?|weeks?|months?|years?)\b',
            r'\b(within|after|before)\s+\d+\s+(days?|weeks?|months?|years?)\b',
            r'\b\d+\s+(day|week|month|year)\s+(period|term)\b'
        ]

        sentences = text.split('.')

        for i, sentence in enumerate(sentences):
            sentence_timeline = {
                'sentence_id': i,
                'text': sentence.strip(),
                'dates': [],
                'durations': [],
                'deadlines': []
            }

            # Find dates
            for pattern in date_patterns:
                matches = re.findall(pattern, sentence, re.IGNORECASE)
                sentence_timeline['dates'].extend(matches)

            # Find durations
            for pattern in duration_patterns:
                matches = re.findall(pattern, sentence, re.IGNORECASE)
                sentence_timeline['durations'].extend(matches)

            # Find deadline keywords
            deadline_keywords = ['deadline', 'due date', 'expiry', 'termination date', 'completion date']
            for keyword in deadline_keywords:
                if keyword.lower() in sentence.lower():
                    sentence_timeline['deadlines'].append(keyword)

            if sentence_timeline['dates'] or sentence_timeline['durations'] or sentence_timeline['deadlines']:
                timeline_info.append(sentence_timeline)

        return timeline_info

    def detect_boilerplate(self, text):
        """Detect boilerplate clauses"""
        boilerplate_clauses = []
        sentences = text.split('.')

        for i, sentence in enumerate(sentences):
            sentence_lower = sentence.lower()

            for pattern in self.boilerplate_patterns:
                if re.search(pattern, sentence_lower):
                    boilerplate_clauses.append({
                        'id': i,
                        'text': sentence.strip(),
                        'pattern_matched': pattern,
                        'confidence': 0.8
                    })
                    break

        return boilerplate_clauses

    def analyze_tone(self, text):
        """Analyze tone of the document"""
        if not sentiment_analyzer:
            return {
                'overall_sentiment': 'neutral',
                'formality_score': 7,
                'assertiveness_score': 5,
                'risk_tone': 'moderate'
            }

        # Basic tone analysis
        sentences = text.split('.')[:10]  # Analyze first 10 sentences for performance

        formal_indicators = ['shall', 'hereby', 'whereas', 'pursuant', 'notwithstanding']
        assertive_indicators = ['must', 'required', 'mandatory', 'obligation', 'duty']
        risky_indicators = ['penalty', 'breach', 'default', 'terminate', 'void']

        formality_score = 0
        assertiveness_score = 0
        risk_tone_score = 0

        for sentence in sentences:
            sentence_lower = sentence.lower()

            formality_score += sum(1 for indicator in formal_indicators if indicator in sentence_lower)
            assertiveness_score += sum(1 for indicator in assertive_indicators if indicator in sentence_lower)
            risk_tone_score += sum(1 for indicator in risky_indicators if indicator in sentence_lower)

        # Normalize scores
        max_score = len(sentences)
        formality_score = min((formality_score / max_score) * 10, 10)
        assertiveness_score = min((assertiveness_score / max_score) * 10, 10)

        risk_tone = 'low' if risk_tone_score < 2 else 'moderate' if risk_tone_score < 5 else 'high'

        return {
            'overall_sentiment': 'formal',
            'formality_score': round(formality_score, 1),
            'assertiveness_score': round(assertiveness_score, 1),
            'risk_tone': risk_tone
        }

    def generate_rewriting_suggestions(self, clauses):
        """Generate suggestions for rewriting risky or unclear clauses"""
        suggestions = []

        for clause in clauses:
            if clause['risk_level'] == 'high' or clause['importance_score'] >= 8:
                suggestion = {
                    'clause_id': clause['id'],
                    'original_text': clause['text'],
                    'issues': [],
                    'suggestions': []
                }

                text_lower = clause['text'].lower()

                # Check for common issues
                if 'may' in text_lower:
                    suggestion['issues'].append('Ambiguous language - "may" creates uncertainty')
                    suggestion['suggestions'].append('Replace "may" with "shall" or "will" for clarity')

                if 'reasonable' in text_lower and 'commercially reasonable' not in text_lower:
                    suggestion['issues'].append('Vague standard - "reasonable" is subjective')
                    suggestion['suggestions'].append('Define specific criteria for what constitutes "reasonable"')

                if len(clause['text']) > 300:
                    suggestion['issues'].append('Overly complex sentence structure')
                    suggestion['suggestions'].append('Break into shorter, clearer sentences')

                if any(word in text_lower for word in ['penalty', 'forfeit', 'liquidated damages']):
                    suggestion['issues'].append('High financial risk language')
                    suggestion['suggestions'].append('Consider adding caps or limitations on penalties')

                if suggestion['issues']:
                    suggestions.append(suggestion)

        return suggestions

    def compare_documents(self, doc1_text, doc2_text):
        """Compare two documents and highlight differences"""
        doc1_clauses = self.classify_clauses(doc1_text)
        doc2_clauses = self.classify_clauses(doc2_text)

        comparison = {
            'doc1_unique_clauses': [],
            'doc2_unique_clauses': [],
            'common_clauses': [],
            'differences': []
        }

        # Simple comparison based on clause types
        doc1_types = set()
        doc2_types = set()

        for clause in doc1_clauses:
            for clause_type in clause['types']:
                doc1_types.add(clause_type)

        for clause in doc2_clauses:
            for clause_type in clause['types']:
                doc2_types.add(clause_type)

        comparison['doc1_unique_types'] = list(doc1_types - doc2_types)
        comparison['doc2_unique_types'] = list(doc2_types - doc1_types)
        comparison['common_types'] = list(doc1_types & doc2_types)

        return comparison

# Initialize analyzer
analyzer = LegalDocumentAnalyzer()

@app.route('/')
def index():
    return "ClauseWise Legal Document Analyzer API - Backend is running!"

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Extract text
        text = analyzer.extract_text_from_file(file_path)

        return jsonify({
            'filename': filename,
            'text_preview': text[:500] + '...' if len(text) > 500 else text,
            'file_id': hashlib.md5(filename.encode()).hexdigest()
        })

@app.route('/api/analyze', methods=['POST'])
def analyze_document():
    data = request.json
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        # Perform all analyses
        clauses = analyzer.classify_clauses(text)
        timeline_info = analyzer.extract_timeline_info(text)
        boilerplate_clauses = analyzer.detect_boilerplate(text)
        tone_analysis = analyzer.analyze_tone(text)
        rewriting_suggestions = analyzer.generate_rewriting_suggestions(clauses)

        # Generate summary statistics
        risk_distribution = Counter(clause['risk_level'] for clause in clauses)
        clause_type_distribution = Counter()
        for clause in clauses:
            for clause_type in clause['types']:
                clause_type_distribution[clause_type] += 1

        analysis_result = {
            'clauses': clauses,
            'timeline_info': timeline_info,
            'boilerplate_clauses': boilerplate_clauses,
            'tone_analysis': tone_analysis,
            'rewriting_suggestions': rewriting_suggestions,
            'statistics': {
                'total_clauses': len(clauses),
                'risk_distribution': dict(risk_distribution),
                'clause_type_distribution': dict(clause_type_distribution),
                'avg_importance_score': round(sum(c['importance_score'] for c in clauses) / len(clauses), 2) if clauses else 0
            }
        }

        return jsonify(analysis_result)

    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/compare', methods=['POST'])
def compare_documents():
    data = request.json
    doc1_text = data.get('doc1_text', '')
    doc2_text = data.get('doc2_text', '')

    if not doc1_text or not doc2_text:
        return jsonify({'error': 'Both documents required for comparison'}), 400

    try:
        comparison_result = analyzer.compare_documents(doc1_text, doc2_text)
        return jsonify(comparison_result)

    except Exception as e:
        return jsonify({'error': f'Comparison failed: {str(e)}'}), 500

@app.route('/api/watson-nlu', methods=['POST'])
def watson_nlu_analysis():
    """Placeholder for IBM Watson NLU integration"""
    data = request.json
    text = data.get('text', '')

    # This would integrate with IBM Watson NLU
    # For now, return mock data
    mock_nlu_result = {
        'entities': [
            {'text': 'Contract', 'type': 'Legal Document', 'confidence': 0.95},
            {'text': 'Payment Terms', 'type': 'Legal Clause', 'confidence': 0.88}
        ],
        'keywords': [
            {'text': 'liability', 'relevance': 0.92},
            {'text': 'termination', 'relevance': 0.85},
            {'text': 'payment', 'relevance': 0.78}
        ],
        'sentiment': {
            'document': {'score': 0.1, 'label': 'neutral'}
        },
        'summary': 'This legal document contains standard contractual clauses with moderate risk levels.'
    }

    return jsonify(mock_nlu_result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
