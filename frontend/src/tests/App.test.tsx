import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import App from "../App";

test("renders route intelligence planner", () => {
  render(
    <QueryClientProvider client={new QueryClient()}>
      <App />
    </QueryClientProvider>,
  );

  expect(screen.getByText("Travel Route Intelligence")).toBeInTheDocument();
  expect(screen.getByText("Parse and map itinerary")).toBeInTheDocument();
});
