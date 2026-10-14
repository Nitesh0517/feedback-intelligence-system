import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

export function FeedbackTrendChart({ dataPoints = [], height = 280 }) {
  if (!dataPoints || dataPoints.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center bg-slate-50/50 rounded-xl border border-dashed border-slate-200">
        <p className="text-xs text-slate-400">No trend velocity data in the selected range.</p>
      </div>
    );
  }

  const labels = dataPoints.map((p) => p.date);
  const totalVolume = dataPoints.map((p) => p.count);
  const positiveCounts = dataPoints.map((p) => p.positive_count);
  const negativeCounts = dataPoints.map((p) => p.negative_count);
  const neutralCounts = dataPoints.map((p) => p.neutral_count);

  const data = {
    labels,
    datasets: [
      {
        label: 'Total Volume',
        data: totalVolume,
        borderColor: '#6366f1',
        backgroundColor: 'rgba(99, 102, 241, 0.1)',
        tension: 0.25,
        fill: true,
      },
      {
        label: 'Positive',
        data: positiveCounts,
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.05)',
        tension: 0.25,
      },
      {
        label: 'Negative',
        data: negativeCounts,
        borderColor: '#f43f5e',
        backgroundColor: 'rgba(244, 63, 94, 0.05)',
        tension: 0.25,
      },
      {
        label: 'Neutral',
        data: neutralCounts,
        borderColor: '#94a3b8',
        backgroundColor: 'transparent',
        tension: 0.25,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: { boxWidth: 12, padding: 12, font: { size: 12 } },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: { stepSize: 1, precision: 0 },
      },
    },
  };

  return (
    <div style={{ height }} className="relative w-full">
      <Line data={data} options={options} />
    </div>
  );
}
