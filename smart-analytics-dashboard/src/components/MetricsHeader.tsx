import { motion } from "framer-motion";
import { BarChart3, Users, Clock, Target } from "lucide-react";
import type { AnalyticsData } from "../types/analytics";
import { formatNumber, formatTime, formatConfidence } from "../lib/utils";

interface MetricsHeaderProps {
  data: AnalyticsData;
}

const MetricsHeader: React.FC<MetricsHeaderProps> = ({ data }) => {
  const { project_metadata, topics } = data;

  // Calculate average confidence score from topics
  const avgConfidence =
    topics.length > 0
      ? topics.reduce((sum, topic) => sum + topic.sentiment_mean, 0) /
        topics.length
      : 0;

  const metrics = [
    {
      title: "Topics Detected",
      value: topics.length,
      description: "Distinct themes identified",
      icon: BarChart3,
      iconClass: "metric-card__icon--blue",
    },
    {
      title: "Total Responses",
      value: formatNumber(project_metadata.total_responses),
      description: "Survey responses analyzed",
      icon: Users,
      iconClass: "metric-card__icon--green",
    },
    {
      title: "Avg. Sentiment",
      value: formatConfidence(avgConfidence),
      description: "Average sentiment",
      icon: Target,
      iconClass: "metric-card__icon--purple",
    },
    {
      title: "Processing Time",
      value: formatTime(project_metadata.processing_time_seconds),
      description: "Analysis completion time",
      icon: Clock,
      iconClass: "metric-card__icon--orange",
    },
  ];

  return (
    <div className="metrics-grid">
      {metrics.map((metric, index) => {
        const Icon = metric.icon;
        return (
          <motion.div
            key={metric.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            className="metric-card"
            style={{ "--index": index } as React.CSSProperties}
          >
            <div className="metric-card__header">
              <div style={{ flex: 1 }}>
                <p className="metric-card__title">{metric.title}</p>
                <p className="metric-card__value">{metric.value}</p>
                <p className="metric-card__description">{metric.description}</p>
              </div>
              <div className={`metric-card__icon ${metric.iconClass}`}>
                <Icon style={{ width: "1.5rem", height: "1.5rem" }} />
              </div>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
};

export default MetricsHeader;
