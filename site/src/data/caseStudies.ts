export interface CaseStudyLink {
  label: string;
  href: string;
}

export interface CaseStudy {
  challenge: string;
  design: string[];
  evidence: string[];
  boundary: string;
  links: CaseStudyLink[];
}

/**
 * Case-study copy is limited to claims supported by each public repository's
 * README and linked artifacts. These are implementation details, not claims
 * of customer adoption, production deployment, or business impact.
 */
export const caseStudies: Record<string, CaseStudy> = {
  "agent-systems": {
    challenge:
      "Make reliability controls visible as small, runnable engineering patterns rather than relying on a broad claim about agent quality.",
    design: [
      "Twelve independently packaged Python labs, each with package metadata, a namespaced module, a command, tests, architecture-diagram source, and captured demo evidence.",
      "Examples cover strict tool parsing, authorization before credential access, bounded retry budgets, idempotency, and independent completion checks.",
    ],
    evidence: [
      "The authorization example denies access before credential use.",
      "The idempotency lab records results for replay, while the completion gate checks postconditions independently.",
    ],
    boundary:
      "The README describes a lab suite and its artifacts; it does not claim production deployment, customer usage, or measured business impact.",
    links: [
      {
        label: "Repository README",
        href: "https://github.com/AmDeep/AIAgents/blob/main/README.md",
      },
      {
        label: "Authorization boundary",
        href: "https://github.com/AmDeep/AIAgents/blob/main/examples/permissions/README.md",
      },
      {
        label: "Idempotency ledger",
        href: "https://github.com/AmDeep/AIAgents/blob/main/examples/idempotency/README.md",
      },
    ],
  },
  "retrieval-labs": {
    challenge:
      "Compare the engineering choices that shape retrieval-augmented systems without requiring hosted model services to run the checked-in examples.",
    design: [
      "Fifteen focused projects are independently packaged, tested, and documented with their contracts and limitations.",
      "Model and hosted-service dependencies are injected; checked-in fixtures run locally.",
    ],
    evidence: [
      "The project map includes hybrid search, reranking, GraphRAG, faithfulness checks, and explicit context precision/recall evaluation.",
      "The README documents local test and verifier commands.",
    ],
    boundary:
      "The repository demonstrates runnable experiments and evaluation fixtures; it does not claim production retrieval quality, hosted-service performance, or customer outcomes.",
    links: [
      {
        label: "Repository README",
        href: "https://github.com/AmDeep/RAGSystemLabs/blob/main/README.md",
      },
      {
        label: "Hybrid search",
        href: "https://github.com/AmDeep/RAGSystemLabs/blob/main/projects/hybrid_search/README.md",
      },
      {
        label: "Faithfulness checks",
        href: "https://github.com/AmDeep/RAGSystemLabs/blob/main/projects/faithfulness/README.md",
      },
    ],
  },
  "inference-portfolio": {
    challenge:
      "Compare inference and serving tradeoffs while making clear which results are measured, calculated, simulated, or not run on the available host.",
    design: [
      "Twelve independent project stages cover capacity arithmetic, event traces, quantization evaluation, cache replay, batching simulation, routing, latency/cost analysis, and serving patterns.",
      "The README labels evidence status by stage instead of presenting every experiment as a benchmark.",
    ],
    evidence: [
      "The stage map distinguishes CPU timing, analytical models, synthetic traces, fixture-only evaluation, and live-engine work.",
      "A shared regression suite and portfolio audit script are documented.",
    ],
    boundary:
      "The README states that no GPU engine run was performed on the development host and that some GPU measurements remain unrun. No production benchmark is implied.",
    links: [
      {
        label: "Repository README and evidence map",
        href: "https://github.com/AmDeep/inference-serving-portfolio/blob/main/README.md",
      },
      {
        label: "Regression tests",
        href: "https://github.com/AmDeep/inference-serving-portfolio/tree/main/tests",
      },
      {
        label: "Serving engines stage",
        href: "https://github.com/AmDeep/inference-serving-portfolio/tree/main/03-serving-engines",
      },
    ],
  },
  "ros2-navigation": {
    challenge:
      "Translate a natural-language mission into a waypoint without letting a language model issue motor commands.",
    design: [
      "A vLLM adapter can produce a structured waypoint; a deterministic local controller converts it to bounded Twist-compatible output.",
      "The model adapter stays outside the control loop, with replay checks and an obstacle-stop boundary documented in the repository.",
    ],
    evidence: [
      "The repository publishes an architecture diagram and replay-output artifact.",
      "The README documents replay and ROS 2 execution paths separately.",
    ],
    boundary:
      "The fixture is replay input, not a physical-robot result. The README explicitly keeps model interpretation out of the motor-command path.",
    links: [
      {
        label: "Repository README",
        href: "https://github.com/AmDeep/ros2-vllm-navigation-bridge/blob/main/README.md",
      },
      {
        label: "Architecture diagram",
        href: "https://github.com/AmDeep/ros2-vllm-navigation-bridge/blob/main/docs/architecture.svg",
      },
      {
        label: "Replay output",
        href: "https://github.com/AmDeep/ros2-vllm-navigation-bridge/blob/main/docs/replay-output.svg",
      },
    ],
  },
  "manipulation-gateway": {
    challenge:
      "Allow a model to express robot-arm intent without trusting it to define actuator limits or execute a motion by itself.",
    design: [
      "The gateway validates request schemas, configured joint limits, maximum joint-space steps, and an explicit execute flag.",
      "The default CLI is dry-run and returns a JSON decision; invalid or unavailable planning produces an explicit rejection state.",
    ],
    evidence: [
      "The README describes a deterministic validation path before any actuator adapter.",
      "Architecture and replay-output artifacts are linked from the repository.",
    ],
    boundary:
      "The repository does not claim a production robot adapter or hardware emergency-stop integration; the README identifies those as separate deployment work.",
    links: [
      {
        label: "Repository README",
        href: "https://github.com/AmDeep/manipulation-vllm-safety-gateway/blob/main/README.md",
      },
      {
        label: "Architecture diagram",
        href: "https://github.com/AmDeep/manipulation-vllm-safety-gateway/blob/main/docs/architecture.svg",
      },
      {
        label: "Replay output",
        href: "https://github.com/AmDeep/manipulation-vllm-safety-gateway/blob/main/docs/replay-output.svg",
      },
    ],
  },
  "edge-vision": {
    challenge:
      "Keep capture metadata, robot state, and safety checks explicit at the edge while treating model interpretation as an optional semantic layer.",
    design: [
      "The pipeline moves from frame metadata to a typed task request, optional vLLM JSON plan, safety gate, and inspection result.",
      "Offline replay is documented separately from live camera and inference integrations.",
    ],
    evidence: [
      "The README links architecture and offline replay artifacts.",
      "It documents a strict JSON response shape and explicitly states which data must come from real inputs.",
    ],
    boundary:
      "The checked-in frame is a replay fixture, not a live camera measurement. The README does not claim GPU execution on the development machine.",
    links: [
      {
        label: "Repository README",
        href: "https://github.com/AmDeep/edge-vision-vllm-inspector/blob/main/README.md",
      },
      {
        label: "Architecture diagram",
        href: "https://github.com/AmDeep/edge-vision-vllm-inspector/blob/main/docs/architecture.svg",
      },
      {
        label: "Offline replay output",
        href: "https://github.com/AmDeep/edge-vision-vllm-inspector/blob/main/docs/replay-output.svg",
      },
    ],
  },
};
