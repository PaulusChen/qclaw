import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard/Dashboard'
import IndicatorsPage from './pages/IndicatorsPage'
import NewsPage from './pages/NewsPage'
import BacktestPage from './pages/BacktestPage'
import SettingsPage from './pages/SettingsPage'
import {
  DeepLearningLayout,
  TrainingPage,
  InferencePage,
  ManagementPage,
  PreprocessingPage,
} from './pages/DeepLearning'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="indicators" element={<IndicatorsPage />} />
        <Route path="news" element={<NewsPage />} />
        <Route path="backtest" element={<BacktestPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
      
      {/* 深度学习模块路由 */}
      <Route path="/deep-learning" element={<DeepLearningLayout />}>
        <Route index element={<Navigate to="training" replace />} />
        <Route path="training" element={<TrainingPage />} />
        <Route path="inference" element={<InferencePage />} />
        <Route path="management" element={<ManagementPage />} />
        <Route path="preprocessing" element={<PreprocessingPage />} />
      </Route>
    </Routes>
  )
}

export default App
