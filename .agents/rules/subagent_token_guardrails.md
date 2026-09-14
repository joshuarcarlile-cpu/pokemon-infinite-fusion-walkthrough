# Strict Token Protection & Subagent Loop Prevention Rules

This rule is mandatory and permanently binding across all Antigravity agents, subagents, and sessions operating in this repository.

---

## 1. Absolute Ban on Exploratory Browser Subagent Loops
* **No Routine Browser Verification**: Never launch a `browser_subagent` for routine HTML, CSS, or JavaScript verification of dashboard changes. The dashboard is a standalone local file (`dist/index.html`) whose layout, classes, rendering logic, and responsiveness can and must be validated deterministically via code review, template checks, and compiler tests (`compile_dashboard.py`).
* **Exploratory Loops Strictly Prohibited**: Agents and subagents must NEVER engage in iterative DOM traversal loops:
  - NO repeated `browser_get_dom` calls interspersed with micro-scrolls.
  - NO interactive DOM element hunting via search boxes, clicking random coordinates, or trial-and-error typing.
  - NO multi-step navigation exploration.

---

## 2. Hard Ceilings for Explicit User-Requested Browser Actions
* If and only if the USER explicitly requests a browser screenshot or video recording:
  1. **Maximum 3 Steps Total**: The subagent must execute at most 3 actions:
     - Step 1: `open_browser_url` (directly targeting the anchor if applicable, e.g. `file:///.../dist/index.html#phase-1-5`).
     - Step 2: Capture screenshot / finalize recording.
     - Step 3: Terminate immediately.
  2. **No Interactive Searching**: If the desired element is not in view upon load, the subagent must capture the visible viewport or full-page screenshot as-is and exit immediately. NEVER attempt to scroll-hunt or search.
  3. **Zero Token Waste**: The subagent prompt MUST explicitly forbid calling `browser_get_dom` more than once, and MUST mandate immediate exit upon capturing the artifact.

---

## 3. General Subagent Token Economy
* All subagents must be strictly single-purpose and ephemeral:
  - Read only the targeted 1–4 KB file.
  - Return final receipts under 30 tokens.
  - Hard step ceiling of $\le 5$ tool calls per subagent invocation.
  - If a subagent encounters any failure or missing element, it must abort immediately rather than attempting open-ended retries.
