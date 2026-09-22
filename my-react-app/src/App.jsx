import { useEffect, useRef, useState } from 'react'
import { Chart, registerables } from 'chart.js'
import { Link, Route, Routes } from 'react-router-dom'
import logo from './assets/DDB_Logo.png'
import './App.css'
import { dex } from './js/pokedex'
import { monData } from './js/mon-data'
import.meta.env.BASE_URL

Chart.register(...registerables)

function getSprite(name) {
  const info = getInfo(name)
  if (!info) {
    return null
  }
  return `${import.meta.env.BASE_URL}sprites/${name}.png`
}

function getInfo(name) {
  if (!name) {
    return null
  }

  const key = name.toLowerCase().replace(/[^a-z0-9]/g, '')
  const pokemon = dex[key]

  if (!pokemon) {
    return null
  }

  const info = {
    name: pokemon.name,
    dexNum: pokemon.num,
    types: pokemon.types,
    stats: pokemon.baseStats
  }
  return info
}

function getStats(name) {
  if (!name) {
    return null
  }

  const key = name.toLowerCase().replace(/[^a-z0-9]/g, '')
  const pokemon = monData[key]

  if (!pokemon) {
    return null
  }

  const stats = {
    gamesPlayed: pokemon.gamesPlayed,
    kills: pokemon.kills,
    deaths: pokemon.deaths,
    diff: pokemon.diff,
    kpg: pokemon.kpg,
    winrate: pokemon.winrate
  }
  return stats
}


function Home() {
  return (
    <div className="cover">
      <div className="nav-bar">
        <img src={logo} alt="logo" />
        <div className="links">
          <Link className="link" to="/"><div className="text">Home</div></Link>
          <Link className="link" to="/battle-stats"><div className="text">Battle Stats</div></Link>
          <Link className="link" to="/mon-lookup"><div className="text">Mon Lookup</div></Link>
        </div>
      </div>
      <div className="section-padding">
        <div className="welcome-section">
          <div className="title">Welcome to DraftDB</div>
          <div className="subtitle">Your one-stop shop for all things Pokémon Draft</div>
        </div>
      </div>
    </div>
  )
}

function BattleStats() {
  const battleMons = Object.values(monData).filter((mon) => mon.gamesPlayed > 500)

  return (
    <div className="cover">
      <div className="nav-bar">
        <img src={logo} alt="logo" />
        <div className="links">
          <Link className="link" to="/"><div className="text">Home</div></Link>
          <Link className="link" to="/battle-stats"><div className="text">Battle Stats</div></Link>
          <Link className="link" to="/mon-lookup"><div className="text">Mon Lookup</div></Link>
        </div>
      </div>
      <style>
        
      </style>
      <div className="section-padding">
        <div className="title">Battle Stats</div>
        <div className="table-container">
          <table className="rounded-corners">
            <tbody className="text-body">
              <tr className="text-header">
                <th>sprite</th>
                <th>name</th>
                <th>points</th>
                <th>games_played</th>
                <th>winrate</th>
                <th>kills</th>
                <th>deaths</th>
                <th>diff</th></tr>
              {battleMons.map((mon) => {
                const sprite = getSprite(mon.name)
                return (
                  <tr key={mon.name}>
                    <td><img src={sprite} alt={mon.name} /></td>
                    <td>{mon.name}</td>
                    <td>{mon.points}</td>
                    <td>{mon.gamesPlayed}</td>
                    <td>{mon.winrate}</td>
                    <td>{mon.kills}</td>
                    <td>{mon.deaths}</td>
                    <td>{mon.diff}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

function MonLookup() {
  const [query, setQuery] = useState('')
  const info = getInfo(query)
  const stats = getStats(query)
  const chartRef = useRef(null)

  useEffect(() => {
    if (!chartRef.current) {
      return undefined
    }

    const chart = new Chart(chartRef.current, {
      type: 'bar',
      data: {
        labels: ['HP', 'Atk', 'Def', 'Sp.Atk', 'Sp.Def', 'Speed'],
        datasets: [{
          label: 'Base Stats',
          data: [
            info?.stats?.hp || 0,
            info?.stats?.atk || 0,
            info?.stats?.def || 0,
            info?.stats?.spa || 0,
            info?.stats?.spd || 0,
            info?.stats?.spe || 0
          ],
          backgroundColor: ['red', 'green', 'blue', 'orange', 'brown', 'purple'],
          borderColor: '#000',
          borderWidth: 1
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          title: {
            display: true,
            text: `Base Stats for ${info?.name || 'Unknown Pokemon'}`,
            font: { size: 16 }
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            font: { family: "Pixelify Sans" },
            max: 200
          }
        }
      }
    })

    return () => chart.destroy()
  }, [info])

  return (
    <div className="cover">
      <div className="nav-bar">
        <img src={logo} alt="logo" />
        <div className="links">
          <Link className="link" to="/"><div className="text">Home</div></Link>
          <Link className="link" to="/battle-stats"><div className="text">Battle Stats</div></Link>
          <Link className="link" to="/mon-lookup"><div className="text">Mon Lookup</div></Link>
        </div>
      </div>
      <div className="section-padding">
        <div className="title">Mon Lookup</div>
        <div className="search-section">
          <div className="h1">Search for a Pokemon</div>
          <div className="h2">Type a Pokemon name to filter stats for that specific mon.</div>
          <div className="search-bar-container">
            <div className="search-bar">
              <input
                className="text"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Enter a Pokemon name..."
              />
            </div>
          </div>
        </div>
        <div className="search-section">
          <div className="info-container">
            <div className="table-container">
              <table className="rounded-corners">
                <tbody className="text-body">
                  <tr><td>Name</td><td>{info?.name || '-'}</td></tr>
                  <tr><td>Pokedex Number</td><td>{info?.dexNum || '-'}</td></tr>
                  <tr><td>Type</td><td>{info?.types?.join(' / ') || '-'}</td></tr>
                </tbody>
              </table>
            </div>
            <img src={getSprite(info?.name) || `${import.meta.env.BASE_URL}sprites/0.png`} className="sprite" alt={info?.name || 'Unknown Pokemon'} />
            <div className="stats-chart">
              <canvas ref={chartRef} aria-label={`${info?.name || 'Pokemon'} base stats`} />
            </div>
          </div>
        </div>
        <div className="search-section">
          <div className="h1">{info?.name || 'Mon Name'}</div>
          <div className="h2">Single mon stat cards.</div>
          <div className="card-grid">
            {[
              ['Matches', stats?.gamesPlayed],
              ['Kills', stats?.kills],
              ['Deaths', stats?.deaths],
              ['Diff', stats?.diff],
              ['KPG', stats?.kpg],
              ['Winrate', stats?.winrate]
            ].map(([label, value]) => (
              <div className="stat-card" key={label}>
                <div className="header-text">{label}</div>
                <div className="stat-text">{value ?? '-'}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/battle-stats" element={<BattleStats />} />
      <Route path="/mon-lookup" element={<MonLookup />} />
    </Routes>
  )
}

export default App