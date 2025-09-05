#!/usr/bin/env python3
"""
JSON Output Demonstration Script
Smart Text Analytics Pipeline - AWS Engineering Day Hackathon

This script demonstrates how to work with the JSON output from the pipeline
and shows various ways frontend engineers can consume the data.
"""

import json
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime

class AnalyticsDataProcessor:
    """Example processor for Smart Text Analytics JSON output"""

    def __init__(self, json_data: Dict[str, Any]):
        """Initialize with JSON data from the pipeline"""
        self.data = json_data
        self.topics = json_data.get('topics', [])
        self.responses = json_data.get('responses', [])
        self.chart_data = json_data.get('chart_data', {})
        self.metadata = json_data.get('project_metadata', {})

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Generate summary data for dashboard widgets"""
        return {
            'project_title': self.metadata.get('project_title', 'Unknown'),
            'total_responses': self.metadata.get('total_responses', 0),
            'processing_time': self.metadata.get('processing_time_seconds', 0),
            'total_topics': len(self.topics),
            'overall_sentiment': self.data.get('summary_stats', {}).get('overall_sentiment_score', 0),
            'pii_protected': self.metadata.get('quality_metrics', {}).get('pii_detected_count', 0),
            'services_used': self.metadata.get('services_used', {}),
            'timestamp': self.metadata.get('timestamp', datetime.now().isoformat())
        }

    def get_top_topics(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top N topics by response count"""
        sorted_topics = sorted(self.topics, key=lambda x: x['count'], reverse=True)
        return sorted_topics[:limit]

    def get_sentiment_breakdown(self) -> Dict[str, int]:
        """Get overall sentiment distribution"""
        sentiment_counts = {'POSITIVE': 0, 'NEGATIVE': 0, 'NEUTRAL': 0, 'MIXED': 0}

        for response in self.responses:
            sentiment = response.get('sentiment', {}).get('sentiment', 'NEUTRAL')
            if sentiment in sentiment_counts:
                sentiment_counts[sentiment] += 1

        return sentiment_counts

    def get_topic_sentiment_matrix(self) -> List[Dict[str, Any]]:
        """Generate data for heatmap visualization"""
        matrix_data = []

        for topic in self.topics:
            matrix_data.append({
                'topic': topic['label'],
                'positive': topic['sentiment_distribution']['positive'],
                'neutral': topic['sentiment_distribution']['neutral'],
                'negative': topic['sentiment_distribution']['negative'],
                'sentiment_score': topic['sentiment_mean'],
                'total_responses': topic['count']
            })

        return matrix_data

    def get_pii_analysis(self) -> Dict[str, Any]:
        """Analyze PII detection patterns"""
        pii_stats = {
            'total_with_pii': 0,
            'pii_types': {},
            'examples': []
        }

        for response in self.responses:
            if response.get('pii_detected', False):
                pii_stats['total_with_pii'] += 1

                for pii_type in response.get('pii_types', []):
                    if pii_type not in pii_stats['pii_types']:
                        pii_stats['pii_types'][pii_type] = 0
                    pii_stats['pii_types'][pii_type] += 1

                # Add example (with PII already redacted)
                if len(pii_stats['examples']) < 3:
                    pii_stats['examples'].append({
                        'response_id': response['response_id'],
                        'clean_text': response['clean_text'],
                        'pii_types': response['pii_types']
                    })

        return pii_stats

    def export_to_csv(self, filename: str = 'analytics_export.csv') -> str:
        """Export response data to CSV for further analysis"""
        export_data = []

        for response in self.responses:
            export_data.append({
                'response_id': response['response_id'],
                'original_text': response['original_text'],
                'clean_text': response['clean_text'],
                'topic_label': response['topic_assignment']['topic_label'],
                'topic_confidence': response['topic_assignment']['confidence_score'],
                'sentiment': response['sentiment']['sentiment'],
                'sentiment_confidence': response['sentiment']['confidence'],
                'pii_detected': response['pii_detected'],
                'pii_types': ', '.join(response['pii_types']),
                'word_count': response['metadata']['word_count']
            })

        df = pd.DataFrame(export_data)
        df.to_csv(filename, index=False)
        return filename

    def generate_chart_configs(self) -> Dict[str, Any]:
        """Generate Chart.js configuration objects"""
        return {
            'topic_distribution': {
                'type': 'doughnut',
                'data': {
                    'labels': [item['label'] for item in self.chart_data.get('topic_distribution', [])],
                    'datasets': [{
                        'data': [item['value'] for item in self.chart_data.get('topic_distribution', [])],
                        'backgroundColor': [item['color'] for item in self.chart_data.get('topic_distribution', [])],
                        'borderWidth': 2
                    }]
                },
                'options': {
                    'responsive': True,
                    'plugins': {
                        'legend': {'position': 'right'},
                        'title': {'display': True, 'text': 'Response Distribution by Topic'}
                    }
                }
            },
            'sentiment_overview': {
                'type': 'bar',
                'data': {
                    'labels': [item['sentiment'] for item in self.chart_data.get('sentiment_overview', [])],
                    'datasets': [{
                        'label': 'Responses',
                        'data': [item['count'] for item in self.chart_data.get('sentiment_overview', [])],
                        'backgroundColor': [item['color'] for item in self.chart_data.get('sentiment_overview', [])]
                    }]
                },
                'options': {
                    'responsive': True,
                    'plugins': {
                        'title': {'display': True, 'text': 'Overall Sentiment Distribution'}
                    },
                    'scales': {
                        'y': {'beginAtZero': True}
                    }
                }
            }
        }

    def get_insights_summary(self) -> List[str]:
        """Generate text insights from the data"""
        insights = []

        # Top topic insight
        if self.topics:
            top_topic = max(self.topics, key=lambda x: x['count'])
            insights.append(f"'{top_topic['label']}' is the most discussed topic with {top_topic['count']} responses ({top_topic['percentage']:.1f}%)")

        # Sentiment insight
        sentiment_data = self.get_sentiment_breakdown()
        total_responses = sum(sentiment_data.values())
        if total_responses > 0:
            positive_pct = (sentiment_data['POSITIVE'] / total_responses) * 100
            insights.append(f"{positive_pct:.1f}% of responses have positive sentiment")

        # PII insight
        pii_data = self.get_pii_analysis()
        if pii_data['total_with_pii'] > 0:
            insights.append(f"{pii_data['total_with_pii']} responses contained PII that was automatically redacted")

        # Processing insight
        processing_time = self.metadata.get('processing_time_seconds', 0)
        total_responses = self.metadata.get('total_responses', 0)
        if processing_time > 0 and total_responses > 0:
            rate = total_responses / processing_time
            insights.append(f"Pipeline processed {rate:.1f} responses per second")

        return insights

    def validate_data_quality(self) -> Dict[str, Any]:
        """Validate the quality of the processed data"""
        quality_report = {
            'valid': True,
            'issues': [],
            'metrics': {}
        }

        # Check for missing topics
        responses_with_topics = sum(1 for r in self.responses if r.get('topic_assignment'))
        if responses_with_topics != len(self.responses):
            quality_report['issues'].append('Some responses missing topic assignments')
            quality_report['valid'] = False

        # Check sentiment confidence
        low_confidence_count = sum(1 for r in self.responses
                                 if r.get('sentiment', {}).get('confidence', 0) < 0.5)
        if low_confidence_count > len(self.responses) * 0.1:  # >10% low confidence
            quality_report['issues'].append(f'{low_confidence_count} responses have low sentiment confidence')

        # Check topic distribution
        if len(self.topics) < 2:
            quality_report['issues'].append('Very few topics detected - data may not be diverse enough')
        elif len(self.topics) > len(self.responses) / 5:  # Too many topics
            quality_report['issues'].append('Too many topics - clustering may be too granular')

        quality_report['metrics'] = {
            'topic_coverage': responses_with_topics / len(self.responses) if self.responses else 0,
            'avg_sentiment_confidence': sum(r.get('sentiment', {}).get('confidence', 0)
                                          for r in self.responses) / len(self.responses) if self.responses else 0,
            'topics_per_response_ratio': len(self.topics) / len(self.responses) if self.responses else 0
        }

        return quality_report


def demo_json_processing():
    """Demonstrate various ways to process the JSON output"""

    # Load example JSON data
    try:
        with open('hackathon_demo_results.json', 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        print("❌ Demo results file not found. Please run hackathon_demo.py first.")
        return

    print("🎯 Smart Text Analytics - JSON Output Demo")
    print("=" * 50)

    # Initialize processor
    processor = AnalyticsDataProcessor(json_data)

    # 1. Dashboard Summary
    print("\n📊 DASHBOARD SUMMARY")
    print("-" * 20)
    summary = processor.get_dashboard_summary()
    for key, value in summary.items():
        if key == 'services_used':
            print(f"{key}: {', '.join([k for k, v in value.items() if v])}")
        else:
            print(f"{key}: {value}")

    # 2. Top Topics
    print("\n🏷️ TOP 5 TOPICS")
    print("-" * 15)
    top_topics = processor.get_top_topics(5)
    for i, topic in enumerate(top_topics, 1):
        emoji = "😊" if topic['sentiment_mean'] > 0.6 else "😐" if topic['sentiment_mean'] > 0.4 else "😞"
        print(f"{i}. {topic['label']} {emoji}")
        print(f"   Count: {topic['count']} | Sentiment: {topic['sentiment_mean']:.2f}")
        if topic['examples']:
            print(f"   Example: \"{topic['examples'][0]['text'][:60]}...\"")

    # 3. Sentiment Analysis
    print("\n😊 SENTIMENT BREAKDOWN")
    print("-" * 20)
    sentiment_breakdown = processor.get_sentiment_breakdown()
    total = sum(sentiment_breakdown.values())
    for sentiment, count in sentiment_breakdown.items():
        percentage = (count / total * 100) if total > 0 else 0
        emoji = {"POSITIVE": "😊", "NEGATIVE": "😞", "NEUTRAL": "😐", "MIXED": "🤔"}.get(sentiment, "")
        print(f"{emoji} {sentiment}: {count} ({percentage:.1f}%)")

    # 4. PII Analysis
    print("\n🔒 PII ANALYSIS")
    print("-" * 15)
    pii_analysis = processor.get_pii_analysis()
    print(f"Responses with PII: {pii_analysis['total_with_pii']}")
    print("PII Types Found:", ', '.join(pii_analysis['pii_types'].keys()) if pii_analysis['pii_types'] else "None")

    # 5. Data Quality Report
    print("\n✅ DATA QUALITY REPORT")
    print("-" * 25)
    quality_report = processor.validate_data_quality()
    print(f"Overall Quality: {'✅ PASS' if quality_report['valid'] else '⚠️ ISSUES FOUND'}")
    if quality_report['issues']:
        for issue in quality_report['issues']:
            print(f"  • {issue}")

    print(f"Topic Coverage: {quality_report['metrics']['topic_coverage']:.1%}")
    print(f"Avg Sentiment Confidence: {quality_report['metrics']['avg_sentiment_confidence']:.2f}")

    # 6. Key Insights
    print("\n💡 KEY INSIGHTS")
    print("-" * 15)
    insights = processor.get_insights_summary()
    for i, insight in enumerate(insights, 1):
        print(f"{i}. {insight}")

    # 7. Export Options
    print("\n📁 EXPORT EXAMPLES")
    print("-" * 18)

    # CSV Export
    csv_filename = processor.export_to_csv('demo_export.csv')
    print(f"✅ CSV exported to: {csv_filename}")

    # Chart Configurations
    chart_configs = processor.generate_chart_configs()
    with open('chart_configs.json', 'w') as f:
        json.dump(chart_configs, f, indent=2)
    print("✅ Chart.js configs saved to: chart_configs.json")

    # Topic-Sentiment Matrix
    matrix_data = processor.get_topic_sentiment_matrix()
    with open('topic_sentiment_matrix.json', 'w') as f:
        json.dump(matrix_data, f, indent=2)
    print("✅ Topic-sentiment matrix saved to: topic_sentiment_matrix.json")

    print("\n🎉 JSON processing demo completed!")
    print("\nNext steps:")
    print("1. Use chart_configs.json with Chart.js in your frontend")
    print("2. Import demo_export.csv into Excel for further analysis")
    print("3. Use topic_sentiment_matrix.json for heatmap visualizations")
    print("4. Integrate the AnalyticsDataProcessor class into your backend API")


def generate_react_examples():
    """Generate React component examples using the JSON data"""

    react_examples = {
        "TopicCard": """
// React component using the JSON data
import React from 'react';

const TopicCard = ({ topic }) => {
  const getSentimentColor = (score) => score > 0.6 ? '#28a745' : score > 0.4 ? '#ffc107' : '#dc3545';

  return (
    <div className="topic-card" style={{ border: '1px solid #ddd', padding: '1rem', borderRadius: '8px' }}>
      <h3>{topic.label}</h3>
      <div className="topic-stats">
        <span>{topic.count} responses ({topic.percentage}%)</span>
        <div
          className="sentiment-bar"
          style={{
            background: getSentimentColor(topic.sentiment_mean),
            width: `${topic.sentiment_mean * 100}%`,
            height: '4px',
            borderRadius: '2px'
          }}
        />
      </div>
      <div className="examples">
        {topic.examples.slice(0, 2).map((example, idx) => (
          <blockquote key={idx}>"{example.text}"</blockquote>
        ))}
      </div>
    </div>
  );
};

export default TopicCard;
""",
        "SentimentChart": """
// Chart.js component for sentiment visualization
import React from 'react';
import { Bar } from 'react-chartjs-2';

const SentimentChart = ({ chartData }) => {
  const data = {
    labels: chartData.sentiment_overview.map(item => item.sentiment),
    datasets: [{
      data: chartData.sentiment_overview.map(item => item.count),
      backgroundColor: chartData.sentiment_overview.map(item => item.color),
    }]
  };

  return <Bar data={data} options={{ responsive: true }} />;
};

export default SentimentChart;
""",
        "DataTable": """
// Data table component for responses
import React, { useState } from 'react';

const ResponseTable = ({ responses }) => {
  const [filter, setFilter] = useState('');

  const filteredResponses = responses.filter(r =>
    r.clean_text.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div>
      <input
        type="text"
        placeholder="Search responses..."
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
      />
      <table className="response-table">
        <thead>
          <tr>
            <th>Response</th>
            <th>Topic</th>
            <th>Sentiment</th>
            <th>PII</th>
          </tr>
        </thead>
        <tbody>
          {filteredResponses.map(response => (
            <tr key={response.response_id}>
              <td>{response.clean_text}</td>
              <td>{response.topic_assignment.topic_label}</td>
              <td className={`sentiment-${response.sentiment.sentiment.toLowerCase()}`}>
                {response.sentiment.sentiment}
              </td>
              <td>{response.pii_detected ? '🔒' : ''}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ResponseTable;
"""
    }

    # Save React examples
    with open('react_examples.js', 'w') as f:
        f.write("// React Component Examples for Smart Text Analytics JSON Data\n\n")
        for component_name, code in react_examples.items():
            f.write(f"// {component_name}\n{code}\n\n")

    print("✅ React examples saved to: react_examples.js")


if __name__ == "__main__":
    demo_json_processing()
    generate_react_examples()
