import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Recycle, Globe, Moon, Sun, ShieldCheck, Factory, Menu, X, LogIn, LogOut, User } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { t, i18n } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  const [isDark, setIsDark] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const userEmail = localStorage.getItem('user_email');
  const userRole = localStorage.getItem('user_role');

  const handleLogout = () => {
    localStorage.removeItem('supabase_access_token');
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_role');
    navigate('/login');
  };

  const toggleLanguage = () => {
    const nextLang = i18n.language === 'en' ? 'ta' : 'en';
    i18n.changeLanguage(nextLang);
  };

  const toggleDarkMode = () => {
    setIsDark(!isDark);
    if (!isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  const navLinks = [
    { path: '/', label: t('nav.marketplace') },
    { path: '/network', label: t('nav.network') },
    { path: '/dashboard', label: t('nav.dashboard') },
  ];

  return (
    <nav className="sticky top-0 z-50 glass-panel border-b border-slate-200 dark:border-slate-800 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-10 h-10 rounded-xl bg-eco-600 flex items-center justify-center text-white shadow-md shadow-eco-500/20 group-hover:scale-105 transition-transform">
              <Recycle className="w-6 h-6 animate-spin-slow" />
            </div>
            <div>
              <span className="font-extrabold text-lg text-slate-900 dark:text-white tracking-tight flex items-center gap-1.5">
                WasteExchange
                <span className="text-xs px-2 py-0.5 rounded-full bg-eco-100 text-eco-800 dark:bg-eco-950 dark:text-eco-300 font-semibold border border-eco-200 dark:border-eco-800">
                  B2B
                </span>
              </span>
              <p className="text-[10px] text-slate-500 dark:text-slate-400 font-medium tracking-wide">
                INDUSTRIAL SYMBIOSIS
              </p>
            </div>
          </Link>

          {/* Desktop Nav Items */}
          <div className="hidden md:flex items-center gap-1 lg:gap-2">
            {navLinks.map((link) => {
              const isActive = location.pathname === link.path;
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`px-3.5 py-2 rounded-lg text-sm font-semibold transition-all ${
                    isActive
                      ? 'bg-eco-600/10 text-eco-700 dark:text-eco-400'
                      : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  {link.label}
                </Link>
              );
            })}
          </div>

          {/* Action Tools */}
          <div className="hidden md:flex items-center gap-3">
            {/* Language Toggle */}
            <button
              onClick={toggleLanguage}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
              title="Toggle English / தமிழ்"
            >
              <Globe className="w-3.5 h-3.5 text-eco-600" />
              <span>{i18n.language === 'en' ? 'தமிழ்' : 'English'}</span>
            </button>

            {/* Dark Mode Toggle */}
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded-lg border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
              title="Toggle theme"
            >
              {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
            </button>

            {userEmail ? (
              <div className="flex items-center gap-2">
                <Link
                  to="/dashboard"
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-eco-50 dark:bg-eco-950/50 border border-eco-200 dark:border-eco-800 text-eco-700 dark:text-eco-300 text-xs font-bold hover:bg-eco-100 transition"
                >
                  <Factory className="w-3.5 h-3.5" />
                  <span className="max-w-[120px] truncate">{userEmail.split('@')[0]}</span>
                  <span className="text-[10px] uppercase px-1.5 py-0.2 rounded bg-eco-200 dark:bg-eco-900 text-eco-800 dark:text-eco-200 font-extrabold">
                    {userRole || 'User'}
                  </span>
                </Link>

                <button
                  onClick={handleLogout}
                  className="p-2 rounded-xl text-slate-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/30 transition"
                  title="Sign Out"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  to="/login"
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-200 text-xs font-bold hover:border-eco-500 hover:text-eco-600 transition"
                >
                  <LogIn className="w-3.5 h-3.5" />
                  <span>Sign In</span>
                </Link>

                <Link
                  to="/register"
                  className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-eco-600 hover:bg-eco-700 text-white text-xs font-bold shadow-sm shadow-eco-500/20 transition"
                >
                  <Factory className="w-3.5 h-3.5" />
                  <span>Register</span>
                </Link>
              </div>
            )}
          </div>

          {/* Mobile hamburger */}
          <div className="md:hidden flex items-center gap-2">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-slate-200 dark:border-slate-800 px-4 py-3 space-y-2 bg-white dark:bg-slate-900">
          {navLinks.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-lg text-sm font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
            >
              {link.label}
            </Link>
          ))}
          
          <div className="pt-2 border-t border-slate-200 dark:border-slate-800 space-y-2">
            {userEmail ? (
              <div className="flex items-center justify-between px-2 py-1">
                <span className="text-xs font-bold text-slate-700 dark:text-slate-300">
                  {userEmail} ({userRole})
                </span>
                <button
                  onClick={handleLogout}
                  className="text-xs text-red-600 font-bold"
                >
                  Sign Out
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-2 pt-1">
                <Link
                  to="/login"
                  onClick={() => setMobileMenuOpen(false)}
                  className="py-2 text-center text-xs font-bold rounded-lg border border-slate-300 dark:border-slate-700"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  onClick={() => setMobileMenuOpen(false)}
                  className="py-2 text-center text-xs font-bold rounded-lg bg-eco-600 text-white"
                >
                  Register
                </Link>
              </div>
            )}
          </div>

          <div className="flex items-center gap-2 pt-2 border-t border-slate-200 dark:border-slate-800">
            <button
              onClick={toggleLanguage}
              className="px-3 py-1.5 rounded-lg border text-xs font-semibold"
            >
              {i18n.language === 'en' ? 'தமிழ்' : 'English'}
            </button>
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded-lg border text-xs"
            >
              {isDark ? 'Light Mode' : 'Dark Mode'}
            </button>
          </div>
        </div>
      )}
    </nav>
  );
};
