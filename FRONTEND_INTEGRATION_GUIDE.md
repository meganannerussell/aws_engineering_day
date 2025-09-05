# Frontend Integration Guide
## Smart Text Analytics Pipeline - AWS Engineering Day Hackathon

This guide shows frontend engineers how to integrate with the Smart Text Analytics Pipeline output and build compelling visualizations.

## 📋 Quick Reference

### Key Files
- `frontend_example_output.json` - Complete example response
- `frontend_types.ts` - TypeScript interfaces
- This guide - Implementation examples

### Main Data Structure
```typescript
interface SmartTextAnalyticsOutput {
  project_metadata: ProjectMetadata;    // Project info & processing stats
  summary_stats: SummaryStats;          // High-level metrics
  topics: Topic[];                      // Main topics with sentiment
  responses: Response[];                // Individual response details
  chart_data: ChartData;               // Pre-formatted chart data
  export_formats: ExportFormats;       // Download links
  api_info: ApiInfo;                   // API metadata
}
```

## 🎨 React Component Examples

### 1. Topic Overview Cards

```jsx
import React from 'react';
import { Topic, SentimentType } from './frontend_types';

const TopicCard = ({ topic, showExamples = true }) => {
  const getSentimentColor = (sentiment_mean) => {
    if (sentiment_mean > 0.6) return '#32CD32'; // Green
    if (sentiment_mean > 0.4) return '#FFD700'; // Yellow
    return '#DC143C'; // Red
  };

  const getSentimentEmoji = (sentiment_mean) => {
    if (sentiment_mean > 0.6) return '😊';
    if (sentiment_mean > 0.4) return '😐';
    return '😞';
  };

  return (
    <div className="topic-card">
      <div className="topic-header">
        <h3 className="topic-title">
          {topic.label} {getSentimentEmoji(topic.sentiment_mean)}
        </h3>
        <div className="topic-stats">
          <span className="response-count">{topic.count} responses</span>
          <span className="percentage">({topic.percentage}%)</span>
        </div>
      </div>

      <div className="sentiment-bar">
        <div 
          className="sentiment-fill"
          style={{
            width: `${topic.sentiment_mean * 100}%`,
            backgroundColor: getSentimentColor(topic.sentiment_mean)
          }}
        />
        <span className="sentiment-score">
          {(topic.sentiment_mean * 100).toFixed(1)}% positive
        </span>
      </div>

      <div className="sentiment-distribution">
        <div className="sentiment-breakdown">
          <span className="positive">👍 {topic.sentiment_distribution.positive}</span>
          <span className="neutral">😐 {topic.sentiment_distribution.neutral}</span>
          <span className="negative">👎 {topic.sentiment_distribution.negative}</span>
        </div>
      </div>

      {showExamples && (
        <div className="topic-examples">
          <h4>Sample Responses:</h4>
          {topic.examples.slice(0, 2).map((example, idx) => (
            <blockquote key={idx} className="example-quote">
              "{example.text}"
              <cite className="sentiment-badge sentiment-{example.sentiment.toLowerCase()}">
                {example.sentiment} ({(example.confidence * 100).toFixed(0)}%)
              </cite>
            </blockquote>
          ))}
        </div>
      )}

      {topic.trend_data && (
        <div className="trend-indicator">
          <span className={`trend trend-${topic.trend_data.sentiment_trend}`}>
            {topic.trend_data.sentiment_trend === 'improving' ? '📈' : 
             topic.trend_data.sentiment_trend === 'declining' ? '📉' : '➡️'}
            {topic.trend_data.sentiment_trend} trend
          </span>
        </div>
      )}
    </div>
  );
};
```

### 2. Dashboard Summary

```jsx
const AnalyticsDashboard = ({ data }) => {
  return (
    <div className="analytics-dashboard">
      <header className="dashboard-header">
        <h1>{data.project_metadata.project_title}</h1>
        <div className="processing-info">
          <span>Processed {data.project_metadata.total_responses} responses</span>
          <span>in {data.project_metadata.processing_time_seconds}s</span>
        </div>
      </header>

      {/* Key Metrics */}
      <div className="metrics-grid">
        <div className="metric-card">
          <h3>Overall Sentiment</h3>
          <div className="metric-value sentiment-positive">
            {(data.summary_stats.overall_sentiment_score * 100).toFixed(1)}%
          </div>
          <div className="metric-subtitle">Positive sentiment</div>
        </div>

        <div className="metric-card">
          <h3>Topics Found</h3>
          <div className="metric-value">{data.summary_stats.total_topics}</div>
          <div className="metric-subtitle">Unique themes identified</div>
        </div>

        <div className="metric-card">
          <h3>PII Protected</h3>
          <div className="metric-value pii-protected">
            {data.project_metadata.quality_metrics.pii_detected_count}
          </div>
          <div className="metric-subtitle">Items redacted</div>
        </div>

        <div className="metric-card">
          <h3>Processing Quality</h3>
          <div className="metric-value">
            {(data.project_metadata.quality_metrics.clustering_confidence * 100).toFixed(0)}%
          </div>
          <div className="metric-subtitle">Clustering confidence</div>
        </div>
      </div>

      {/* Topics Grid */}
      <div className="topics-section">
        <h2>Topics Overview</h2>
        <div className="topics-grid">
          {data.topics.slice(0, 6).map(topic => (
            <TopicCard key={topic.topic_id} topic={topic} />
          ))}
        </div>
      </div>
    </div>
  );
};
```

### 3. Chart Components (with Chart.js)

```jsx
import { Doughnut, Bar, Line } from 'react-chartjs-2';

// Topic Distribution Pie Chart
const TopicDistributionChart = ({ chartData }) => {
  const data = {
    labels: chartData.topic_distribution.map(item => item.label),
    datasets: [{
      data: chartData.topic_distribution.map(item => item.value),
      backgroundColor: chartData.topic_distribution.map(item => item.color),
      borderWidth: 2,
      borderColor: '#fff'
    }]
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { position: 'right' },
      title: { display: true, text: 'Response Distribution by Topic' }
    }
  };

  return <Doughnut data={data} options={options} />;
};

// Sentiment by Topic Bar Chart
const SentimentByTopicChart = ({ chartData }) => {
  const data = {
    labels: chartData.sentiment_by_topic.map(item => item.topic),
    datasets: [
      {
        label: 'Positive',
        data: chartData.sentiment_by_topic.map(item => item.positive),
        backgroundColor: '#32CD32'
      },
      {
        label: 'Neutral', 
        data: chartData.sentiment_by_topic.map(item => item.neutral),
        backgroundColor: '#FFD700'
      },
      {
        label: 'Negative',
        data: chartData.sentiment_by_topic.map(item => item.negative),
        backgroundColor: '#DC143C'
      }
    ]
  };

  const options = {
    responsive: true,
    scales: { x: { stacked: true }, y: { stacked: true } },
    plugins: {
      title: { display: true, text: 'Sentiment Distribution by Topic' }
    }
  };

  return <Bar data={data} options={options} />;
};

// Trend Line Chart
const TrendChart = ({ chartData }) => {
  const topics = Object.keys(chartData.timeline_data[0]?.topics || {});
  
  const datasets = topics.map((topic, idx) => ({
    label: topic,
    data: chartData.timeline_data.map(period => 
      period.topics[topic]?.sentiment || 0
    ),
    borderColor: `hsl(${idx * 60}, 70%, 50%)`,
    backgroundColor: `hsl(${idx * 60}, 70%, 50%, 0.1)`,
    fill: false
  }));

  const data = {
    labels: chartData.timeline_data.map(item => item.period),
    datasets
  };

  const options = {
    responsive: true,
    plugins: {
      title: { display: true, text: 'Sentiment Trends Over Time' }
    },
    scales: {
      y: { 
        beginAtZero: true, 
        max: 1,
        title: { display: true, text: 'Sentiment Score' }
      }
    }
  };

  return <Line data={data} options={options} />;
};
```

### 4. Response Explorer with Filters

```jsx
const ResponseExplorer = ({ responses, topics }) => {
  const [filters, setFilters] = useState({
    topicId: '',
    sentiment: '',
    piiOnly: false,
    searchTerm: ''
  });

  const filteredResponses = responses.filter(response => {
    if (filters.topicId && response.topic_assignment.topic_id !== filters.topicId) {
      return false;
    }
    if (filters.sentiment && response.sentiment.sentiment !== filters.sentiment) {
      return false;
    }
    if (filters.piiOnly && !response.pii_detected) {
      return false;
    }
    if (filters.searchTerm && 
        !response.clean_text.toLowerCase().includes(filters.searchTerm.toLowerCase())) {
      return false;
    }
    return true;
  });

  return (
    <div className="response-explorer">
      <div className="filters">
        <select 
          value={filters.topicId} 
          onChange={(e) => setFilters({...filters, topicId: e.target.value})}
        >
          <option value="">All Topics</option>
          {topics.map(topic => (
            <option key={topic.topic_id} value={topic.topic_id}>
              {topic.label}
            </option>
          ))}
        </select>

        <select 
          value={filters.sentiment}
          onChange={(e) => setFilters({...filters, sentiment: e.target.value})}
        >
          <option value="">All Sentiments</option>
          <option value="POSITIVE">Positive</option>
          <option value="NEUTRAL">Neutral</option>
          <option value="NEGATIVE">Negative</option>
        </select>

        <label>
          <input
            type="checkbox"
            checked={filters.piiOnly}
            onChange={(e) => setFilters({...filters, piiOnly: e.target.checked})}
          />
          PII Detected Only
        </label>

        <input
          type="text"
          placeholder="Search responses..."
          value={filters.searchTerm}
          onChange={(e) => setFilters({...filters, searchTerm: e.target.value})}
        />
      </div>

      <div className="results-summary">
        Showing {filteredResponses.length} of {responses.length} responses
      </div>

      <div className="responses-list">
        {filteredResponses.map(response => (
          <div key={response.response_id} className="response-card">
            <div className="response-header">
              <span className="response-id">{response.response_id}</span>
              <span className={`sentiment-badge sentiment-${response.sentiment.sentiment.toLowerCase()}`}>
                {response.sentiment.sentiment} ({(response.sentiment.confidence * 100).toFixed(0)}%)
              </span>
              {response.pii_detected && (
                <span className="pii-badge">🔒 PII Protected</span>
              )}
            </div>
            
            <div className="response-text">
              {response.clean_text}
            </div>
            
            <div className="response-meta">
              <span className="topic-assignment">
                📂 {response.topic_assignment.topic_label}
              </span>
              <span className="word-count">
                📝 {response.metadata.word_count} words
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

## 🎨 CSS Styling Guide

```css
/* Topic Cards */
.topic-card {
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  padding: 1.5rem;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.topic-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.topic-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.topic-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  color: #2c3e50;
}

.topic-stats {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  font-size: 0.875rem;
  color: #6c757d;
}

/* Sentiment Bar */
.sentiment-bar {
  position: relative;
  height: 24px;
  background-color: #f8f9fa;
  border-radius: 12px;
  margin-bottom: 1rem;
  overflow: hidden;
}

.sentiment-fill {
  height: 100%;
  border-radius: 12px;
  transition: width 0.3s ease;
}

.sentiment-score {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.75rem;
  font-weight: 500;
  color: #495057;
}

/* Sentiment Distribution */
.sentiment-breakdown {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.sentiment-breakdown span {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

/* Examples */
.topic-examples {
  margin-top: 1rem;
}

.example-quote {
  font-style: italic;
  color: #6c757d;
  margin: 0.5rem 0;
  padding-left: 1rem;
  border-left: 3px solid #e9ecef;
  position: relative;
}

.sentiment-badge {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  margin-left: 0.5rem;
}

.sentiment-positive { background: #d4edda; color: #155724; }
.sentiment-neutral { background: #fff3cd; color: #856404; }
.sentiment-negative { background: #f8d7da; color: #721c24; }

/* Dashboard Layout */
.analytics-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.dashboard-header {
  text-align: center;
  margin-bottom: 2rem;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.metric-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  text-align: center;
  border: 1px solid #e1e5e9;
}

.metric-value {
  font-size: 2rem;
  font-weight: bold;
  margin: 0.5rem 0;
}

.sentiment-positive { color: #28a745; }
.pii-protected { color: #6f42c1; }

.topics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

/* Response Explorer */
.response-explorer {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #e1e5e9;
}

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  align-items: center;
}

.filters select, .filters input[type="text"] {
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
}

.response-card {
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 1rem;
  background: #f8f9fa;
}

.response-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.response-meta {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #6c757d;
}

.pii-badge {
  background: #6f42c1;
  color: white;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
}
```

## 📡 API Integration Examples

### React Hook for Data Fetching

```javascript
import { useState, useEffect } from 'react';

const useAnalyticsData = (processingId) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/analytics/${processingId}`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (processingId) {
      fetchData();
    }
  }, [processingId]);

  return { data, loading, error };
};

// Usage in component
const AnalyticsPage = ({ processingId }) => {
  const { data, loading, error } = useAnalyticsData(processingId);

  if (loading) return <div>Loading analytics...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!data) return <div>No data available</div>;

  return <AnalyticsDashboard data={data} />;
};
```

### Real-time Processing Updates

```javascript
const useProcessingUpdates = (processingId) => {
  const [updates, setUpdates] = useState(null);

  useEffect(() => {
    const eventSource = new EventSource(`/api/processing/${processingId}/updates`);
    
    eventSource.onmessage = (event) => {
      const update = JSON.parse(event.data);
      setUpdates(update);
    };

    eventSource.onerror = () => {
      eventSource.close();
    };

    return () => eventSource.close();
  }, [processingId]);

  return updates;
};

// Progress indicator component
const ProcessingProgress = ({ processingId }) => {
  const updates = useProcessingUpdates(processingId);

  if (!updates) return null;

  return (
    <div className="processing-progress">
      <div className="progress-bar">
        <div 
          className="progress-fill" 
          style={{ width: `${updates.progress_percentage}%` }}
        />
      </div>
      <div className="progress-info">
        <span>{updates.current_step_description}</span>
        <span>{updates.progress_percentage}% complete</span>
      </div>
    </div>
  );
};
```

## 📊 Data Visualization Best Practices

### 1. Topic Distribution
- Use pie/doughnut charts for topic distribution
- Limit to top 10 topics, group others as "Other"
- Use consistent color palette across all charts

### 2. Sentiment Analysis
- Use traffic light colors: Green (positive), Yellow (neutral), Red (negative)
- Show confidence scores when space permits
- Consider stacked bar charts for sentiment by topic

### 3. Trend Analysis
- Use line charts for time-series data
- Highlight significant changes with annotations
- Include comparison periods when available

### 4. Response Explorer
- Implement virtual scrolling for large datasets
- Use search and filter capabilities
- Highlight PII-protected responses clearly

## 🔧 Performance Tips

1. **Lazy Loading**: Load topic details on demand
2. **Virtual Scrolling**: For large response lists
3. **Memoization**: Cache chart data transformations
4. **Pagination**: Limit initial data load
5. **Search Debouncing**: Delay search API calls

## 📱 Mobile Considerations

- Stack metric cards vertically on mobile
- Use horizontal scrolling for topic cards
- Simplify charts for small screens
- Make touch targets at least 44px

## 🎯 Key Integration Points

### Dashboard Entry Points
1. **Project List** → Select project → Analytics dashboard
2. **Real-time Processing** → Progress indicator → Results
3. **Historical Data** → Comparison views → Trends

### Export Capabilities
- CSV downloads for raw data
- Excel reports with formatting
- PowerPoint summaries for presentations
- API endpoints for custom integrations

---

*This integration guide provides everything your frontend team needs to build compelling visualizations for the Smart Text Analytics Pipeline. The examples are production-ready and follow modern React best practices.*