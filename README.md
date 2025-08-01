# ClauseWise - Legal Document Analyzer

🏆 **Hackathon-Ready Legal AI Platform** - Advanced clause analysis with IBM Watson NLU integration

## 🚀 Features

### ✅ Core Features
- **Clause Extraction & Classification** - AI-powered identification of legal clauses
- **Risk & Obligation Highlighter** - Color-coded risk assessment with severity levels
- **IBM Watson NLU Integration** - Professional-grade text analysis and summarization
- **Contract Comparison** - Side-by-side document analysis with difference highlighting
- **Explainable Clause Insights** - Detailed explanations for each analysis result

### 💡 Unique Competitive Features
- **Clause Grading System** - Importance and risk scoring (1-10 scale)
- **Timeline Extractor** - Automatically detects dates, deadlines, and durations
- **Boilerplate Detector** - Identifies generic/copy-pasted legal text
- **Tone Analysis** - Analyzes formal, assertive, and risky language patterns
- **Clause Rewriting Suggestions** - AI-powered recommendations for improvement

## 📁 Project Structure

```
clausewise-legal-analyzer/
├── app.py                  # Main Flask application
├── config.py              # Configuration settings
├── watson_nlu.py          # IBM Watson NLU integration
├── requirements.txt       # Python dependencies
├── setup.sh               # Installation script
├── frontend.html          # Complete frontend interface
├── uploads/               # File upload directory (created on first run)
└── README.md             # This documentation
```

## 🛠 Tech Stack

- **Backend**: Python Flask with REST API
- **AI/ML**: IBM Watson NLU, spaCy, Transformers (BERT, BART)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **File Processing**: PyPDF2, python-docx
- **Data Analysis**: pandas, numpy

## ⚡ Quick Start

### 1. Clone/Download Files
Download all the Python files and the frontend HTML file to your project directory.

### 2. Setup Environment
```bash
# Make setup script executable
chmod +x setup.sh

# Run setup (creates virtual environment and installs dependencies)
./setup.sh
```

### 3. Configure IBM Watson NLU (Optional)
```bash
# Set environment variables for Watson NLU
export WATSON_NLU_APIKEY="your-watson-api-key"
export WATSON_NLU_URL="your-watson-service-url"

# Or edit config.py directly
```

### 4. Run the Application
```bash
# Activate virtual environment
source clausewise_env/bin/activate

# Start the Flask backend
python app.py
```

### 5. Open Frontend
- Open `frontend.html` in your web browser
- Backend API runs on `http://localhost:5000`

## 🎯 API Endpoints

### File Upload
```http
POST /api/upload
Content-Type: multipart/form-data

# Upload PDF, DOCX, or TXT files
```

### Document Analysis
```http
POST /api/analyze
Content-Type: application/json

{
  "text": "Your legal document text here..."
}
```

### Document Comparison
```http
POST /api/compare
Content-Type: application/json

{
  "doc1_text": "First document text...",
  "doc2_text": "Second document text..."
}
```

### Watson NLU Analysis
```http
POST /api/watson-nlu
Content-Type: application/json

{
  "text": "Document text for Watson analysis..."
}
```

## 🏆 Hackathon Demo Features

### Live Demo Capabilities
- **Real-time Analysis** - Upload and analyze documents instantly
- **Interactive Visualizations** - Charts, progress bars, risk indicators
- **Professional UI** - Modern, responsive design that impresses judges
- **Sample Documents** - Pre-loaded examples for quick demonstrations

### Presentation Points
1. **AI-Powered** - Multiple ML models working together
2. **Enterprise-Ready** - IBM Watson integration shows scalability
3. **Comprehensive** - Covers all aspects of legal document analysis
4. **User-Friendly** - Intuitive interface for non-technical users
5. **Innovative** - Unique features like boilerplate detection and clause rewriting

## 🔧 Customization

### Adding New Clause Types
Edit `config.py` and add new patterns to `CLAUSE_PATTERNS`:

```python
CLAUSE_PATTERNS = {
    'your_new_type': [r'pattern1', r'pattern2', r'pattern3'],
    # ... existing patterns
}
```

### Modifying Risk Assessment
Adjust risk keywords in the `LegalDocumentAnalyzer` class:

```python
self.risk_keywords = {
    'high': ['your', 'high', 'risk', 'terms'],
    'medium': ['medium', 'risk', 'terms'],
    'low': ['low', 'risk', 'terms']
}
```

## 📊 Analysis Features Explained

### Clause Classification
- Automatically identifies 10+ clause types
- Confidence scoring for each classification
- Support for overlapping clause types

### Risk Assessment
- 3-tier risk levels (High, Medium, Low)
- Keyword-based risk scoring
- Context-aware risk evaluation

### Timeline Extraction
- Date pattern recognition
- Duration parsing (days, weeks, months, years)
- Deadline keyword detection

### Tone Analysis
- Formality scoring (1-10)
- Assertiveness measurement
- Risk tone assessment

## 🚨 Troubleshooting

### Common Issues

**1. spaCy Model Not Found**
```bash
python -m spacy download en_core_web_sm
```

**2. Watson NLU Errors**
- Check API credentials in `config.py`
- Verify service URL format
- Application falls back to mock data if Watson is unavailable

**3. File Upload Issues**
- Ensure `uploads/` directory exists
- Check file size limits (16MB max)
- Verify file format support (PDF, DOCX, TXT)

**4. Memory Issues with Large Documents**
- Documents are automatically truncated for Watson NLU
- Consider implementing text chunking for very large files

## 🎪 Demo Script for Hackathon

### 2-Minute Demo Flow
1. **Upload Sample Contract** (30 seconds)
   - Show file upload interface
   - Demonstrate text extraction

2. **Live Analysis** (45 seconds)
   - Run complete analysis
   - Highlight key insights and visualizations

3. **Unique Features** (30 seconds)
   - Show timeline extraction
   - Demonstrate clause rewriting suggestions

4. **IBM Watson Integration** (15 seconds)
   - Show professional NLU analysis
   - Highlight enterprise readiness

## 📈 Scalability & Production

### Deployment Options
- **Heroku**: Easy deployment with `Procfile`
- **AWS/GCP**: Container-based deployment
- **Docker**: Included `Dockerfile` for containerization

### Performance Optimizations
- Async processing for large documents
- Redis caching for repeated analyses
- Database integration for document storage

## 🏅 Competitive Advantages

1. **Complete Solution** - End-to-end legal document analysis
2. **Enterprise Integration** - IBM Watson shows professional grade
3. **Unique Features** - Timeline extraction, boilerplate detection
4. **Modern Architecture** - RESTful API, responsive frontend
5. **Hackathon Ready** - Professional presentation, live demo capable

## 📝 License

MIT License - Free for hackathon use and further development.

## 🤝 Contributing

This is a hackathon project, but contributions and improvements are welcome!

---

**Built for hackathons, ready for production** 🚀

*Good luck with your hackathon! This platform demonstrates advanced AI capabilities while remaining accessible and impressive to judges.*
