import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";
import type { Topic, ChartType } from "../../types/analytics";
import { getSentimentColor } from "../../lib/utils";

interface SentimentDistributionChartProps {
  topics: Topic[];
  chartType: ChartType;
}

const SentimentDistributionChart: React.FC<SentimentDistributionChartProps> = ({
  topics,
  chartType,
}) => {
  // Aggregate sentiment data from all topics
  const sentimentData = topics.reduce(
    (acc, topic) => {
      const { sentiment_distribution } = topic;
      acc.positive += sentiment_distribution.positive;
      acc.negative += sentiment_distribution.negative;
      acc.neutral += sentiment_distribution.neutral;
      acc.mixed += sentiment_distribution.mixed;
      return acc;
    },
    { positive: 0, negative: 0, neutral: 0, mixed: 0 }
  );

  console.log('SentimentDistributionChart - topics:', topics.length, 'sentimentData:', sentimentData, 'chartType:', chartType);

  const total = Object.values(sentimentData).reduce(
    (sum, count) => sum + count,
    0
  );

  const chartData = Object.entries(sentimentData)
    .filter(([_, count]) => count > 0)
    .map(([sentiment, count]) => ({
      sentiment: sentiment.charAt(0).toUpperCase() + sentiment.slice(1),
      count,
      percentage: ((count / total) * 100).toFixed(1),
    }))
    .sort((a, b) => b.count - a.count);

  const colors = chartData.map((item) => getSentimentColor(item.sentiment));

  const renderChart = () => {
    switch (chartType) {
      case "pie":
        return (
          <ResponsiveContainer width="100%" height={500}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ sentiment, percentage }) =>
                  `${sentiment} (${percentage}%)`
                }
                outerRadius={120}
                fill="#8884d8"
                dataKey="count"
              >
                {chartData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={colors[index]} />
                ))}
              </Pie>
              <Tooltip
                formatter={(value: number, _: string, props: any) => [
                  `${value.toLocaleString()} (${props.payload.percentage}%)`,
                  "Responses",
                ]}
                labelFormatter={(label: string) => `Sentiment: ${label}`}
              />
            </PieChart>
          </ResponsiveContainer>
        );

      case "donut":
        return (
          <ResponsiveContainer width="100%" height={500}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ sentiment, percentage }) =>
                  `${sentiment} (${percentage}%)`
                }
                innerRadius={60}
                outerRadius={120}
                fill="#8884d8"
                dataKey="count"
              >
                {chartData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={colors[index]} />
                ))}
              </Pie>
              <Tooltip
                formatter={(value: number, _: string, props: any) => [
                  `${value.toLocaleString()} (${props.payload.percentage}%)`,
                  "Responses",
                ]}
                labelFormatter={(label: string) => `Sentiment: ${label}`}
              />
            </PieChart>
          </ResponsiveContainer>
        );

      case "bar":
        return (
          <ResponsiveContainer width="100%" height={500}>
            <BarChart
              data={chartData}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
              <XAxis dataKey="sentiment" fontSize={12} />
              <YAxis
                fontSize={12}
                tickFormatter={(value) => value.toLocaleString()}
              />
              <Tooltip
                formatter={(value: number, _: string, props: any) => [
                  `${value.toLocaleString()} (${props.payload.percentage}%)`,
                  "Responses",
                ]}
                labelFormatter={(label: string) => `Sentiment: ${label}`}
              />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {chartData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={colors[index]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        );

      default:
        return null;
    }
  };

  if (chartData.length === 0) {
    return (
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          height: "500px",
          color: "#6b7280",
        }}
      >
        <p>No sentiment data available</p>
      </div>
    );
  }

  return <div style={{ width: "100%", height: "500px" }}>{renderChart()}</div>;
};

export default SentimentDistributionChart;
