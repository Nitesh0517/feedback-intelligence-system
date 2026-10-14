import React from 'react';
import { Filter, RotateCcw } from 'lucide-react';

export const CATEGORIES = [
  'All',
  'Product Quality',
  'Customer Support',
  'Pricing',
  'Delivery',
  'User Experience',
  'Feature Request',
  'Other',
];

export const SENTIMENTS = ['All', 'positive', 'neutral', 'negative'];

export const SOURCES = [
  'All',
  'Web Form',
  'Mobile App',
  'Email',
  'Survey',
  'Twitter/Social',
  'Customer Support',
  'API',
];

export const STATUSES = ['All', 'new', 'analyzed', 'resolved', 'archived'];

export function FilterPanel({
  category,
  onCategoryChange,
  sentiment,
  onSentimentChange,
  source,
  onSourceChange,
  status,
  onStatusChange,
  onReset,
}) {
  const isFiltered =
    category !== 'All' || sentiment !== 'All' || source !== 'All' || (status && status !== 'All');

  return (
    <div className="flex flex-wrap items-center gap-3 text-xs">
      <div className="flex items-center gap-1.5 text-slate-500 font-semibold">
        <Filter className="w-3.5 h-3.5 text-slate-400" />
        Filter:
      </div>

      {/* Category */}
      <select
        value={category}
        onChange={(e) => onCategoryChange(e.target.value)}
        className="px-2.5 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-700 text-xs focus:ring-1 focus:ring-indigo-500"
      >
        {CATEGORIES.map((cat) => (
          <option key={cat} value={cat}>
            Category: {cat}
          </option>
        ))}
      </select>

      {/* Sentiment */}
      <select
        value={sentiment}
        onChange={(e) => onSentimentChange(e.target.value)}
        className="px-2.5 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-700 text-xs capitalize focus:ring-1 focus:ring-indigo-500"
      >
        {SENTIMENTS.map((sent) => (
          <option key={sent} value={sent}>
            Sentiment: {sent}
          </option>
        ))}
      </select>

      {/* Source */}
      <select
        value={source}
        onChange={(e) => onSourceChange(e.target.value)}
        className="px-2.5 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-700 text-xs focus:ring-1 focus:ring-indigo-500"
      >
        {SOURCES.map((src) => (
          <option key={src} value={src}>
            Source: {src}
          </option>
        ))}
      </select>

      {/* Status (Optional) */}
      {status !== undefined && onStatusChange && (
        <select
          value={status}
          onChange={(e) => onStatusChange(e.target.value)}
          className="px-2.5 py-1.5 rounded-lg border border-slate-200 bg-white text-slate-700 text-xs capitalize focus:ring-1 focus:ring-indigo-500"
        >
          {STATUSES.map((st) => (
            <option key={st} value={st}>
              Status: {st}
            </option>
          ))}
        </select>
      )}

      {isFiltered && onReset && (
        <button
          onClick={onReset}
          className="inline-flex items-center gap-1 text-indigo-600 hover:text-indigo-800 font-semibold ml-auto transition"
        >
          <RotateCcw className="w-3 h-3" />
          Reset Filters
        </button>
      )}
    </div>
  );
}
