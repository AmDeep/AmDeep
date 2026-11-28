import { lazy, Suspense, useMemo, useState } from "react";
import type { ReactNode } from "react";
import {
  Activity,
  ArrowDown,
  ArrowUpRight,
  Bot,
  Boxes,
  Code2,
  Database,
  ExternalLink,
  GitFork,
  GitBranch,
  Search,
  Star,
  Waypoints,
  Workflow,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { motion, useReducedMotion } from "motion/react";
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

const iconForCategory: Record<string, LucideIcon> = {
  "Agent systems": Bot,
  Retrieval: Database,
  Inference: Workflow,
  Robotics: Waypoints,
  "Edge vision": Boxes,
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

function ProjectCard({ project, index }: { project: PortfolioProject; index: number }) {
  const Icon = iconForCategory[project.category] ?? Code2;
  return (
    <Reveal delay={(index % 3) * 0.06}>
      <article className="project-card">
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
        <div className="project-card__footer">
          {project.language && <span>{project.language}</span>}
          <span>
            <Star aria-hidden="true" size={13} /> {formatNumber.format(project.stars)}
          </span>
          <span className="repo-date">Pushed {formatDate(project.pushedAt)}</span>
        </div>
      </article>
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
  const reduced = useReducedMotion();
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

  const filteredRepositories = useMemo(() => {
    const query = search.trim().toLocaleLowerCase();
    const rows = dataset.repositories.filter((repo) => {
      const matchesQuery =
        !query ||
        repo.name.toLocaleLowerCase().includes(query) ||
        repo.description.toLocaleLowerCase().includes(query) ||
        (repo.topics ?? []).some((topic) => topic.toLocaleLowerCase().includes(query));
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

  return (
    <div className="app-shell" id="top">
      <div className="ambient ambient--one" aria-hidden="true" />
      <div className="ambient ambient--two" aria-hidden="true" />
      <header className="site-header">
        <a className="wordmark" href="#top" aria-label="AmDeep home">
          <span className="wordmark__mark">A</span>
          <span>AMDEEP<span className="wordmark__dot">.</span></span>
        </a>
        <nav className="main-nav" aria-label="Main navigation">
          <a href="#work">Selected work</a>
          <a href="#signals">Live signals</a>
          <a href="#repositories">Repository explorer</a>
        </nav>
        <a
          className="header-link"
          href="https://github.com/AmDeep"
          target="_blank"
          rel="noreferrer"
        >
          GitHub <ArrowUpRight aria-hidden="true" size={15} />
        </a>
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
            </div>
            <div className="hero__focus">
              <span>FOCUS</span>
              <p>Retrieval · Agent Systems · Inference · Robotics · Edge Vision</p>
            </div>
          </div>
          <motion.div
            className="hero-visual"
            role="img"
            aria-label="Diagram showing a model proposal passing through validation before bounded action"
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
            <div className="visual-node visual-node--top">
              <span className="visual-node__icon"><Database aria-hidden="true" size={15} /></span>
              CONTEXT
            </div>
            <div className="visual-node visual-node--right">
              <span className="visual-node__icon"><Code2 aria-hidden="true" size={15} /></span>
              VALIDATION
            </div>
            <div className="visual-node visual-node--bottom">
              <span className="visual-node__icon"><Waypoints aria-hidden="true" size={15} /></span>
              BOUNDED ACTION
            </div>
            <div className="visual-node visual-node--left">
              <span className="visual-node__icon"><Bot aria-hidden="true" size={15} /></span>
              PROPOSAL
            </div>
            <div className="visual-signal" aria-hidden="true" />
            <div className="visual-caption">A recurring design pattern<br />across selected projects</div>
          </motion.div>
        </section>

        <section className="metrics section-wrap" id="signals" aria-labelledby="signals-title">
          <div className="section-heading">
            <div>
              <p className="eyebrow">LIVE REPOSITORY SIGNALS</p>
              <h2 id="signals-title">Proof that updates with the work.</h2>
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

          <Suspense fallback={<div className="dashboard-loading" role="status">Loading charts…</div>}>
            <ActivityCharts
              monthly={chartData}
              languages={snapshot.languages}
              ranges={ranges}
              rangeDays={rangeDays}
              onRangeChange={setRangeDays}
            />
          </Suspense>
        </section>

        <section className="work section-wrap" id="work" aria-labelledby="work-title">
          <div className="section-heading">
            <div>
              <p className="eyebrow">SELECTED WORK</p>
              <h2 id="work-title">Systems with inspectable decisions.</h2>
            </div>
            <p className="section-aside">
              Portfolio projects and reference implementations. Each card links to code and its README.
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
          <div className="project-grid">
            {visibleProjects.map((project, index) => (
              <ProjectCard key={project.id} project={project} index={index} />
            ))}
          </div>
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
                placeholder="Search repositories or topics"
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
          <div className="repo-list">
            {filteredRepositories.slice(0, visibleCount).map((repo) => (
              <RepoRow key={repo.name} repository={repo} />
            ))}
          </div>
          {filteredRepositories.length === 0 && (
            <p className="empty-state">No public repositories match those filters.</p>
          )}
          {filteredRepositories.length > visibleCount && (
            <button
              className="button button--more"
              type="button"
              onClick={() => setVisibleCount((count) => count + 12)}
            >
              Show 12 more <ArrowDown aria-hidden="true" size={15} />
            </button>
          )}
        </section>
      </main>

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
          <a href="https://github.com/AmDeep" target="_blank" rel="noreferrer">
            View GitHub <ArrowUpRight aria-hidden="true" size={14} />
          </a>
        </div>
      </footer>
    </div>
  );
}
