import { lazy, Suspense, useEffect, useMemo, useRef, useState } from "react";
import type { CSSProperties, ReactNode } from "react";
import {
  Activity,
  ArrowDown,
  ArrowRight,
  ArrowUpRight,
  Bot,
  Boxes,
  Code2,
  Command,
  Copy,
  Database,
  ExternalLink,
  GitFork,
  GitBranch,
  Menu,
  Pause,
  Play,
  Search,
  Star,
  Waypoints,
  Workflow,
  X,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import {
  AnimatePresence,
  MotionConfig,
  motion,
  useReducedMotion,
  useScroll,
} from "motion/react";
import { caseStudies } from "./data/caseStudies";
import profileData from "./data/profile.json";
import type {
  PortfolioData,
  PortfolioProject,
  PublicRepository,
} from "./types";

const ActivityCharts = lazy(() => import("./ActivityCharts"));
const data = profileData as PortfolioData;
const ranges = [7, 30, 90] as const;
type RangeDays = (typeof ranges)[number];
type DialogState =
  | { kind: "palette" }
  | { kind: "project"; project: PortfolioProject }
  | null;

type PaletteCommand =
  | {
      id: string;
      kind: "section";
      title: string;
      description: string;
      target: string;
    }
  | {
      id: string;
      kind: "project";
      title: string;
      description: string;
      project: PortfolioProject;
    };

type SystemStage = {
  id: string;
  label: string;
  description: string;
  category: string;
};

const systemStages: SystemStage[] = [
  {
    id: "context",
    label: "Context",
    description: "Retrieval examples keep source metadata and evidence visible.",
    category: "Retrieval",
  },
  {
    id: "proposal",
    label: "Proposal",
    description: "Agent labs make tool contracts and failure boundaries runnable.",
    category: "Agent systems",
  },
  {
    id: "validation",
    label: "Validation",
    description: "Schemas, limits, and postconditions gate model proposals.",
    category: "Robotics",
  },
  {
    id: "action",
    label: "Bounded action",
    description: "Deterministic controllers—not the model—own the final action.",
    category: "Robotics",
  },
];

const sectionCommands = [
  {
    id: "section-work",
    kind: "section" as const,
    title: "Selected work",
    description: "Open the six verified project deep-dives.",
    target: "work",
  },
  {
    id: "section-principles",
    kind: "section" as const,
    title: "Engineering approach",
    description: "Inspect the principles behind the projects.",
    target: "principles",
  },
  {
    id: "section-signals",
    kind: "section" as const,
    title: "Live repository signals",
    description: "Review the refreshed public GitHub snapshot.",
    target: "signals",
  },
  {
    id: "section-repositories",
    kind: "section" as const,
    title: "Repository explorer",
    description: "Search and filter the public repository list.",
    target: "repositories",
  },
  {
    id: "section-contact",
    kind: "section" as const,
    title: "Contact on LinkedIn",
    description: "Open the direct hiring and collaboration link.",
    target: "contact",
  },
];

const iconForCategory: Record<string, LucideIcon> = {
  "Agent systems": Bot,
  Retrieval: Database,
  Inference: Workflow,
  Robotics: Waypoints,
  "Edge vision": Boxes,
};

const iconForStage: Record<string, LucideIcon> = {
  context: Database,
  proposal: Bot,
  validation: Code2,
  action: Waypoints,
};

const formatNumber = new Intl.NumberFormat("en-CA");
const formatDate = (value: string | null) => {
  if (!value) return "No push recorded";
  const date = new Date(value);
  return new Intl.DateTimeFormat("en-CA", {
    dateStyle: "medium",
    timeZone: "UTC",
  }).format(date);
};

function Reveal({
  children,
  className,
  delay = 0,
}: {
  children: ReactNode;
  className?: string;
  delay?: number;
}) {
  const reduced = useReducedMotion();
  return (
    <motion.div
      className={className}
      initial={reduced ? false : { opacity: 0, y: 18 }}
      whileInView={reduced ? undefined : { opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.12 }}
      transition={{ duration: 0.48, delay, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </motion.div>
  );
}

function StatCard({
  label,
  value,
  note,
  icon: Icon,
  delay,
}: {
  label: string;
  value: string;
  note: string;
  icon: LucideIcon;
  delay: number;
}) {
  return (
    <Reveal delay={delay}>
      <article className="stat-card" aria-label={`${label}: ${value}. ${note}`}>
        <div className="stat-card__top">
          <span className="eyebrow">{label}</span>
          <Icon aria-hidden="true" size={17} strokeWidth={1.8} />
        </div>
        <strong className="stat-card__value">{value}</strong>
        <span className="stat-card__note">{note}</span>
      </article>
    </Reveal>
  );
}

const architectureLabels: Record<string, string[]> = {
  "agent-systems": ["REQUEST", "POLICY", "TOOL", "VERIFY"],
  "retrieval-labs": ["QUERY", "RETRIEVE", "RERANK", "CITE"],
  "inference-portfolio": ["LOAD", "BATCH", "CACHE", "SERVE"],
  "ros2-navigation": ["MISSION", "WAYPOINT", "GUARD", "CONTROL"],
  "manipulation-gateway": ["TARGET", "LIMITS", "DRY RUN", "EXECUTE"],
  "edge-vision": ["FRAME", "METADATA", "SAFETY", "INSPECT"],
};

function ProjectArtwork({ project }: { project: PortfolioProject }) {
  const labels = architectureLabels[project.id] ?? ["INPUT", "PROCESS", "CHECK", "OUTPUT"];
  const gradientId = `project-glow-${project.id}`;
  const accent = project.color || "#5ed9c5";

  return (
    <div
      className="project-card__artwork"
      style={{ "--project-accent": accent } as CSSProperties}
      aria-hidden="true"
    >
      <svg viewBox="0 0 600 150" preserveAspectRatio="xMidYMid slice">
        <defs>
          <linearGradient id={gradientId} x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor={accent} stopOpacity=".17" />
            <stop offset="1" stopColor="#0d1721" stopOpacity="0" />
          </linearGradient>
        </defs>
        <rect width="600" height="150" rx="16" fill="#101b27" />
        <rect width="600" height="150" rx="16" fill={`url(#${gradientId})`} />
        <path className="artwork-path" d="M 68 64 H 532" />
        {labels.map((label, index) => {
          const x = 68 + index * 154.7;
          return (
            <g key={label}>
              <circle className="artwork-node-halo" cx={x} cy="64" r="27" />
              <circle className="artwork-node" cx={x} cy="64" r="20" />
              <text className="artwork-node-number" x={x} y="68">
                {String(index + 1).padStart(2, "0")}
              </text>
              <text className="artwork-node-label" x={x} y="113">
                {label}
              </text>
            </g>
          );
        })}
        <circle className="artwork-signal" cx="68" cy="64" r="3" />
      </svg>
    </div>
  );
}

function ProjectCard({
  project,
  index,
  onOpen,
}: {
  project: PortfolioProject;
  index: number;
  onOpen: (project: PortfolioProject) => void;
}) {
  const Icon = iconForCategory[project.category] ?? Code2;
  const detail = caseStudies[project.id];
  return (
    <Reveal delay={(index % 3) * 0.06}>
      <motion.article
        className="project-card"
        id={`project-${project.id}`}
        layout
        transition={{ duration: 0.26, ease: [0.22, 1, 0.36, 1] }}
      >
        {detail && <ProjectArtwork project={project} />}
        <div className="project-card__head">
          <span className="project-card__icon">
            <Icon aria-hidden="true" size={19} />
          </span>
          <span className="project-card__category">{project.category}</span>
          <a
            className="icon-link"
            href={project.url}
            target="_blank"
            rel="noreferrer"
            aria-label={`Open ${project.name} repository`}
          >
            <ArrowUpRight aria-hidden="true" size={18} />
          </a>
        </div>
        <p className="project-card__scope">{project.scope}</p>
        <h3>
          <a href={project.url} target="_blank" rel="noreferrer">
            {project.name}
          </a>
        </h3>
        <p className="project-card__summary">{project.summary}</p>
        <div className="project-card__proof">
          <span className="proof-label">Evidence</span>
          <p>{project.evidence}</p>
        </div>
        <button
          className="project-card__deep-dive"
          type="button"
          onClick={() => onOpen(project)}
          aria-label={`Open technical case study for ${project.name}`}
        >
          Technical case study <ArrowRight aria-hidden="true" size={15} />
        </button>
        <div className="project-card__footer">
          {project.language && <span>{project.language}</span>}
          <span>
            <Star aria-hidden="true" size={13} /> {formatNumber.format(project.stars)}
          </span>
          <span className="repo-date">Pushed {formatDate(project.pushedAt)}</span>
        </div>
      </motion.article>
    </Reveal>
  );
}

function RepoRow({ repository }: { repository: PublicRepository }) {
  const detail = repository.description || repository.topics?.slice(0, 3).join(" · ");
  return (
    <a
      className="repo-row"
      href={repository.url}
      target="_blank"
      rel="noreferrer"
    >
      <div className="repo-row__main">
        <span className="repo-row__title">
          <GitBranch aria-hidden="true" size={16} />
          {repository.name}
          {repository.archived && <span className="archived-tag">Archived</span>}
        </span>
        {detail && <span className="repo-row__description">{detail}</span>}
      </div>
      <div className="repo-row__meta">
        {repository.language && <span className="language-dot">{repository.language}</span>}
        <span>
          <Star aria-hidden="true" size={13} /> {formatNumber.format(repository.stars)}
        </span>
        <span>
          <GitFork aria-hidden="true" size={13} /> {formatNumber.format(repository.forks)}
        </span>
        <span className="repo-date">{formatDate(repository.pushedAt)}</span>
        <ExternalLink aria-hidden="true" size={15} />
      </div>
    </a>
  );
}

export default function App({ dataset = data }: { dataset?: PortfolioData }) {
  const [rangeDays, setRangeDays] = useState<RangeDays>(30);
  const [selectedCategory, setSelectedCategory] = useState("All work");
  const [search, setSearch] = useState("");
  const [language, setLanguage] = useState("All languages");
  const [sortBy, setSortBy] = useState("recent");
  const [visibleCount, setVisibleCount] = useState(12);
  const [dialog, setDialog] = useState<DialogState>(null);
  const [paletteQuery, setPaletteQuery] = useState("");
  const [activeCommand, setActiveCommand] = useState(0);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeStageId, setActiveStageId] = useState("validation");
  const [motionPaused, setMotionPaused] = useState(false);
  const [copyFeedback, setCopyFeedback] = useState("");
  const dialogRef = useRef<HTMLDialogElement>(null);
  const reduced = useReducedMotion();
  const { scrollYProgress } = useScroll();
  const snapshot = dataset.snapshot;

  const categories = useMemo(
    () => ["All work", ...new Set(dataset.projects.map((project) => project.category))],
    [dataset.projects],
  );

  const visibleProjects = useMemo(
    () =>
      dataset.projects.filter(
        (project) =>
          selectedCategory === "All work" || project.category === selectedCategory,
      ),
    [dataset.projects, selectedCategory],
  );

  const languages = useMemo(
    () => ["All languages", ...dataset.snapshot.languages.map((item) => item.name)],
    [dataset.snapshot.languages],
  );

  const paletteCommands = useMemo<PaletteCommand[]>(
    () => [
      ...sectionCommands,
      ...dataset.projects.map((project) => ({
        id: `project-${project.id}`,
        kind: "project" as const,
        title: project.name,
        description: `${project.category} · ${project.scope}`,
        project,
      })),
    ],
    [dataset.projects],
  );
  const matchedCommands = useMemo(() => {
    const query = paletteQuery.trim().toLocaleLowerCase();
    if (!query) return paletteCommands;
    return paletteCommands.filter((command) =>
      `${command.title} ${command.description}`.toLocaleLowerCase().includes(query),
    );
  }, [paletteCommands, paletteQuery]);

  const filteredRepositories = useMemo(() => {
    const query = search.trim().toLocaleLowerCase();
    const rows = dataset.repositories.filter((repo) => {
      const matchesQuery =
        !query ||
        repo.name.toLocaleLowerCase().includes(query) ||
        repo.description.toLocaleLowerCase().includes(query) ||
        (repo.topics ?? []).some((topic) => topic.toLocaleLowerCase().includes(query)) ||
        (repo.language ?? "").toLocaleLowerCase().includes(query);
      const matchesLanguage = language === "All languages" || repo.language === language;
      return matchesQuery && matchesLanguage;
    });
    return rows.sort((a, b) => {
      if (sortBy === "stars") return b.stars - a.stars || a.name.localeCompare(b.name);
      if (sortBy === "name") return a.name.localeCompare(b.name);
      return (b.pushedAt ?? "").localeCompare(a.pushedAt ?? "");
    });
  }, [dataset.repositories, language, search, sortBy]);

  const recentCount =
    rangeDays === 7
      ? snapshot.repositoriesPushed7d
      : rangeDays === 30
        ? snapshot.repositoriesPushed30d
        : snapshot.repositoriesPushed90d;

  const chartData = snapshot.monthlyLatestPushes;

  const generatedAt = new Date(dataset.generatedAt);
  const readableGeneratedAt = new Intl.DateTimeFormat("en-CA", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "UTC",
  }).format(generatedAt);

  const activeStage =
    systemStages.find((stage) => stage.id === activeStageId) ?? systemStages[2];
  const selectedProject = dialog?.kind === "project" ? dialog.project : null;
  const selectedCase = selectedProject ? caseStudies[selectedProject.id] : undefined;

  useEffect(() => {
    const node = dialogRef.current;
    if (!node) return;

    if (dialog) {
      if (!node.open) node.showModal();
      requestAnimationFrame(() => {
        const selector =
          dialog.kind === "palette" ? "[data-palette-input]" : "[data-dialog-title]";
        node.querySelector<HTMLElement>(selector)?.focus();
      });
    } else if (node.open) {
      node.close();
    }
  }, [dialog]);

  useEffect(() => {
    const onGlobalKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLocaleLowerCase() === "k") {
        event.preventDefault();
        setPaletteQuery("");
        setActiveCommand(0);
        setDialog({ kind: "palette" });
      }
    };
    window.addEventListener("keydown", onGlobalKeyDown);
    return () => window.removeEventListener("keydown", onGlobalKeyDown);
  }, []);

  useEffect(() => {
    setActiveCommand(0);
  }, [paletteQuery]);

  const chooseCommand = (command: PaletteCommand) => {
    if (command.kind === "project") {
      setDialog({ kind: "project", project: command.project });
      return;
    }
    setDialog(null);
    setMobileMenuOpen(false);
    document.getElementById(command.target)?.scrollIntoView({
      behavior: reduced ? "auto" : "smooth",
      block: "start",
    });
  };

  const selectSystemStage = (stage: SystemStage) => {
    setActiveStageId(stage.id);
    setSelectedCategory(stage.category);
  };

  const showRelatedWork = () => {
    document.getElementById("work")?.scrollIntoView({
      behavior: reduced ? "auto" : "smooth",
      block: "start",
    });
  };

  const copyProjectLink = async (project: PortfolioProject) => {
    const link = `${window.location.origin}${window.location.pathname}#project-${project.id}`;
    try {
      await navigator.clipboard.writeText(link);
      setCopyFeedback("Case-study link copied.");
    } catch {
      setCopyFeedback("Clipboard access is unavailable in this browser.");
    }
  };

  return (
    <MotionConfig reducedMotion="user">
    <div
      className="app-shell"
      id="top"
      data-motion-paused={motionPaused}
    >
      <motion.div
        className="scroll-progress"
        style={{ scaleX: scrollYProgress }}
        aria-hidden="true"
      />
      <div className="ambient ambient--one" aria-hidden="true" />
      <div className="ambient ambient--two" aria-hidden="true" />
      <header className="site-header">
        <a className="wordmark" href="#top" aria-label="AmDeep home">
          <span className="wordmark__mark">A</span>
          <span>AMDEEP<span className="wordmark__dot">.</span></span>
        </a>
        <nav
          className={`main-nav${mobileMenuOpen ? " is-open" : ""}`}
          id="main-navigation"
          aria-label="Main navigation"
        >
          <a href="#work" onClick={() => setMobileMenuOpen(false)}>Selected work</a>
          <a href="#signals" onClick={() => setMobileMenuOpen(false)}>Live signals</a>
          <a href="#repositories" onClick={() => setMobileMenuOpen(false)}>Repository explorer</a>
          <a href="#contact" onClick={() => setMobileMenuOpen(false)}>Contact</a>
        </nav>
        <div className="header-actions">
          <button
            className="mobile-menu-trigger"
            type="button"
            aria-expanded={mobileMenuOpen}
            aria-controls="main-navigation"
            aria-label={mobileMenuOpen ? "Close section navigation" : "Open section navigation"}
            onClick={() => setMobileMenuOpen((open) => !open)}
          >
            {mobileMenuOpen ? <X aria-hidden="true" size={17} /> : <Menu aria-hidden="true" size={17} />}
            <span>{mobileMenuOpen ? "Close" : "Menu"}</span>
          </button>
          <button
            className="palette-trigger"
            type="button"
            aria-label="Open project and section search. Keyboard shortcut Control or Command K."
            onClick={() => {
              setPaletteQuery("");
              setDialog({ kind: "palette" });
            }}
          >
            <Search aria-hidden="true" size={15} />
            <span>Jump to</span>
            <kbd><Command aria-hidden="true" size={11} /> K</kbd>
          </button>
          <a
            className="header-link"
            href="https://github.com/AmDeep"
            target="_blank"
            rel="noreferrer"
          >
            GitHub <ArrowUpRight aria-hidden="true" size={15} />
          </a>
          <a
            className="header-link header-link--contact"
            href="https://www.linkedin.com/in/a-s-70a471a3/"
            target="_blank"
            rel="noreferrer"
          >
            LinkedIn <ArrowUpRight aria-hidden="true" size={15} />
          </a>
        </div>
      </header>

      <main>
        <section className="hero section-wrap" aria-labelledby="hero-title">
          <div className="hero__copy">
            <div className="live-label">
              <span className="live-label__pulse" />
              PUBLIC PORTFOLIO · TORONTO
            </div>
            <h1 id="hero-title">
              Applied AI,
              <br />
              <span>built for the real world.</span>
            </h1>
            <p className="hero__lede">
              I build inspectable systems across retrieval, agent workflows,
              inference, and robotics—where model output needs to meet explicit
              boundaries and evidence.
            </p>
            <div className="hero__actions">
              <a className="button button--primary" href="#work">
                Explore selected work <ArrowDown aria-hidden="true" size={16} />
              </a>
              <a
                className="button button--quiet"
                href="https://github.com/AmDeep"
                target="_blank"
                rel="noreferrer"
              >
                <GitBranch aria-hidden="true" size={16} /> GitHub profile
              </a>
              <a
                className="button button--quiet"
                href="https://www.linkedin.com/in/a-s-70a471a3/"
                target="_blank"
                rel="noreferrer"
              >
                Connect on LinkedIn <ArrowUpRight aria-hidden="true" size={15} />
              </a>
            </div>
            <div className="hero__focus">
              <span>FOCUS</span>
              <p>Retrieval · Agent Systems · Inference · Robotics · Edge Vision</p>
            </div>
          </div>
          <motion.div
            className="hero-visual"
            role="group"
            aria-label="Interactive model-to-action system diagram"
            initial={reduced ? false : { opacity: 0, scale: 0.96 }}
            animate={reduced ? undefined : { opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          >
            <div className="visual-orbit visual-orbit--outer" />
            <div className="visual-orbit visual-orbit--inner" />
            <div className="visual-core">
              <Workflow aria-hidden="true" size={29} />
              <span>MODEL<br />TO ACTION</span>
            </div>
            <div className="visual-stages" role="group" aria-label="Select a system stage">
              {systemStages.map((stage) => {
                const Icon = iconForStage[stage.id] ?? Code2;
                const position = {
                  context: "top",
                  validation: "right",
                  action: "bottom",
                  proposal: "left",
                }[stage.id];
                return (
                  <button
                    key={stage.id}
                    className={`visual-node visual-node--${position}${activeStageId === stage.id ? " is-active" : ""}`}
                    type="button"
                    aria-pressed={activeStageId === stage.id}
                    onClick={() => selectSystemStage(stage)}
                  >
                    <span className="visual-node__icon"><Icon aria-hidden="true" size={15} /></span>
                    {stage.label}
                  </button>
                );
              })}
            </div>
            <div className="visual-signal" aria-hidden="true" />
            <div className="visual-caption">
              <p aria-live="polite">{activeStage.description}</p>
              <button type="button" onClick={showRelatedWork}>
                Explore {activeStage.category} work <ArrowRight aria-hidden="true" size={13} />
              </button>
            </div>
            <button
              className="motion-toggle"
              type="button"
              aria-pressed={motionPaused}
              onClick={() => setMotionPaused((paused) => !paused)}
            >
              {motionPaused ? <Play aria-hidden="true" size={13} /> : <Pause aria-hidden="true" size={13} />}
              {motionPaused ? "Play motion" : "Pause motion"}
            </button>
          </motion.div>
        </section>

        <section className="work section-wrap" id="work" aria-labelledby="work-title">
          <div className="section-heading">
            <div>
              <p className="eyebrow">SELECTED WORK</p>
              <h2 id="work-title">Systems with inspectable decisions.</h2>
            </div>
            <p className="section-aside">
              Six code-first case studies. Open the implementation, inspect the evidence, and see where each result stops.
            </p>
          </div>
          <div className="filter-row" role="group" aria-label="Filter featured projects">
            {categories.map((category) => (
              <button
                key={category}
                type="button"
                className={`filter-chip ${selectedCategory === category ? "is-active" : ""}`}
                aria-pressed={selectedCategory === category}
                onClick={() => setSelectedCategory(category)}
              >
                {category}
              </button>
            ))}
          </div>
          <motion.div className="project-grid" layout>
            {visibleProjects.map((project, index) => (
              <ProjectCard
                key={project.id}
                project={project}
                index={index}
                onOpen={(selected) => setDialog({ kind: "project", project: selected })}
              />
            ))}
          </motion.div>
          {visibleProjects.length === 0 && (
            <p className="empty-state">No featured projects match this filter.</p>
          )}
        </section>

        <section className="principles section-wrap" aria-labelledby="principles-title">
          <div className="principles-card">
            <div className="principles-card__intro">
              <p className="eyebrow">ENGINEERING APPROACH</p>
              <h2 id="principles-title">A model can propose.<br /><span>Systems still need proof.</span></h2>
            </div>
            <div className="principle-list">
              <div><span>01</span><p>Keep model output structured and inspectable.</p></div>
              <div><span>02</span><p>Validate proposals before tool or actuator boundaries.</p></div>
              <div><span>03</span><p>Use tests, replay, and explicit limitations as evidence.</p></div>
            </div>
          </div>
        </section>

        <section className="metrics section-wrap" id="signals" aria-labelledby="signals-title">
          <div className="section-heading">
            <div>
              <p className="eyebrow">LIVE REPOSITORY SIGNALS</p>
              <h2 id="signals-title">Activity, with the definition attached.</h2>
            </div>
            <div className="freshness">
              <span className="freshness__dot" />
              Snapshot updated {readableGeneratedAt} UTC
            </div>
          </div>
          <div className="stats-grid">
            <StatCard
              label="Original public repos"
              value={formatNumber.format(snapshot.originalPublicRepositories)}
              note="Owned · public · non-fork"
              icon={Boxes}
              delay={0}
            />
            <StatCard
              label="Stars"
              value={formatNumber.format(snapshot.stars)}
              note="Across original public repos"
              icon={Star}
              delay={0.06}
            />
            <StatCard
              label="Primary languages"
              value={formatNumber.format(snapshot.primaryLanguageCount)}
              note="Counted by repository"
              icon={Code2}
              delay={0.12}
            />
            <StatCard
              label={`Repos pushed · ${rangeDays} days`}
              value={formatNumber.format(recentCount)}
              note="Based on each repo's latest push"
              icon={Activity}
              delay={0.18}
            />
          </div>

          <div className="metric-controls">
            <span>Recent repository pushes</span>
            <div className="segmented-control" role="group" aria-label="Recent-push summary window">
              {ranges.map((range) => (
                <button
                  key={range}
                  type="button"
                  aria-pressed={rangeDays === range}
                  onClick={() => setRangeDays(range)}
                >
                  {range}d
                </button>
              ))}
            </div>
          </div>
          <p className="metric-definition">
            Recent activity counts repositories by each repository’s latest push—not commit volume.
          </p>
          <Suspense fallback={<div className="dashboard-loading" role="status">Loading charts…</div>}>
            <ActivityCharts
              monthly={chartData}
              languages={snapshot.languages}
            />
          </Suspense>
        </section>

        <section className="repository-section section-wrap" id="repositories" aria-labelledby="repositories-title">
          <div className="section-heading">
            <div>
              <p className="eyebrow">PUBLIC REPOSITORY EXPLORER</p>
              <h2 id="repositories-title">Browse the rest of the work.</h2>
            </div>
            <p className="section-aside">
              {formatNumber.format(dataset.repositories.length)} owned public non-fork repositories in this snapshot.
            </p>
          </div>
          <div className="explorer-controls">
            <label className="search-field">
              <Search aria-hidden="true" size={17} />
              <input
                type="search"
                placeholder="Search name, description, topic, or language"
                value={search}
                onChange={(event) => {
                  setSearch(event.target.value);
                  setVisibleCount(12);
                }}
                aria-label="Search public repositories"
              />
            </label>
            <label className="select-field">
              <span className="sr-only">Filter by primary language</span>
              <select
                aria-label="Filter by primary language"
                value={language}
                onChange={(event) => {
                  setLanguage(event.target.value);
                  setVisibleCount(12);
                }}
              >
                {languages.map((item) => <option key={item} value={item}>{item}</option>)}
              </select>
            </label>
            <label className="select-field">
              <span className="sr-only">Sort repositories</span>
              <select aria-label="Sort repositories" value={sortBy} onChange={(event) => setSortBy(event.target.value)}>
                <option value="recent">Most recently pushed</option>
                <option value="stars">Most stars</option>
                <option value="name">Name A–Z</option>
              </select>
            </label>
          </div>
          <div className="repo-results-row">
            <p className="results-count" role="status" aria-live="polite">
              Showing {Math.min(visibleCount, filteredRepositories.length)} of {filteredRepositories.length} matching repositories
            </p>
            {(search || language !== "All languages" || sortBy !== "recent") && (
              <button
                className="clear-filters"
                type="button"
                onClick={() => {
                  setSearch("");
                  setLanguage("All languages");
                  setSortBy("recent");
                  setVisibleCount(12);
                }}
              >
                Clear filters
              </button>
            )}
          </div>
          <div className="repo-list">
            {filteredRepositories.slice(0, visibleCount).map((repo) => (
              <RepoRow key={repo.name} repository={repo} />
            ))}
          </div>
          {filteredRepositories.length === 0 && (
            <div className="empty-state">
              <p>No repositories match those filters.</p>
              <button
                type="button"
                className="clear-filters"
                onClick={() => {
                  setSearch("");
                  setLanguage("All languages");
                  setSortBy("recent");
                  setVisibleCount(12);
                }}
              >
                Reset search and language
              </button>
            </div>
          )}
          {filteredRepositories.length > visibleCount && (
            <button
              className="button button--more"
              type="button"
              onClick={() => setVisibleCount((count) => count + 12)}
            >
              Show {Math.min(12, filteredRepositories.length - visibleCount)} more <ArrowDown aria-hidden="true" size={15} />
            </button>
          )}
        </section>

        <section className="contact-cta section-wrap" id="contact" aria-labelledby="contact-title">
          <div>
            <p className="eyebrow">HIRING OR COLLABORATING?</p>
            <h2 id="contact-title">Let’s talk about systems that need evidence.</h2>
            <p>
              For applied AI, retrieval, inference, or robotics conversations, reach me on LinkedIn.
            </p>
          </div>
          <div className="contact-cta__actions">
            <a
              className="button button--primary"
              href="https://www.linkedin.com/in/a-s-70a471a3/"
              target="_blank"
              rel="noreferrer"
            >
              Connect on LinkedIn <ArrowUpRight aria-hidden="true" size={16} />
            </a>
            <a
              className="button button--quiet"
              href="https://github.com/AmDeep"
              target="_blank"
              rel="noreferrer"
            >
              Inspect the code <GitBranch aria-hidden="true" size={15} />
            </a>
          </div>
        </section>
      </main>

      <dialog
        ref={dialogRef}
        className="site-dialog"
        aria-labelledby={dialog?.kind === "palette" ? "palette-title" : "case-study-title"}
        onClose={() => setDialog(null)}
        onCancel={(event) => {
          event.preventDefault();
          setDialog(null);
        }}
        onClick={(event) => {
          if (event.target === event.currentTarget) setDialog(null);
        }}
      >
        <AnimatePresence mode="wait" initial={false}>
          {dialog?.kind === "palette" && (
            <motion.div
              key="command-palette"
              className="dialog-panel command-panel"
              initial={reduced ? false : { opacity: 0, y: 10, scale: 0.99 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 6 }}
              transition={{ duration: 0.18 }}
            >
              <div className="dialog-heading">
                <div>
                  <p className="eyebrow">QUICK NAVIGATION</p>
                  <h2 id="palette-title" data-dialog-title tabIndex={-1}>Find a project or section</h2>
                </div>
                <button
                  className="dialog-close"
                  type="button"
                  aria-label="Close navigation search"
                  onClick={() => setDialog(null)}
                >
                  <X aria-hidden="true" size={18} />
                </button>
              </div>
              <label className="command-search">
                <Search aria-hidden="true" size={17} />
                <input
                  data-palette-input
                  type="search"
                  role="combobox"
                  aria-label="Search projects and page sections"
                  aria-autocomplete="list"
                  aria-expanded="true"
                  aria-controls="command-results"
                  aria-activedescendant={matchedCommands[activeCommand]?.id}
                  placeholder="Type a project, technology, or section"
                  value={paletteQuery}
                  onChange={(event) => setPaletteQuery(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === "ArrowDown") {
                      event.preventDefault();
                      setActiveCommand((index) =>
                        Math.min(index + 1, Math.max(0, matchedCommands.length - 1)),
                      );
                    } else if (event.key === "ArrowUp") {
                      event.preventDefault();
                      setActiveCommand((index) => Math.max(0, index - 1));
                    } else if (event.key === "Enter" && matchedCommands[activeCommand]) {
                      event.preventDefault();
                      chooseCommand(matchedCommands[activeCommand]);
                    }
                  }}
                />
                <kbd>Esc</kbd>
              </label>
              <p className="command-count" role="status" aria-live="polite">
                {matchedCommands.length} {matchedCommands.length === 1 ? "result" : "results"}
              </p>
              <div
                className="command-results"
                id="command-results"
                role="listbox"
                aria-label="Search results"
              >
                {matchedCommands.map((command, index) => (
                  <div
                    key={command.id}
                    id={command.id}
                    className={`command-option${index === activeCommand ? " is-active" : ""}`}
                    role="option"
                    aria-selected={index === activeCommand}
                    onMouseDown={(event) => event.preventDefault()}
                    onMouseEnter={() => setActiveCommand(index)}
                    onClick={() => chooseCommand(command)}
                  >
                    <span className="command-option__icon">
                      {command.kind === "project"
                        ? <Code2 aria-hidden="true" size={16} />
                        : <ArrowUpRight aria-hidden="true" size={16} />}
                    </span>
                    <span className="command-option__copy">
                      <strong>{command.title}</strong>
                      <span>{command.description}</span>
                    </span>
                    <ArrowRight aria-hidden="true" size={15} />
                  </div>
                ))}
                {matchedCommands.length === 0 && (
                  <p className="command-empty">
                    No matches. Try “robotics”, “retrieval”, or a project name.
                  </p>
                )}
              </div>
              <div className="command-help">
                <span><kbd>↑</kbd><kbd>↓</kbd> move</span>
                <span><kbd>↵</kbd> open</span>
                <span><kbd>Esc</kbd> close</span>
              </div>
            </motion.div>
          )}
          {selectedProject && selectedCase && (
            <motion.div
              key={`case-${selectedProject.id}`}
              className="dialog-panel case-study-panel"
              initial={reduced ? false : { opacity: 0, y: 10, scale: 0.99 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 6 }}
              transition={{ duration: 0.18 }}
            >
              <div className="dialog-heading">
                <div>
                  <p className="eyebrow">{selectedProject.category} · CASE STUDY</p>
                  <h2 id="case-study-title" data-dialog-title tabIndex={-1}>{selectedProject.name}</h2>
                </div>
                <button
                  className="dialog-close"
                  type="button"
                  aria-label={`Close ${selectedProject.name} case study`}
                  onClick={() => setDialog(null)}
                >
                  <X aria-hidden="true" size={18} />
                </button>
              </div>
              <div className="case-study-summary">
                <ProjectArtwork project={selectedProject} />
                <div>
                  <span className="case-study-scope">{selectedProject.scope}</span>
                  <p>{selectedCase.challenge}</p>
                </div>
              </div>
              <div className="case-study-grid">
                <section aria-labelledby="case-design-title">
                  <p className="eyebrow">SYSTEM DESIGN</p>
                  <h3 id="case-design-title">What the repository implements</h3>
                  <ul>
                    {selectedCase.design.map((item) => <li key={item}>{item}</li>)}
                  </ul>
                </section>
                <section aria-labelledby="case-evidence-title">
                  <p className="eyebrow">REVIEWABLE PROOF</p>
                  <h3 id="case-evidence-title">What to inspect</h3>
                  <ul>
                    {selectedCase.evidence.map((item) => <li key={item}>{item}</li>)}
                  </ul>
                </section>
                <section className="case-study-boundary" aria-labelledby="case-boundary-title">
                  <p className="eyebrow">SCOPE BOUNDARY</p>
                  <h3 id="case-boundary-title">What this does not claim</h3>
                  <p>{selectedCase.boundary}</p>
                </section>
              </div>
              <div className="case-study-footer">
                <div className="case-study-links">
                  {selectedCase.links.map((link) => (
                    <a key={link.href} href={link.href} target="_blank" rel="noreferrer">
                      {link.label}<ArrowUpRight aria-hidden="true" size={14} />
                    </a>
                  ))}
                </div>
                <button
                  className="copy-link"
                  type="button"
                  aria-label={`Copy link to ${selectedProject.name} case study`}
                  onClick={() => void copyProjectLink(selectedProject)}
                >
                  <Copy aria-hidden="true" size={14} /> Copy link
                </button>
              </div>
              <p className="copy-feedback" role="status" aria-live="polite">{copyFeedback}</p>
            </motion.div>
          )}
        </AnimatePresence>
      </dialog>

      <footer className="site-footer section-wrap">
        <div>
          <a className="wordmark wordmark--footer" href="#top">
            <span className="wordmark__mark">A</span>
            <span>AMDEEP<span className="wordmark__dot">.</span></span>
          </a>
          <p>Applied AI · Retrieval · Inference · Robotics</p>
        </div>
        <div className="site-footer__meta">
          <span>Data source: GitHub public repository metadata</span>
          <div className="site-footer__links">
            <a href="https://www.linkedin.com/in/a-s-70a471a3/" target="_blank" rel="noreferrer">
              LinkedIn <ArrowUpRight aria-hidden="true" size={14} />
            </a>
            <a href="https://github.com/AmDeep" target="_blank" rel="noreferrer">
              GitHub <ArrowUpRight aria-hidden="true" size={14} />
            </a>
          </div>
        </div>
      </footer>
    </div>
    </MotionConfig>
  );
}
