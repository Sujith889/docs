#!/bin/bash

echo "🚀 Setting up ClauseWise Legal Document Analyzer..."

# Create virtual environment
python3 -m venv clausewise_env
source clausewise_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm

# Create uploads directory
mkdir -p uploads

echo "✅ Setup complete!"
echo ""
echo "To run the application:"
echo "1. Activate virtual environment: source clausewise_env/bin/activate"
echo "2. Run the app: python app.py"
echo "3. Open frontend HTML file in browser"
echo "4. Backend API will be available at http://localhost:5000"
