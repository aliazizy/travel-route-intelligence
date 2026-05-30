type WarningPanelProps = {
  warnings: string[];
};

export function WarningPanel({ warnings }: WarningPanelProps) {
  const uniqueWarnings = Array.from(new Set(warnings));

  return (
    <section className="rounded-[1.5rem] border border-atlas-danger/30 bg-atlas-paper/80 p-4">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="font-display text-xl">Warnings</h2>
        <span className="rounded-full bg-atlas-danger px-3 py-1 text-xs font-bold text-white">{uniqueWarnings.length}</span>
      </div>
      {uniqueWarnings.length === 0 ? (
        <p className="text-sm text-atlas-ink/60">No validation warnings yet.</p>
      ) : (
        <ul className="space-y-2 text-sm">
          {uniqueWarnings.map((warning, index) => (
            <li className="rounded-2xl bg-white/70 p-3 text-atlas-ink/80" key={`${warning}-${index}`}>
              {warning}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
