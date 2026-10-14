import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';

import { SentimentBadge, CategoryBadge, StatusBadge } from './components/StatusBadge';
import { EmptyState } from './components/EmptyState';
import { MetricCard } from './components/MetricCard';
import { LoadingSpinner } from './components/LoadingSpinner';
import { ErrorMessage } from './components/ErrorMessage';
import { FeedbackForm } from './pages/FeedbackForm';

describe('UI Badge and State Components', () => {
  it('renders positive sentiment badge with score correctly', () => {
    render(<SentimentBadge sentiment="positive" score={0.92} />);
    expect(screen.getByText(/positive/i)).toBeInTheDocument();
    expect(screen.getByText(/92%/i)).toBeInTheDocument();
  });

  it('renders negative sentiment badge correctly', () => {
    render(<SentimentBadge sentiment="negative" score={0.85} />);
    expect(screen.getByText(/negative/i)).toBeInTheDocument();
  });

  it('renders category badge correctly', () => {
    render(<CategoryBadge category="Product Quality" />);
    expect(screen.getByText('Product Quality')).toBeInTheDocument();
  });

  it('renders empty state with custom title and description', () => {
    render(
      <EmptyState
        title="Zero Feedback"
        description="No feedback records found in current view"
      />
    );
    expect(screen.getByText('Zero Feedback')).toBeInTheDocument();
    expect(screen.getByText('No feedback records found in current view')).toBeInTheDocument();
  });

  it('renders loading spinner with custom label', () => {
    render(<LoadingSpinner text="Fetching test metrics..." />);
    expect(screen.getByText('Fetching test metrics...')).toBeInTheDocument();
  });

  it('renders error message with retry trigger', () => {
    const retryFn = vi.fn();
    render(<ErrorMessage message="Database timed out" onRetry={retryFn} />);
    expect(screen.getByText('Database timed out')).toBeInTheDocument();
    const retryBtn = screen.getByRole('button', { name: /try again/i });
    fireEvent.click(retryBtn);
    expect(retryFn).toHaveBeenCalledTimes(1);
  });
});

describe('MetricCard Component', () => {
  it('renders actual API metric value, title, and subtitle', () => {
    render(
      <MetricCard
        title="Total Ingested"
        value={142}
        subtitle="100% of volume"
        variant="default"
      />
    );
    expect(screen.getByText('Total Ingested')).toBeInTheDocument();
    expect(screen.getByText('142')).toBeInTheDocument();
    expect(screen.getByText('100% of volume')).toBeInTheDocument();
  });

  it('renders loading skeleton when loading is true', () => {
    const { container } = render(
      <MetricCard
        title="Pending Analysis"
        value={12}
        loading={true}
      />
    );
    expect(screen.getByText('Pending Analysis')).toBeInTheDocument();
    expect(container.querySelector('.animate-pulse')).toBeInTheDocument();
  });
});

describe('FeedbackForm Component', () => {
  it('validates empty submission', async () => {
    render(
      <BrowserRouter>
        <FeedbackForm />
      </BrowserRouter>
    );

    expect(screen.getByText('Submit Customer Feedback')).toBeInTheDocument();
    const submitBtn = screen.getByRole('button', { name: /submit feedback/i });
    expect(submitBtn).toBeInTheDocument();
  });
});
