import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { 
  Recycle, 
  Leaf, 
  TrendingUp, 
  ShieldCheck, 
  Truck, 
  MapPin, 
  Search, 
  ArrowRight, 
  Layers, 
  Factory, 
  CheckCircle2, 
  Sparkles,
  QrCode
} from 'lucide-react';
import { apiClient } from '../api/client';

interface Listing {
  id: string;
  title: string;
  description: string;
  quantity: number;
  unit: string;
  price_per_unit: number;
  batch_code: string;
  is_hazardous: boolean;
  industry?: {
    name: string;
    city: string;
    trust_score: number;
  };
  waste_types?: {
    name: string;
  };
}

export const HomePage: React.FC = () => {
  const { t } = useTranslation();
  const [stats, setStats] = useState({
    verified_industries_count: 8,
    active_listings_count: 14,
    total_tonnes_diverted: 100.0,
    total_co2_tonnes_mitigated: 95.2,
    total_economic_volume_inr: 106000.0,
  });

  const [listings, setListings] = useState<Listing[]>([
    {
      id: 'l1',
      title: 'Dry Crushed Bagasse Fiber (Low Moisture)',
      description: 'High fiber sugar mill bagasse suitable for kraft paper and biofuel briquettes.',
      quantity: 50.0,
      unit: 'ton',
      price_per_unit: 1800,
      batch_code: 'BAGASSE-2026-NMK-01',
      is_hazardous: false,
      industry: { name: 'Cauvery Sugar Mills Ltd', city: 'Namakkal', trust_score: 4.9 },
      waste_types: { name: 'Sugar Mill Bagasse' },
    },
    {
      id: 'l2',
      title: 'Class-F Pozzolanic Fly Ash (Silo Conditioned)',
      description: 'Dry pulverized coal fly ash conforming to IS:3812 Part 1 for Portland Pozzolana Cement.',
      quantity: 120.0,
      unit: 'ton',
      price_per_unit: 650,
      batch_code: 'FLYASH-2026-MTR-02',
      is_hazardous: false,
      industry: { name: 'Mettur Thermal Power Station', city: 'Salem', trust_score: 4.8 },
      waste_types: { name: 'Thermal Power Fly Ash' },
    },
    {
      id: 'l3',
      title: 'Crushed Steel Converter Slag Aggregates',
      description: 'Dense air-cooled steel slag aggregate suitable for flexible pavement sub-base.',
      quantity: 80.0,
      unit: 'ton',
      price_per_unit: 420,
      batch_code: 'SLAG-2026-SLM-03',
      is_hazardous: false,
      industry: { name: 'Jindal Steels Salem Works', city: 'Salem', trust_score: 4.88 },
      waste_types: { name: 'Steel Converter Slag' },
    },
  ]);

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  useEffect(() => {
    // Fetch live public stats if backend is running
    apiClient.get('/public/stats')
      .then((res) => {
        if (res.data?.data) {
          setStats(res.data.data);
        }
      })
      .catch(() => {
        // Keeps sensible defaults
      });

    apiClient.get('/listings')
      .then((res) => {
        if (res.data?.data && res.data.data.length > 0) {
          setListings(res.data.data);
        }
      })
      .catch(() => {});
  }, []);

  const filteredListings = listings.filter((item) => {
    const matchesSearch = item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          item.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  return (
    <div className="space-y-16 pb-20">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-16 lg:pt-20 lg:pb-24 border-b border-slate-200 dark:border-slate-800 bg-gradient-to-b from-eco-50/50 via-white to-transparent dark:from-slate-900/50 dark:via-slate-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto space-y-6">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-eco-100 text-eco-800 dark:bg-eco-950 dark:text-eco-300 border border-eco-200 dark:border-eco-800 text-xs font-bold tracking-wide animate-pulse">
              <Sparkles className="w-3.5 h-3.5 text-eco-600" />
              <span>TNPCB & CPCB COMPLIANT B2B CIRCULAR MARKETPLACE</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 dark:text-white tracking-tight leading-[1.15]">
              One Industry's <span className="text-eco-600 underline decoration-eco-300">Waste</span> Is Another's <span className="text-emerald-700 dark:text-emerald-400">Raw Material</span>.
            </h1>

            <p className="text-base sm:text-lg text-slate-600 dark:text-slate-300 font-medium leading-relaxed">
              Connect generators of industrial byproducts directly with manufacturing plants that repurpose them. Eliminating brokers, cutting landfill dumping, and proving verified ESG carbon offsets.
            </p>

            <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
              <a
                href="#marketplace"
                className="px-6 py-3.5 rounded-xl bg-eco-600 text-white font-bold text-sm shadow-lg shadow-eco-600/25 hover:bg-eco-700 hover:shadow-eco-700/35 transition flex items-center gap-2"
              >
                <Search className="w-4 h-4" />
                <span>Explore Byproduct Marketplace</span>
              </a>

              <Link
                to="/network"
                className="px-6 py-3.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 font-bold text-sm text-slate-800 dark:text-white hover:bg-slate-50 dark:hover:bg-slate-800 transition flex items-center gap-2"
              >
                <Layers className="w-4 h-4 text-eco-600" />
                <span>View Symbiosis Network</span>
              </Link>
            </div>
          </div>

          {/* Live ESG KPI Counters Banner */}
          <div className="mt-14 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-5xl mx-auto">
            <div className="glass-panel p-5 rounded-2xl text-center shadow-sm">
              <div className="text-2xl sm:text-3xl font-extrabold text-eco-600 tracking-tight">
                {stats.total_tonnes_diverted.toLocaleString()} MT
              </div>
              <div className="text-xs font-semibold text-slate-500 dark:text-slate-400 mt-1 flex items-center justify-center gap-1">
                <Leaf className="w-3.5 h-3.5 text-eco-500" />
                <span>Landfill Waste Diverted</span>
              </div>
            </div>

            <div className="glass-panel p-5 rounded-2xl text-center shadow-sm">
              <div className="text-2xl sm:text-3xl font-extrabold text-emerald-600 tracking-tight">
                {stats.total_co2_tonnes_mitigated.toLocaleString()} MT
              </div>
              <div className="text-xs font-semibold text-slate-500 dark:text-slate-400 mt-1 flex items-center justify-center gap-1">
                <TrendingUp className="w-3.5 h-3.5 text-emerald-500" />
                <span>CO₂ Emissions Mitigated</span>
              </div>
            </div>

            <div className="glass-panel p-5 rounded-2xl text-center shadow-sm">
              <div className="text-2xl sm:text-3xl font-extrabold text-blue-600 tracking-tight">
                {stats.verified_industries_count}
              </div>
              <div className="text-xs font-semibold text-slate-500 dark:text-slate-400 mt-1 flex items-center justify-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5 text-blue-500" />
                <span>Verified Facilities</span>
              </div>
            </div>

            <div className="glass-panel p-5 rounded-2xl text-center shadow-sm">
              <div className="text-2xl sm:text-3xl font-extrabold text-amber-600 tracking-tight">
                ₹{(stats.total_economic_volume_inr / 1000).toFixed(1)}k
              </div>
              <div className="text-xs font-semibold text-slate-500 dark:text-slate-400 mt-1 flex items-center justify-center gap-1">
                <Recycle className="w-3.5 h-3.5 text-amber-500" />
                <span>Circular Trade Value</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Synergistic Industrial Pairs Showcase */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-10">
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white">
            Proven Industrial Symbiosis Pairs
          </h2>
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-2">
            Real circular supply chains currently operating across Tamil Nadu manufacturing clusters.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm hover:border-eco-500 transition space-y-4">
            <div className="flex items-center justify-between">
              <span className="px-2.5 py-1 rounded-md bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 text-xs font-bold">
                Organic Biomass
              </span>
              <span className="text-xs text-eco-600 font-semibold">-1.15 MT CO₂/Ton</span>
            </div>
            <h3 className="font-bold text-base text-slate-900 dark:text-white">
              Sugar Mill $\rightarrow$ Paper & Biofuel
            </h3>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
              Sugarcane bagasse residue provides high cellulose pulp for kraft packaging and biomass briquettes, replacing virgin forest wood.
            </p>
            <div className="pt-2 text-xs font-semibold text-slate-500 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-eco-500" />
              <span>Namakkal Sugar Mill to Karur Paper</span>
            </div>
          </div>

          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm hover:border-eco-500 transition space-y-4">
            <div className="flex items-center justify-between">
              <span className="px-2.5 py-1 rounded-md bg-slate-200 text-slate-800 dark:bg-slate-800 dark:text-slate-300 text-xs font-bold">
                Mineral Pozzolan
              </span>
              <span className="text-xs text-eco-600 font-semibold">-0.82 MT CO₂/Ton</span>
            </div>
            <h3 className="font-bold text-base text-slate-900 dark:text-white">
              Thermal Plant $\rightarrow$ Cement & AAC Bricks
            </h3>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
              Class-F pulverized coal fly ash replaces energy-intensive clinker in Portland Pozzolana Cement and lightweight aerated masonry blocks.
            </p>
            <div className="pt-2 text-xs font-semibold text-slate-500 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-eco-500" />
              <span>Mettur Thermal to Dalmia Cement</span>
            </div>
          </div>

          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm hover:border-eco-500 transition space-y-4">
            <div className="flex items-center justify-between">
              <span className="px-2.5 py-1 rounded-md bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300 text-xs font-bold">
                Metallurgical Aggregate
              </span>
              <span className="text-xs text-eco-600 font-semibold">-0.65 MT CO₂/Ton</span>
            </div>
            <h3 className="font-bold text-base text-slate-900 dark:text-white">
              Steel Mill $\rightarrow$ Highway Pavements
            </h3>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
              Air-cooled dense blast furnace and converter slag serves as heavy-load asphalt sub-base, stopping mountain stone blasting.
            </p>
            <div className="pt-2 text-xs font-semibold text-slate-500 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-eco-500" />
              <span>Salem Steel Works to Road Infrastructure</span>
            </div>
          </div>
        </div>
      </section>

      {/* Active Marketplace Section */}
      <section id="marketplace" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
          <div>
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white">
              Active Industrial Byproduct Listings
            </h2>
            <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
              Verified lots available for immediate consignment negotiation.
            </p>
          </div>

          {/* Search bar */}
          <div className="relative w-full md:w-80">
            <Search className="w-4 h-4 absolute left-3.5 top-3.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search by material, grade..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-eco-500"
            />
          </div>
        </div>

        {/* Listings Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredListings.map((item) => (
            <div
              key={item.id}
              className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-hidden shadow-sm hover:shadow-md transition flex flex-col justify-between"
            >
              <div className="p-6 space-y-4">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold px-2.5 py-1 rounded-md bg-eco-50 text-eco-700 dark:bg-eco-950 dark:text-eco-300 border border-eco-200 dark:border-eco-800">
                    {item.waste_types?.name || 'Byproduct'}
                  </span>
                  <span className="font-mono text-slate-500 flex items-center gap-1">
                    <QrCode className="w-3.5 h-3.5" />
                    {item.batch_code.slice(0, 15)}
                  </span>
                </div>

                <div>
                  <h3 className="font-bold text-lg text-slate-900 dark:text-white line-clamp-1">
                    {item.title}
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 line-clamp-2">
                    {item.description}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-3 py-3 border-y border-slate-100 dark:border-slate-800 text-xs">
                  <div>
                    <span className="text-slate-400 block font-medium">Available Volume</span>
                    <span className="font-bold text-slate-800 dark:text-white text-sm">
                      {item.quantity} {item.unit.toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block font-medium">Offer Rate</span>
                    <span className="font-bold text-eco-600 text-sm">
                      ₹{item.price_per_unit} / {item.unit}
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs text-slate-500">
                  <div className="flex items-center gap-1.5">
                    <Factory className="w-3.5 h-3.5 text-slate-400" />
                    <span className="font-medium text-slate-700 dark:text-slate-300">
                      {item.industry?.name || 'Verified Mill'}
                    </span>
                  </div>
                  <div className="flex items-center gap-1 text-slate-400">
                    <MapPin className="w-3.5 h-3.5" />
                    <span>{item.industry?.city || 'Tamil Nadu'}</span>
                  </div>
                </div>
              </div>

              <div className="p-4 bg-slate-50 dark:bg-slate-800/40 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
                <Link
                  to={`/passport/${item.batch_code}`}
                  className="text-xs font-bold text-eco-700 dark:text-eco-400 hover:underline flex items-center gap-1"
                >
                  <span>Waste Passport</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>

                <button
                  onClick={() => alert(`Quote request initiated for ${item.title}. Deal room negotiation channel created.`)}
                  className="px-3.5 py-1.5 rounded-lg bg-eco-600 hover:bg-eco-700 text-white font-bold text-xs transition"
                >
                  Send Price Quote
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};
