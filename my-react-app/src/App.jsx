import { Link, Route, Routes } from 'react-router-dom'
import logo from './assets/DDB_Logo.png'
import './App.css'

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
          <table>
            <tbody className="text-body">
              <tr className="text-header"><th>sprite</th><th>name</th><th>points</th><th>games_played</th><th>winrate</th><th>kills</th><th>deaths</th><th>diff</th></tr>
              <tr><td><img/></td><td>Venusaur</td><td>7</td><td>2320.0</td><td>38.92</td><td>1785</td><td>1806</td><td>-21</td></tr>
              <tr><td><img/></td><td>Charizard</td><td>1</td><td>1033.0</td><td>42.69</td><td>865</td><td>788</td><td>77</td></tr>
              <tr><td><img/></td><td>Blastoise</td><td>8</td><td>4894.0</td><td>45.63</td><td>2538</td><td>3716</td><td>-1178</td></tr>
              <tr><td><img/></td><td>Raichu</td><td>2</td><td>550.0</td><td>40.36</td><td>265</td><td>435</td><td>-170</td></tr>
              <tr><td><img/></td><td>Raichu-Alola</td><td>2</td><td>679.0</td><td>36.82</td><td>462</td><td>536</td><td>-74</td></tr>
              <tr><td><img/></td><td>Sandslash</td><td>1</td><td>828.0</td><td>44.81</td><td>351</td><td>677</td><td>-326</td></tr>
              <tr><td><img/></td><td>Sandslash-Alola</td><td>2</td><td>1431.0</td><td>43.82</td><td>1124</td><td>1129</td><td>-5</td></tr>
              <tr><td><img/></td><td>Clefable</td><td>10</td><td>6536.0</td><td>46.28</td><td>3268</td><td>4804</td><td>-1536</td></tr>
              <tr><td><img/></td><td>Ninetales</td><td>8</td><td>2546.0</td><td>42.77</td><td>1092</td><td>2111</td><td>-1019</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

function MonLookup() {
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