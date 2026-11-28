import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ReactNode } from "react";
import { motion, useReducedMotion } from "motion/react";
import type { MetricLanguage, MonthlyPush } from "./types";

function ChartTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: Array<{ value: number }>;
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="chart-tooltip">
      <strong>{label}</strong>
      <span>{payload[0].value} repositories</span>
    </div>
  );
}

function ChartPanel({
  children,
  className,
  delay = 0,
}: {
  children: ReactNode;
  className: string;
  delay?: number;
}) {
  const reduced = useReducedMotion();
  return (
    <motion.div
      className={className}
      initial={reduced ? false : { opacity: 0, y: 14 }}
      whileInView={reduced ? undefined : { opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.12 }}
      transition={{ duration: 0.45, delay, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </motion.div>
  );
}

export default function ActivityCharts({
  monthly,
  languages,
}: {
  monthly: MonthlyPush[];
  languages: MetricLanguage[];
}) {
  return (
    <div className="dashboard-grid">
      <ChartPanel className="panel panel--chart">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">PUSH RECENCY</p>
            <h3>Repositories by latest push month</h3>
            <p className="panel-subtitle">One point per repository—not commit volume.</p>
          </div>
        </div>
        <div
          className="chart-wrap"
          role="img"
          aria-label="Monthly count of public repositories grouped by latest push date"
        >
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={monthly} margin={{ top: 10, right: 8, left: -22, bottom: 0 }}>
              <CartesianGrid stroke="#233143" strokeDasharray="3 5" vertical={false} />
              <XAxis
                dataKey="label"
                tick={{ fill: "#8fa1b6", fontSize: 11 }}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                allowDecimals={false}
                tick={{ fill: "#8fa1b6", fontSize: 11 }}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip
                content={<ChartTooltip />}
                cursor={{ stroke: "#44556a", strokeDasharray: "4 4" }}
              />
              <Line
                type="monotone"
                dataKey="repositories"
                name="Repositories"
                stroke="#5ed9c5"
                strokeWidth={3}
                dot={{ r: 3, fill: "#5ed9c5", strokeWidth: 0 }}
                activeDot={{ r: 6, fill: "#e6fffa", stroke: "#5ed9c5", strokeWidth: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <p className="chart-footnote">
          Metric definition: the most recent <code>pushed_at</code> timestamp for each eligible
          repository.
        </p>
      </ChartPanel>

      <ChartPanel className="panel panel--languages" delay={0.08}>
        <div className="panel-heading panel-heading--stack">
          <div>
            <p className="eyebrow">LANGUAGE MIX</p>
            <h3>Primary language by repo</h3>
            <p className="panel-subtitle">
              GitHub’s primary language field; not code-volume share.
            </p>
          </div>
        </div>
        <div
          className="chart-wrap chart-wrap--languages"
          role="img"
          aria-label="Top primary languages by repository count"
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={languages.slice(0, 6)}
              layout="vertical"
              margin={{ top: 0, right: 10, left: 4, bottom: 0 }}
            >
              <CartesianGrid stroke="#233143" strokeDasharray="3 5" horizontal={false} />
              <XAxis
                type="number"
                allowDecimals={false}
                tick={{ fill: "#8fa1b6", fontSize: 10 }}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                type="category"
                dataKey="name"
                width={94}
                tick={{ fill: "#c6d2e0", fontSize: 11 }}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip content={<ChartTooltip />} cursor={{ fill: "rgba(94,217,197,.08)" }} />
              <Bar
                dataKey="repositories"
                name="Repositories"
                fill="#5ed9c5"
                radius={[0, 5, 5, 0]}
                barSize={13}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="language-footer">
          {languages.slice(0, 4).map((item) => (
            <span key={item.name}>
              {item.name}
              <b>{item.repositories}</b>
            </span>
          ))}
        </div>
      </ChartPanel>
    </div>
  );
}
