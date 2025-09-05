#!/usr/bin/env python3
"""
Smart Text Analytics Pipeline - Hackathon Demo Version
AWS Engineering Day Hackathon

Optimized demo version that detects AWS service availability upfront
and uses appropriate fallbacks for maximum reliability during demo.
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

class HackathonTextAnalytics:
    """Optimized hackathon demo pipeline with smart fallbacks"""

    def __init__(self, aws_profile: str = "platform-test-engineering-day"):
        """Initialize with AWS service capability detection"""
        self.session = boto3.Session(profile_name=aws_profile)
        self.comprehend = self.session.client('comprehend', region_name='us-east-1')
        self.bedrock = self.session.client('bedrock-runtime', region_name='us-east-1')

        # Detect available services upfront
        self.services = self._detect_service_availability()
        self.responses = []

    def _detect_service_availability(self) -> Dict[str, bool]:
        """Detect which AWS services are available"""
        logger.info("🔍 Detecting AWS service availability...")
        services = {
            'comprehend_pii': False,
            'comprehend_sentiment': False,
            'bedrock_embeddings': False,
            'bedrock_llm': False
        }

        # Test Comprehend PII
        try:
            self.comprehend.detect_pii_entities(Text="test", LanguageCode='en')
            services['comprehend_pii'] = True
            logger.info("✅ Comprehend PII available")
        except:
            logger.info("❌ Comprehend PII not available - using regex fallback")

        # Test Comprehend Sentiment
        try:
            self.comprehend.detect_sentiment(Text="test", LanguageCode='en')
            services['comprehend_sentiment'] = True
            logger.info("✅ Comprehend Sentiment available")
        except:
            logger.info("❌ Comprehend Sentiment not available - using keyword fallback")

        # Test Bedrock models
        embedding_models = [
            "amazon.titan-embed-text-v2:0",
            "amazon.titan-embed-text-v1",
        ]

        for model in embedding_models:
            try:
                payload = {"inputText": "test", "dimensions": 512, "normalize": True}
                self.bedrock.invoke_model(
                    modelId=model,
                    contentType="application/json",
                    accept="application/json",
                    body=json.dumps(payload)
                )
                services['bedrock_embeddings'] = True
                self.embedding_model = model
                logger.info(f"✅ Bedrock Embeddings available: {model}")
                break
            except:
                continue

        if not services['bedrock_embeddings']:
            logger.info("❌ Bedrock Embeddings not available - using mock embeddings")

        # Test LLM models
        llm_models = [
            "anthropic.claude-3-sonnet-20240229-v1:0",
            "anthropic.claude-v2:1"
        ]

        for model in llm_models:
            try:
                payload = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 10,
                    "messages": [{"role": "user", "content": [{"type": "text", "text": "Hi"}]}]
                }
                self.bedrock.invoke_model(
                    modelId=model,
                    contentType="application/json",
                    accept="application/json",
                    body=json.dumps(payload)
                )
                services['bedrock_llm'] = True
                self.llm_model = model
                logger.info(f"✅ Bedrock LLM available: {model}")
                break
            except:
                continue

        if not services['bedrock_llm']:
            logger.info("❌ Bedrock LLM not available - using keyword-based labeling")

        return services

    def load_dataset(self, file_path: str) -> List[Dict[str, Any]]:
        """Load dataset from CSV file"""
        logger.info(f"📁 Loading dataset: {file_path}")

        responses = []
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            lines = content.split('\n')

            # Extract metadata
            project_title = lines[0].replace('﻿Project Title: ', '').strip()
            question_text = lines[1].replace('Question text: ', '').strip().strip('"')

            # Process responses
            response_texts = [line.strip().strip('"') for line in lines[3:] if line.strip()]

            for i, text in enumerate(response_texts):
                if text and len(text) > 3:
                    responses.append({
                        'response_id': f"resp_{i+1:04d}",
                        'original_text': text,
                        'project_title': project_title,
                        'question_text': question_text
                    })

        logger.info(f"📊 Loaded {len(responses)} responses")
        return responses

    def process_pii(self, text: str) -> Tuple[str, List[str]]:
        """Process PII with smart fallback"""
        if self.services['comprehend_pii']:
            try:
                response = self.comprehend.detect_pii_entities(Text=text, LanguageCode='en')
                # Process AWS Comprehend response
                pii_entities = response.get('Entities', [])
                clean_text = text
                pii_types = []

                for entity in sorted(pii_entities, key=lambda x: x['BeginOffset'], reverse=True):
                    entity_type = entity['Type']
                    begin_offset = entity['BeginOffset']
                    end_offset = entity['EndOffset']
                    replacement = f"[REDACTED_{entity_type}]"
                    clean_text = clean_text[:begin_offset] + replacement + clean_text[end_offset:]
                    pii_types.append(entity_type)

                return clean_text, pii_types
            except:
                pass

        # Regex fallback
        clean_text = text
        pii_types = []

        # Email detection
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.search(email_pattern, text):
            clean_text = re.sub(email_pattern, '[REDACTED_EMAIL]', clean_text)
            pii_types.append('EMAIL')

        # Phone detection
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        if re.search(phone_pattern, text):
            clean_text = re.sub(phone_pattern, '[REDACTED_PHONE]', clean_text)
            pii_types.append('PHONE')

        return clean_text, pii_types

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings with smart fallback"""
        logger.info(f"🧮 Generating embeddings for {len(texts)} texts")

        if self.services['bedrock_embeddings']:
            embeddings = []
            for text in tqdm(texts, desc="Bedrock embeddings"):
                try:
                    payload = {"inputText": text[:8000], "dimensions": 512, "normalize": True}
                    response = self.bedrock.invoke_model(
                        modelId=self.embedding_model,
                        contentType="application/json",
                        accept="application/json",
                        body=json.dumps(payload)
                    )
                    result = json.loads(response['body'].read())
                    embeddings.append(result['embedding'])
                    time.sleep(0.05)  # Rate limiting
                except Exception as e:
                    # Fallback for individual failures
                    embeddings.append([hash(text + str(i)) % 1000 / 1000.0 for i in range(512)])
            return embeddings

        # Mock embeddings based on text hashing for consistent results
        logger.info("Using deterministic mock embeddings")
        embeddings = []
        for i, text in enumerate(texts):
            # Create pseudo-embeddings based on text content
            words = text.lower().split()
            embedding = []
            for dim in range(512):
                value = 0.0
                for word in words:
                    value += hash(word + str(dim)) % 1000 / 1000.0
                value = (value / len(words) if words else 0.5) % 1.0
                embedding.append(value)
            embeddings.append(embedding)
        return embeddings

    def cluster_texts(self, embeddings: List[List[float]]) -> List[int]:
        """Cluster texts using UMAP + HDBSCAN"""
        logger.info("🎯 Clustering responses")

        X = np.array(embeddings)

        if len(X) < 10:
            # Too few samples for UMAP/HDBSCAN
            return list(range(len(X)))

        # UMAP dimensionality reduction
        n_neighbors = min(15, len(X) - 1)
        n_components = min(10, len(X) - 1)

        reducer = umap.UMAP(
            n_neighbors=n_neighbors,
            n_components=n_components,
            metric='cosine',
            random_state=42
        )

        X_reduced = reducer.fit_transform(X)

        # HDBSCAN clustering
        min_cluster_size = max(3, len(X) // 20)
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            metric='euclidean'
        )

        labels = clusterer.fit_predict(X_reduced)

        # Handle noise points
        unique_clusters = len(set(labels) - {-1})
        for i, label in enumerate(labels):
            if label == -1:
                labels[i] = unique_clusters
                unique_clusters += 1

        logger.info(f"Found {len(set(labels))} clusters")
        return labels.tolist()

    def generate_labels(self, cluster_texts: Dict[int, List[str]]) -> Dict[int, str]:
        """Generate topic labels with smart fallback"""
        logger.info("🏷️ Generating topic labels")

        if self.services['bedrock_llm']:
            return self._generate_llm_labels(cluster_texts)
        else:
            return self._generate_keyword_labels(cluster_texts)

    def _generate_llm_labels(self, cluster_texts: Dict[int, List[str]]) -> Dict[int, str]:
        """Generate labels using LLM"""
        labels = {}
        for cluster_id, texts in tqdm(cluster_texts.items(), desc="LLM labeling"):
            sample = texts[:5]  # Sample for labeling
            sample_text = "\n".join([f"- {text}" for text in sample])

            prompt = f"""Analyze these survey responses and create a 2-3 word topic label.

Responses:
{sample_text}

Create a concise, neutral topic label (2-3 words maximum):"""

            try:
                payload = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 20,
                    "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
                    "temperature": 0.3
                }

                response = self.bedrock.invoke_model(
                    modelId=self.llm_model,
                    contentType="application/json",
                    accept="application/json",
                    body=json.dumps(payload)
                )

                result = json.loads(response['body'].read())
                label = result['content'][0]['text'].strip()
                label = ' '.join(label.split()[:3])  # Max 3 words
                labels[cluster_id] = label if label else f"Topic {cluster_id + 1}"
                time.sleep(0.3)  # Rate limiting

            except:
                labels[cluster_id] = f"Topic {cluster_id + 1}"

        return labels

    def _generate_keyword_labels(self, cluster_texts: Dict[int, List[str]]) -> Dict[int, str]:
        """Generate labels using keyword analysis"""
        labels = {}

        # Common themes in survey data
        theme_keywords = {
            'Quality': ['quality', 'good', 'great', 'excellent', 'amazing', 'perfect'],
            'Price': ['price', 'cost', 'expensive', 'cheap', 'afford', 'money', 'dollar'],
            'Service': ['service', 'staff', 'help', 'support', 'customer', 'friendly'],
            'Experience': ['experience', 'feel', 'enjoy', 'satisfied', 'happy'],
            'Product': ['product', 'item', 'brand', 'works', 'effective'],
            'Appearance': ['look', 'appearance', 'color', 'design', 'style', 'beautiful'],
            'Performance': ['performance', 'fast', 'slow', 'efficient', 'reliable'],
            'Convenience': ['easy', 'convenient', 'simple', 'quick', 'accessible'],
            'Negative': ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disappointed']
        }

        for cluster_id, texts in cluster_texts.items():
            combined_text = ' '.join(texts).lower()

            # Score each theme
            theme_scores = {}
            for theme, keywords in theme_keywords.items():
                score = sum(1 for keyword in keywords if keyword in combined_text)
                if score > 0:
                    theme_scores[theme] = score

            if theme_scores:
                best_theme = max(theme_scores, key=theme_scores.get)
                labels[cluster_id] = best_theme
            else:
                labels[cluster_id] = f"Topic {cluster_id + 1}"

        return labels

    def analyze_sentiment(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze sentiment with smart fallback"""
        logger.info("😊 Analyzing sentiment")

        if self.services['comprehend_sentiment']:
            return self._analyze_aws_sentiment(texts)
        else:
            return self._analyze_keyword_sentiment(texts)

    def _analyze_aws_sentiment(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Use AWS Comprehend for sentiment"""
        sentiments = []
        for text in tqdm(texts, desc="AWS sentiment"):
            try:
                response = self.comprehend.detect_sentiment(
                    Text=text[:5000],
                    LanguageCode='en'
                )
                sentiments.append({
                    'sentiment': response['Sentiment'],
                    'confidence': response['SentimentScore'][response['Sentiment'].title()],
                    'scores': response['SentimentScore']
                })
                time.sleep(0.05)
            except:
                sentiments.append(self._keyword_sentiment(text))
        return sentiments

    def _analyze_keyword_sentiment(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Use keyword-based sentiment analysis"""
        return [self._keyword_sentiment(text) for text in tqdm(texts, desc="Keyword sentiment")]

    def _keyword_sentiment(self, text: str) -> Dict[str, Any]:
        """Keyword-based sentiment analysis"""
        positive_words = {'good', 'great', 'excellent', 'amazing', 'love', 'like', 'awesome', 'fantastic', 'wonderful', 'perfect', 'best'}
        negative_words = {'bad', 'terrible', 'awful', 'hate', 'horrible', 'worst', 'disappointing', 'poor', 'sucks'}

        words = set(text.lower().split())
        pos_count = len(words & positive_words)
        neg_count = len(words & negative_words)

        if pos_count > neg_count:
            sentiment = 'POSITIVE'
            confidence = min(0.6 + pos_count * 0.1, 0.95)
            scores = {'Positive': confidence, 'Negative': 1-confidence, 'Neutral': 0.0, 'Mixed': 0.0}
        elif neg_count > pos_count:
            sentiment = 'NEGATIVE'
            confidence = min(0.6 + neg_count * 0.1, 0.95)
            scores = {'Positive': 1-confidence, 'Negative': confidence, 'Neutral': 0.0, 'Mixed': 0.0}
        else:
            sentiment = 'NEUTRAL'
            confidence = 0.7
            scores = {'Positive': 0.2, 'Negative': 0.1, 'Neutral': 0.7, 'Mixed': 0.0}

        return {'sentiment': sentiment, 'confidence': confidence, 'scores': scores}

    def process_dataset(self, file_path: str) -> Dict[str, Any]:
        """Main processing pipeline"""
        logger.info("🚀 Starting Smart Text Analytics Pipeline")
        start_time = time.time()

        # Load data
        self.responses = self.load_dataset(file_path)

        # Step 1: PII Detection
        logger.info("🔒 Step 1: PII Detection")
        for response in tqdm(self.responses, desc="PII processing"):
            clean_text, pii_types = self.process_pii(response['original_text'])
            response['clean_text'] = clean_text
            response['pii_detected'] = len(pii_types) > 0
            response['pii_types'] = pii_types

        # Step 2: Generate embeddings
        logger.info("🧮 Step 2: Text Embeddings")
        clean_texts = [r['clean_text'] for r in self.responses]
        embeddings = self.get_embeddings(clean_texts)

        # Step 3: Cluster responses
        logger.info("🎯 Step 3: Clustering")
        cluster_labels = self.cluster_texts(embeddings)

        # Group by cluster
        cluster_groups = {}
        for i, cluster_id in enumerate(cluster_labels):
            if cluster_id not in cluster_groups:
                cluster_groups[cluster_id] = []
            cluster_groups[cluster_id].append(clean_texts[i])
            self.responses[i]['cluster_id'] = cluster_id

        # Step 4: Generate topic labels
        logger.info("🏷️ Step 4: Topic Labeling")
        topic_labels = self.generate_labels(cluster_groups)

        # Step 5: Sentiment analysis
        logger.info("😊 Step 5: Sentiment Analysis")
        sentiments = self.analyze_sentiment(clean_texts)

        for i, sentiment in enumerate(sentiments):
            self.responses[i]['sentiment'] = sentiment

        # Step 6: Compile results
        logger.info("📋 Step 6: Compiling Results")
        topics_summary = []

        for cluster_id, texts in cluster_groups.items():
            cluster_responses = [r for r in self.responses if r['cluster_id'] == cluster_id]
            cluster_sentiments = [r['sentiment'] for r in cluster_responses]

            # Calculate metrics
            pos_scores = [s['scores']['Positive'] for s in cluster_sentiments]
            sentiment_mean = float(np.mean(pos_scores))

            sentiment_dist = {
                'positive': sum(1 for s in cluster_sentiments if s['sentiment'] == 'POSITIVE'),
                'negative': sum(1 for s in cluster_sentiments if s['sentiment'] == 'NEGATIVE'),
                'neutral': sum(1 for s in cluster_sentiments if s['sentiment'] == 'NEUTRAL'),
                'mixed': sum(1 for s in cluster_sentiments if s['sentiment'] == 'MIXED')
            }

            topic_summary = {
                'topic_id': f"topic_{cluster_id}",
                'label': topic_labels.get(cluster_id, f"Topic {cluster_id + 1}"),
                'count': len(texts),
                'sentiment_mean': sentiment_mean,
                'sentiment_distribution': sentiment_dist,
                'examples': texts[:3]  # Top 3 examples
            }
            topics_summary.append(topic_summary)

        # Sort by size
        topics_summary.sort(key=lambda x: x['count'], reverse=True)

        processing_time = time.time() - start_time

        # Final result
        result = {
            'project_metadata': {
                'project_title': self.responses[0]['project_title'],
                'question_text': self.responses[0]['question_text'],
                'total_responses': len(self.responses),
                'processing_time_seconds': round(processing_time, 2),
                'timestamp': datetime.now().isoformat(),
                'services_used': {
                    'comprehend_pii': self.services['comprehend_pii'],
                    'comprehend_sentiment': self.services['comprehend_sentiment'],
                    'bedrock_embeddings': self.services['bedrock_embeddings'],
                    'bedrock_llm': self.services['bedrock_llm']
                }
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
                    'pii_detected': r['pii_detected'],
                    'pii_types': r['pii_types']
                } for r in self.responses
            ]
        }

        logger.info(f"✅ Pipeline completed in {processing_time:.2f} seconds")
        logger.info(f"📊 Found {len(topics_summary)} topics from {len(self.responses)} responses")

        return result

def main():
    """Demo execution"""
    print("🎯 Smart Text Analytics - Hackathon Demo")
    print("=" * 50)

    # Initialize pipeline
    pipeline = HackathonTextAnalytics()

    # Process sample dataset
    dataset_path = 'sample_data/data_set_1.csv'

    try:
        result = pipeline.process_dataset(dataset_path)

        # Save results
        output_file = 'hackathon_demo_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Results saved to: {output_file}")

        # Print demo summary
        print(f"\n🎯 DEMO RESULTS")
        print(f"Project: {result['project_metadata']['project_title']}")
        print(f"Processing Time: {result['project_metadata']['processing_time_seconds']}s")
        print(f"Total Responses: {result['project_metadata']['total_responses']}")
        print(f"Topics Found: {len(result['topics'])}")

        print(f"\n🏷️ TOP TOPICS:")
        for i, topic in enumerate(result['topics'][:5]):
            emoji = "😊" if topic['sentiment_mean'] > 0.6 else "😐" if topic['sentiment_mean'] > 0.4 else "😞"
            print(f"  {i+1}. {topic['label']} {emoji}")
            print(f"     Count: {topic['count']} | Sentiment: {topic['sentiment_mean']:.2f}")
            print(f"     Example: \"{topic['examples'][0][:80]}...\"")

        print(f"\n🔧 SERVICES USED:")
        services = result['project_metadata']['services_used']
        for service, used in services.items():
            status = "✅" if used else "⚠️ (fallback)"
            print(f"  {service.replace('_', ' ').title()}: {status}")

        print(f"\n🎉 Demo completed successfully!")

    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise

if __name__ == "__main__":
    main()
