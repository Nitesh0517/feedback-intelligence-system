import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';

import { Overview } from './pages/Overview';
import { analyticsApi, feedbackApi } from './services/api';

// Mock the API client
vi.mock('./services/api', () => ({
  analyticsApi: {
    getOverview: vi.fn(),
    getSentiment: vi.fn(),
    getCategories: vi.fn(),
    getTrends: vi.fn(),
  },
  feedbackApi: {
    list: vi.fn(),
    create: vi.fn(),
    get: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    analyze: vi.fn(),
  },
  healthApi: {
    checkHealth: vi.fn(),
    checkReady: vi.fn(),
  },
}));

describe('Dashboard Overview Live Metrics and Visualizations', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders loading state initially', () => {
    analyticsApi.getOverview.mockReturnValue(new Promise(() => {}));
    analyticsApi.getSentiment.mockReturnValue(new Promise(() => {}));
    analyticsApi.getCategories.mockReturnValue(new Promise(() => {}));
    feedbackApi.list.mockReturnValue(new Promise(() => {}));

    render(
      <BrowserRouter>
        <Overview />
      </BrowserRouter>
    );

    expect(screen.getByText(/aggregating live feedback intelligence/i)).toBeInTheDocument();
  });

  it('displays the 6 live metric cards with actual API data', async () => {
    analyticsApi.getOverview.mockResolvedValue({
      data: {
        total_feedback: 88,
        positive_count: 50,
        negative_count: 20,
        neutral_count: 18,
        analyzed_count: 80,
        pending_count: 8,
        sentiment_distribution: { positive: 56.8, neutral: 20.5, negative: 22.7 },
      },
    });

    analyticsApi.getSentiment.mockResolvedValue({
      data: {
        total: 88,
        positive: 50,
        negative: 20,
        neutral: 18,
        percentages: { positive: 56.8, neutral: 20.5, negative: 22.7 },
        average_sentiment_score: 0.82,
      },
    });

    analyticsApi.getCategories.mockResolvedValue({
      data: {
        categories: {
          'Product Quality': 30,
          'Customer Support': 25,
          'Pricing': 15,
          'Delivery': 10,
          'User Experience': 5,
          'Feature Request': 3,
          'Other': 0,
        },
        total: 88,
        percentages: {},
        uncategorized: 0,
      },
    });

    feedbackApi.list.mockResolvedValue({
      data: {
        items: [
          {
            id: 1,
            source: 'Web Form',
            customer_identifier: 'user1',
            feedback_text: 'Excellent service and great delivery!',
            category: 'Delivery',
            sentiment: 'positive',
            sentiment_score: 0.92,
            status: 'analyzed',
            created_at: new Date().toISOString(),
          },
        ],
        total: 1,
        skip: 0,
        limit: 5,
      },
    });

    render(
      <BrowserRouter>
        <Overview />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Executive Dashboard')).toBeInTheDocument();
    });

    // Verify all 6 metric cards
    expect(screen.getByText('Total Feedback')).toBeInTheDocument();
    expect(screen.getByText('88')).toBeInTheDocument();

    expect(screen.getByText('Positive')).toBeInTheDocument();
    expect(screen.getByText('50')).toBeInTheDocument();

    expect(screen.getByText('Neutral')).toBeInTheDocument();
    expect(screen.getByText('18')).toBeInTheDocument();

    expect(screen.getByText('Negative')).toBeInTheDocument();
    expect(screen.getByText('20')).toBeInTheDocument();

    expect(screen.getByText('Analyzed')).toBeInTheDocument();
    expect(screen.getByText('80')).toBeInTheDocument();

    expect(screen.getByText('Pending')).toBeInTheDocument();
    expect(screen.getByText('8')).toBeInTheDocument();
  });

  it('handles API errors with retry option', async () => {
    analyticsApi.getOverview.mockRejectedValue(new Error('Network error connecting to backend'));
    analyticsApi.getSentiment.mockResolvedValue({ data: {} });
    analyticsApi.getCategories.mockResolvedValue({ data: {} });
    feedbackApi.list.mockResolvedValue({ data: { items: [] } });

    render(
      <BrowserRouter>
        <Overview />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
      expect(screen.getByText(/network error connecting to backend/i)).toBeInTheDocument();
    });

    expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
  });
});
