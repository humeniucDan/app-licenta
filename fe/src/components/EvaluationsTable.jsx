const METRIC_NAMES = ['MSE', 'MAE', 'SMAPE', 'R^2']

export default function EvaluationsTable({ evaluations }) {
  if (!evaluations || evaluations.length === 0) return null

  return (
    <div className="evals-section">
      <h3>Model Evaluations</h3>
      <table className="evals-table">
        <thead>
          <tr>
            <th>Model</th>
            {METRIC_NAMES.map(m => (
              <th key={m} className="num">{m}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {evaluations.map(ev => (
            <tr key={ev.model_id}>
              <td>{ev.model_name}</td>
              {METRIC_NAMES.map(m => (
                <td key={m} className="num">
                  {ev.metrics[m] != null ? Number(ev.metrics[m]).toFixed(4) : '—'}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
