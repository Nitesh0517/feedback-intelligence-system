import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Send, Sparkles, CheckCircle2 } from 'lucide-react';
import { feedbackApi } from '../services/api';
import { ErrorMessage } from '../components/ErrorMessage';

const SOURCES = [
  'Web Form',
  'Mobile App',
  'Email',
  'Survey',
  'Twitter/Social',
  'Customer Support',
  'In-Store',
];

export function FeedbackForm() {
  const navigate = useNavigate();
  const [source, setSource] = useState('Web Form');
  const [customerIdentifier, setCustomerIdentifier] = useState('');
  const [feedbackText, setFeedbackText] = useState('');
  const [analyzeImmediately, setAnalyzeImmediately] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!feedbackText.trim()) {
      setError('Feedback text cannot be empty.');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const payload = {
        source,
        feedback_text: feedbackText.trim(),
        customer_identifier: customerIdentifier.trim() || null,
      };

      const res = await feedbackApi.create(payload);
      const newFeedback = res.data;

      if (analyzeImmediately && newFeedback?.id) {
        try {
          await feedbackApi.analyze(newFeedback.id);
        } catch (analyzeErr) {
          console.warn('Initial analysis background failure:', analyzeErr);
        }
      }

      setSuccess(true);
      setTimeout(() => {
        navigate(`/feedback/${newFeedback.id}`);
      }, 1200);
    } catch (err) {
      setError(err.message || 'Failed to submit feedback.');
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Submit Customer Feedback</h1>
        <p className="text-sm text-slate-500 mt-1">
          Ingest new feedback from any customer touchpoint for automated AI categorization and sentiment scoring.
        </p>
      </div>

      {error && <ErrorMessage message={error} />}

      {success ? (
        <div className="p-8 bg-emerald-50 border border-emerald-200 rounded-2xl text-center space-y-3">
          <CheckCircle2 className="w-12 h-12 text-emerald-600 mx-auto" />
          <h3 className="text-lg font-bold text-emerald-900">Feedback Ingested Successfully!</h3>
          <p className="text-sm text-emerald-700">Redirecting to feedback intelligence view...</p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="bg-white p-6 sm:p-8 rounded-2xl border border-slate-200 shadow-xs space-y-6">
          {/* Source */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-2">
              Ingestion Source *
            </label>
            <select
              value={source}
              onChange={(e) => setSource(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
              required
            >
              {SOURCES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>

          {/* Customer Identifier */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-2">
              Customer Identifier (Optional)
            </label>
            <input
              type="text"
              placeholder="e.g. user_9824, alice@example.com, or enterprise-corp"
              value={customerIdentifier}
              onChange={(e) => setCustomerIdentifier(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
            />
            <p className="text-xs text-slate-400 mt-1">
              Helpful for correlating feedback with user account cohorts.
            </p>
          </div>

          {/* Feedback Text */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600">
                Customer Feedback Text *
              </label>
              <span className="text-xs text-slate-400">{feedbackText.length} characters</span>
            </div>
            <textarea
              rows={5}
              placeholder="Paste raw customer review, ticket message, or survey response..."
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
              className="w-full px-4 py-3 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
              required
              minLength={3}
            />
          </div>

          {/* Options */}
          <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
            <label className="flex items-center gap-2 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={analyzeImmediately}
                onChange={(e) => setAnalyzeImmediately(e.target.checked)}
                className="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 border-slate-300"
              />
              <span className="text-sm font-medium text-slate-700 flex items-center gap-1.5">
                <Sparkles className="w-4 h-4 text-indigo-600" />
                Run AI analysis immediately
              </span>
            </label>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={submitting}
            className="w-full py-3 px-4 rounded-xl font-semibold text-sm bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 transition flex items-center justify-center gap-2 shadow-sm"
          >
            {submitting ? (
              <span>Ingesting & Processing...</span>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span>Submit Feedback</span>
              </>
            )}
          </button>
        </form>
      )}
    </div>
  );
}
