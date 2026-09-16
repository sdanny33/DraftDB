import { useState } from 'react'
import logo from './assets/DDB_Logo.png'
import './App.css'

function App() {
  return (
    <div className="cover">
      <div className="nav-bar">
        <img src={logo} alt="logo" />
        <div className="links">
          <div className="link"><div className="text">Battle Stats</div></div>
          <div className="link"><div className="text">Mon Lookup</div></div>
        </div>
      </div>
      <div className="welcome-section-padding">
        <div className="welcome-section">
          <div className="title">Welcome to DraftDB</div>
          <div className="subtitle">Your one-stop shop for all things Pokémon Draft</div>
        </div>
      </div>
    </div>
  )
}

export default App