import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import {
  Package,
  Users,
  DollarSign,
  Settings,
  Bot,
  Download,
  LayoutDashboard,
  Menu,
  X
} from 'lucide-react';
import { cn } from '@/utils/cn';
import { Button } from '@/components/ui/button';
import Dashboard from '@/pages/Dashboard';
import Items from '@/pages/Items';
import Leads from '@/pages/Leads';
import Sales from '@/pages/Sales';
import AIAssistant from '@/pages/AIAssistant';
import SettingsPage from '@/pages/Settings';
import ExportPage from '@/pages/Export';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/items', icon: Package, label: 'Items' },
  { to: '/leads', icon: Users, label: 'Leads' },
  { to: '/sales', icon: DollarSign, label: 'Sales' },
  { to: '/ai', icon: Bot, label: 'AI Assistant' },
  { to: '/export', icon: Download, label: 'Export' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
        {/* Mobile header */}
        <header className="lg:hidden fixed top-0 left-0 right-0 h-16 bg-white dark:bg-slate-900 border-b z-40 flex items-center px-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
          <div className="flex items-center gap-2 ml-4">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
              <span className="text-white font-bold text-lg">S</span>
            </div>
            <span className="font-bold text-xl">Scrounger</span>
          </div>
        </header>

        {/* Sidebar */}
        <aside className={cn(
          "fixed top-0 left-0 h-full w-64 bg-white dark:bg-slate-900 border-r z-50 transition-transform duration-300",
          "lg:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}>
          <div className="p-6 border-b">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-xl">S</span>
              </div>
              <div>
                <h1 className="font-bold text-xl">Scrounger</h1>
                <p className="text-xs text-muted-foreground">Sales Tracker</p>
              </div>
            </div>
          </div>

          <nav className="p-4 space-y-2">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={() => setSidebarOpen(false)}
                className={({ isActive }) => cn(
                  "flex items-center gap-3 px-4 py-3 rounded-lg transition-all",
                  "hover:bg-slate-100 dark:hover:bg-slate-800",
                  isActive && "bg-primary/10 text-primary font-medium shadow-sm"
                )}
              >
                <item.icon className="h-5 w-5" />
                <span>{item.label}</span>
              </NavLink>
            ))}
          </nav>

          <div className="absolute bottom-0 left-0 right-0 p-4 border-t">
            <div className="bg-gradient-to-r from-primary/10 to-purple-500/10 rounded-lg p-4">
              <p className="text-sm font-medium">Track your sales</p>
              <p className="text-xs text-muted-foreground mt-1">
                Reddit, eBay, Swappa & more
              </p>
            </div>
          </div>
        </aside>

        {/* Mobile overlay */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 bg-black/50 z-40 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Main content */}
        <main className="lg:ml-64 min-h-screen pt-16 lg:pt-0">
          <div className="p-6 lg:p-8 max-w-7xl mx-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/items" element={<Items />} />
              <Route path="/leads" element={<Leads />} />
              <Route path="/sales" element={<Sales />} />
              <Route path="/ai" element={<AIAssistant />} />
              <Route path="/export" element={<ExportPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  );
}

export default App;
