import L from "leaflet";
import { useEffect } from "react";
import { GeoJSON, MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";

import type { FullProcessResponse, ItineraryStep } from "../api/types";

type MapViewProps = {
  result: FullProcessResponse | null;
  selectedStep: ItineraryStep | null;
  onSelectStep: (step: ItineraryStep) => void;
};

export function MapView({ result, selectedStep, onSelectStep }: MapViewProps) {
  const steps = result?.sequence.filter((step) => step.latitude != null && step.longitude != null) ?? [];

  return (
    <section className="relative min-h-[640px] overflow-hidden rounded-[2rem] border border-atlas-ink/10 bg-atlas-paper shadow-panel">
      <div className="absolute left-5 top-5 z-[500] rounded-full bg-atlas-ink/90 px-4 py-2 text-xs font-bold uppercase tracking-[0.24em] text-atlas-paper">
        Mock map layer
      </div>
      <MapContainer center={[54.3, -2.8]} zoom={6} scrollWheelZoom className="h-full min-h-[640px]">
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {result?.geojson ? (
          <GeoJSON
            data={result.geojson}
            key={result.request_id}
            style={{ color: "#2d6f88", weight: 5, opacity: 0.72 }}
            filter={(feature) => feature.properties?.kind === "route_segment"}
          />
        ) : null}
        {steps.map((step) => (
          <Marker
            eventHandlers={{ click: () => onSelectStep(step) }}
            icon={numberedIcon(step)}
            key={step.sequence_index}
            position={[step.latitude as number, step.longitude as number]}
          >
            <Popup>
              <strong>{step.sequence_index}. {step.name}</strong>
              <br />
              Day {step.day ?? "-"} · confidence {Math.round(step.confidence * 100)}%
            </Popup>
          </Marker>
        ))}
        <FitToSteps steps={steps} selectedStep={selectedStep} />
      </MapContainer>
    </section>
  );
}

function numberedIcon(step: ItineraryStep) {
  const hasWarning = step.warnings.length > 0 || step.confidence < 0.7;
  return L.divIcon({
    className: "",
    html: `<div class="numbered-marker" style="background:${hasWarning ? "#b84634" : "#101820"}">${step.sequence_index}</div>`,
    iconSize: [30, 30],
    iconAnchor: [15, 15],
  });
}

function FitToSteps({ steps, selectedStep }: { steps: ItineraryStep[]; selectedStep: ItineraryStep | null }) {
  const map = useMap();
  useEffect(() => {
    if (selectedStep?.latitude && selectedStep.longitude) {
      map.flyTo([selectedStep.latitude, selectedStep.longitude], Math.max(map.getZoom(), 9), { duration: 0.8 });
      return;
    }
    if (steps.length > 1) {
      const bounds = L.latLngBounds(steps.map((step) => [step.latitude as number, step.longitude as number]));
      map.fitBounds(bounds, { padding: [36, 36] });
    }
  }, [map, selectedStep, steps]);
  return null;
}
