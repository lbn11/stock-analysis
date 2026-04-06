import { BrowserRouter, Routes, Route } from 'react-router-dom';
import MainLayout from './components/layout/MainLayout';
import HomePage from './pages/HomePage';
import AnalysisPage from './pages/AnalysisPage';
import PredictionPage from './pages/PredictionPage';
import FactorsPage from './pages/FactorsPage';
import HistoryPage from './pages/HistoryPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<HomePage />} />
          <Route path="analysis" element={<AnalysisPage />} />
          <Route path="analysis/:stockCode" element={<AnalysisPage />} />
          <Route path="prediction" element={<PredictionPage />} />
          <Route path="prediction/:stockCode" element={<PredictionPage />} />
          <Route path="factors" element={<FactorsPage />} />
          <Route path="history" element={<HistoryPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
