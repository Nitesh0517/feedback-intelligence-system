import React from 'react';

export function SentimentBadge({ sentiment, score }) {
  const normalized = (sentiment || 'neutral').toLowerCase();
  
  const styles = {
    positive: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    negative: 'bg-rose-50 text-rose-700 border-rose-200',
    neutral: 'bg-slate-100 text-slate-700 border-slate-200',
    pending: 'bg-amber-50 text-amber-700 border-amber-200',
  };

  const style = styles[normalized] || styles.neutral;
  const scoreDisplay = typeof score === 'number' ? ` (${Math.round(score * 100)}%)` : '';

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border capitalize ${style}`}>
      <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${
        normalized === 'positive' ? 'bg-emerald-500' :
        normalized === 'negative' ? 'bg-rose-500' :
        normalized === 'pending' ? 'bg-amber-500' : 'bg-slate-400'
      }`} />
      {normalized}{scoreDisplay}
    </span>
  );
}

export function CategoryBadge({ category }) {
  const label = category || 'Unassigned';
  const colors = {
    'Product Quality': 'bg-blue-50 text-blue-700 border-blue-200',
    'Customer Support': 'bg-purple-50 text-purple-700 border-purple-200',
    'Pricing': 'bg-amber-50 text-amber-700 border-amber-200',
    'Delivery': 'bg-orange-50 text-orange-700 border-orange-200',
    'User Experience': 'bg-indigo-50 text-indigo-700 border-indigo-200',
    'Feature Request': 'bg-teal-50 text-teal-700 border-teal-200',
    'Other': 'bg-slate-100 text-slate-700 border-slate-200',
  };

  const style = colors[label] || 'bg-slate-100 text-slate-700 border-slate-200';

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${style}`}>
      {label}
    </span>
  );
}

export function StatusBadge({ status }) {
  const s = (status || 'new').toLowerCase();
  const styles = {
    new: 'bg-sky-50 text-sky-700 border-sky-200',
    analyzed: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    processing: 'bg-amber-50 text-amber-700 border-amber-200',
    resolved: 'bg-indigo-50 text-indigo-700 border-indigo-200',
    archived: 'bg-slate-100 text-slate-600 border-slate-200',
  };
  const style = styles[s] || styles.new;

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium border capitalize ${style}`}>
      {s}
    </span>
  );
}
