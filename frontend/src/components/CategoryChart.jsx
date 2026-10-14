import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

export function CategoryChart({ categories = {}, height = 240 }) {
  const labels = Object.keys(categories);
  const dataValues = Object.values(categories);
  const total = dataValues.reduce((acc, curr) => acc + curr, 0);

  if (total === 0 || labels.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center bg-slate-50/50 rounded-xl border border-dashed border-slate-200">
        <p className="text-xs text-slate-400">No category breakdown data available yet.</p>
      </div>
    );
  }

  const data = {
    labels,
    datasets: [
      {
        label: 'Feedback Entries',
        data: dataValues,
        backgroundColor: '#6366f1',
        borderRadius: 6,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (context) => ` ${context.raw} submissions`,
        },
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
      <Bar data={data} options={options} />
    </div>
  );
}
