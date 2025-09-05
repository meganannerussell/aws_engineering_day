import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import type { AnalyticsData, ChartType } from "../types/analytics";
import MetricsHeader from "../components/MetricsHeader";
import ChartCard from "../components/ChartCard";
import TopicFrequencyChart from "../components/charts/TopicFrequencyChart";
import SentimentDistributionChart from "../components/charts/SentimentDistributionChart";

const Results: React.FC = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [topicChartType, setTopicChartType] = useState<ChartType>("bar");
  const [sentimentChartType, setSentimentChartType] =
    useState<ChartType>("pie");

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const response = await fetch("/hackathon_demo_results.json");
        if (!response.ok) {
          throw new Error("Failed to load data");
        }
        const analyticsData: AnalyticsData = await response.json();
        setData(analyticsData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "An error occurred");
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

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
    <div style={{ minHeight: "100vh", backgroundColor: "#f9fafb" }}>
      <div
        className="container"
        style={{ paddingTop: "2rem", paddingBottom: "2rem" }}
      >
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="header"
        >
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

        {/* Topic Details Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="topic-details"
        >
          <div className="topic-details__header">
            <h3 className="topic-details__title">Topic Details</h3>
            <p className="topic-details__description">
              Detailed breakdown of each identified topic with example responses
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
                        <span>•</span>
                        <span>
                          {(topic.sentiment_mean * 100).toFixed(1)}% avg
                          confidence
                        </span>
                      </div>
                    </div>
                    <div className="topic-item__rank">#{index + 1}</div>
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
  );
};

export default Results;
