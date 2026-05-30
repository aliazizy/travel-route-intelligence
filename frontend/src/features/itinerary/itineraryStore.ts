import { create } from "zustand";

import type { FullProcessResponse, ItineraryStep } from "../../api/types";

type ItineraryState = {
  result: FullProcessResponse | null;
  selectedStep: ItineraryStep | null;
  setResult: (result: FullProcessResponse) => void;
  selectStep: (step: ItineraryStep | null) => void;
};

export const useItineraryStore = create<ItineraryState>((set) => ({
  result: null,
  selectedStep: null,
  setResult: (result) => set({ result, selectedStep: result.sequence[0] ?? null }),
  selectStep: (step) => set({ selectedStep: step }),
}));
