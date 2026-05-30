import { postJson } from "./client";
import type { FullProcessResponse, TravelRequest } from "./types";

export function runFullProcess(request: TravelRequest) {
  return postJson<FullProcessResponse, TravelRequest>("/workflows/full-process", request);
}
