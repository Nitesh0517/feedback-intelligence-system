import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  MessageSquare,
  Smile,
  Frown,
  Meh,
  CheckCircle2,
  Clock,
  PlusCircle,
  ArrowRight,
  Sparkles,
} from 'lucide-react';

import { analyticsApi, feedbackApi } from '../services/api';
import { MetricCard } from '../components/MetricCard';
import { SentimentChart } from '../components/SentimentChart';
import { CategoryChart } from '../components/CategoryChart';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorMessage } from '../components/ErrorMessage';
import { EmptyState } from '../components/EmptyState';
import { SentimentBadge, CategoryBadge } from '../components/StatusBadge';

export function Overview() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [overview, setOverview] = useState(null);
  const [sentimentData, setSentimentData] = useState(null);
  const [categoriesData, setCategoriesData] = useState(null);
  const [recentFeedback, setRecentFeedback] = useState([]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [overviewRes, sentimentRes, categoriesRes, feedbackRes] = await Promise.all([
        analyticsApi.getOverview(),
        analyticsApi.getSentiment(),
        analyticsApi.getCategories(),
        feedbackApi.list({ limit: 5 }),
      ]);
      setOverview(overviewRes.data);
      setSentimentData(sentimentRes.data);
      setCategoriesData(categoriesRes.data);
      setRecentFeedback(feedbackRes.data?.items || []);
    } catch (err) {
      setError(err.message || 'Failed to load executive dashboard data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return <LoadingSpinner text="Aggregating live feedback intelligence..." />;
  }

  if (error) {
    return <ErrorMessage message={error} onRetry={fetchData} />;
  }

  const total = overview?.total_feedback || 0;
  const positiveCount = overview?.positive_count || 0;
  const negativeCount = overview?.negative_count || 0;
  const neutralCount = overview?.neutral_count || 0;
  const analyzedCount = overview?.analyzed_count || 0;
  const pendingCount = overview?.pending_count || 0;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Executive Dashboard</h1>
          <p className="text-sm text-slate-500 mt-1">
            Real-time multi-channel customer sentiment and operational category intelligence.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/submit"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold bg-indigo-600 text-white hover:bg-indigo-700 transition shadow-sm"
          >
            <PlusCircle className="w-4 h-4" />
            Submit Feedback
          </Link>
        </div>
      </div>

      {/* 6 Required Live Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {/* 1. Total Feedback */}
        <MetricCard
          title="Total Feedback"
          value={total}
          subtitle="All ingested items"
          icon={MessageSquare}
          variant="default"
        />

        {/* 2. Positive Feedback */}
        <MetricCard
          title="Positive"
          value={positiveCount}
          subtitle={total > 0 ? `${Math.round((positiveCount / total) * 100)}% of total` : '0%'}
          icon={Smile}
          variant="positive"
        />

        {/* 3. Neutral Feedback */}
        <MetricCard
          title="Neutral"
          value={neutralCount}
          subtitle={total > 0 ? `${Math.round((neutralCount / total) * 100)}% of total` : '0%'}
          icon={Meh}
          variant="neutral"
        />

        {/* 4. Negative Feedback */}
        <MetricCard
          title="Negative"
          value={negativeCount}
          subtitle={total > 0 ? `${Math.round((negativeCount / total) * 100)}% of total` : '0%'}
          icon={Frown}
          variant="negative"
        />

        {/* 5. Analyzed Feedback */}
        <MetricCard
          title="Analyzed"
          value={analyzedCount}
          subtitle={total > 0 ? `${Math.round((analyzedCount / total) * 100)}% completed` : '0%'}
          icon={CheckCircle2}
          variant="indigo"
        />

        {/* 6. Pending Analysis */}
        <MetricCard
          title="Pending"
          value={pendingCount}
          subtitle={pendingCount > 0 ? 'Awaiting classification' : 'Queue clear'}
          icon={Clock}
          variant="amber"
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sentiment Distribution Doughnut */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-semibold text-slate-900">Sentiment Distribution</h2>
              <p className="text-xs text-slate-500">Live polarity breakdown from database</p>
            </div>
          </div>
          <SentimentChart
            positive={positiveCount}
            neutral={neutralCount}
            negative={negativeCount}
            height={240}
          />
        </div>

        {/* Category Breakdown Bar Chart */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-semibold text-slate-900">Category Breakdown</h2>
              <p className="text-xs text-slate-500">Feedback frequency across operational departments</p>
            </div>
            <Link
              to="/analytics"
              className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 inline-flex items-center gap-1"
            >
              Explore Trends <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
          <CategoryChart categories={categoriesData?.categories || {}} height={240} />
        </div>
      </div>

      {/* Recent Feedback Feed Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h2 className="text-base font-semibold text-slate-900">Recent Customer Submissions</h2>
            <p className="text-xs text-slate-500 mt-0.5">Latest ingested customer touchpoint records</p>
          </div>
          <Link
            to="/feedback"
            className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 inline-flex items-center gap-1"
          >
            See all feedback <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {recentFeedback.length === 0 ? (
          <div className="p-8">
            <EmptyState
              title="No recent feedback"
              description="Get started by submitting your first customer feedback item."
              actionLabel="Submit Feedback"
              onAction={() => window.location.assign('/submit')}
            />
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {recentFeedback.map((item) => (
              <div
                key={item.id}
                className="p-5 hover:bg-slate-50/80 transition flex flex-col sm:flex-row sm:items-center justify-between gap-4"
              >
                <div className="space-y-1.5 max-w-2xl">
                  <div className="flex items-center gap-2 flex-wrap">
                    <SentimentBadge sentiment={item.sentiment} score={item.sentiment_score} />
                    <CategoryBadge category={item.category} />
                    <span className="text-xs text-slate-400">
                      Source: <strong className="text-slate-600 font-medium">{item.source}</strong>
                    </span>
                  </div>
                  <p className="text-sm text-slate-800 font-medium line-clamp-2">
                    {item.feedback_text}
                  </p>
                  <p className="text-xs text-slate-400 flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5" />
                    {new Date(item.created_at).toLocaleString()}
                    {item.customer_identifier && ` • User: ${item.customer_identifier}`}
                  </p>
                </div>
                <div>
                  <Link
                    to={`/feedback/${item.id}`}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-100 text-slate-700 hover:bg-slate-200 transition"
                  >
                    View Details <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
