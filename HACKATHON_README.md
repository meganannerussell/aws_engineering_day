# Smart Text Analytics Pipeline - Hackathon Demo

🚀 **AWS Engineering Day Hackathon Project**

A lightweight pipeline that transforms unstructured survey responses into actionable insights using AWS AI/ML services.

## What This Does

Takes messy open-ended survey responses like:
- "The music was great but the lines were too long"
- "I love the product quality but hate the price"
- "Amazing customer service experience!"

And produces:
- **Topics**: "Music Quality", "Wait Times", "Pricing", "Customer Service"
- **Sentiment**: Per-response and per-topic sentiment analysis
- **PII Safety**: Automatically detects and redacts sensitive information
- **Chart-Ready Output**: JSON format ready for visualization

## Architecture

- **PII Detection**: Amazon Comprehend
- **Text Embeddings**: Bedrock Titan Text Embeddings v2
- **Topic Labeling**: Bedrock Claude Sonnet
- **Sentiment Analysis**: Amazon Comprehend
- **Clustering**: UMAP + HDBSCAN (local processing)

## Quick Start

### 1. Setup Environment
```bash
# Make sure you're in the aws_engineering_day directory
cd aws_engineering_day

# Set AWS profile (should already be set for hackathon)
export AWS_PROFILE=platform-test-engineering-day

# Run setup script
python setup.py
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Pipeline
```bash
python smart_analytics_pipeline.py
```

This will:
- Process the first sample dataset (Beauty products survey)
- Generate topics and sentiment analysis
- Output results to `output_data_set_1.json`

## Sample Output

```json
{
  "project_metadata": {
    "project_title": "Ask Anything Beauty Demo",
    "total_responses": 156,
    "processing_time_seconds": 45.2
  },
  "topics": [
    {
      "topic_id": "topic_0",
      "label": "Product Quality",
      "count": 34,
      "sentiment_mean": 0.78,
      "examples": ["These products are high-quality...", "..."]
    },
    {
      "topic_id": "topic_1", 
      "label": "Skin Compatibility",
      "count": 28,
      "sentiment_mean": 0.65,
      "examples": ["It works on my skin type", "..."]
    }
  ],
  "responses": [
    {
      "response_id": "resp_0001",
      "original_text": "It works on my skin type",
      "clean_text": "It works on my skin type",
      "topic_assignment": {
        "topic_id": "topic_1",
        "topic_label": "Skin Compatibility"
      },
      "sentiment": {
        "sentiment": "POSITIVE",
        "confidence": 0.89
      },
      "pii_detected": false
    }
  ]
}
```

## Files Included

- `smart_analytics_pipeline.py` - Main pipeline script
- `setup.py` - Environment setup and AWS connectivity test
- `requirements.txt` - Python dependencies
- `sample_data/` - 6 sample datasets for testing
- `exampleScript.py` - Original Bedrock example (reference)

## Key Features for Hackathon

✅ **End-to-End Pipeline**: Complete workflow from raw text to insights
✅ **Multi-Service Architecture**: Uses 3 different AWS AI services appropriately
✅ **PII Safety**: Automatically redacts sensitive information
✅ **Robust Error Handling**: Graceful degradation if services fail
✅ **Scalable Design**: Async-ready, can handle 100-4000 responses
✅ **Chart-Ready Output**: JSON format perfect for visualization

## Customization

The pipeline is designed to work with any CSV format containing open-ended responses. Simply:

1. Update the `load_dataset()` method for your CSV structure
2. Adjust clustering parameters in `cluster_responses()`
3. Modify topic labeling prompts in `generate_topic_labels()`

## Performance Targets (Hackathon Goals)

- **Speed**: <15 minutes for 4k responses ⏱️
- **Cost**: <$5 per 10k responses 💰
- **Insightfulness**: Coherent topics, minimal duplicates 🧠
- **Reliability**: <1% records to DLQ 🛡️

## Demo Script

1. Show the raw sample data (`cat sample_data/data_set_1.csv`)
2. Run the pipeline (`python smart_analytics_pipeline.py`)
3. Show the JSON output (`cat output_data_set_1.json`)
4. Highlight key insights: topics found, sentiment analysis, PII handling

## Next Steps (Post-Hackathon)

- Add Step Functions orchestration
- Implement OpenSearch Serverless for vector storage
- Add Bedrock Guardrails for content safety
- Create QuickSight dashboard for visualization
- Add multi-language support
- Implement batch processing with SQS

---

**Built for AWS Engineering Day Hackathon 2024** 🏆