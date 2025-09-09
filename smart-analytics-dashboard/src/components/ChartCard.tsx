import { motion } from "framer-motion";
import { BarChart3, PieChart, LineChart, Donut } from "lucide-react";
import type { ChartType } from "../types/analytics";

interface ChartCardProps {
  title: string;
  description: string;
  children: React.ReactNode;
  chartType: ChartType;
  onChartTypeChange: (type: ChartType) => void;
  availableTypes?: ChartType[];
  className?: string;
}

const ChartCard: React.FC<ChartCardProps> = ({
  title,
  description,
  children,
  chartType,
  onChartTypeChange,
  availableTypes = ["bar", "pie", "line"],
  className = "",
}) => {
  const chartIcons = {
    bar: BarChart3,
    pie: PieChart,
    line: LineChart,
    donut: Donut,
  };

  const getNextType = (
    currentType: ChartType,
    available: ChartType[]
  ): ChartType => {
    const currentIndex = available.indexOf(currentType);
    const nextIndex = (currentIndex + 1) % available.length;
    return available[nextIndex];
  };

  const handleToggle = () => {
    const nextType = getNextType(chartType, availableTypes);
    onChartTypeChange(nextType);
  };

  const Icon = chartIcons[chartType];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className={`chart-card ${className}`}
    >
      <div className="chart-card__header">
        <div className="chart-card__header-content">
          <div className="chart-card__text">
            <h3 className="chart-card__title">{title}</h3>
            <p className="chart-card__description">{description}</p>
          </div>
          <button
            onClick={handleToggle}
            className="chart-card__toggle"
            title={`Switch to ${getNextType(chartType, availableTypes)} chart`}
          >
            <Icon style={{ width: "1.25rem", height: "1.25rem" }} />
          </button>
        </div>
      </div>
      <div className="chart-card__content">{children}</div>
    </motion.div>
  );
};

export default ChartCard;
