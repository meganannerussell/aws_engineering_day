import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import type { AnalyticsData, ChartType } from "../types/analytics";
import MetricsHeader from "../components/MetricsHeader";
import ChartCard from "../components/ChartCard";
import TopicFrequencyChart from "../components/charts/TopicFrequencyChart";
import SentimentDistributionChart from "../components/charts/SentimentDistributionChart";
import DarkModeToggle from "../components/DarkModeToggle";

const Results: React.FC = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [topicChartType, setTopicChartType] = useState<ChartType>("bar");
  const [sentimentChartType, setSentimentChartType] =
    useState<ChartType>("pie");
  const [selectedDataset, setSelectedDataset] = useState<string>(
    "hackathon_demo_results.json"
  );

  const datasets = [
    {
      value: "hackathon_demo_results.json",
      label: "Beauty Products Survey",
    },
    {
      value: "customer_service_analysis.json",
      label: "Customer Service Experience",
    },
    {
      value: "product_feedback_analysis.json",
      label: "Mobile App User Experience",
    },
  ];

  const loadData = async (filename: string) => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`/${filename}`);
      if (!response.ok) {
        throw new Error(`Failed to load data from ${filename}`);
      }
      const analyticsData: AnalyticsData = await response.json();
      setData(analyticsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData(selectedDataset);
  }, [selectedDataset]);

  const handleDatasetChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedDataset(event.target.value);
  };

  if (loading) {
    return (
      <div className="loading-state">
        <div className="loading-spinner"></div>
        <p className="loading-state__text">Loading analytics data...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="error-state">
        <div className="error-state__icon">⚠️</div>
        <h2 className="error-state__title">Error</h2>
        <p className="error-state__message">{error || "No data available"}</p>
        <button
          onClick={() => window.location.reload()}
          className="error-state__button"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="results-page">
      {/* Dataset Sidebar */}
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
        className="dataset-sidebar"
      >
        <div className="dataset-sidebar__content">
          <h3 className="dataset-sidebar__title">
            <span className="dataset-sidebar__icon">📊</span>
            Analytics Datasets
          </h3>
          <div className="dataset-selector-enhanced">
            <label
              htmlFor="dataset-select"
              className="dataset-selector-enhanced__label"
            >
              Select Dataset:
            </label>
            <select
              id="dataset-select"
              value={selectedDataset}
              onChange={handleDatasetChange}
              className="dataset-selector-enhanced__select"
            >
              {datasets.map((dataset) => (
                <option key={dataset.value} value={dataset.value}>
                  {dataset.label}
                </option>
              ))}
            </select>
          </div>
          {data && (
            <div className="dataset-sidebar__info">
              <div className="dataset-info-card">
                <h4 className="dataset-info-card__title">Current Dataset</h4>
                <p className="dataset-info-card__project">
                  {data.project_metadata.project_title}
                </p>
                <div className="dataset-info-card__stats">
                  <div className="stat-mini">
                    <span className="stat-mini__value">
                      {data.project_metadata.total_responses.toLocaleString()}
                    </span>
                    <span className="stat-mini__label">Responses</span>
                  </div>
                  <div className="stat-mini">
                    <span className="stat-mini__value">
                      {data.topics.length}
                    </span>
                    <span className="stat-mini__label">Topics</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* This is Fine GIF */}
          <div className="dataset-sidebar__gif">
            <img
              src="/src/assets/fire-fine.gif"
              alt="This is fine"
              className="this-is-fine-gif"
            />
          </div>
        </div>
      </motion.div>

      <div className="main-content">
        <div className="container results-container">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="header"
          >
            <div className="header__content">
              <div className="header__text">
                <h1 className="header__title">
                  {data.project_metadata.project_title}
                </h1>
                <p className="header__subtitle">
                  {data.project_metadata.question_text}
                </p>
                <div className="header__meta">
                  Analysis completed on{" "}
                  {new Date(data.project_metadata.timestamp).toLocaleString()}
                </div>
              </div>
              <div className="header__actions">
                <DarkModeToggle />
              </div>
            </div>
          </motion.div>
          {/* Summary Text */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="summary-narrative"
          >
            {(() => {
              const totalResponses = data.topics.reduce(
                (sum, topic) => sum + topic.count,
                0
              );
              const topTopics = [...data.topics]
                .sort((a, b) => b.count - a.count)
                .slice(0, 3);

              const totalSentimentAnalyzed = data.topics.reduce(
                (sum, topic) =>
                  sum +
                  topic.sentiment_distribution.positive +
                  topic.sentiment_distribution.negative +
                  topic.sentiment_distribution.neutral +
                  topic.sentiment_distribution.mixed,
                0
              );

              const totalPositive = data.topics.reduce(
                (sum, topic) => sum + topic.sentiment_distribution.positive,
                0
              );
              const totalNegative = data.topics.reduce(
                (sum, topic) => sum + topic.sentiment_distribution.negative,
                0
              );

              const positivePercentage =
                (totalPositive / totalSentimentAnalyzed) * 100;
              const negativePercentage =
                (totalNegative / totalSentimentAnalyzed) * 100;

              return (
                <p className="summary-narrative__text">
                  The most frequently cited aspects that respondents mentioned
                  were <strong>{topTopics[0]?.label.toLowerCase()}</strong> (
                  {Math.round(
                    ((topTopics[0]?.count || 0) / totalResponses) * 100
                  )}
                  %)
                  {topTopics[1] && (
                    <>
                      , <strong>{topTopics[1].label.toLowerCase()}</strong> (
                      {Math.round((topTopics[1].count / totalResponses) * 100)}
                      %)
                    </>
                  )}
                  {topTopics[2] && (
                    <>
                      , and <strong>{topTopics[2].label.toLowerCase()}</strong>{" "}
                      ({Math.round((topTopics[2].count / totalResponses) * 100)}
                      %)
                    </>
                  )}
                  . Sentiment analysis reveals positive feedback (
                  {Math.round(positivePercentage)}% positive vs{" "}
                  {Math.round(negativePercentage)}% negative).
                </p>
              );
            })()}
          </motion.div>
          {/* Metrics Header */}
          <MetricsHeader data={data} />
          {/* Charts Section */}
          <div className="charts-grid">
            {/* Topic Frequency Chart */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <ChartCard
                title="Topic Frequency"
                description="Distribution of responses across identified themes"
                chartType={topicChartType}
                onChartTypeChange={setTopicChartType}
                availableTypes={["bar", "pie", "line"]}
              >
                <TopicFrequencyChart
                  topics={data.topics}
                  chartType={topicChartType}
                />
              </ChartCard>
            </motion.div>

            {/* Sentiment Distribution Chart */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              <ChartCard
                title="Sentiment Distribution"
                description="Overall sentiment analysis of responses"
                chartType={sentimentChartType}
                onChartTypeChange={setSentimentChartType}
                availableTypes={["pie", "donut", "bar"]}
              >
                <SentimentDistributionChart
                  topics={data.topics}
                  chartType={sentimentChartType}
                />
              </ChartCard>
            </motion.div>
          </div>

          {/* Top Themes Identified Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="topic-details"
          >
            <div className="topic-details__header">
              <h3 className="topic-details__title">Top Themes Identified</h3>
              <p className="topic-details__description">
                Most frequently mentioned themes with example responses and
                sentiment breakdown
              </p>
            </div>
            <div className="topic-details__list">
              {data.topics
                .sort((a, b) => b.count - a.count)
                .slice(0, 5)
                .map((topic, index) => (
                  <motion.div
                    key={topic.topic_id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                    className="topic-item"
                    style={{ "--index": index } as React.CSSProperties}
                  >
                    <div className="topic-item__header">
                      <div style={{ flex: 1 }}>
                        <h4 className="topic-item__title">{topic.label}</h4>
                        <div className="topic-item__stats">
                          <span>{topic.count.toLocaleString()} responses</span>
                        </div>
                        <div className="topic-item__sentiment-tags">
                          {topic.sentiment_distribution.positive > 0 && (
                            <span className="sentiment-tag sentiment-tag--positive">
                              {topic.sentiment_distribution.positive} positive
                            </span>
                          )}
                          {topic.sentiment_distribution.negative > 0 && (
                            <span className="sentiment-tag sentiment-tag--negative">
                              {topic.sentiment_distribution.negative} negative
                            </span>
                          )}
                          {topic.sentiment_distribution.neutral > 0 && (
                            <span className="sentiment-tag sentiment-tag--neutral">
                              {topic.sentiment_distribution.neutral} neutral
                            </span>
                          )}
                          {topic.sentiment_distribution.mixed > 0 && (
                            <span className="sentiment-tag sentiment-tag--mixed">
                              {topic.sentiment_distribution.mixed} mixed
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="topic-item__number">#{index + 1}</div>
                    </div>

                    <div className="topic-item__examples">
                      <p className="topic-item__examples-title">
                        Example responses:
                      </p>
                      <div>
                        {topic.examples
                          .slice(0, 2)
                          .map((example, exampleIndex) => (
                            <div
                              key={exampleIndex}
                              className="topic-item__example"
                            >
                              "{example}"
                            </div>
                          ))}
                      </div>
                    </div>
                  </motion.div>
                ))}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default Results;
