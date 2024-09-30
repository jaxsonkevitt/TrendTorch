'use client';

import { useState } from 'react';
import dynamic from 'next/dynamic';
import '../styles/TrendingProducts.css';

const Chart = dynamic(() => import('react-chartjs-2').then((mod) => mod.Line), { ssr: false });
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

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

export default function TrendingProducts({ trends }) {
  return (
    <div className="trending-products-grid">
      {trends.map((trend, index) => (
        <div key={index} className="trend-item">
          <div className="trend-item-content">
            <h2 title={trend.query}>{trend.query}</h2>
            <p>
              Spike Percentage: <span className="spike-percentage">{trend.spike_percentage.toFixed(2)}%</span>
            </p>
            <div className="trend-graph">
              <Chart
                data={{
                  labels: Array.from({ length: trend.trend_data.length }, (_, i) => i + 1),
                  datasets: [{
                    label: 'Trend Data',
                    data: trend.trend_data,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1,
                    fill: true,
                  }]
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      display: false,
                    },
                    tooltip: {
                      mode: 'index',
                      intersect: false,
                    },
                  },
                  scales: {
                    y: {
                      beginAtZero: true,
                      ticks: {
                        maxTicksLimit: 3,
                      },
                    },
                    x: {
                      display: false,
                    },
                  },
                }}
              />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
