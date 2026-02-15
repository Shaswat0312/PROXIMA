import { useState } from "react";
import {
  RadialBarChart,
  RadialBar,
  ResponsiveContainer
} from "recharts";

const regionsList = [
  "Northern",
  "Western",
  "Eastern",
  "Southern",
  "North-Eastern"
];

function App() {
  const [region, setRegion] = useState("Northern");

  const [lag24, setLag24] = useState("");
  const [lag168, setLag168] = useState("");
  const [hour, setHour] = useState("");
  const [month, setMonth] = useState("");
  const [actualDemand, setActualDemand] = useState("");
  const [supply, setSupply] = useState("");

  const [analysis, setAnalysis] = useState(null);
  const [distribution, setDistribution] = useState(null);

  const [nationalGrid, setNationalGrid] = useState(
    regionsList.map(r => ({
      region: r,
      predicted_demand: "",
      supply: ""
    }))
  );

  const analyzeGrid = async () => {
    const response = await fetch("http://127.0.0.1:8000/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        region,
        lag_24: Number(lag24),
        lag_168: Number(lag168),
        hour: Number(hour),
        month: Number(month),
        actual_demand: Number(actualDemand),
        supply: Number(supply)
      })
    });

    const data = await response.json();
    setAnalysis(data);

    const updated = nationalGrid.map(r =>
      r.region === region
        ? { ...r, predicted_demand: data.predicted_demand, supply }
        : r
    );
    setNationalGrid(updated);
  };

  const optimizeDistribution = async () => {
    const response = await fetch("http://127.0.0.1:8000/optimize-distribution", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        regions: nationalGrid.map(r => ({
          region: r.region,
          predicted_demand: Number(r.predicted_demand),
          supply: Number(r.supply)
        }))
      })
    });

    const data = await response.json();
    setDistribution(data);
  };

  const updateNationalGrid = (index, field, value) => {
    const updated = [...nationalGrid];
    updated[index][field] = value;
    setNationalGrid(updated);
  };

  // ================= SCORE HANDLING =================
  const safeScore = analysis
    ? Math.min(Math.max(analysis.inefficiency_score, 0), 1)
    : 0;

  const gaugeData = analysis
    ? [{ name: "Inefficiency", value: safeScore * 100 }]
    : [];

  const getGaugeColor = (score) => {
    if (score < 0.35) return "#22c55e";
    if (score < 0.65) return "#facc15";
    return "#ef4444";
  };

  const getRisk = (score) => {
    if (score < 0.35)
      return { label: "Stable", color: "bg-green-500 text-black" };
    if (score < 0.65)
      return { label: "Moderate Stress", color: "bg-yellow-400 text-black" };
    return { label: "Critical Risk", color: "bg-red-500 text-white" };
  };

  const risk = getRisk(safeScore);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-black text-white p-10">

      <h1 className="text-5xl font-bold mb-14 text-blue-400 tracking-wide">
        ⚡ IdleGrid AI — National Energy Control Room
      </h1>

      {/* ================= ANALYSIS SECTION ================= */}
      <div className="grid grid-cols-2 gap-12">

        {/* INPUT PANEL */}
        <div className="bg-slate-900/70 border border-slate-700 p-6 rounded-2xl shadow-2xl">
          <h2 className="text-xl mb-6 text-blue-300">Regional Analysis</h2>

          <select
            value={region}
            onChange={(e) => setRegion(e.target.value)}
            className="bg-slate-700 p-2 rounded w-full mb-4"
          >
            {regionsList.map(r => <option key={r}>{r}</option>)}
          </select>

          <div className="grid grid-cols-2 gap-3">
            {[
              "Lag 24",
              "Lag 168",
              "Hour",
              "Month",
              "Actual Demand",
              "Supply"
            ].map((label, i) => (
              <input
                key={i}
                placeholder={label}
                className="bg-slate-700 p-2 rounded"
                onChange={e =>
                  [setLag24,setLag168,setHour,setMonth,setActualDemand,setSupply][i](e.target.value)
                }
              />
            ))}
          </div>

          <button
            onClick={analyzeGrid}
            className="mt-6 w-full bg-blue-600 hover:bg-blue-500 transition px-6 py-2 rounded-xl text-lg"
          >
            Analyze Grid
          </button>
        </div>

        {/* GAUGE PANEL */}
        {analysis && (
          <div className="bg-slate-900/70 border border-slate-700 p-6 rounded-2xl shadow-2xl flex flex-col items-center justify-center">
            <h2 className="text-xl mb-6 text-blue-300">Inefficiency Meter</h2>

            <div className="w-72 h-72">
              <ResponsiveContainer>
                <RadialBarChart
                  innerRadius="70%"
                  outerRadius="100%"
                  data={gaugeData}
                  startAngle={180}
                  endAngle={0}
                >
                  <RadialBar
                    minAngle={15}
                    dataKey="value"
                    fill={getGaugeColor(safeScore)}
                  />
                </RadialBarChart>
              </ResponsiveContainer>
            </div>

            <p
              className="text-4xl mt-6 font-bold"
              style={{ color: getGaugeColor(safeScore) }}
            >
              {(safeScore * 100).toFixed(1)}%
            </p>

            <span className={`mt-3 px-5 py-2 rounded-full text-sm font-semibold ${risk.color}`}>
              {risk.label}
            </span>
          </div>
        )}
      </div>

      {/* ================= METRICS ================= */}
      {analysis && (
        <div className="mt-12 grid grid-cols-4 gap-6">
          {[
            { label: "Utilization %", value: analysis.utilization_percent.toFixed(2) },
            { label: "Residual", value: analysis.residual.toFixed(2) },
            { label: "Supply-Demand Gap", value: analysis.gap.toFixed(2) },
            { label: "Anomaly", value: analysis.anomaly_flag ? "Yes" : "No" }
          ].map((m, i) => (
            <div key={i} className="bg-slate-900/70 p-6 rounded-2xl border border-slate-700 shadow-xl">
              <p className="text-gray-400 text-sm">{m.label}</p>
              <p className="text-2xl font-bold text-blue-400 mt-2">{m.value}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;