/**
 * QCLaw 主应用组件
 */

import { Provider } from 'react-redux'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { store } from './store'
import Dashboard from './pages/Dashboard'

function App() {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <div className="app">
          <h1>QCLaw 投资分析仪表盘</h1>
          <Routes>
            <Route path="/" element={<Dashboard />} />
          </Routes>
        </div>
      </BrowserRouter>
    </Provider>
  )
}

export default App
