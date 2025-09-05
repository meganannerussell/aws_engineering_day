import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from "recharts";
import type { Topic, ChartType } from "../../types/analytics";
import { getChartColors } from "../../lib/utils";

interface TopicFrequencyChartProps {
  topics: Topic[];
  chartType: ChartType;
}

const TopicFrequencyChart: React.FC<TopicFrequencyChartProps> = ({
  topics,
  chartType,
}) => {
  // Sort topics by count and take top 10
  const sortedTopics = [...topics]
    .sort((a, b) => b.count - a.count)
    .slice(0, 10);

  const colors = getChartColors(sortedTopics.length);

  const renderChart = () => {
    switch (chartType) {
      case "bar":
        return (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart
              data={sortedTopics}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
              <XAxis
                dataKey="label"
                angle={-45}
                textAnchor="end"
                height={100}
                fontSize={12}
                interval={0}
              />
              <YAxis
                fontSize={12}
                tickFormatter={(value) => value.toLocaleString()}
              />
              <Tooltip
                formatter={(value: number) => [
                  value.toLocaleString(),
                  "Responses",
                ]}
                labelFormatter={(label: string) => `Topic: ${label}`}
                contentStyle={{
                  backgroundColor: "white",
                  border: "1px solid #e5e7eb",
                  borderRadius: "8px",
                  boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                }}
              />
              <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        );

      case "pie":
        return (
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={sortedTopics}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ label, percent }) =>
                  `${label.slice(0, 15)}${label.length > 15 ? "..." : ""} (${(
                    (percent || 0) * 100
                  ).toFixed(1)}%)`
                }
                outerRadius={120}
                fill="#8884d8"
                dataKey="count"
              >
                {sortedTopics.map((_, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={colors[index % colors.length]}
                  />
                ))}
              </Pie>
              <Tooltip
                formatter={(value: number) => [
                  value.toLocaleString(),
                  "Responses",
                ]}
                labelFormatter={(label: string) => `Topic: ${label}`}
              />
            </PieChart>
          </ResponsiveContainer>
        );

      case "line":
        return (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart
              data={sortedTopics}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
              <XAxis
                dataKey="label"
                angle={-45}
                textAnchor="end"
                height={100}
                fontSize={12}
                interval={0}
              />
              <YAxis
                fontSize={12}
                tickFormatter={(value) => value.toLocaleString()}
              />
              <Tooltip
                formatter={(value: number) => [
                  value.toLocaleString(),
                  "Responses",
                ]}
                labelFormatter={(label: string) => `Topic: ${label}`}
              />
              <Line
                type="monotone"
                dataKey="count"
                stroke="#3b82f6"
                strokeWidth={3}
                dot={{ fill: "#3b82f6", strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, stroke: "#3b82f6", strokeWidth: 2 }}
              />
            </LineChart>
          </ResponsiveContainer>
        );

      default:
        return null;
    }
  };

  if (sortedTopics.length === 0) {
    return (
      <div className="flex items-center justify-center h-96 text-gray-500">
        <p>No topic data available</p>
      </div>
    );
  }

  return <div className="w-full">{renderChart()}</div>;
};

export default TopicFrequencyChart;
