#!/usr/bin/env python3
"""
Quick Demo Script - Smart Text Analytics Pipeline
AWS Engineering Day Hackathon

Quick way to test the pipeline on different datasets and compare results.
"""

import json
import os
from hackathon_demo import HackathonTextAnalytics

def run_quick_demo(dataset_num=1, max_responses=100):
    """Run demo on specific dataset with response limit"""

    dataset_path = f'sample_data/data_set_{dataset_num}.csv'

    if not os.path.exists(dataset_path):
        print(f"❌ Dataset {dataset_num} not found!")
        return

    print(f"🎯 Quick Demo - Dataset {dataset_num}")
    print("=" * 40)

    # Initialize pipeline
    pipeline = HackathonTextAnalytics()

    # Load and limit responses for quick demo
    responses = pipeline.load_dataset(dataset_path)
    if len(responses) > max_responses:
        print(f"⚡ Limiting to {max_responses} responses for quick demo")
        responses = responses[:max_responses]
        # Update the pipeline with limited responses
        pipeline.responses = responses

    # Process subset
    try:
        # Manual processing for speed
        print("🔒 Processing PII...")
        for response in responses:
            clean_text, pii_types = pipeline.process_pii(response['original_text'])
            response['clean_text'] = clean_text
            response['pii_detected'] = len(pii_types) > 0
            response['pii_types'] = pii_types

        print("🧮 Generating embeddings...")
        clean_texts = [r['clean_text'] for r in responses]
        embeddings = pipeline.get_embeddings(clean_texts)

        print("🎯 Clustering...")
        cluster_labels = pipeline.cluster_texts(embeddings)

        # Group by cluster
        cluster_groups = {}
        for i, cluster_id in enumerate(cluster_labels):
            if cluster_id not in cluster_groups:
                cluster_groups[cluster_id] = []
            cluster_groups[cluster_id].append(clean_texts[i])
            responses[i]['cluster_id'] = cluster_id

        print("🏷️ Generating labels...")
        topic_labels = pipeline.generate_labels(cluster_groups)

        print("😊 Analyzing sentiment...")
        sentiments = pipeline.analyze_sentiment(clean_texts)

        for i, sentiment in enumerate(sentiments):
            responses[i]['sentiment'] = sentiment

        # Quick results summary
        print(f"\n📊 QUICK RESULTS:")
        print(f"Responses Processed: {len(responses)}")
        print(f"Topics Found: {len(cluster_groups)}")

        # Show top topics
        topic_counts = {}
        for cluster_id, texts in cluster_groups.items():
            topic_counts[cluster_id] = len(texts)

        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)

        print(f"\n🏷️ TOP 5 TOPICS:")
        for i, (cluster_id, count) in enumerate(sorted_topics[:5]):
            label = topic_labels.get(cluster_id, f"Topic {cluster_id + 1}")
            example = cluster_groups[cluster_id][0][:60] + "..."
            print(f"  {i+1}. {label} ({count} responses)")
            print(f"     Example: \"{example}\"")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

    print(f"\n✅ Quick demo completed!")
    return True

def compare_datasets():
    """Compare results across multiple datasets"""
    print("🔍 Dataset Comparison")
    print("=" * 50)

    results = {}

    for dataset_num in range(1, 7):
        dataset_path = f'sample_data/data_set_{dataset_num}.csv'
        if not os.path.exists(dataset_path):
            continue

        try:
            pipeline = HackathonTextAnalytics()
            responses = pipeline.load_dataset(dataset_path)

            # Quick stats
            results[dataset_num] = {
                'title': responses[0]['project_title'],
                'response_count': len(responses),
                'avg_length': sum(len(r['original_text']) for r in responses) / len(responses)
            }

        except Exception as e:
            results[dataset_num] = {'error': str(e)}

    # Display comparison
    print(f"{'Dataset':<10} {'Title':<30} {'Responses':<12} {'Avg Length':<12}")
    print("-" * 70)

    for dataset_num, data in results.items():
        if 'error' in data:
            print(f"Dataset {dataset_num:<3} ERROR: {data['error']}")
        else:
            title = data['title'][:28] + ".." if len(data['title']) > 30 else data['title']
            print(f"Dataset {dataset_num:<3} {title:<30} {data['response_count']:<12} {data['avg_length']:<12.1f}")

def main():
    """Interactive demo menu"""
    print("🎯 Smart Text Analytics - Quick Demo")
    print("=" * 40)

    while True:
        print("\nChoose an option:")
        print("1. Quick demo - Dataset 1 (Beauty)")
        print("2. Quick demo - Dataset 2 (Prebiotic Sodas)")
        print("3. Quick demo - Custom dataset number")
        print("4. Compare all datasets")
        print("5. Full demo (all responses)")
        print("0. Exit")

        choice = input("\nEnter choice (0-5): ").strip()

        if choice == '0':
            print("👋 Goodbye!")
            break
        elif choice == '1':
            run_quick_demo(1, 50)
        elif choice == '2':
            run_quick_demo(2, 50)
        elif choice == '3':
            try:
                dataset_num = int(input("Enter dataset number (1-6): "))
                if 1 <= dataset_num <= 6:
                    run_quick_demo(dataset_num, 50)
                else:
                    print("❌ Invalid dataset number")
            except ValueError:
                print("❌ Please enter a valid number")
        elif choice == '4':
            compare_datasets()
        elif choice == '5':
            dataset_num = int(input("Enter dataset number (1-6): ") or "1")
            print("⚠️  Running full demo - this may take several minutes...")

            # Import and run full demo
            from hackathon_demo import HackathonTextAnalytics
            pipeline = HackathonTextAnalytics()
            dataset_path = f'sample_data/data_set_{dataset_num}.csv'

            try:
                result = pipeline.process_dataset(dataset_path)

                output_file = f'quick_demo_results_{dataset_num}.json'
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2)

                print(f"✅ Full results saved to: {output_file}")
                print(f"📊 Found {len(result['topics'])} topics from {result['project_metadata']['total_responses']} responses")

            except Exception as e:
                print(f"❌ Full demo failed: {e}")
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()
