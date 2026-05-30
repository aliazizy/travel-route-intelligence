type RequestInputProps = {
  value: string;
  isLoading: boolean;
  error?: string | null;
  onChange: (value: string) => void;
  onSubmit: () => void;
};

export function RequestInput({ value, isLoading, error, onChange, onSubmit }: RequestInputProps) {
  return (
    <section className="rounded-[2rem] bg-atlas-ink p-5 text-atlas-paper shadow-panel">
      <div className="mb-4">
        <p className="text-xs font-bold uppercase tracking-[0.32em] text-atlas-brass">Route brief</p>
        <h1 className="font-display text-4xl leading-tight">Travel Route Intelligence</h1>
        <p className="mt-2 text-sm text-atlas-paper/70">
          Paste a consultant brief and generate a mock parsed itinerary, geocoded sequence, route lines and GeoJSON.
        </p>
      </div>
      <textarea
        className="min-h-56 w-full resize-y rounded-3xl border border-atlas-paper/15 bg-atlas-paper/10 p-4 text-sm leading-6 outline-none ring-atlas-brass transition focus:ring-2"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Group of 25 arrives at Heathrow..."
      />
      {error ? <p className="mt-3 text-sm text-red-200">{error}</p> : null}
      <button
        className="mt-4 w-full rounded-full bg-atlas-brass px-5 py-3 text-sm font-extrabold uppercase tracking-[0.22em] text-atlas-ink transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
        disabled={isLoading}
        onClick={onSubmit}
      >
        {isLoading ? "Processing..." : "Parse and map itinerary"}
      </button>
    </section>
  );
}
