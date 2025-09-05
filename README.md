# Smart Text Analytics Dashboard

A modern, responsive dashboard for analyzing survey open-ended responses using React 18, TypeScript, Vite, and SCSS.

## 🚀 Features

- **Interactive Charts** - Bar, pie, line, and donut charts with smooth transitions
- **Real-time Metrics** - Topics detected, total responses, confidence scores, processing time
- **Modern UI** - Clean, professional design with SCSS and custom components
- **Responsive** - Mobile-friendly grid layout
- **Smooth Animations** - Framer Motion for delightful user interactions
- **Data Visualization** - Recharts for beautiful, interactive charts

## 📁 Project Structure

```
aws_engineering_day/
├── smart-analytics-dashboard/     # Main React dashboard
│   ├── src/
│   │   ├── components/           # Reusable UI components
│   │   ├── pages/               # Main dashboard page
│   │   ├── styles/              # SCSS stylesheets
│   │   ├── types/               # TypeScript type definitions
│   │   └── lib/                 # Utility functions
│   ├── public/                  # Static assets
│   └── package.json
├── sample_data/                  # Sample CSV data files
├── hackathon_demo_results.json  # Demo analytics data
└── README.md
```

## 🛠 Tech Stack

- **React 18** + **TypeScript** + **Vite**
- **SCSS** for styling (no TailwindCSS dependencies)
- **Recharts** for data visualization
- **Framer Motion** for animations
- **Lucide React** for icons

## 🚀 Getting Started

### Prerequisites

- Node.js 16+
- npm or yarn

### Installation

1. Navigate to the dashboard directory:

   ```bash
   cd smart-analytics-dashboard
   ```

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

## 📊 Dashboard Features

The dashboard automatically loads and visualizes data from `hackathon_demo_results.json`:

- **979 total responses** from a beauty survey
- **Multiple topics** including "Personalized Skincare Products", "Non-users opinions", etc.
- **Sentiment analysis** with positive/negative/neutral/mixed distribution
- **Processing metrics** showing analysis completion time

### Interactive Elements

1. **Metrics Cards**: Top 4 KPIs with icons and descriptions
2. **Interactive Charts**: Click chart icons to switch between bar/pie/line/donut
3. **Topic Details**: Top 5 topics with example responses
4. **Responsive Layout**: Works on desktop, tablet, and mobile

## 🎨 Styling

The dashboard uses a custom SCSS architecture with:

- **Variables** for consistent colors, spacing, and typography
- **Mixins** for reusable component styles
- **Component-based CSS** with BEM methodology
- **Responsive design** with mobile-first approach
- **Smooth animations** and transitions

## 📈 Data Format

The dashboard expects data in the following format:

```typescript
interface AnalyticsData {
  project_metadata: {
    project_title: string;
    question_text: string;
    total_responses: number;
    processing_time_seconds: number;
    timestamp: string;
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

## 🔧 Development

- **Hot Module Replacement** - Changes reflect immediately
- **TypeScript** - Full type safety
- **ESLint** - Code quality and consistency
- **SCSS** - Modular, maintainable styles

## 📱 Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## 📄 License

MIT License - see LICENSE file for details
