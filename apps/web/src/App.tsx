import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { HomePage } from './pages/HomePage';
import { PassportPage } from './pages/PassportPage';
import { DashboardPage } from './pages/DashboardPage';
import { SymbiosisNetworkPage } from './pages/SymbiosisNetworkPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { Recycle, ShieldCheck, Heart } from 'lucide-react';

export const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans">
        <Navbar />

        <main className="flex-1">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/passport/:batchCode" element={<PassportPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/network" element={<SymbiosisNetworkPage />} />
          </Routes>
        </main>

        <footer className="border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 py-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-lg bg-eco-600 flex items-center justify-center text-white">
                <Recycle className="w-3.5 h-3.5" />
              </div>
              <span className="font-bold text-slate-700 dark:text-slate-300">
                Waste Exchange Platform (Industrial Symbiosis)
              </span>
            </div>

            <div className="flex items-center gap-6">
              <span className="flex items-center gap-1 text-eco-600 font-semibold">
                <ShieldCheck className="w-4 h-4" />
                <span>TNPCB Compliant & OWASP Hardened</span>
              </span>
              <span>© 2026 Circular Economy Initiative</span>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
};

export default App;
