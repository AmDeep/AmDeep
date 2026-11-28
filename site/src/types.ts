export interface MetricLanguage {
  name: string;
  repositories: number;
}

export interface MonthlyPush {
  key: string;
  label: string;
  repositories: number;
}

export interface PortfolioSnapshot {
  originalPublicRepositories: number;
  stars: number;
  forks: number;
  primaryLanguageCount: number;
  repositoriesPushed7d: number;
  repositoriesPushed30d: number;
  repositoriesPushed90d: number;
  lastPushAt: string | null;
  languages: MetricLanguage[];
  monthlyLatestPushes: MonthlyPush[];
}

export interface PortfolioProject {
  id: string;
  name: string;
  repo: string;
  url: string;
  category: string;
  scope: string;
  summary: string;
  evidence: string;
  featured: boolean;
  language: string | null;
  stars: number;
  forks: number;
  pushedAt: string | null;
}

export interface PublicRepository {
  name: string;
  description: string;
  url: string;
  language: string | null;
  stars: number;
  forks: number;
  pushedAt: string | null;
  createdAt: string | null;
  archived: boolean;
  topics: string[];
}

export interface PortfolioData {
  schemaVersion: number;
  username: string;
  generatedAt: string;
  source: string;
  scope: string;
  definitions: {
    recentPushes: string;
    monthlyActivity: string;
    languages: string;
  };
  snapshot: PortfolioSnapshot;
  projects: PortfolioProject[];
  repositories: PublicRepository[];
}
