#!/usr/bin/env python3
"""
Smart Text Analytics Pipeline - Clean Demo Runner
AWS Engineering Day Hackathon 2024

Simple, human-readable demo that showcases the complete pipeline:
- Load survey data
- Process with DBSCAN clustering
- Generate smart topic labels
- Analyze sentiment
- Output results

Usage: python demo.py
"""

from text_analytics_pipeline import TextAnalyticsPipeline
import json
import time
from datetime import datetime


def main():
    """Run the demo with clean, readable output"""

    # Welcome message
    print("🎯 Smart Text Analytics Pipeline Demo")
    print("=" * 50)
    print("Transforming unstructured survey responses into actionable insights")
    print()

    # What we're doing
    print("📋 Pipeline Steps:")
    print("  1. 📁 Load survey data from CSV")
    print("  2. 🔒 Detect and redact PII for privacy")
    print("  3. 🧮 Generate text embeddings (with smart caching)")
    print("  4. 🎯 Cluster with DBSCAN (perfect for unstructured data)")
    print("  5. 🏷️  Generate topic labels using LLM")
    print("  6. 😊 Analyze sentiment with context awareness")
    print("  7. 📊 Compile results into chart-ready JSON")
    print()

    try:
        # Initialize the pipeline
        print("🚀 Initializing pipeline...")
        pipeline = TextAnalyticsPipeline()

        # Process the survey
        survey_file = 'sample_data/data_set_1.csv'
        print(f"📂 Processing survey: {survey_file}")
        print("⏳ This may take 30-60 seconds...")
        print()

        start_time = time.time()
        results = pipeline.process_survey(survey_file, max_responses=250)
        processing_time = time.time() - start_time

        # Save results
        output_file = f'analysis_results_{datetime.now().strftime("%H%M%S")}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        # Show results
        print_results(results, processing_time, output_file)

        return True

    except FileNotFoundError:
        print("❌ Error: Sample data file not found!")
        print("Make sure you're running from the aws_engineering_day directory")
        print("and that sample_data/data_set_1.csv exists")
        return False

    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        return False


def print_results(results, processing_time, output_file):
    """Print results in a clean, readable format"""

    metadata = results['project_metadata']
    stats = results['summary_stats']
    topics = results['topics']

    # Header
    print("🎉 ANALYSIS COMPLETE!")
    print("=" * 50)

    # Key metrics
    print(f"📊 Survey: {metadata['project_title']}")
    print(f"❓ Question: {metadata['question_text'][:80]}...")
    print(f"📝 Responses: {metadata['total_responses']}")
    print(f"⏱️  Processing: {processing_time:.1f} seconds")
    print(f"🎯 Topics Found: {stats['total_topics']}")
    print(f"😊 Overall Sentiment: {stats['overall_sentiment_score']:.2f} (0=negative, 1=positive)")
    print(f"💾 Results: {output_file}")
    print()

    # Topics breakdown
    print("🏷️  DISCOVERED TOPICS:")
    print("-" * 30)

    for i, topic in enumerate(topics[:6], 1):
        # Sentiment emoji
        sentiment_score = topic['sentiment_mean']
        if sentiment_score > 0.7:
            emoji = "😊"  # Very positive
        elif sentiment_score > 0.5:
            emoji = "🙂"  # Positive
        elif sentiment_score > 0.3:
            emoji = "😐"  # Neutral
        else:
            emoji = "😞"  # Negative

        print(f"{i}. {topic['label']} {emoji}")
        print(f"   📊 {topic['count']} responses ({topic['percentage']}%)")
        print(f"   💭 Sentiment: {sentiment_score:.2f}")

        # Show sentiment breakdown
        dist = topic['sentiment_distribution']
        print(f"   📈 Positive: {dist['positive']}, Neutral: {dist['neutral']}, Negative: {dist['negative']}")

        # Show example
        if topic['examples']:
            example = topic['examples'][0]
            if len(example) > 60:
                example = example[:60] + "..."
            print(f"   💡 Example: \"{example}\"")
        print()

    # Performance info
    print("⚡ PERFORMANCE METRICS:")
    print("-" * 25)
    print(f"Processing Rate: {stats['processing_rate']:.1f} responses/second")

    if 'cache_performance' in stats:
        cache = stats['cache_performance']
        print(f"Cache Efficiency: {cache['embedding_cache_size']} embeddings cached")
        print(f"PII Detection: {stats['pii_detection_rate']:.1%} of responses had PII")

    # Success indicator
    if processing_time <= 60:
        print(f"✅ Performance Target: {processing_time:.1f}s ≤ 60s target ✅")
    else:
        print(f"⚠️  Performance: {processing_time:.1f}s exceeded 60s target")

    print()
    print("🚀 Ready for frontend integration!")
    print("📋 The JSON file contains all data needed for charts and dashboards")


def print_usage():
    """Print usage instructions"""
    print("Smart Text Analytics Pipeline Demo")
    print()
    print("Usage:")
    print("  python demo.py")
    print()
    print("Requirements:")
    print("  - AWS credentials configured (AWS_PROFILE=platform-test-engineering-day)")
    print("  - Python dependencies installed (see requirements.txt)")
    print("  - Sample data in sample_data/ directory")
    print()
    print("What it does:")
    print("  - Loads survey responses from CSV")
    print("  - Processes with DBSCAN clustering and LLM labeling")
    print("  - Outputs JSON file ready for frontend integration")


if __name__ == "__main__":
    import sys

    # Handle help flags
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        print_usage()
        sys.exit(0)

    # Run the demo
    success = main()

    if success:
        print("\n🎯 Demo completed successfully!")
        print("Next steps:")
        print("  1. Check the generated JSON file")
        print("  2. Use the JSON for frontend integration")
        print("  3. Scale up to full production if needed")
    else:
        print("\n❌ Demo failed - check error messages above")

    sys.exit(0 if success else 1)
