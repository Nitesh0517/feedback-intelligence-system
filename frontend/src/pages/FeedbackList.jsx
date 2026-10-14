import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  PlusCircle,
  Eye,
  Trash2,
  Sparkles,
  ChevronLeft,
  ChevronRight,
  RefreshCw,
} from 'lucide-react';

import { feedbackApi } from '../services/api';
import { SearchBar } from '../components/SearchBar';
import { FilterPanel } from '../components/FilterPanel';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorMessage } from '../components/ErrorMessage';
import { EmptyState } from '../components/EmptyState';
import { SentimentBadge, CategoryBadge, StatusBadge } from '../components/StatusBadge';
import { useAuth } from '../context/AuthContext';

export function FeedbackList() {
  const { hasRole } = useAuth();
  const canAnalyze = hasRole(['admin', 'analyst']);
  const canDelete = hasRole('admin');
  const canCreate = hasRole(['admin', 'analyst']);

  const [feedback, setFeedback] = useState([]);
  const [total, setTotal] = useState(0);

  const [page, setPage] = useState(1);
  const [limit] = useState(10);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('All');
  const [sentiment, setSentiment] = useState('All');
  const [source, setSource] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');
  const [loading, setLoading] = useState(true);
  const [analyzingId, setAnalyzingId] = useState(null);
  const [batchAnalyzing, setBatchAnalyzing] = useState(false);
  const [error, setError] = useState(null);

  const fetchFeedback = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        skip: (page - 1) * limit,
        limit,
      };
      if (search.trim()) params.search = search.trim();
      if (category !== 'All') params.category = category;
      if (sentiment !== 'All') params.sentiment = sentiment;
      if (source !== 'All') params.source = source;
      if (statusFilter !== 'All') params.status = statusFilter;

      const res = await feedbackApi.list(params);
      setFeedback(res.data?.items || []);
      setTotal(res.data?.total || 0);
    } catch (err) {
      setError(err.message || 'Failed to load feedback records.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFeedback();
  }, [page, category, sentiment, source, statusFilter]);

  const handleSearch = (term) => {
    setSearch(term);
    setPage(1);
    fetchFeedback();
  };

  const handleAnalyze = async (id) => {
    try {
      setAnalyzingId(id);
      await feedbackApi.analyze(id);
      fetchFeedback();
    } catch (err) {
      alert(`Analysis failed: ${err.message}`);
    } finally {
      setAnalyzingId(null);
    }
  };

  const handleBatchAnalyze = async () => {
    try {
      setBatchAnalyzing(true);
      const res = await feedbackApi.batchAnalyze({ limit: 50 });
      alert(`Batch analysis complete: ${res.data?.processed_count || 0} items analyzed.`);
      fetchFeedback();
    } catch (err) {
      alert(`Batch analysis failed: ${err.message}`);
    } finally {
      setBatchAnalyzing(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to permanently delete this feedback entry?')) return;
    try {
      await feedbackApi.delete(id);
      fetchFeedback();
    } catch (err) {
      alert(`Deletion failed: ${err.message}`);
    }
  };

  const handleResetFilters = () => {
    setCategory('All');
    setSentiment('All');
    setSource('All');
    setStatusFilter('All');
    setSearch('');
    setPage(1);
  };

  const totalPages = Math.ceil(total / limit) || 1;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Customer Feedback Feed</h1>
          <p className="text-sm text-slate-500 mt-1">
            Search, filter, inspect, and analyze all ingested feedback.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {canAnalyze && (
            <button
              onClick={handleBatchAnalyze}
              disabled={batchAnalyzing}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-sm font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 disabled:opacity-50 transition"
            >
              <Sparkles className={`w-4 h-4 text-indigo-600 ${batchAnalyzing ? 'animate-spin' : ''}`} />
              {batchAnalyzing ? 'Analyzing Batch...' : 'Analyze Pending'}
            </button>
          )}
          {canCreate && (
            <Link
              to="/submit"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold bg-indigo-600 text-white hover:bg-indigo-700 transition shadow-sm"
            >
              <PlusCircle className="w-4 h-4" />
              Add Feedback
            </Link>
          )}
        </div>

      </div>

      {/* Filters & Search Toolbar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs space-y-3">
        <SearchBar
          value={search}
          onChange={setSearch}
          onSubmit={handleSearch}
          placeholder="Search customer feedback or identifier..."
        />

        <div className="pt-2 border-t border-slate-100">
          <FilterPanel
            category={category}
            onCategoryChange={(val) => {
              setCategory(val);
              setPage(1);
            }}
            sentiment={sentiment}
            onSentimentChange={(val) => {
              setSentiment(val);
              setPage(1);
            }}
            source={source}
            onSourceChange={(val) => {
              setSource(val);
              setPage(1);
            }}
            status={statusFilter}
            onStatusChange={(val) => {
              setStatusFilter(val);
              setPage(1);
            }}
            onReset={handleResetFilters}
          />
        </div>
      </div>

      {/* Main Table / Content */}
      {loading ? (
        <LoadingSpinner text="Fetching feedback..." />
      ) : error ? (
        <ErrorMessage message={error} onRetry={fetchFeedback} />
      ) : feedback.length === 0 ? (
        <EmptyState
          title="No feedback matching criteria"
          description="Try adjusting your search query or filters to find what you are looking for."
          actionLabel="Clear Filters"
          onAction={handleResetFilters}
        />
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50/75 border-b border-slate-200 text-xs font-semibold uppercase tracking-wider text-slate-500">
                  <th className="p-4">Customer & Source</th>
                  <th className="p-4">Feedback Text</th>
                  <th className="p-4">Sentiment</th>
                  <th className="p-4">Category</th>
                  <th className="p-4">Status</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-sm">
                {feedback.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50/70 transition">
                    <td className="p-4 align-top whitespace-nowrap">
                      <div className="font-medium text-slate-800">
                        {item.customer_identifier || 'Anonymous'}
                      </div>
                      <div className="text-xs text-slate-400 mt-0.5">
                        {item.source} • {new Date(item.created_at).toLocaleDateString()}
                      </div>
                    </td>
                    <td className="p-4 align-top max-w-md">
                      <p className="text-slate-700 line-clamp-2">{item.feedback_text}</p>
                    </td>
                    <td className="p-4 align-top whitespace-nowrap">
                      <SentimentBadge sentiment={item.sentiment} score={item.sentiment_score} />
                    </td>
                    <td className="p-4 align-top whitespace-nowrap">
                      <CategoryBadge category={item.category} />
                    </td>
                    <td className="p-4 align-top whitespace-nowrap">
                      <StatusBadge status={item.status} />
                    </td>
                    <td className="p-4 align-top text-right whitespace-nowrap space-x-2">
                      {canAnalyze && (
                        <button
                          onClick={() => handleAnalyze(item.id)}
                          disabled={analyzingId === item.id}
                          title="Run AI Analysis"
                          className="inline-flex items-center p-1.5 rounded-lg text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 transition"
                        >
                          <Sparkles
                            className={`w-4 h-4 ${analyzingId === item.id ? 'animate-spin text-indigo-600' : ''}`}
                          />
                        </button>
                      )}
                      <Link
                        to={`/feedback/${item.id}`}
                        title="View Details"
                        className="inline-flex items-center p-1.5 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition"
                      >
                        <Eye className="w-4 h-4" />
                      </Link>
                      {canDelete && (
                        <button
                          onClick={() => handleDelete(item.id)}
                          title="Delete Feedback"
                          className="inline-flex items-center p-1.5 rounded-lg text-slate-500 hover:text-rose-600 hover:bg-rose-50 transition"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </td>

                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination Footer */}
          <div className="p-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
            <div>
              Showing <span className="font-semibold text-slate-700">{feedback.length}</span> of{' '}
              <span className="font-semibold text-slate-700">{total}</span> items
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(p - 1, 1))}
                disabled={page === 1}
                className="p-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="font-medium text-slate-700">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(p + 1, totalPages))}
                disabled={page >= totalPages}
                className="p-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
