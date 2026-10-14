import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Sparkles,
  Trash2,
  Clock,
  User,
  Share2,
  Edit3,
  Save,
  X,
} from 'lucide-react';
import { feedbackApi } from '../services/api';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorMessage } from '../components/ErrorMessage';
import { SentimentBadge, CategoryBadge, StatusBadge } from '../components/StatusBadge';
import { useAuth } from '../context/AuthContext';

const CATEGORIES = [
  'Product Quality',
  'Customer Support',
  'Pricing',
  'Delivery',
  'User Experience',
  'Feature Request',
  'Other',
];

export function FeedbackDetail() {
  const { hasRole } = useAuth();
  const canModify = hasRole(['admin', 'analyst']);
  const canDelete = hasRole('admin');

  const { id } = useParams();
  const navigate = useNavigate();
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [updatingStatus, setUpdatingStatus] = useState(false);

  
  // Edit mode state
  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState('');
  const [editCategory, setEditCategory] = useState('');
  const [savingEdit, setSavingEdit] = useState(false);

  const fetchDetail = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await feedbackApi.get(id);
      setFeedback(res.data);
      setEditText(res.data.feedback_text);
      setEditCategory(res.data.category || 'Other');
    } catch (err) {
      setError(err.message || 'Failed to retrieve feedback record.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetail();
  }, [id]);

  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      const res = await feedbackApi.analyze(id);
      setFeedback(res.data);
      setEditCategory(res.data.category || 'Other');
    } catch (err) {
      alert(`AI analysis failed: ${err.message}`);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleStatusChange = async (newStatus) => {
    setUpdatingStatus(true);
    try {
      const res = await feedbackApi.update(id, { status: newStatus });
      setFeedback(res.data);
    } catch (err) {
      alert(`Status update failed: ${err.message}`);
    } finally {
      setUpdatingStatus(false);
    }
  };

  const handleSaveEdit = async () => {
    if (!editText.trim()) {
      alert('Feedback text cannot be empty.');
      return;
    }
    setSavingEdit(true);
    try {
      const res = await feedbackApi.update(id, {
        feedback_text: editText.trim(),
        category: editCategory,
      });
      setFeedback(res.data);
      setIsEditing(false);
    } catch (err) {
      alert(`Save failed: ${err.message}`);
    } finally {
      setSavingEdit(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to permanently delete this feedback item? This cannot be undone.')) {
      return;
    }
    try {
      await feedbackApi.delete(id);
      navigate('/feedback');
    } catch (err) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  if (loading) {
    return <LoadingSpinner text="Loading feedback record..." />;
  }

  if (error) {
    return <ErrorMessage message={error} onRetry={fetchDetail} />;
  }

  if (!feedback) {
    return <ErrorMessage message="Feedback record not found." />;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Top Back Link & Actions */}
      <div className="flex items-center justify-between">
        <Link
          to="/feedback"
          className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-slate-800 transition"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Feed
        </Link>
        <div className="flex items-center gap-2">
          {canModify && !isEditing && (
            <button
              onClick={() => setIsEditing(true)}
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 transition"
            >
              <Edit3 className="w-3.5 h-3.5" />
              Edit
            </button>
          )}
          {canModify && (
            <button
              onClick={handleAnalyze}
              disabled={analyzing}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 transition shadow-sm"
            >
              <Sparkles className={`w-3.5 h-3.5 ${analyzing ? 'animate-spin' : ''}`} />
              {analyzing ? 'Analyzing...' : 'Run AI Analysis'}
            </button>
          )}
          {canDelete && (
            <button
              onClick={handleDelete}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-rose-50 text-rose-700 hover:bg-rose-100 border border-rose-200 transition"
            >
              <Trash2 className="w-3.5 h-3.5" />
              Delete
            </button>
          )}
        </div>
      </div>


      {/* Main Feedback Content Box */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-xs space-y-6">
        {/* Header Metadata */}
        <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-slate-100">
          <div className="flex items-center gap-2 flex-wrap">
            <SentimentBadge sentiment={feedback.sentiment} score={feedback.sentiment_score} />
            <CategoryBadge category={feedback.category} />
            <StatusBadge status={feedback.status} />
          </div>

          <div className="flex items-center gap-4 text-xs text-slate-500">
            <span className="flex items-center gap-1">
              <Share2 className="w-3.5 h-3.5 text-slate-400" />
              Source: <strong className="text-slate-700">{feedback.source}</strong>
            </span>
            <span className="flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              {new Date(feedback.created_at).toLocaleString()}
            </span>
          </div>
        </div>

        {/* Customer Identifier */}
        {feedback.customer_identifier && (
          <div className="flex items-center gap-2 text-xs font-medium text-slate-600 bg-slate-50 px-3 py-2 rounded-lg border border-slate-200">
            <User className="w-4 h-4 text-slate-400" />
            <span>Customer ID: {feedback.customer_identifier}</span>
          </div>
        )}

        {/* Feedback Body (Edit Mode vs Read Mode) */}
        {isEditing ? (
          <div className="space-y-4 bg-slate-50 p-5 rounded-xl border border-slate-200">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1">
                Edit Feedback Text
              </label>
              <textarea
                rows={5}
                value={editText}
                onChange={(e) => setEditText(e.target.value)}
                className="w-full p-3 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-indigo-500 bg-white"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1">
                Category
              </label>
              <select
                value={editCategory}
                onChange={(e) => setEditCategory(e.target.value)}
                className="px-3 py-2 rounded-lg border border-slate-300 text-sm bg-white"
              >
                {CATEGORIES.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex items-center gap-2 pt-2">
              <button
                onClick={handleSaveEdit}
                disabled={savingEdit}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-semibold bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50"
              >
                <Save className="w-3.5 h-3.5" />
                {savingEdit ? 'Saving...' : 'Save Changes'}
              </button>
              <button
                onClick={() => {
                  setEditText(feedback.feedback_text);
                  setEditCategory(feedback.category || 'Other');
                  setIsEditing(false);
                }}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-semibold bg-slate-200 text-slate-700 hover:bg-slate-300"
              >
                <X className="w-3.5 h-3.5" />
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
              Feedback Text
            </h3>
            <p className="text-base text-slate-800 leading-relaxed whitespace-pre-wrap bg-slate-50/50 p-4 rounded-xl border border-slate-100">
              {feedback.feedback_text}
            </p>
          </div>
        )}

        {/* Intelligence Breakdown Card */}
        <div className="bg-gradient-to-br from-indigo-50/50 to-purple-50/30 rounded-xl border border-indigo-100 p-5 space-y-4">
          <div className="flex items-center gap-2 text-indigo-900 font-semibold text-sm">
            <Sparkles className="w-4 h-4 text-indigo-600" />
            <span>AI Intelligence Insights</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div className="bg-white p-3 rounded-lg border border-indigo-100/60 shadow-2xs">
              <span className="text-slate-500">Sentiment Score</span>
              <p className="text-base font-bold text-slate-800 mt-0.5">
                {feedback.sentiment_score !== null && feedback.sentiment_score !== undefined
                  ? `${Math.round(feedback.sentiment_score * 100)}% Confidence`
                  : 'Pending'}
              </p>
            </div>
            <div className="bg-white p-3 rounded-lg border border-indigo-100/60 shadow-2xs">
              <span className="text-slate-500">Classification Model</span>
              <p className="text-base font-bold text-slate-800 mt-0.5">
                Baseline Heuristic ML
              </p>
            </div>
            <div className="bg-white p-3 rounded-lg border border-indigo-100/60 shadow-2xs">
              <span className="text-slate-500">Processing Status</span>
              <p className="text-base font-bold text-slate-800 mt-0.5 capitalize">
                {feedback.status}
              </p>
            </div>
          </div>
        </div>

        {/* Status Workflow Action */}
        <div className="pt-4 border-t border-slate-100 flex flex-wrap items-center justify-between gap-4">
          <span className="text-xs font-medium text-slate-600">Workflow State:</span>
          <div className="flex items-center gap-2">
            {['new', 'analyzed', 'resolved', 'archived'].map((st) => (
              <button
                key={st}
                onClick={() => handleStatusChange(st)}
                disabled={updatingStatus || feedback.status === st}
                className={`px-3 py-1 rounded-lg text-xs font-semibold capitalize transition ${
                  feedback.status === st
                    ? 'bg-slate-900 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                Mark {st}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
