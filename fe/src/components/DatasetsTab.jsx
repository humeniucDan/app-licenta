import { useState, useEffect } from 'react'
import { getDatasets, getDatasetDetail, getEvaluationsByDataset } from '../api'
import DatasetChart from './DatasetChart'
import EvaluationsTable from './EvaluationsTable'

export default function DatasetsTab() {
  const [datasets, setDatasets] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [detail, setDetail] = useState(null)
  const [evaluations, setEvaluations] = useState(null)
  const [loading, setLoading] = useState(true)
  const [loadingDetail, setLoadingDetail] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    getDatasets()
      .then(setDatasets)
      .catch(setError)
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!selectedId) {
      setDetail(null)
      setEvaluations(null)
      return
    }
    setLoadingDetail(true)
    Promise.all([
      getDatasetDetail(selectedId),
      getEvaluationsByDataset(selectedId),
    ])
      .then(([d, ev]) => {
        setDetail(d)
        setEvaluations(ev)
      })
      .catch(setError)
      .finally(() => setLoadingDetail(false))
  }, [selectedId])

  if (loading) return <p>Loading datasets...</p>
  if (error) return <p className="error">{error.message}</p>

  return (
    <div>
      <h2>Datasets</h2>
      {datasets.length === 0 ? (
        <p>No datasets found.</p>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            {datasets.map(ds => (
              <tr
                key={ds.id}
                className={selectedId === ds.id ? 'selected' : ''}
                onClick={() => setSelectedId(ds.id)}
              >
                <td>{ds.name}</td>
                <td>{ds.description || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {selectedId && (
        <div className="detail-panel">
          <h3>{datasets.find(d => d.id === selectedId)?.name}</h3>
          {loadingDetail ? (
            <p>Loading data...</p>
          ) : detail ? (
            <>
              <DatasetChart dataSeries={detail.data_series} />
              {evaluations && <EvaluationsTable evaluations={evaluations} />}
            </>
          ) : null}
        </div>
      )}
    </div>
  )
}
