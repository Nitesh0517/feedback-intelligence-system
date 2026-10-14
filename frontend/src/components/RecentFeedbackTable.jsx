import React from 'react';
import { Link } from 'react-router-dom';
import { Clock, ArrowRight } from 'lucide-react';
import { SentimentBadge, CategoryBadge, StatusBadge } from './StatusBadge';
import { EmptyState } from './EmptyState';

export function RecentFeedbackTable({ feedback = [], title = 'Recent Feedback', viewAllLink = '/feedback' }) {
  if (!feedback || feedback.length === 0) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs p-6">
        <EmptyState
          title="No customer feedback"
          description="Feedback will appear here once ingested from customer channels."
        />
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
      <div className="p-5 border-b border-slate-100 flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-slate-900">{title}</h2>
          <p className="text-xs text-slate-500 mt-0.5">Live ingested submissions from all connected channels</p>
        </div>
        {viewAllLink && (
          <Link
            to={viewAllLink}
            className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 inline-flex items-center gap-1 transition"
          >
            View Feed <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        )}
      </div>

      <div className="divide-y divide-slate-100">
        {feedback.map((item) => (
          <div
            key={item.id}
            className="p-5 hover:bg-slate-50/80 transition flex flex-col sm:flex-row sm:items-center justify-between gap-4"
          >
            <div className="space-y-1.5 max-w-2xl">
              <div className="flex items-center gap-2 flex-wrap">
                <SentimentBadge sentiment={item.sentiment} score={item.sentiment_score} />
                <CategoryBadge category={item.category} />
                <StatusBadge status={item.status} />
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
            <div className="flex-shrink-0">
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
    </div>
  );
}
