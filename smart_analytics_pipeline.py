#!/usr/bin/env python3
"""
Smart Text Analytics Pipeline - Minimal Working Model
AWS Engineering Day Hackathon

This script demonstrates an end-to-end pipeline for processing unstructured
open-ended survey responses using various AWS services:
- PII Detection: Amazon Comprehend
- Text Embeddings: Bedrock Titan Text Embeddings v2
- Topic Labeling: Bedrock Claude Sonnet
- Sentiment Analysis: Amazon Comprehend
- Clustering: UMAP + HDBSCAN (local processing)
"""

import csv
import json
import logging
import os
import re
import time
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional

import boto3
import numpy as np
import pandas as pd
from botocore.exceptions import ClientError
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm
import umap
import hdbscan

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SmartTextAnalyticsPipeline:
    """Main pipeline class for smart text analytics"""

    def __init__(self, aws_profile: str = "platform-test-engineering-day"):
        """Initialize AWS clients with specified profile"""
        self.session = boto3.Session(profile_name=aws_profile)
        self.comprehend = self.session.client('comprehend', region_name='us-east-1')
        self.bedrock = self.session.client('bedrock-runtime', region_name='us-east-1')

        # Model configurations - try multiple model IDs as fallbacks
        self.embedding_models = [
            "amazon.titan-embed-text-v2:0",
            "amazon.titan-embed-text-v1",
            "cohere.embed-english-v3"
        ]
        self.labeling_models = [
            "anthropic.claude-3-sonnet-20240229-v1:0",
            "anthropic.claude-v2:1",
            "amazon.titan-text-premier-v1:0"
        ]

        # Pipeline data storage
        self.responses = []
        self.clean_responses = []
        self.embeddings = []
        self.clusters = []
        self.topics = []

    def load_dataset(self, file_path: str) -> List[Dict[str, Any]]:
        """Load dataset from CSV file"""
        logger.info(f"Loading dataset from {file_path}")

        responses = []
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

            # Extract project metadata from first two lines
            lines = content.split('\n')
            project_title = lines[0].replace('﻿Project Title: ', '').strip()
            question_text = lines[1].replace('Question text: ', '').strip().strip('"')

            # Process responses (skip first 3 lines - title, question, empty line)
            response_texts = [line.strip().strip('"') for line in lines[3:] if line.strip()]

            for i, text in enumerate(response_texts):
                if text and len(text) > 3:  # Filter out very short responses
                    responses.append({
                        'response_id': f"resp_{i+1:04d}",
                        'original_text': text,
                        'project_title': project_title,
                        'question_text': question_text
                    })

        logger.info(f"Loaded {len(responses)} responses")
        return responses

    def detect_and_redact_pii(self, text: str) -> Tuple[str, List[Dict]]:
        """Detect and redact PII using Amazon Comprehend with fallback"""
        try:
            response = self.comprehend.detect_pii_entities(
                Text=text,
                LanguageCode='en'
            )

            pii_entities = response.get('Entities', [])
            clean_text = text

            # Sort entities by offset in reverse order to maintain positions during replacement
            pii_entities.sort(key=lambda x: x['BeginOffset'], reverse=True)

            for entity in pii_entities:
                entity_type = entity['Type']
                begin_offset = entity['BeginOffset']
                end_offset = entity['EndOffset']

                # Redact based on entity type
                if entity_type in ['EMAIL', 'PHONE', 'SSN', 'CREDIT_DEBIT_NUMBER']:
                    replacement = f"[REDACTED_{entity_type}]"
                elif entity_type in ['NAME', 'ADDRESS']:
                    replacement = f"[REDACTED_{entity_type}]"
                else:
                    replacement = f"[REDACTED]"

                clean_text = clean_text[:begin_offset] + replacement + clean_text[end_offset:]

            return clean_text, pii_entities

        except ClientError as e:
            logger.warning(f"PII detection failed, using simple regex fallback: {e}")
            # Simple regex-based PII detection fallback
            import re
            clean_text = text
            pii_entities = []

            # Email detection
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.finditer(email_pattern, text)
            for match in reversed(list(emails)):
                clean_text = clean_text[:match.start()] + "[REDACTED_EMAIL]" + clean_text[match.end():]
                pii_entities.append({'Type': 'EMAIL', 'BeginOffset': match.start(), 'EndOffset': match.end()})

            # Phone detection (simple pattern)
            phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
            phones = re.finditer(phone_pattern, text)
            for match in reversed(list(phones)):
                clean_text = clean_text[:match.start()] + "[REDACTED_PHONE]" + clean_text[match.end():]
                pii_entities.append({'Type': 'PHONE', 'BeginOffset': match.start(), 'EndOffset': match.end()})

            return clean_text, pii_entities

    def get_embeddings(self, texts: List[str], batch_size: int = 10) -> List[List[float]]:
        """Generate embeddings using Bedrock with fallback models"""
        logger.info(f"Generating embeddings for {len(texts)} texts")

        embeddings = []
        working_model = None

        # Try to find a working embedding model
        for model_id in self.embedding_models:
            try:
                test_payload = {
                    "inputText": "test",
                    "dimensions": 512 if "titan" in model_id else None,
                    "normalize": True
                }
                if "cohere" in model_id:
                    test_payload = {
                        "texts": ["test"],
                        "input_type": "search_document",
                        "truncate": "NONE"
                    }

                self.bedrock.invoke_model(
                    modelId=model_id,
                    contentType="application/json",
                    accept="application/json",
                    body=json.dumps(test_payload)
                )
                working_model = model_id
                logger.info(f"Using embedding model: {model_id}")
                break
            except ClientError as e:
                logger.warning(f"Model {model_id} failed: {e}")
                continue

        if not working_model:
            logger.error("No working embedding model found, using mock embeddings")
            # Generate mock embeddings for demo
            import random
            return [[random.random() for _ in range(512)] for _ in texts]

        for i in tqdm(range(0, len(texts), batch_size), desc="Generating embeddings"):
            batch = texts[i:i + batch_size]

            for text in batch:
                try:
                    if "titan" in working_model:
                        payload = {
                            "inputText": text,
                            "dimensions": 512,
                            "normalize": True
                        }
                    elif "cohere" in working_model:
                        payload = {
                            "texts": [text],
                            "input_type": "search_document",
                            "truncate": "NONE"
                        }

                    response = self.bedrock.invoke_model(
                        modelId=working_model,
                        contentType="application/json",
                        accept="application/json",
                        body=json.dumps(payload)
                    )

                    response_body = json.loads(response['body'].read())

                    if "titan" in working_model:
                        embedding = response_body['embedding']
                    elif "cohere" in working_model:
                        embedding = response_body['embeddings'][0]

                    embeddings.append(embedding)

                    # Small delay to avoid rate limits
                    time.sleep(0.1)

                except ClientError as e:
                    logger.warning(f"Embedding generation failed: {e}")
                    # Use mock embedding as fallback
                    import random
                    embeddings.append([random.random() for _ in range(512)])

        return embeddings

    def cluster_responses(self, embeddings: List[List[float]], min_cluster_size: int = 3) -> List[int]:
        """Cluster responses using UMAP + HDBSCAN"""
        logger.info("Clustering responses using UMAP + HDBSCAN")

        # Convert to numpy array
        X = np.array(embeddings)

        # Reduce dimensionality with UMAP
        umap_reducer = umap.UMAP(
            n_neighbors=min(15, len(embeddings) - 1),
            n_components=min(10, len(embeddings) - 1),
            metric='cosine',
            random_state=42
        )

        X_reduced = umap_reducer.fit_transform(X)

        # Cluster with HDBSCAN
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=max(2, min_cluster_size),
            metric='euclidean',
            cluster_selection_epsilon=0.1
        )

        cluster_labels = clusterer.fit_predict(X_reduced)

        # Handle noise points (label -1) by assigning them to nearest cluster or creating singleton clusters
        unique_clusters = len(set(cluster_labels) - {-1})
        noise_points = np.where(cluster_labels == -1)[0]

        for noise_idx in noise_points:
            cluster_labels[noise_idx] = unique_clusters
            unique_clusters += 1

        logger.info(f"Found {len(set(cluster_labels))} clusters")
        return cluster_labels.tolist()

    def generate_topic_labels(self, cluster_texts: Dict[int, List[str]]) -> Dict[int, str]:
        """Generate topic labels using Bedrock with fallback models"""
        logger.info("Generating topic labels using LLM")

        topic_labels = {}
        working_model = None

        # Try to find a working labeling model
        for model_id in self.labeling_models:
            try:
                if "anthropic" in model_id:
                    test_payload = {
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 10,
                        "messages": [
                            {"role": "user", "content": [{"type": "text", "text": "Hi"}]}
                        ]
                    }
                else:
                    test_payload = {
                        "inputText": "Hi",
                        "textGenerationConfig": {
                            "maxTokenCount": 10,
                            "temperature": 0.3
                        }
                    }

                self.bedrock.invoke_model(
                    modelId=model_id,
                    contentType="application/json",
                    accept="application/json",
                    body=json.dumps(test_payload)
                )
                working_model = model_id
                logger.info(f"Using labeling model: {model_id}")
                break
            except ClientError as e:
                logger.warning(f"Model {model_id} failed: {e}")
                continue

        if not working_model:
            logger.error("No working labeling model found, using simple keyword-based labels")
            # Generate simple labels based on common words
            for cluster_id, texts in cluster_texts.items():
                words = ' '.join(texts).lower().split()
                common_words = ['product', 'quality', 'service', 'price', 'good', 'bad', 'like', 'love', 'hate']
                found_words = [w for w in common_words if w in words]
                if found_words:
                    topic_labels[cluster_id] = found_words[0].title()
                else:
                    topic_labels[cluster_id] = f"Topic {cluster_id + 1}"
            return topic_labels

        for cluster_id, texts in tqdm(cluster_texts.items(), desc="Generating labels"):
            try:
                # Sample up to 10 representative texts
                sample_texts = texts[:10] if len(texts) > 10 else texts
                sample_text = "\n".join([f"- {text}" for text in sample_texts])

                prompt = f"""Analyze these survey responses and create a concise topic label (2-3 words maximum).

Survey responses:
{sample_text}

Requirements:
- Label must be 2-3 words maximum
- Focus on the main theme/topic
- Use neutral language (avoid sentiment words like "good" or "bad")
- Be specific enough to distinguish from other topics
- Use title case

Topic label:"""

                if "anthropic" in working_model:
                    payload = {
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 50,
                        "messages": [
                            {"role": "user", "content": [{"type": "text", "text": prompt}]}
                        ],
                        "temperature": 0.3
                    }
                else:
                    payload = {
                        "inputText": prompt,
                        "textGenerationConfig": {
                            "maxTokenCount": 50,
                            "temperature": 0.3
                        }
                    }

                response = self.bedrock.invoke_model(
                    modelId=working_model,
                    contentType="application/json",
                    accept="application/json",
                    body=json.dumps(payload)
                )

                response_body = json.loads(response['body'].read())

                if "anthropic" in working_model:
                    label = response_body['content'][0]['text'].strip()
                else:
                    label = response_body['results'][0]['outputText'].strip()

                # Clean up the label
                label = re.sub(r'^[^\w\s]+|[^\w\s]+$', '', label)  # Remove leading/trailing punctuation
                label = ' '.join(label.split()[:3])  # Ensure max 3 words

                topic_labels[cluster_id] = label if label else f"Topic {cluster_id + 1}"

                # Small delay to avoid rate limits
                time.sleep(0.5)

            except ClientError as e:
                logger.warning(f"Topic labeling failed for cluster {cluster_id}: {e}")
                topic_labels[cluster_id] = f"Topic {cluster_id + 1}"

        return topic_labels

    def analyze_sentiment(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze sentiment using Amazon Comprehend with fallback"""
        logger.info(f"Analyzing sentiment for {len(texts)} texts")

        sentiments = []
        use_fallback = False

        # Test Comprehend access
        try:
            test_response = self.comprehend.detect_sentiment(
                Text="This is a test message",
                LanguageCode='en'
            )
            logger.info("Using Amazon Comprehend for sentiment analysis")
        except ClientError as e:
            logger.warning(f"Comprehend sentiment analysis not available, using fallback: {e}")
            use_fallback = True

        for text in tqdm(texts, desc="Analyzing sentiment"):
            if not use_fallback:
                try:
                    response = self.comprehend.detect_sentiment(
                        Text=text[:5000],  # Comprehend has text length limits
                        LanguageCode='en'
                    )

                    sentiment_data = {
                        'sentiment': response['Sentiment'],
                        'confidence': response['SentimentScore'][response['Sentiment'].title()],
                        'scores': response['SentimentScore']
                    }

                    sentiments.append(sentiment_data)
                    time.sleep(0.1)  # Small delay to avoid rate limits
                    continue

                except ClientError as e:
                    logger.warning(f"Comprehend failed for text, using fallback: {e}")
                    use_fallback = True

            # Fallback sentiment analysis using simple keyword matching
            text_lower = text.lower()
            positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'like', 'awesome', 'fantastic', 'wonderful', 'perfect']
            negative_words = ['bad', 'terrible', 'awful', 'hate', 'horrible', 'worst', 'disappointing', 'poor', 'sucks', 'disgusting']

            pos_count = sum(1 for word in positive_words if word in text_lower)
            neg_count = sum(1 for word in negative_words if word in text_lower)

            if pos_count > neg_count:
                sentiment = 'POSITIVE'
                confidence = min(0.6 + (pos_count * 0.1), 0.95)
                scores = {'Positive': confidence, 'Negative': 1-confidence, 'Neutral': 0.0, 'Mixed': 0.0}
            elif neg_count > pos_count:
                sentiment = 'NEGATIVE'
                confidence = min(0.6 + (neg_count * 0.1), 0.95)
                scores = {'Positive': 1-confidence, 'Negative': confidence, 'Neutral': 0.0, 'Mixed': 0.0}
            else:
                sentiment = 'NEUTRAL'
                confidence = 0.7
                scores = {'Positive': 0.2, 'Negative': 0.1, 'Neutral': 0.7, 'Mixed': 0.0}

            sentiment_data = {
                'sentiment': sentiment,
                'confidence': confidence,
                'scores': scores
            }
            sentiments.append(sentiment_data)

        return sentiments

    def process_dataset(self, file_path: str) -> Dict[str, Any]:
        """Main processing pipeline"""
        logger.info("Starting smart text analytics pipeline")
        start_time = time.time()

        # Step 1: Load data
        self.responses = self.load_dataset(file_path)

        # Step 2: PII detection and redaction
        logger.info("Step 2: PII detection and redaction")
        clean_texts = []
        pii_flags = []

        for response in tqdm(self.responses, desc="Processing PII"):
            clean_text, pii_entities = self.detect_and_redact_pii(response['original_text'])
            clean_texts.append(clean_text)
            pii_flags.append(pii_entities)
            response['clean_text'] = clean_text
            response['pii_detected'] = pii_entities

        # Step 3: Generate embeddings
        logger.info("Step 3: Generating embeddings")
        self.embeddings = self.get_embeddings(clean_texts)

        # Step 4: Cluster responses
        logger.info("Step 4: Clustering responses")
        cluster_labels = self.cluster_responses(self.embeddings)

        # Group responses by cluster
        cluster_groups = {}
        for i, cluster_id in enumerate(cluster_labels):
            if cluster_id not in cluster_groups:
                cluster_groups[cluster_id] = []
            cluster_groups[cluster_id].append(clean_texts[i])
            self.responses[i]['cluster_id'] = cluster_id

        # Step 5: Generate topic labels
        logger.info("Step 5: Generating topic labels")
        topic_labels = self.generate_topic_labels(cluster_groups)

        # Step 6: Sentiment analysis
        logger.info("Step 6: Analyzing sentiment")
        sentiments = self.analyze_sentiment(clean_texts)

        for i, sentiment in enumerate(sentiments):
            self.responses[i]['sentiment'] = sentiment

        # Step 7: Aggregate results
        logger.info("Step 7: Aggregating results")
        topics_summary = []

        for cluster_id, texts in cluster_groups.items():
            cluster_responses = [r for r in self.responses if r['cluster_id'] == cluster_id]
            cluster_sentiments = [r['sentiment'] for r in cluster_responses]

            # Calculate sentiment statistics
            positive_scores = [s['scores']['Positive'] for s in cluster_sentiments]
            sentiment_mean = np.mean(positive_scores)

            # Get example responses (up to 3)
            examples = texts[:3]

            topic_summary = {
                'topic_id': f"topic_{cluster_id}",
                'label': topic_labels.get(cluster_id, f"Topic {cluster_id + 1}"),
                'count': len(texts),
                'sentiment_mean': float(sentiment_mean),
                'sentiment_distribution': {
                    'positive': len([s for s in cluster_sentiments if s['sentiment'] == 'POSITIVE']),
                    'negative': len([s for s in cluster_sentiments if s['sentiment'] == 'NEGATIVE']),
                    'neutral': len([s for s in cluster_sentiments if s['sentiment'] == 'NEUTRAL']),
                    'mixed': len([s for s in cluster_sentiments if s['sentiment'] == 'MIXED'])
                },
                'examples': examples
            }
            topics_summary.append(topic_summary)

        # Sort topics by count (largest first)
        topics_summary.sort(key=lambda x: x['count'], reverse=True)

        processing_time = time.time() - start_time

        # Create final output
        result = {
            'project_metadata': {
                'project_title': self.responses[0]['project_title'],
                'question_text': self.responses[0]['question_text'],
                'total_responses': len(self.responses),
                'processing_time_seconds': round(processing_time, 2),
                'timestamp': datetime.now().isoformat()
            },
            'topics': topics_summary,
            'responses': [
                {
                    'response_id': r['response_id'],
                    'original_text': r['original_text'],
                    'clean_text': r['clean_text'],
                    'topic_assignment': {
                        'topic_id': f"topic_{r['cluster_id']}",
                        'topic_label': topic_labels.get(r['cluster_id'], f"Topic {r['cluster_id'] + 1}")
                    },
                    'sentiment': r['sentiment'],
                    'pii_detected': len(r['pii_detected']) > 0,
                    'pii_entities': [e['Type'] for e in r['pii_detected']]
                } for r in self.responses
            ]
        }

        logger.info(f"Pipeline completed in {processing_time:.2f} seconds")
        logger.info(f"Found {len(topics_summary)} topics from {len(self.responses)} responses")

        return result


def main():
    """Main function to run the pipeline"""
    pipeline = SmartTextAnalyticsPipeline()

    # Process all sample datasets
    sample_datasets = [
        'sample_data/data_set_1.csv',
        'sample_data/data_set_2.csv',
        'sample_data/data_set_3.csv',
        'sample_data/data_set_4.csv',
        'sample_data/data_set_5.csv',
        'sample_data/data_set_6.csv'
    ]

    # For hackathon demo, process first dataset
    dataset_path = sample_datasets[0]
    print(f"\n🚀 Processing dataset: {dataset_path}")

    try:
        result = pipeline.process_dataset(dataset_path)

        # Save results
        output_file = f"output_{dataset_path.split('/')[-1].replace('.csv', '')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Results saved to: {output_file}")

        # Print summary
        print(f"\n📊 SUMMARY")
        print(f"Project: {result['project_metadata']['project_title']}")
        print(f"Total Responses: {result['project_metadata']['total_responses']}")
        print(f"Processing Time: {result['project_metadata']['processing_time_seconds']}s")
        print(f"Topics Found: {len(result['topics'])}")

        print(f"\n🏷️ TOPICS:")
        for topic in result['topics']:
            print(f"  • {topic['label']} ({topic['count']} responses, avg sentiment: {topic['sentiment_mean']:.2f})")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    main()
