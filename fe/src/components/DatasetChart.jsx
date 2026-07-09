import { useMemo } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Line } from 'react-chartjs-2'
import zoomPlugin from 'chartjs-plugin-zoom'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  zoomPlugin,
)

const COLORS = [
  '#e6194b', '#3cb44b', '#4363d8', '#f58231', '#911eb4',
  '#42d4f4', '#f032e6', '#bfef45', '#fabed4', '#469990',
  '#dcbeff', '#9A6324', '#800000', '#aaffc3', '#808000',
  '#ffd8b1', '#000075', '#a9a9a9',
]

function formatDate(iso) {
  const d = new Date(iso)
  return d.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export default function DatasetChart({ dataSeries }) {
  const { datasets, labels } = useMemo(() => {
    if (!dataSeries || dataSeries.length === 0) return { datasets: [], labels: [] }

    const first = dataSeries[0]
    const labels = first.timestamps.map(ts => formatDate(ts.date))

    const sorted = [...dataSeries].sort((a, b) => a.name.localeCompare(b.name))
    const datasets = sorted.map((series, i) => ({
      label: series.name,
      data: series.timestamps.map(ts => Number(ts.value.OT)),
      borderColor: COLORS[i % COLORS.length],
      borderWidth: 0.5,
      pointRadius: 0,
      pointHoverRadius: 3,
      tension: 0,
      fill: false,
    }))

    return { datasets, labels }
  }, [dataSeries])

  if (!dataSeries || dataSeries.length === 0) {
    return <p>No data series in this dataset.</p>
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'bottom',
        labels: { boxWidth: 12, padding: 12, font: { size: 11 } },
      },
      tooltip: {
        callbacks: {
          label(ctx) {
            return `${ctx.dataset.label}: ${ctx.parsed.y}`
          },
        },
      },
      zoom: {
        pan: {
          enabled: true,
          mode: 'x',
        },
        zoom: {
          wheel: { enabled: true },
          pinch: { enabled: true },
          drag: false,
          mode: 'x',
        },
      },
    },
    scales: {
      x: {
        title: { display: true, text: 'Date' },
        ticks: {
          maxRotation: 45,
          autoSkip: true,
          maxTicksLimit: 20,
          font: { size: 10 },
        },
      },
      y: {
        title: { display: true, text: 'OT Value' },
        beginAtZero: false,
        ticks: { font: { size: 10 } },
      },
    },
  }

  return (
    <div className="chart-wrapper">
      <div className="chart-hint">Scroll to zoom, drag to pan, double-click to reset</div>
      <div className="chart-container">
        <Line data={{ labels, datasets }} options={options} />
      </div>
    </div>
  )
}
