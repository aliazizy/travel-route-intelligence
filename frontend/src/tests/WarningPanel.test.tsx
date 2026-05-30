import { render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import { WarningPanel } from "../components/WarningPanel";

test("deduplicates repeated warning messages", () => {
  const consoleError = vi.spyOn(console, "error").mockImplementation(() => undefined);

  render(
    <WarningPanel
      warnings={[
        "Low-confidence geocoding result for 'Oxford'.",
        "Low-confidence geocoding result for 'Oxford'.",
        "Primary geocoder failed; used fallback mock geocoder for this request.",
      ]}
    />,
  );

  expect(screen.getByText("2")).toBeInTheDocument();
  expect(screen.getAllByText("Low-confidence geocoding result for 'Oxford'.")).toHaveLength(1);
  expect(consoleError).not.toHaveBeenCalled();

  consoleError.mockRestore();
});
