import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import App from "./App";
import dataset from "./data/profile.json";
import type { PortfolioData } from "./types";

vi.mock("motion/react", async () => {
  const React = await import("react");
  const cache = new Map<string, React.ComponentType<Record<string, unknown>>>();
  const motion = new Proxy({}, {
    get: (_target, elementName: string) => {
      if (!cache.has(elementName)) {
        cache.set(
          elementName,
          React.forwardRef<HTMLElement, Record<string, unknown>>((props, ref) => {
            const {
              initial: _initial,
              animate: _animate,
              exit: _exit,
              whileInView: _whileInView,
              viewport: _viewport,
              transition: _transition,
              layout: _layout,
              layoutId: _layoutId,
              children,
              ...htmlProps
            } = props;
            return React.createElement(elementName, { ...htmlProps, ref }, children as React.ReactNode);
          }),
        );
      }
      return cache.get(elementName);
    },
  });

  return {
    motion,
    AnimatePresence: ({ children }: { children: React.ReactNode }) => children,
    MotionConfig: ({ children }: { children: React.ReactNode }) => children,
    useReducedMotion: () => true,
    useScroll: () => ({ scrollYProgress: 0 }),
  };
});

vi.mock("./ActivityCharts", () => {
  return {
    default: () => (
      <div>
        <p>One point per repository—not commit volume.</p>
      </div>
    ),
  };
});

describe("portfolio dashboard", () => {
  it("shows the generated snapshot and scopes its metrics", async () => {
    render(<App dataset={dataset as PortfolioData} />);
    expect(screen.getByRole("article", { name: /Original public repos: 124/ })).toBeInTheDocument();
    expect(screen.getByRole("article", { name: /Stars: 14/ })).toBeInTheDocument();
    expect(screen.getByText(/Snapshot updated/)).toBeInTheDocument();
    expect(screen.getByText(/Recent activity counts repositories/i)).toBeInTheDocument();
  });

  it("changes the recent-push window without changing source data", async () => {
    render(<App dataset={dataset as PortfolioData} />);
    expect(screen.getByRole("article", { name: /Repos pushed · 30 days: 8/ })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "7d" }));
    expect(screen.getByRole("article", { name: /Repos pushed · 7 days: 2/ })).toBeInTheDocument();
  });

  it("filters the featured work by category", () => {
    render(<App dataset={dataset as PortfolioData} />);
    fireEvent.click(screen.getByRole("button", { name: "Agent systems" }));
    const work = screen.getByRole("region", { name: /systems with inspectable decisions/i });
    expect(within(work).getByText("Agent Systems Labs")).toBeInTheDocument();
    expect(within(work).queryByText("RAG Systems Labs")).not.toBeInTheDocument();
  });

  it("uses the hero system stages to filter related work", () => {
    render(<App dataset={dataset as PortfolioData} />);
    fireEvent.click(screen.getByRole("button", { name: "Context" }));

    const work = screen.getByRole("region", { name: /systems with inspectable decisions/i });
    expect(within(work).getByRole("button", { name: "Retrieval" })).toHaveAttribute("aria-pressed", "true");
    expect(within(work).getByText("RAG Systems Labs")).toBeInTheDocument();
    expect(within(work).queryByText("Agent Systems Labs")).not.toBeInTheDocument();
  });

  it("lets readers pause the decorative motion", () => {
    render(<App dataset={dataset as PortfolioData} />);
    fireEvent.click(screen.getByRole("button", { name: "Pause motion" }));

    expect(screen.getByRole("button", { name: "Play motion" })).toHaveAttribute("aria-pressed", "true");
    expect(document.getElementById("top")).toHaveAttribute("data-motion-paused", "true");
  });

  it("opens the mobile section navigation", () => {
    render(<App dataset={dataset as PortfolioData} />);
    const trigger = screen.getByRole("button", { name: "Open section navigation", hidden: true });
    fireEvent.click(trigger);

    expect(trigger).toHaveAttribute("aria-expanded", "true");
    expect(screen.getByRole("navigation", { name: "Main navigation" })).toHaveClass("is-open");
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

  it("opens a project case study from the keyboard command palette", async () => {
    render(<App dataset={dataset as PortfolioData} />);
    fireEvent.keyDown(window, { key: "k", ctrlKey: true });

    const search = screen.getByRole("combobox", { name: /search projects and page sections/i });
    fireEvent.change(search, { target: { value: "Agent Systems Labs" } });
    fireEvent.keyDown(search, { key: "Enter" });

    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(await screen.findByRole("heading", { name: "What this does not claim" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Repository README" })).toHaveAttribute(
      "href",
      "https://github.com/AmDeep/AIAgents/blob/main/README.md",
    );
  });

  it("shows helpful empty-search recovery and resets the repository explorer", () => {
    render(<App dataset={dataset as PortfolioData} />);
    const search = screen.getByRole("searchbox", { name: /search public repositories/i });
    fireEvent.change(search, { target: { value: "nothing-matches-this" } });

    const explorer = screen.getByRole("region", { name: /browse the rest of the work/i });
    expect(within(explorer).getByText("No repositories match those filters.")).toBeInTheDocument();
    fireEvent.click(within(explorer).getByRole("button", { name: "Reset search and language" }));
    expect(search).toHaveValue("");
    expect(within(explorer).getByRole("link", { name: /AIAgents/i })).toBeInTheDocument();
  });

  it("includes a direct LinkedIn route in the contact section", () => {
    render(<App dataset={dataset as PortfolioData} />);
    const contact = screen.getByRole("region", { name: /let’s talk about systems that need evidence/i });
    expect(within(contact).getByRole("link", { name: /connect on linkedin/i })).toHaveAttribute(
      "href",
      "https://www.linkedin.com/in/a-s-70a471a3/",
    );
  });
});
