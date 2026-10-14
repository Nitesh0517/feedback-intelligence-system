import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  AlertTriangle,
  Lightbulb,
  Calendar,
  Sparkles,
  BarChart3,
  PieChart,
} from 'lucide-react';

import { analyticsApi } from '../services/api';
import { FeedbackTrendChart } from '../components/FeedbackTrendChart';
import { SentimentChart } from '../components/SentimentChart';
import { CategoryChart } from '../components/CategoryChart';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorMessage } from '../components/ErrorMessage';

export function Analytics() {
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [trendsData, setTrendsData] = useState(null);
  const [sentimentData, setSentimentData] = useState(null);
  const [categoryData, setCategoryData] = useState(null);

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const [trendsRes, sentimentRes, categoryRes] = await Promise.all([
        analyticsApi.getTrends({ days }),
        analyticsApi.getSentiment(),
        analyticsApi.getCategories(),
      ]);
      setTrendsData(trendsRes.data);
      setSentimentData(sentimentRes.data);
      setCategoryData(categoryRes.data);
    } catch (err) {
      setError(err.message || 'Failed to fetch analytics intelligence.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, [days]);

  if (loading) {
    return <LoadingSpinner text="Computing trends and sentiment analytics from database..." />;
  }

  if (error) {
    return <ErrorMessage message={error} onRetry={fetchAnalytics} />;
  }

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Analytics & Intelligence</h1>
          <p className="text-sm text-slate-500 mt-1">
            Detect patterns, negative feedback spikes, and AI-driven business recommendations.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-slate-400" />
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="px-3 py-1.5 rounded-xl border border-slate-200 bg-white text-xs font-semibold text-slate-700 shadow-2xs focus:ring-1 focus:ring-indigo-500"
          >
            <option value={7}>Last 7 Days</option>
            <option value={14}>Last 14 Days</option>
            <option value={30}>Last 30 Days</option>
            <option value={90}>Last 90 Days</option>
          </select>
        </div>
      </div>

      {/* Negative Spike Alert Banner */}
      {trendsData?.negative_spike_detected && (
        <div className="p-4 rounded-xl border border-amber-300 bg-amber-50 text-amber-900 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" />
          <div>
            <h4 className="text-sm font-bold">Negative Feedback Spike Alert</h4>
            <p className="text-xs text-amber-800 mt-0.5">
              {trendsData.spike_message ||
                'A statistically meaningful increase in negative feedback was detected in the selected time range.'}
            </p>
          </div>
        </div>
      )}

      {/* Main Trends Over Time Chart */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-base font-semibold text-slate-900 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-indigo-600" />
              Feedback Volume & Polarity Velocity
            </h2>
            <p className="text-xs text-slate-500">Historical trend across the past {days} days</p>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-indigo-50 text-indigo-700">
            {trendsData?.total_volume || 0} Total Submissions
          </span>
        </div>
        <FeedbackTrendChart dataPoints={trendsData?.data_points || []} height={280} />
      </div>

      {/* Two Column Grid for Breakdown Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Breakdown */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
          <h2 className="text-base font-semibold text-slate-900 flex items-center gap-2 mb-1">
            <BarChart3 className="w-4 h-4 text-indigo-600" />
            Operational Categories
          </h2>
          <p className="text-xs text-slate-500 mb-4">Total feedback categorized per business area</p>
          <CategoryChart categories={categoryData?.categories || {}} height={240} />
        </div>

        {/* Sentiment Doughnut */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
          <h2 className="text-base font-semibold text-slate-900 flex items-center gap-2 mb-1">
            <PieChart className="w-4 h-4 text-indigo-600" />
            Overall Sentiment Share
          </h2>
          <p className="text-xs text-slate-500 mb-4">Proportion of customer sentiment</p>
          <SentimentChart
            positive={sentimentData?.positive || 0}
            neutral={sentimentData?.neutral || 0}
            negative={sentimentData?.negative || 0}
            height={240}
          />
        </div>
      </div>

      {/* Executive Summary & Recommendations Panel */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
        <div className="flex items-center gap-2 text-indigo-900 font-semibold text-base">
          <Sparkles className="w-4 h-4 text-indigo-600" />
          <span>Executive Summary & Actionable Recommendations</span>
        </div>

        <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 text-sm text-slate-700 leading-relaxed">
          {trendsData?.summary || (
            <span>
              Customer sentiment is actively tracked. With {sentimentData?.total || 0} total reviews ingested,
              positive sentiment represents{' '}
              {sentimentData?.total
                ? Math.round((sentimentData.positive / sentimentData.total) * 100)
                : 0}
              % of submissions.
            </span>
          )}
        </div>

        {/* Recommendations list */}
        <div className="space-y-2 pt-2">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Suggested Next Steps
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {(trendsData?.recommendations || [
              'Continue monitoring customer response times in Customer Support tickets.',
              'Prioritize bug fixes reported under User Experience and Delivery.',
              'Expand automated categorization coverage across incoming review feeds.',
            ]).map((rec, idx) => (
              <div
                key={idx}
                className="flex items-start gap-2.5 p-3 rounded-xl bg-indigo-50/40 border border-indigo-100 text-xs text-indigo-950 font-medium"
              >
                <Lightbulb className="w-4 h-4 text-indigo-600 mt-0.5 flex-shrink-0" />
                <span>{rec}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
