import React, { useState } from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line
} from 'recharts';
import { 
  Leaf, 
  TrendingUp, 
  IndianRupee, 
  Award, 
  CheckCircle2, 
  Clock, 
  FileText,
  Truck,
  Download
} from 'lucide-react';

const monthlyData = [
  { month: 'Jun', tonnes: 18, co2: 20.7, savings: 24000 },
  { month: 'Jul', tonnes: 32, co2: 36.8, savings: 41000 },
  { month: 'Aug', tonnes: 45, co2: 51.7, savings: 59000 },
  { month: 'Sep', tonnes: 60, co2: 69.0, savings: 82000 },
  { month: 'Oct', tonnes: 85, co2: 97.7, savings: 114000 },
];

export const DashboardPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'deals'>('overview');

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Dashboard Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">
              Cauvery Sugar Mills Ltd
            </h1>
            <span className="px-2.5 py-0.5 rounded-full bg-eco-100 text-eco-800 dark:bg-eco-950 dark:text-eco-300 text-xs font-bold border border-eco-200 dark:border-eco-800">
              Verified Seller
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            GSTIN: 33AABCC1234F1Z1 | PCB Auth: PCB/NM/SMR-2023-41 | Trust Score: 4.90 / 5.0
          </p>
        </div>

        <button
          onClick={() => alert("Downloading official ESG Sustainability & CSR Carbon Offset Certificate (PDF)...")}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-eco-600 hover:bg-eco-700 text-white font-bold text-xs shadow-sm transition"
        >
          <Download className="w-4 h-4" />
          <span>Download CSR Certificate</span>
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span>Landfill Waste Diverted</span>
            <Leaf className="w-4 h-4 text-eco-600" />
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-white">
            140.0 MT
          </div>
          <div className="text-[11px] text-eco-600 font-semibold flex items-center gap-1">
            <span>+28% vs previous quarter</span>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span>Scope 3 CO₂ Mitigated</span>
            <TrendingUp className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-black text-emerald-600">
            161.0 MT CO₂e
          </div>
          <div className="text-[11px] text-slate-400 font-medium">
            Certified EPA standard factor
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span>Byproduct Revenue Earned</span>
            <IndianRupee className="w-4 h-4 text-amber-600" />
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-white">
            ₹2,52,000
          </div>
          <div className="text-[11px] text-eco-600 font-semibold">
            Zero disposal cost incurred
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span>Eco Partner Trust Badges</span>
            <Award className="w-4 h-4 text-blue-600" />
          </div>
          <div className="flex items-center gap-1.5 pt-1">
            <span className="px-2 py-0.5 rounded-md bg-blue-50 dark:bg-blue-950 text-blue-700 dark:text-blue-300 font-bold text-xs border border-blue-200 dark:border-blue-800">
              Verified
            </span>
            <span className="px-2 py-0.5 rounded-md bg-eco-50 dark:bg-eco-950 text-eco-700 dark:text-eco-300 font-bold text-xs border border-eco-200 dark:border-eco-800">
              Eco Partner
            </span>
          </div>
        </div>
      </div>

      {/* Analytics Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-4">
          <h2 className="font-bold text-base text-slate-900 dark:text-white">
            Monthly Landfill Diversion Trend (Metric Tonnes)
          </h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                <XAxis dataKey="month" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} />
                <Tooltip />
                <Bar dataKey="tonnes" fill="#16a34a" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-4">
          <h2 className="font-bold text-base text-slate-900 dark:text-white">
            CO₂ Abatement & Economic Value (INR)
          </h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                <XAxis dataKey="month" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} />
                <Tooltip />
                <Line type="monotone" dataKey="co2" stroke="#059669" strokeWidth={3} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Contracts & Deal Room Stepper Preview */}
      <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="font-bold text-base text-slate-900 dark:text-white">
            Active Consignment Deal Room
          </h2>
          <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-eco-100 text-eco-800 dark:bg-eco-950 dark:text-eco-300">
            Contract #DEAL-2026-001
          </span>
        </div>

        {/* Stepper */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-xs">
          <div className="p-3 rounded-xl bg-eco-50 dark:bg-eco-950 border border-eco-200 dark:border-eco-800 text-eco-800 dark:text-eco-300 flex flex-col gap-1">
            <span className="font-bold flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-eco-600" />
              1. Negotiation
            </span>
            <span className="text-[10px] text-eco-600">Quote Accepted</span>
          </div>

          <div className="p-3 rounded-xl bg-eco-50 dark:bg-eco-950 border border-eco-200 dark:border-eco-800 text-eco-800 dark:text-eco-300 flex flex-col gap-1">
            <span className="font-bold flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-eco-600" />
              2. Agreed
            </span>
            <span className="text-[10px] text-eco-600">Contact Unmasked</span>
          </div>

          <div className="p-3 rounded-xl bg-eco-50 dark:bg-eco-950 border border-eco-200 dark:border-eco-800 text-eco-800 dark:text-eco-300 flex flex-col gap-1">
            <span className="font-bold flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-eco-600" />
              3. Payment
            </span>
            <span className="text-[10px] text-eco-600">Simulated Verified</span>
          </div>

          <div className="p-3 rounded-xl bg-amber-50 dark:bg-amber-950 border border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-300 flex flex-col gap-1 animate-pulse">
            <span className="font-bold flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-amber-600" />
              4. In Transit
            </span>
            <span className="text-[10px] text-amber-600">Truck TN-28-AK-8899</span>
          </div>

          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800 text-slate-400 flex flex-col gap-1">
            <span className="font-bold">5. Completed</span>
            <span className="text-[10px]">Gate In & ESG Log</span>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-3">
            <FileText className="w-5 h-5 text-slate-500" />
            <div>
              <span className="font-bold text-slate-800 dark:text-slate-200 block">
                Digital Consignment Manifest (E-Challan)
              </span>
              <span className="text-slate-400 font-mono text-[11px]">
                SHA-256: 7e2d9b41...f89c02 (Embedded QR code verified)
              </span>
            </div>
          </div>

          <button
            onClick={() => alert("Manifest PDF downloaded with cryptographic SHA-256 fingerprint.")}
            className="px-3.5 py-1.5 rounded-lg bg-slate-900 dark:bg-white text-white dark:text-slate-900 font-bold text-xs"
          >
            Download E-Challan PDF
          </button>
        </div>
      </div>
    </div>
  );
};
