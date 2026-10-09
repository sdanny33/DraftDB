import { useEffect, useRef, useState } from 'react'
import { Chart, registerables } from 'chart.js'
import { NavLink, Route, Routes } from 'react-router-dom'
import './App.css'
import { dex } from './js/pokedex'
import { monData } from './js/mon-data'
Chart.register(...registerables)
Chart.defaults.font.family = "'Geist Pixel', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
Chart.defaults.color = 'rgba(0, 0, 0, 0.6)'

const logo = `${import.meta.env.BASE_URL}DDB_LogoFinal.png`

function getLeaderMons(stat) {
  return Object.values(monData)
    .sort((firstMon, secondMon) => secondMon[stat] - firstMon[stat])
    .slice(0, 10)
    .map((mon) => ({
      name: mon.name,
      sprite: getSprite(mon.name),
      [stat]: mon[stat]
    }))
}

const killLeaders = getLeaderMons('kills')
const deathLeaders = getLeaderMons('deaths')

function getSprite(name) {
  const info = getInfo(name)
  if (!info) {
    return null
  }

  const key = name.toLowerCase().replace(/[^a-z0-9]/g, '')
  const spritePath = monData[key]?.sprite || `sprites/${info.dexNum}.png`
  return `${import.meta.env.BASE_URL}${spritePath}`
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
    winrate: pokemon.winrate,
    points: pokemon.points,
    move: pokemon.move,
    super_effective: pokemon.super_effective,
    resisted: pokemon.resisted,
    immune: pokemon.immune,
    crit: pokemon.crit,
    dpg: pokemon.avg_damage,
    dtpg: pokemon.avg_damage_taken,
    hpg: pokemon.avg_healing,
    switches: pokemon.avg_switches,
    hit_percent: pokemon.hit_percent,
    tera: pokemon.tera_percent,
  }
  return stats
}

function cssVar(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
}

const navItems = [
  { to: '/', label: 'Home', end: true },
  { to: '/battle-stats', label: 'Battle Stats' },
  { to: '/mon-lookup', label: 'Mon Lookup' },
]

function Layout({ children }) {
  return (
    <div className="cover">
      <header className="nav-bar">
        <NavLink className="brand" to="/" end>
          <img className="logo" src={logo} alt="" />
          <span className="brand-name">DraftDB</span>
        </NavLink>
        <nav className="links" aria-label="Primary">
          {navItems.map(({ to, label, end }) => (
            <NavLink key={to} to={to} end={end} className={({ isActive }) => `link${isActive ? ' active' : ''}`}>
              {label}
            </NavLink>
          ))}
        </nav>
      </header>
      {children}
    </div>
  )
}

function LeadersMarquee({ mons = [], speed = 30, stat = '' }) {
  // Duplicate the list so the CSS animation can loop seamlessly at -50%.
  const looped = [...mons, ...mons]

  return (
    <div className="marquee" style={{ '--marquee-duration': `${speed}s` }}>
      <div className="marquee__track">
        {looped.map((mon, i) => {
          const rank = (i % mons.length) + 1
          return (
            <div className="scroll-card" key={i} aria-hidden={i >= mons.length ? true : undefined}>
              <img className="sprite" src={mon.sprite} alt={mon.name} />
              <div className="info-container">
                <span className={`rank${rank === 1 ? ' first' : ''}`}>#{rank}</span>
                <span className="header-text">{mon.name}</span>
                <span className="stat-text">{mon[stat].toLocaleString()} {stat}</span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function Home() {
  return (
    <Layout>
      <section className="hero">
        <div className="hero-inner">
          <span className="eyebrow">Gen 9 Draft League</span>
          <h1 className="title">Welcome to <span className="accent">DraftDB</span></h1>
          <p className="subtitle">
            Battle statistics for every drafted Pokémon: kills, deaths, damage and winrate, all in one place.
          </p>
        </div>
      </section>
      <div className="section-heading">
        <h2 className="h1">Kill leaders</h2>
        <span className="h2">Top 10 by total kills</span>
      </div>
      <LeadersMarquee mons={killLeaders} speed={30} stat="kills" />
      <div className="section-heading">
        <h2 className="h1">Death leaders</h2>
        <span className="h2">Top 10 by total deaths</span>
      </div>
      <LeadersMarquee mons={deathLeaders} speed={30} stat="deaths" />
    </Layout>
  )
}

function BattleStats() {
  const battleMons = Object.values(monData).filter((mon) => mon.gamesPlayed > 500)

  const [selectedColumn, setSelectedColumn] = useState(null)
  const [sortDirection, setSortDirection] = useState('ascending')
  const headers = ['sprite', 'name', 'points', 'games', 'winrate', 'kills', 'deaths', 'diff', 'kpg', 'move', 'crit', 'dpg', 'dtpg', 'hpg', 'hit','switches']
  const columnValues = { sprite: 'name', name: 'name', points: 'points', games: 'gamesPlayed', winrate: 'winrate', kills: 'kills', deaths: 'deaths', diff: 'diff', kpg: 'kpg', move: 'move', crit: 'crit', dpg: 'avg_damage', dtpg: 'avg_damage_taken', hpg: 'avg_healing', hit: 'hit_percent', switches: 'avg_switches' }

  function handleSort(column) {
    const nextDirection = selectedColumn === column && sortDirection === 'descending'
      ? 'ascending'
      : 'descending'
    setSelectedColumn(column)
    setSortDirection(nextDirection)
  }

  const sortedBattleMons = [...battleMons].sort((firstMon, secondMon) => {
    if (!selectedColumn) {
      return 0
    }

    const property = columnValues[selectedColumn]
    const firstValue = firstMon[property]
    const secondValue = secondMon[property]
    const comparison = typeof firstValue === 'string'
      ? firstValue.localeCompare(secondValue)
      : firstValue - secondValue

    return sortDirection === 'ascending' ? comparison : -comparison
  })

  return (
    <Layout>
      <main className="page">
        <div className="page-header">
          <span className="eyebrow">Season stats</span>
          <h1 className="title">Battle Stats</h1>
          <p className="subtitle">Pokémon with more than 500 games played. Click a column header to sort.</p>
        </div>
        <div className="surface">
          <div className="table-meta">
            <span>{sortedBattleMons.length} Pokémon</span>
          </div>
          <div className="table-container">
            <table className="rounded-corners">
              <thead>
                <tr>
                  {headers.map((header) => (
                    <th
                      className={selectedColumn === header ? 'selected-column' : ''}
                      key={header}
                      scope="col"
                      tabIndex={0}
                      aria-sort={selectedColumn === header ? sortDirection : undefined}
                      onClick={() => handleSort(header)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault()
                          handleSort(header)
                        }
                      }}
                    >
                      {header === 'sprite' ? '' : header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {sortedBattleMons.map((mon) => {
                  const sprite = getSprite(mon.name)
                  return (
                    <tr key={mon.name}>
                      <td><img src={sprite} alt={mon.name} loading="lazy" /></td>
                      <td className="name-cell">{mon.name}</td>
                      <td>{mon.points}</td>
                      <td>{mon.gamesPlayed}</td>
                      <td>{mon.winrate}%</td>
                      <td>{mon.kills}</td>
                      <td>{mon.deaths}</td>
                      <td>{mon.diff}</td>
                      <td>{mon.kpg}</td>
                      <td>{mon.move}</td>
                      <td>{mon.crit}</td>
                      <td>{mon.avg_damage}</td>
                      <td>{mon.avg_damage_taken}</td>
                      <td>{mon.avg_healing}</td>
                      <td>{mon.hit_percent}</td>
                      <td>{mon.avg_switches}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </Layout>
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
    const tickColor = cssVar('--text-secondary')
    const gridColor = cssVar('--divider')

    const chart = new Chart(chartRef.current, {
      type: 'bar',
      data: {
        labels: ['HP', 'Atk', 'Def', 'Sp.Atk', 'Sp.Def', 'Speed'],
        datasets: [{
          label: 'Base Stats',
          data: [info?.stats?.hp || 0, info?.stats?.atk || 0, info?.stats?.def || 0, info?.stats?.spa || 0, info?.stats?.spd || 0, info?.stats?.spe || 0],
          backgroundColor: cssVar('--primary-600'),
          hoverBackgroundColor: cssVar('--primary-700'),
          borderRadius: 4,
          borderSkipped: false,
          barThickness: 18,
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
            color: cssVar('--neutral-700'),
            font: { size: 14, weight: 500 },
            padding: { bottom: 12 },
          }
        },
        scales: {
          x: { beginAtZero: true, max: 200, ticks: { color: tickColor }, grid: { color: gridColor }, border: { display: false } },
          y: { ticks: { color: tickColor }, grid: { display: false }, border: { display: false } },
        }
      }
    })

    return () => chart.destroy()
  }, [info?.name])

  const pct = (v) => (v == null ? v : `${v}%`)

  return (
    <Layout>
      <main className="page">
        <div className="page-header">
          <span className="eyebrow">Lookup</span>
          <h1 className="title">Mon Lookup</h1>
          <p className="subtitle">Pick a Pokémon to see its base stats and its draft league performance.</p>
        </div>

        <section className="search-section">
          <div className="surface-header">
            <h2 className="h1">Search for a Pokémon</h2>
            <p className="h2">Select a Pokémon to filter stats for that specific mon.</p>
          </div>
          <div className="search-bar-container">
            <div className="search-bar">
              <select value={query} onChange={(e) => setQuery(e.target.value)} className="text" aria-label="Pokémon">
                <option value="">Select a Pokemon</option>
                {Object.values(dex).map((pokemon) => (
                  <option key={pokemon.name} value={pokemon.name}>
                    {pokemon.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </section>

        <section className="search-section">
          <div className="info-container">
            <div className="table-container">
              <table className="rounded-corners kv">
                <tbody>
                  <tr><td>Name</td><td>{info?.name || '—'}</td></tr>
                  <tr><td>Pokédex Number</td><td>{info?.dexNum || '—'}</td></tr>
                  <tr>
                    <td>Type</td>
                    <td>
                      {info?.types
                        ? <span className="tag-list">{info.types.map((t) => <span className="tag" key={t}>{t}</span>)}</span>
                        : '—'}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div className="sprite-frame">
              <img src={getSprite(info?.name) || `${import.meta.env.BASE_URL}sprites/0.png`} className="sprite" alt={info?.name || 'Unknown Pokemon'} />
            </div>
            <div className="stats-chart">
              <canvas ref={chartRef} aria-label={`${info?.name || 'Pokemon'} base stats`} />
            </div>
          </div>
        </section>

        <section className="search-section">
          <div className="surface-header">
            <h2 className="h1">{info?.name || 'Mon Name'}</h2>
            <p className="h2">Draft league performance.</p>
          </div>
          <div className="card-grid">
            {[
              ['Games', stats?.gamesPlayed],
              ['Points', stats?.points],
              ['Winrate', pct(stats?.winrate)],
              ['Kills', stats?.kills],
              ['Deaths', stats?.deaths],
              ['Diff', stats?.diff],
              ['KPG', stats?.kpg],
              ['Move', stats?.move],
              ['Crit', stats?.crit],
              ['DPG', stats?.dpg],
              ['DTPG', stats?.dtpg],
              ['HPG', stats?.hpg],
              ['Hit', stats?.hit_percent],
              ['Switches', stats?.switches],
            ].map(([label, value]) => (
              <div className="stat-card" key={label}>
                <div className="header-text">{label}</div>
                <div className="stat-text">{value ?? '–'}</div>
              </div>
            ))}
          </div>
        </section>
      </main>
    </Layout>
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
