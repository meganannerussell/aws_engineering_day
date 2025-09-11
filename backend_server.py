#!/usr/bin/env python3
"""
Flask Backend Server for Smart Text Analytics Dashboard
AWS Engineering Day Hackathon 2024

This server provides API endpoints to process datasets using the text analytics pipeline.
"""

import os
import json
import logging
import hashlib
import tempfile
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from text_analytics_pipeline import TextAnalyticsPipeline

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize the text analytics pipeline
pipeline = None

# Cache directory for storing analysis results
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_key(dataset_path):
    """Generate a cache key based on dataset file path and modification time"""
    stat = os.stat(dataset_path)
    # Include file path and modification time in the hash
    key_data = f"{dataset_path}:{stat.st_mtime}:{stat.st_size}"
    return hashlib.md5(key_data.encode()).hexdigest()

def get_cached_result(dataset_name):
    """Check if we have a cached result for this dataset"""
    cache_key = get_cache_key(os.path.join('sample_data', dataset_name))
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            logger.info(f"📦 Using cached result for {dataset_name}")
            return cached_data
        except Exception as e:
            logger.warning(f"⚠️ Failed to load cached result: {e}")
            return None
    return None

def cache_result(dataset_name, result):
    """Cache the analysis result"""
    cache_key = get_cache_key(os.path.join('sample_data', dataset_name))
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
    
    try:
        with open(cache_file, 'w') as f:
            json.dump(result, f, indent=2)
        logger.info(f"💾 Cached result for {dataset_name}")
    except Exception as e:
        logger.warning(f"⚠️ Failed to cache result: {e}")

def initialize_pipeline():
    """Initialize the text analytics pipeline"""
    global pipeline
    try:
        pipeline = TextAnalyticsPipeline()
        logger.info("✅ Text Analytics Pipeline initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize pipeline: {e}")
        return False

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'pipeline_initialized': pipeline is not None,
        'available_datasets': get_available_datasets()
    })

@app.route('/api/datasets', methods=['GET'])
def get_datasets():
    """Get list of available datasets"""
    return jsonify({
        'datasets': get_available_datasets()
    })

def get_available_datasets():
    """Get list of available CSV datasets"""
    sample_data_dir = 'sample_data'
    datasets = []
    
    if os.path.exists(sample_data_dir):
        for filename in os.listdir(sample_data_dir):
            if filename.endswith('.csv'):
                datasets.append({
                    'filename': filename,
                    'name': filename.replace('.csv', '').replace('_', ' ').title(),
                    'path': os.path.join(sample_data_dir, filename)
                })
    
    return datasets

@app.route('/api/analyze', methods=['POST'])
def analyze_dataset():
    """Analyze a dataset using the text analytics pipeline"""
    try:
        data = request.get_json()
        dataset_name = data.get('dataset')
        force_fresh = data.get('force_fresh', False)
        
        if not dataset_name:
            return jsonify({'error': 'Dataset name is required'}), 400
        
        if not pipeline:
            return jsonify({'error': 'Pipeline not initialized'}), 500
        
        # Find the dataset file
        dataset_path = None
        for dataset in get_available_datasets():
            if dataset['filename'] == dataset_name:
                dataset_path = dataset['path']
                break
        
        if not dataset_path or not os.path.exists(dataset_path):
            return jsonify({'error': f'Dataset {dataset_name} not found'}), 404
        
        # Check if we have a cached result (only if not forcing fresh)
        if not force_fresh:
            cached_result = get_cached_result(dataset_name)
            if cached_result:
                logger.info(f"📋 Returning cached result for {dataset_name}")
                return jsonify(cached_result)
        
        logger.info(f"🔬 Starting analysis of {dataset_name}")
        
        # Process the dataset
        results = pipeline.process_survey(dataset_path, max_responses=250)
        
        # Cache the result
        cache_result(dataset_name, results)
        
        logger.info(f"✅ Analysis completed for {dataset_name}")
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-upload', methods=['POST'])
def analyze_uploaded_file():
    """Analyze an uploaded CSV file using the text analytics pipeline"""
    try:
        # Check if file is present in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        if not file.filename.lower().endswith('.csv'):
            return jsonify({'error': 'Only CSV files are allowed'}), 400
        
        if not pipeline:
            return jsonify({'error': 'Pipeline not initialized'}), 500
        
        # Save uploaded file to temporary location
        filename = secure_filename(file.filename)
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, filename)
        file.save(temp_path)
        
        logger.info(f"📁 Uploaded file saved to: {temp_path}")
        
        # Get force_fresh parameter from form data
        force_fresh = request.form.get('force_fresh', 'false').lower() == 'true'
        
        # Generate cache key for uploaded file
        cache_key = get_cache_key(temp_path)
        cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
        
        # Check if we have a cached result for this exact file (only if not forcing fresh)
        if not force_fresh and os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                logger.info(f"📦 Using cached result for uploaded file {filename}")
                # Clean up temp file
                os.remove(temp_path)
                os.rmdir(temp_dir)
                return jsonify(cached_data)
            except Exception as e:
                logger.warning(f"⚠️ Failed to load cached result: {e}")
        
        logger.info(f"🔬 Starting analysis of uploaded file: {filename}")
        
        # Process the uploaded file
        results = pipeline.process_survey(temp_path, max_responses=250)
        
        # Cache the result
        try:
            with open(cache_file, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"💾 Cached result for uploaded file {filename}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to cache result: {e}")
        
        # Clean up temp file
        os.remove(temp_path)
        os.rmdir(temp_dir)
        
        logger.info(f"✅ Analysis completed for uploaded file: {filename}")
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"❌ Upload analysis failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze/<dataset_name>', methods=['GET'])
def analyze_dataset_get(dataset_name):
    """Analyze a dataset via GET request (for testing)"""
    return analyze_dataset()

if __name__ == '__main__':
    # Initialize the pipeline
    if initialize_pipeline():
        logger.info("🚀 Starting Flask backend server...")
        logger.info("📊 Available datasets:")
        for dataset in get_available_datasets():
            logger.info(f"  - {dataset['name']} ({dataset['filename']})")
        
        # Run the Flask server
        app.run(
            host='0.0.0.0',
            port=5002,
            debug=True,
            threaded=True
        )
    else:
        logger.error("❌ Failed to start server - pipeline initialization failed")
        exit(1)
