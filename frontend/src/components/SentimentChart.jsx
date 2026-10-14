import React from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Doughnut } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend);

export function SentimentChart({ positive = 0, neutral = 0, negative = 0, height = 240 }) {
  const total = positive + neutral + negative;

  if (total === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center bg-slate-50/50 rounded-xl border border-dashed border-slate-200">
        <p className="text-xs text-slate-400">No sentiment data recorded yet.</p>
      </div>
    );
  }

  const data = {
    labels: ['Positive', 'Neutral', 'Negative'],
    datasets: [
      {
        data: [positive, neutral, negative],
        backgroundColor: ['#10b981', '#94a3b8', '#f43f5e'],
        borderWidth: 2,
        borderColor: '#ffffff',
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          boxWidth: 12,
          padding: 16,
          font: { size: 12 },
        },
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const val = context.raw || 0;
            const pct = Math.round((val / total) * 100);
            return ` ${context.label}: ${val} (${pct}%)`;
          },
        },
      },
    },
  };

  return (
    <div style={{ height }} className="relative flex items-center justify-center">
      <Doughnut data={data} options={options} />
    </div>
  );
}
