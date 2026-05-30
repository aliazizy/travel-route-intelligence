import type { FullProcessResponse } from "../api/types";

type JsonPreviewProps = {
  result: FullProcessResponse | null;
};

export function JsonPreview({ result }: JsonPreviewProps) {
  const exportJson = (filename: string, payload: unknown) => {
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = filename;
    anchor.click();
    URL.revokeObjectURL(url);
  };

  return (
    <section className="rounded-[1.5rem] bg-atlas-ink p-4 text-atlas-paper shadow-panel">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="font-display text-2xl">Debug JSON</h2>
        <div className="flex gap-2">
          <button className="rounded-full bg-atlas-paper px-3 py-2 text-xs font-bold text-atlas-ink" disabled={!result} onClick={() => result && exportJson("itinerary.json", result)}>
            Export itinerary
          </button>
          <button className="rounded-full bg-atlas-brass px-3 py-2 text-xs font-bold text-atlas-ink" disabled={!result} onClick={() => result && exportJson("route.geojson", result.geojson)}>
            Export GeoJSON
          </button>
        </div>
      </div>
      <pre className="mt-3 max-h-64 overflow-auto rounded-2xl bg-black/25 p-4 text-xs leading-5 text-atlas-paper/80">
        {result ? JSON.stringify(result, null, 2) : "Run the workflow to inspect structured output."}
      </pre>
    </section>
  );
}
