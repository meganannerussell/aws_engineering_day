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
import { useTheme } from "../../contexts/ThemeContext";
import React from "react";

interface TopicFrequencyChartProps {
  topics: Topic[];
  chartType: ChartType;
}

// Custom tick component for X-axis labels
const CustomTick = (props: any) => {
  const { x, y, payload } = props;

  return (
    <g>
      <text
        x={x}
        y={y}
        textAnchor="end"
        fill="#666"
        fontSize="12"
        transform={`rotate(-60, ${x}, ${y})`}
      >
        {payload.value}
      </text>
    </g>
  );
};

const TopicFrequencyChart: React.FC<TopicFrequencyChartProps> = ({
  topics,
  chartType,
}) => {
  const { theme } = useTheme();

  // Sort topics by count and take top 10
  const sortedTopics = [...topics]
    .sort((a, b) => b.count - a.count)
    .slice(0, 10);

  console.log(
    "TopicFrequencyChart - topics:",
    topics.length,
    "sortedTopics:",
    sortedTopics.length,
    "chartType:",
    chartType
  );

  const colors = getChartColors(sortedTopics.length);

  const renderChart = () => {
    switch (chartType) {
      case "bar":
        return (
          <ResponsiveContainer width="100%" height={500}>
            <BarChart
              data={sortedTopics}
              margin={{ top: 20, right: 30, left: 20, bottom: 80 }}
            >
              <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
              <XAxis
                dataKey="label"
                height={120}
                interval={0}
                tick={<CustomTick />}
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
                  backgroundColor:
                    theme === "dark" ? "rgba(0, 0, 0, 0.9)" : "white",
                  border:
                    theme === "dark"
                      ? "1px solid #374151"
                      : "1px solid #e5e7eb",
                  borderRadius: "8px",
                  boxShadow:
                    theme === "dark"
                      ? "0 4px 6px -1px rgba(0, 0, 0, 0.3)"
                      : "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                  color: theme === "dark" ? "white" : "#374151",
                }}
                labelStyle={{
                  color: theme === "dark" ? "white" : "#374151",
                  fontWeight: "600",
                }}
              />
              <Bar
                dataKey="count"
                fill="#3b82f6"
                radius={[4, 4, 0, 0]}
                onMouseEnter={(_, __, event) => {
                  if (
                    theme === "dark" &&
                    event &&
                    event.target &&
                    "style" in event.target
                  ) {
                    (event.target as any).style.fill = "#000000";
                  }
                }}
                onMouseLeave={(_, __, event) => {
                  if (
                    theme === "dark" &&
                    event &&
                    event.target &&
                    "style" in event.target
                  ) {
                    (event.target as any).style.fill = "#3b82f6";
                  }
                }}
              />
            </BarChart>
          </ResponsiveContainer>
        );

      case "pie":
        return (
          <ResponsiveContainer width="100%" height={500}>
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
                contentStyle={{
                  backgroundColor:
                    theme === "dark" ? "rgba(0, 0, 0, 0.9)" : "white",
                  border:
                    theme === "dark"
                      ? "1px solid #374151"
                      : "1px solid #e5e7eb",
                  borderRadius: "8px",
                  boxShadow:
                    theme === "dark"
                      ? "0 4px 6px -1px rgba(0, 0, 0, 0.3)"
                      : "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                  color: theme === "dark" ? "white" : "#374151",
                }}
                labelStyle={{
                  color: theme === "dark" ? "white" : "#374151",
                  fontWeight: "600",
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        );

      case "line":
        return (
          <ResponsiveContainer width="100%" height={500}>
            <LineChart
              data={sortedTopics}
              margin={{ top: 20, right: 30, left: 20, bottom: 80 }}
            >
              <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
              <XAxis
                dataKey="label"
                height={120}
                interval={0}
                tick={<CustomTick />}
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
                  backgroundColor:
                    theme === "dark" ? "rgba(0, 0, 0, 0.9)" : "white",
                  border:
                    theme === "dark"
                      ? "1px solid #374151"
                      : "1px solid #e5e7eb",
                  borderRadius: "8px",
                  boxShadow:
                    theme === "dark"
                      ? "0 4px 6px -1px rgba(0, 0, 0, 0.3)"
                      : "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                  color: theme === "dark" ? "white" : "#374151",
                }}
                labelStyle={{
                  color: theme === "dark" ? "white" : "#374151",
                  fontWeight: "600",
                }}
              />
              <Line
                type="monotone"
                dataKey="count"
                stroke="#3b82f6"
                strokeWidth={3}
                dot={{ fill: "#3b82f6", strokeWidth: 2, r: 4 }}
                activeDot={{
                  r: 6,
                  stroke: theme === "dark" ? "#000000" : "#3b82f6",
                  fill: theme === "dark" ? "#000000" : "#3b82f6",
                  strokeWidth: 2,
                }}
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
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          height: "500px",
          color: "#6b7280",
        }}
      >
        <p>No topic data available</p>
      </div>
    );
  }

  return <div style={{ width: "100%", height: "500px" }}>{renderChart()}</div>;
};

export default TopicFrequencyChart;
