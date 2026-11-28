import { fireEvent, render, screen, within } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import App from "./App";
import dataset from "./data/profile.json";
import type { PortfolioData } from "./types";

vi.mock("recharts", () => {
  const Box = ({ children }: { children?: ReactNode }) => <div>{children}</div>;
  return {
    ResponsiveContainer: Box,
    LineChart: Box,
    BarChart: Box,
    CartesianGrid: () => null,
    Line: () => null,
    Bar: () => null,
    XAxis: () => null,
    YAxis: () => null,
    Tooltip: () => null,
  };
});

describe("portfolio dashboard", () => {
  it("shows the generated snapshot and scopes its metrics", async () => {
    render(<App dataset={dataset as PortfolioData} />);
    expect(screen.getByRole("article", { name: /Original public repos: 124/ })).toBeInTheDocument();
    expect(screen.getByRole("article", { name: /Stars: 14/ })).toBeInTheDocument();
    expect(screen.getByText(/Snapshot updated/)).toBeInTheDocument();
    expect(await screen.findByText(/not commit volume/i)).toBeInTheDocument();
  });

  it("changes the recent-push window without changing source data", async () => {
    render(<App dataset={dataset as PortfolioData} />);
    expect(screen.getByRole("article", { name: /Repos pushed · 30 days: 8/ })).toBeInTheDocument();
    fireEvent.click(await screen.findByRole("button", { name: "7d" }));
    expect(screen.getByRole("article", { name: /Repos pushed · 7 days: 2/ })).toBeInTheDocument();
  });

  it("filters the featured work by category", () => {
    render(<App dataset={dataset as PortfolioData} />);
    fireEvent.click(screen.getByRole("button", { name: "Agent systems" }));
    const work = screen.getByRole("region", { name: /systems with inspectable decisions/i });
    expect(within(work).getByText("Agent Systems Labs")).toBeInTheDocument();
    expect(within(work).queryByText("RAG Systems Labs")).not.toBeInTheDocument();
  });

  it("searches the public repository explorer", () => {
    render(<App dataset={dataset as PortfolioData} />);
    fireEvent.change(screen.getByRole("searchbox", { name: /search public repositories/i }), {
      target: { value: "AIAgents" },
    });
    const explorer = screen.getByRole("region", { name: /browse the rest of the work/i });
    expect(within(explorer).getByRole("link", { name: /AIAgents/i })).toBeInTheDocument();
    expect(within(explorer).queryByRole("link", { name: /RAGSystemLabs/i })).not.toBeInTheDocument();
  });
});
