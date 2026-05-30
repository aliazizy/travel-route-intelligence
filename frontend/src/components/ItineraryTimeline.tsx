import type { ItineraryStep } from "../api/types";

type ItineraryTimelineProps = {
  steps: ItineraryStep[];
  selectedStep: ItineraryStep | null;
  onSelect: (step: ItineraryStep) => void;
};

export function ItineraryTimeline({ steps, selectedStep, onSelect }: ItineraryTimelineProps) {
  return (
    <section className="rounded-[1.5rem] bg-white/70 p-4 shadow-panel">
      <h2 className="font-display text-2xl">Ordered Sequence</h2>
      <div className="mt-4 max-h-[52vh] space-y-3 overflow-auto pr-1">
        {steps.map((step) => {
          const selected = selectedStep?.sequence_index === step.sequence_index;
          return (
            <button
              className={`w-full rounded-3xl border p-3 text-left transition ${
                selected ? "border-atlas-brass bg-atlas-brass/15" : "border-atlas-ink/10 bg-atlas-paper/70"
              }`}
              key={step.sequence_index}
              onClick={() => onSelect(step)}
            >
              <div className="flex items-start gap-3">
                <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-atlas-ink text-sm font-black text-atlas-paper">
                  {step.sequence_index}
                </span>
                <div>
                  <p className="font-bold">{step.name}</p>
                  <p className="text-xs uppercase tracking-[0.18em] text-atlas-ink/50">
                    Day {step.day ?? "-"} · {step.step_type} · confidence {Math.round(step.confidence * 100)}%
                  </p>
                  {step.warnings.length ? <p className="mt-1 text-xs text-atlas-danger">{step.warnings[0]}</p> : null}
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </section>
  );
}
