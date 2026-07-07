import { useState } from 'react'
import ModelsTab from './components/ModelsTab'
import DatasetsTab from './components/DatasetsTab'
import './App.css'

const TABS = [
  { key: 'datasets', label: 'Datasets' },
  { key: 'models', label: 'Models' },
]

function App() {
  const [active, setActive] = useState('datasets')

  return (
    <div className="app">
      <header className="app-header">
        <h1>Time Series Explorer</h1>
        <nav className="tabs">
          {TABS.map(t => (
            <button
              key={t.key}
              className={active === t.key ? 'tab active' : 'tab'}
              onClick={() => setActive(t.key)}
            >
              {t.label}
            </button>
          ))}
        </nav>
      </header>
      <main className="app-main">
        {active === 'models' && <ModelsTab />}
        {active === 'datasets' && <DatasetsTab />}
      </main>
    </div>
  )
}

export default App
