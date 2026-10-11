import React, { useState } from 'react';
import { Layers, ArrowRight, Factory, Recycle, ShieldCheck, Info } from 'lucide-react';

interface NetworkNode {
  id: string;
  name: string;
  type: string;
  city: string;
  role: 'producer' | 'consumer' | 'dual';
}

interface NetworkEdge {
  from: string;
  to: string;
  material: string;
  quantity: string;
  co2Offset: string;
}

export const SymbiosisNetworkPage: React.FC = () => {
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  const nodes: NetworkNode[] = [
    { id: 'n1', name: 'Cauvery Sugar Mills', type: 'Sugar Mill', city: 'Namakkal', role: 'producer' },
    { id: 'n2', name: 'TNPL Karur', type: 'Paper Mill', city: 'Karur', role: 'consumer' },
    { id: 'n3', name: 'Mettur Thermal Power', type: 'Thermal Power', city: 'Salem', role: 'producer' },
    { id: 'n4', name: 'Dalmia Cement', type: 'Cement Factory', city: 'Tiruchirappalli', role: 'consumer' },
    { id: 'n5', name: 'Coimbatore AAC Bricks', type: 'Brick Unit', city: 'Coimbatore', role: 'consumer' },
    { id: 'n6', name: 'Jindal Steels Salem', type: 'Steel Plant', city: 'Salem', role: 'producer' },
    { id: 'n7', name: 'Highway Infra TN', type: 'Road Contractor', city: 'Erode', role: 'consumer' },
  ];

  const edges: NetworkEdge[] = [
    { from: 'Cauvery Sugar Mills', to: 'TNPL Karur', material: 'Bagasse Pulp (40 MT)', quantity: '40 MT', co2Offset: '46 MT CO₂e' },
    { from: 'Mettur Thermal Power', to: 'Dalmia Cement', material: 'Fly Ash Class-F (60 MT)', quantity: '60 MT', co2Offset: '49 MT CO₂e' },
    { from: 'Mettur Thermal Power', to: 'Coimbatore AAC Bricks', material: 'Fly Ash Mineral (25 MT)', quantity: '25 MT', co2Offset: '20 MT CO₂e' },
    { from: 'Jindal Steels Salem', to: 'Highway Infra TN', material: 'Blast Furnace Slag (80 MT)', quantity: '80 MT', co2Offset: '52 MT CO₂e' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-eco-100 text-eco-800 dark:bg-eco-950 dark:text-eco-300 text-xs font-bold border border-eco-200 dark:border-eco-800 mb-2">
          <Layers className="w-4 h-4 text-eco-600" />
          <span>CIRCULAR SUPPLY CHAIN TOPOLOGY</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">
          Regional Industrial Symbiosis Graph
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-2xl">
          Visualizing direct closed-loop material transfers between factories across Tamil Nadu clusters.
        </p>
      </div>

      {/* Network Visual Canvas */}
      <div className="rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-8 shadow-sm space-y-8">
        <div className="flex items-center justify-between text-xs text-slate-500 pb-4 border-b border-slate-100 dark:border-slate-800">
          <span className="font-semibold text-slate-700 dark:text-slate-300">Active Trade Routes ({edges.length} Verified Loops)</span>
          <span className="flex items-center gap-1 text-eco-600 font-bold">
            <Recycle className="w-3.5 h-3.5" />
            <span>100% Landfill Diverted</span>
          </span>
        </div>

        {/* Directed Graph Edges Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {edges.map((edge, idx) => (
            <div
              key={idx}
              className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 flex flex-col justify-between space-y-4 hover:border-eco-500 transition"
            >
              <div className="flex items-center justify-between">
                <span className="px-2.5 py-0.5 rounded-full bg-eco-100 dark:bg-eco-950 text-eco-800 dark:text-eco-300 text-[11px] font-bold">
                  {edge.material}
                </span>
                <span className="text-xs font-bold text-emerald-600">
                  {edge.co2Offset}
                </span>
              </div>

              <div className="flex items-center justify-between gap-3 text-xs">
                <div className="flex-1 p-3 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                  <span className="text-[10px] text-slate-400 uppercase font-bold block">Generator</span>
                  <span className="font-bold text-slate-900 dark:text-white block mt-0.5">
                    {edge.from}
                  </span>
                </div>

                <div className="w-8 h-8 rounded-full bg-eco-600 flex items-center justify-center text-white shrink-0 shadow-sm">
                  <ArrowRight className="w-4 h-4" />
                </div>

                <div className="flex-1 p-3 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                  <span className="text-[10px] text-slate-400 uppercase font-bold block">Consumer</span>
                  <span className="font-bold text-slate-900 dark:text-white block mt-0.5">
                    {edge.to}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Facilities Register Table */}
      <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-4">
        <h2 className="font-bold text-base text-slate-900 dark:text-white">
          Registered Symbiotic Nodes
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 dark:bg-slate-800/60 text-slate-500">
              <tr>
                <th className="p-3 font-semibold">Facility Name</th>
                <th className="p-3 font-semibold">Industrial Type</th>
                <th className="p-3 font-semibold">Location</th>
                <th className="p-3 font-semibold">Role</th>
                <th className="p-3 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800 text-slate-700 dark:text-slate-300">
              {nodes.map((node) => (
                <tr key={node.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition">
                  <td className="p-3 font-bold text-slate-900 dark:text-white flex items-center gap-2">
                    <Factory className="w-4 h-4 text-slate-400" />
                    <span>{node.name}</span>
                  </td>
                  <td className="p-3">{node.type}</td>
                  <td className="p-3">{node.city}</td>
                  <td className="p-3">
                    <span className="px-2 py-0.5 rounded-full capitalize font-semibold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                      {node.role}
                    </span>
                  </td>
                  <td className="p-3 text-eco-600 font-bold flex items-center gap-1">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>Verified</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
