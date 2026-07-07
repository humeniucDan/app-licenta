import { useState, useEffect } from 'react'
import { getModels } from '../api'

export default function ModelsTab() {
  const [models, setModels] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getModels()
      .then(setModels)
      .catch(setError)
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p>Loading models...</p>
  if (error) return <p className="error">{error.message}</p>

  return (
    <div>
      <h2>Models</h2>
      {models.length === 0 ? (
        <p>No models found.</p>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>ID</th>
            </tr>
          </thead>
          <tbody>
            {models.map(m => (
              <tr key={m.id}>
                <td>{m.name}</td>
                <td className="mono">{m.id}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
