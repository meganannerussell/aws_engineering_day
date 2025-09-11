import { useState } from "react";
import { motion } from "framer-motion";
import type { AnalyticsData, ChartType } from "../types/analytics";
import MetricsHeader from "../components/MetricsHeader";
import ChartCard from "../components/ChartCard";
import TopicFrequencyChart from "../components/charts/TopicFrequencyChart";
import SentimentDistributionChart from "../components/charts/SentimentDistributionChart";
import DarkModeToggle from "../components/DarkModeToggle";
import ExportButton from "../components/ExportButton";
import DatasetAnalyzer from "../components/DatasetAnalyzer";
import ExcitingLoader from "../components/ExcitingLoader";

const Results: React.FC = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [topicChartType, setTopicChartType] = useState<ChartType>("bar");
  const [sentimentChartType, setSentimentChartType] =
    useState<ChartType>("pie");
  const [isDrawerCollapsed, setIsDrawerCollapsed] = useState(false);

  const handleAnalysisComplete = (analyticsData: AnalyticsData) => {
    setData(analyticsData);
    setError(null);
  };

  const handleLoadingChange = (isLoading: boolean) => {
    setLoading(isLoading);
  };

  const handleDrawerToggle = (collapsed: boolean) => {
    setIsDrawerCollapsed(collapsed);
  };

  if (loading) {
    return (
      <div className="results-page">
        <DatasetAnalyzer
          onAnalysisComplete={handleAnalysisComplete}
          onLoadingChange={handleLoadingChange}
          onDrawerToggle={handleDrawerToggle}
        />
        <ExcitingLoader duration={30} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="results-page">
        <DatasetAnalyzer
          onAnalysisComplete={handleAnalysisComplete}
          onLoadingChange={handleLoadingChange}
          onDrawerToggle={handleDrawerToggle}
        />
        <div className="error-state">
          <div className="error-state__icon">⚠️</div>
          <h2 className="error-state__title">Error</h2>
          <p className="error-state__message">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="error-state__button"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="welcome-state">
        <div className="welcome-state__content">
          <h1 className="welcome-state__title">
            Smart Text Analytics Dashboard
          </h1>
          <p className="welcome-state__subtitle">
            Transform unstructured text data into actionable insights using
            advanced AI-powered analysis
          </p>

          <div className="welcome-state__features">
            <div className="feature-item">
              <div className="feature-item__icon">🧠</div>
              <div className="feature-item__content">
                <h3>AI-Powered Topic Discovery</h3>
                <p>
                  Automatically identify key themes using DBSCAN clustering and
                  LLM labeling
                </p>
              </div>
            </div>
            <div className="feature-item">
              <div className="feature-item__icon">😊</div>
              <div className="feature-item__content">
                <h3>Advanced Sentiment Analysis</h3>
                <p>
                  Understand emotional context with sophisticated sentiment
                  detection
                </p>
              </div>
            </div>
            <div className="feature-item">
              <div className="feature-item__icon">📊</div>
              <div className="feature-item__content">
                <h3>Interactive Visualizations</h3>
                <p>
                  Explore your data with dynamic charts and real-time insights
                </p>
              </div>
            </div>
          </div>
        </div>

        <DatasetAnalyzer
          onAnalysisComplete={handleAnalysisComplete}
          onLoadingChange={handleLoadingChange}
          onDrawerToggle={handleDrawerToggle}
        />
      </div>
    );
  }

  return (
    <div
      className={`results-page ${isDrawerCollapsed ? "drawer-collapsed" : ""}`}
    >
      {data ? (
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
                  <DatasetAnalyzer
                    onAnalysisComplete={handleAnalysisComplete}
                    onLoadingChange={handleLoadingChange}
                    onDrawerToggle={handleDrawerToggle}
                  />
                  <ExportButton />
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
                        {Math.round(
                          (topTopics[1].count / totalResponses) * 100
                        )}
                        %)
                      </>
                    )}
                    {topTopics[2] && (
                      <>
                        , and{" "}
                        <strong>{topTopics[2].label.toLowerCase()}</strong> (
                        {Math.round(
                          (topTopics[2].count / totalResponses) * 100
                        )}
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
                  title="Topic Distribution"
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
                            <span>
                              {topic.count.toLocaleString()} responses
                            </span>
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
      ) : (
        <div className="main-content">
          <div className="container results-container">
            <div className="welcome-state">
              <div className="welcome-state__content">
                <h2 className="welcome-state__title">
                  Welcome to Smart Text Analytics
                </h2>
                <p className="welcome-state__message">
                  Select a dataset above and click "Analyze Dataset" to begin
                  processing your survey data with our advanced AI pipeline.
                </p>
                <div className="welcome-state__features">
                  <div className="feature-item">
                    <span className="feature-item__icon">🧮</span>
                    <span className="feature-item__text">
                      DBSCAN Clustering
                    </span>
                  </div>
                  <div className="feature-item">
                    <span className="feature-item__icon">🏷️</span>
                    <span className="feature-item__text">
                      LLM Topic Labeling
                    </span>
                  </div>
                  <div className="feature-item">
                    <span className="feature-item__icon">😊</span>
                    <span className="feature-item__text">
                      Sentiment Analysis
                    </span>
                  </div>
                  <div className="feature-item">
                    <span className="feature-item__icon">🔒</span>
                    <span className="feature-item__text">PII Detection</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Results;
