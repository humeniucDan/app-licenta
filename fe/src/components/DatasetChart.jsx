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
  if (!dataSeries || dataSeries.length === 0) {
    return <p>No data series in this dataset.</p>
  }

  const datasets = dataSeries.map((series, i) => {
    const color = COLORS[i % COLORS.length]
    const sorted = [...series.timestamps].sort(
      (a, b) => new Date(a.date) - new Date(b.date),
    )
    return {
      label: series.name,
      data: sorted.map(ts => ({
        x: formatDate(ts.date),
        y: Number(ts.value.OT),
      })),
      borderColor: color,
      backgroundColor: color + '33',
      pointRadius: 2,
      pointHoverRadius: 5,
      tension: 0.1,
      fill: false,
    }
  })

  const allTimestamps = dataSeries.flatMap(s => s.timestamps)
  const allLabels = [...new Set(allTimestamps.map(ts => formatDate(ts.date)))]
  allLabels.sort((a, b) => new Date(a) - new Date(b))

  const data = { labels: allLabels, datasets }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'bottom',
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
          drag: {
            enabled: true,
            backgroundColor: 'rgba(0,0,0,0.05)',
            borderColor: '#666',
            borderWidth: 1,
          },
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
        },
      },
      y: {
        title: { display: true, text: 'OT Value' },
        beginAtZero: false,
      },
    },
  }

  return (
    <div className="chart-wrapper">
      <div className="chart-hint">Scroll to zoom, drag to pan, double-click to reset</div>
      <div className="chart-container">
        <Line data={data} options={options} />
      </div>
    </div>
  )
}
