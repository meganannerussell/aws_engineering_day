# Smart Text Analytics Dashboard

A modern, responsive dashboard for analyzing survey open-ended responses using React 18, TypeScript, Vite, TailwindCSS, and Recharts.

## Features

- 📊 **Interactive Charts** - Bar, pie, line, and donut charts with smooth transitions
- 📈 **Real-time Metrics** - Topics detected, total responses, confidence scores, processing time
- 🎨 **Modern UI** - Clean, professional design with TailwindCSS and shadcn/ui components
- 📱 **Responsive** - Mobile-friendly grid layout
- ⚡ **Fast Performance** - Built with Vite for lightning-fast development and builds
- 🎭 **Smooth Animations** - Framer Motion for delightful user interactions

## Tech Stack

- **React 18** with TypeScript
- **Vite** for build tooling
- **TailwindCSS** for styling
- **Recharts** for data visualization
- **Framer Motion** for animations
- **Lucide React** for icons

## Getting Started

### Prerequisites

- Node.js 16+
- npm or yarn

### Installation

1. Clone the repository
2. Install dependencies:

   ```bash
   npm install
   ```

3. Start the development server:

   ```bash
   npm run dev
   ```

4. Open [http://localhost:5173](http://localhost:5173) in your browser

### Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Project Structure

```
src/
├── components/
│   ├── charts/
│   │   ├── TopicFrequencyChart.tsx
│   │   └── SentimentDistributionChart.tsx
│   ├── ChartCard.tsx
│   └── MetricsHeader.tsx
├── lib/
│   └── utils.ts
├── pages/
│   └── Results.tsx
├── types/
│   └── analytics.ts
├── App.tsx
├── index.css
└── main.tsx
```

## Data Format

The dashboard expects data in the following format:

```typescript
interface AnalyticsData {
  project_metadata: {
    project_title: string;
    question_text: string;
    total_responses: number;
    processing_time_seconds: number;
    timestamp: string;
    services_used: {
      comprehend_pii: boolean;
      comprehend_sentiment: boolean;
      bedrock_embeddings: boolean;
      bedrock_llm: boolean;
    };
  };
  topics: Array<{
    topic_id: string;
    label: string;
    count: number;
    sentiment_mean: number;
    sentiment_distribution: {
      positive: number;
      negative: number;
      neutral: number;
      mixed: number;
    };
    examples: string[];
  }>;
}
```

## Customization

### Chart Types

The dashboard supports multiple chart types:

- **Bar Charts** - Best for comparing values
- **Pie Charts** - Best for showing proportions
- **Line Charts** - Best for showing trends
- **Donut Charts** - Alternative to pie charts

### Styling

The dashboard uses TailwindCSS with custom CSS variables for theming. You can customize colors in `src/index.css`.

### Adding New Charts

1. Create a new component in `src/components/charts/`
2. Follow the pattern of existing chart components
3. Add the new chart type to the `ChartType` union in `src/types/analytics.ts`
4. Update the `ChartCard` component to support the new type

## Performance

- Optimized bundle size with Vite
- Lazy loading for better performance
- Responsive images and charts
- Smooth animations with Framer Motion

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details
