import { useMutation } from "@tanstack/react-query";
import { useState } from "react";

import { runFullProcess } from "../api/itineraryApi";
import { ItineraryTimeline } from "../components/ItineraryTimeline";
import { JsonPreview } from "../components/JsonPreview";
import { MapView } from "../components/MapView";
import { RequestInput } from "../components/RequestInput";
import { RouteSummary } from "../components/RouteSummary";
import { WarningPanel } from "../components/WarningPanel";
import { useItineraryStore } from "../features/itinerary/itineraryStore";

const SAMPLE_REQUEST =
  "Group of 25 arrives at Heathrow on 10 September. Stay 3 nights in London. Visit Tower of London, Westminster Abbey and Windsor Castle. Then travel to Edinburgh for 2 nights, visit Edinburgh Castle and Royal Mile, and fly back from Edinburgh Airport.";

export function ItineraryPlannerPage() {
  const [requestText, setRequestText] = useState(SAMPLE_REQUEST);
  const { result, selectedStep, setResult, selectStep } = useItineraryStore();
  const mutation = useMutation({
    mutationFn: () =>
      runFullProcess({
        request_text: requestText,
        default_country: "United Kingdom",
        language: "en",
        client_context: { travel_style: "private coach" },
      }),
    onSuccess: setResult,
  });

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,#f8f0df,#d8c49b_45%,#99a993)] p-4 text-atlas-ink md:p-6">
      <div className="mx-auto grid max-w-[1800px] gap-5 xl:grid-cols-[390px_minmax(0,1fr)_420px]">
        <aside className="space-y-5">
          <RequestInput
            error={mutation.error instanceof Error ? mutation.error.message : null}
            isLoading={mutation.isPending}
            onChange={setRequestText}
            onSubmit={() => mutation.mutate()}
            value={requestText}
          />
          <WarningPanel warnings={result?.warnings ?? []} />
        </aside>

        <div className="space-y-5">
          <MapView result={result} selectedStep={selectedStep} onSelectStep={selectStep} />
          <RouteSummary result={result} />
        </div>

        <aside className="space-y-5">
          <ItineraryTimeline steps={result?.sequence ?? []} selectedStep={selectedStep} onSelect={selectStep} />
          {selectedStep ? (
            <section className="rounded-[1.5rem] bg-atlas-paper/85 p-4 shadow-panel">
              <p className="text-xs font-bold uppercase tracking-[0.26em] text-atlas-moss">Selected marker</p>
              <h2 className="mt-1 font-display text-3xl">{selectedStep.name}</h2>
              <dl className="mt-3 grid grid-cols-2 gap-3 text-sm">
                <Detail label="Type" value={selectedStep.step_type} />
                <Detail label="Role" value={selectedStep.role ?? "-"} />
                <Detail label="Latitude" value={selectedStep.latitude?.toFixed(4) ?? "-"} />
                <Detail label="Longitude" value={selectedStep.longitude?.toFixed(4) ?? "-"} />
              </dl>
              <p className="mt-3 text-sm text-atlas-ink/60">
                Edit controls and alternative geocoder selection are reserved for the next increment.
              </p>
            </section>
          ) : null}
        </aside>
      </div>

      <div className="mx-auto mt-5 max-w-[1800px]">
        <JsonPreview result={result} />
      </div>
    </main>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl bg-white/60 p-3">
      <dt className="text-xs uppercase tracking-[0.18em] text-atlas-ink/45">{label}</dt>
      <dd className="font-bold">{value}</dd>
    </div>
  );
}
