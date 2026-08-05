import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

interface TrustGaugeProps {
  score: number;
  size?: number;
}

export function TrustGauge({ score, size = 200 }: TrustGaugeProps) {
  // Normalize score 0-100
  const normalizedScore = Math.min(100, Math.max(0, score));
  
  // Determine color based on score
  let color = "hsl(var(--trust-high))"; // Green
  let verdict = "TRUSTED";
  
  if (normalizedScore < 50) {
    color = "hsl(var(--trust-low))"; // Red
    verdict = "CRITICAL";
  } else if (normalizedScore < 80) {
    color = "hsl(var(--trust-med))"; // Yellow
    verdict = "WARNING";
  }

  // Create chart data - the "needle" effect is simulated by filling the pie to a certain point
  // We actually use a simple donut chart where "value" is the filled part
  const data = [
    { name: 'Score', value: normalizedScore },
    { name: 'Remaining', value: 100 - normalizedScore },
  ];

  return (
    <div className="relative flex flex-col items-center justify-center" style={{ width: size, height: size }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            startAngle={180}
            endAngle={0}
            innerRadius={size / 2 - 20}
            outerRadius={size / 2}
            paddingAngle={0}
            dataKey="value"
            stroke="none"
          >
            <Cell key="score" fill={color} className="drop-shadow-[0_0_8px_rgba(0,0,0,0.5)]" />
            <Cell key="remaining" fill="rgba(255,255,255,0.1)" />
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      
      {/* Center Text */}
      <div className="absolute inset-0 flex flex-col items-center justify-center pt-8">
        <span className="text-4xl font-display font-bold tabular-nums tracking-tighter" style={{ color }}>
          {normalizedScore}
        </span>
        <span className="text-[10px] uppercase tracking-widest text-muted-foreground font-semibold mt-1">
          Trust Score
        </span>
        <div className="mt-2 px-2 py-0.5 rounded text-[10px] font-bold bg-background/50 border border-border" style={{ color }}>
          {verdict}
        </div>
      </div>
    </div>
  );
}
