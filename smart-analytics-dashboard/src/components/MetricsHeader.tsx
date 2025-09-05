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
      color: "text-blue-600",
      bgColor: "bg-blue-50",
    },
    {
      title: "Total Responses",
      value: formatNumber(project_metadata.total_responses),
      description: "Survey responses analyzed",
      icon: Users,
      color: "text-green-600",
      bgColor: "bg-green-50",
    },
    {
      title: "Avg. Confidence",
      value: formatConfidence(avgConfidence),
      description: "Average sentiment confidence",
      icon: Target,
      color: "text-purple-600",
      bgColor: "bg-purple-50",
    },
    {
      title: "Processing Time",
      value: formatTime(project_metadata.processing_time_seconds),
      description: "Analysis completion time",
      icon: Clock,
      color: "text-orange-600",
      bgColor: "bg-orange-50",
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
              <div
                className={`metric-card__icon ${metric.bgColor
                  .replace("bg-", "")
                  .replace("-50", "")}`}
              >
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
