import type { FullProcessResponse } from "../api/types";

type RouteSummaryProps = {
  result: FullProcessResponse | null;
};

export function RouteSummary({ result }: RouteSummaryProps) {
  const distance = result?.route_segments.reduce((sum, segment) => sum + (segment.distance_meters ?? 0), 0) ?? 0;
  const duration = result?.route_segments.reduce((sum, segment) => sum + (segment.duration_seconds ?? 0), 0) ?? 0;

  return (
    <section className="rounded-[1.5rem] bg-atlas-moss p-4 text-atlas-paper shadow-panel">
      <p className="text-xs font-bold uppercase tracking-[0.28em] text-atlas-brass">Route summary</p>
      <div className="mt-3 grid grid-cols-3 gap-3">
        <Metric label="Distance" value={`${Math.round(distance / 1000)} km`} />
        <Metric label="Duration" value={`${Math.round(duration / 3600)} h`} />
        <Metric label="Confidence" value={`${Math.round((result?.confidence_summary.overall ?? 0) * 100)}%`} />
      </div>
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl bg-atlas-paper/10 p-3">
      <p className="text-xs text-atlas-paper/60">{label}</p>
      <p className="font-display text-2xl">{value}</p>
    </div>
  );
}
