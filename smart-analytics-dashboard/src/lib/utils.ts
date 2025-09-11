import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatNumber(num: number): string {
  return new Intl.NumberFormat().format(num)
}

export function formatTime(seconds: number): string {
  if (seconds < 60) {
    return `${seconds.toFixed(1)}s`
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}m ${remainingSeconds.toFixed(0)}s`
  } else {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  }
}

export function formatConfidence(score: number): string {
  return `${(score * 100).toFixed(1)}%`
}

export function formatSentimentPolarity(polarity: number): string {
  // Convert polarity (-1 to +1) to a more readable format
  if (polarity >= 0.3) {
    return `+${polarity.toFixed(2)}`
  } else if (polarity <= -0.3) {
    return polarity.toFixed(2)
  } else {
    return polarity.toFixed(2)
  }
}

export function getSentimentDescription(polarity: number): string {
  if (polarity >= 0.6) {
    return "Very positive overall"
  } else if (polarity >= 0.3) {
    return "Mostly positive"
  } else if (polarity >= 0.1) {
    return "Slightly positive"
  } else if (polarity >= -0.1) {
    return "Neutral sentiment"
  } else if (polarity >= -0.3) {
    return "Slightly negative"
  } else if (polarity >= -0.6) {
    return "Mostly negative"
  } else {
    return "Very negative overall"
  }
}

export function formatSentimentFraction(score: number): string {
  // Convert score to a fraction (e.g., 0.75 -> "3/4")
  const numerator = Math.round(score * 4) // Scale to 4 for common fractions
  const denominator = 4
  
  // Simplify the fraction
  const gcd = (a: number, b: number): number => b === 0 ? a : gcd(b, a % b)
  const divisor = gcd(numerator, denominator)
  
  const simplifiedNum = numerator / divisor
  const simplifiedDen = denominator / divisor
  
  return `${simplifiedNum}/${simplifiedDen}`
}

export function getSentimentColor(sentiment: string): string {
  switch (sentiment.toLowerCase()) {
    case 'positive':
      return '#10b981' // green-500
    case 'negative':
      return '#ef4444' // red-500
    case 'neutral':
      return '#6b7280' // gray-500
    case 'mixed':
      return '#f59e0b' // amber-500
    default:
      return '#6b7280'
  }
}

export function getSentimentColorFromPolarity(polarity: number): string {
  if (polarity >= 0.3) {
    return '#10b981' // green-500 - positive
  } else if (polarity >= 0.1) {
    return '#84cc16' // lime-500 - slightly positive
  } else if (polarity >= -0.1) {
    return '#6b7280' // gray-500 - neutral
  } else if (polarity >= -0.3) {
    return '#f59e0b' // amber-500 - slightly negative
  } else {
    return '#ef4444' // red-500 - negative
  }
}

export function getChartColors(count: number): string[] {
  const baseColors = [
    '#3b82f6', // blue-500
    '#10b981', // emerald-500
    '#f59e0b', // amber-500
    '#ef4444', // red-500
    '#8b5cf6', // violet-500
    '#06b6d4', // cyan-500
    '#84cc16', // lime-500
    '#f97316', // orange-500
    '#ec4899', // pink-500
    '#6366f1', // indigo-500
  ]
  
  return Array.from({ length: count }, (_, i) => baseColors[i % baseColors.length])
}
