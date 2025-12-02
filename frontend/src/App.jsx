import React, { useEffect, useState } from 'react'
import { Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const fetchData = async () => {
  const response = await fetch('/sample_recommendations.json')
  return response.json()
}

export default function App() {
  const [data, setData] = useState(null)

  useEffect(() => {
    fetchData().then(setData).catch(console.error)
  }, [])

  if (!data) return <div className="container">Loading data storytelling dashboard...</div>

  const labels = data.recommendations.map(r => `${r.user_id} (${r.model})`)
  const values = data.recommendations.map(r => r.titles.length)

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Titles recommended',
        data: values,
        backgroundColor: '#ef4444'
      }
    ]
  }

  return (
    <div className="container">
      <div className="card header">
        <div>
          <h1>Netflix Data Storytelling</h1>
          <p>React + Chart.js dashboard showing recommender strength.</p>
        </div>
        <span className="badge">Precision@K: {data.metrics.precision_at_k}</span>
      </div>

      <div className="card">
        <h2>Recommendation Coverage</h2>
        <Bar data={chartData} options={{ responsive: true, plugins: { legend: { display: false } } }} />
      </div>

      <div className="card">
        <h2>What we would pitch to Netflix</h2>
        <ul className="list">
          {data.recommendations.map((rec) => (
            <li key={`${rec.user_id}-${rec.model}`}>
              <strong>{rec.user_id}</strong> via {rec.model}: {rec.titles.join(', ')}
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
