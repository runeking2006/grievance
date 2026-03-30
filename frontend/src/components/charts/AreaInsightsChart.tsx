"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

const COLORS = ["#f26b5b", "#4fc0d0", "#f3b53f", "#8acb88", "#d16ba5"];

export function AreaInsightsChart({
  data,
}: {
  data: { location: string; count: number }[];
}) {
  return (
    <div className="h-72">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={data} dataKey="count" nameKey="location" innerRadius={50} outerRadius={95}>
            {data.map((entry, index) => (
              <Cell key={entry.location} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip contentStyle={{ background: "#13293d", borderRadius: 16, border: "1px solid rgba(255,255,255,0.1)" }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
