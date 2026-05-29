# The Parser Engine

The **Parser Engine** acts as the central nervous system for GBT configuration management. It is responsible for parsing **both** the project initialization parameters (`gbt_project.yaml`) and the schema models (`models/*.yml`) concurrently. Each component is parsed and loaded directly into a unified **Manifest Tree** (the Source of Truth) before any database execution begins.

---

## The Compilation Pipeline

To convert decoupled project assets into an actionable execution plan, the Parser executes two major resolution tracks that culminate into the exact same Manifest object:

<style>
  .gbt-pipeline-container {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    margin: 2rem 0;
    padding: 1.5rem 1rem;
    background: var(--md-default-bg-color, #ffffff);
    border: 1px solid var(--md-default-fg-color--lightest, #e0e0e0);
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  }
  .gbt-pipeline {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    overflow-x: auto;
  }
  .gbt-node {
    flex: 0 0 auto;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 0.8rem;
    border-radius: 8px;
    color: #ffffff;
    font-weight: 600;
    text-align: center;
    width: 125px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    z-index: 2;
    font-size: 0.75rem;
    line-height: 1.2;
  }
  .gbt-node-icon { font-size: 1.5rem; margin-bottom: 0.3rem; }
  
  .gbt-edge {
    flex: 1 1 90px;
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
    min-width: 90px;
    margin: 0 -2px;
    z-index: 1;
  }
  .gbt-edge-label {
    font-size: 0.55rem;
    font-weight: 700;
    padding: 0.15rem 0.3rem;
    background: var(--md-default-bg-color, #ffffff);
    color: var(--md-default-fg-color, #333333);
    border: 1px solid var(--md-default-fg-color--lightest, #e0e0e0);
    border-radius: 8px;
    margin-bottom: 5px;
    white-space: nowrap;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  }
  .gbt-edge-track {
    width: 100%;
    height: 6px;
    background: var(--md-default-fg-color--lightest, #e0e0e0);
    position: relative;
    overflow: hidden;
  }
  .gbt-edge-flow {
    position: absolute;
    top: 0;
    left: -50%;
    width: 50%;
    height: 100%;
    background: linear-gradient(90deg, transparent, #29b6f6, #0277bd, transparent);
    animation: flow 1.2s infinite linear;
  }
  @keyframes flow {
    0% { left: -50%; }
    100% { left: 100%; }
  }

  .gbt-node.proj { background: linear-gradient(135deg, #5c6bc0, #37474f); }
  .gbt-node.loader { background: linear-gradient(135deg, #fbc02d, #f57f17); }
  .gbt-node.schema { background: linear-gradient(135deg, #00897b, #004d40); }
  .gbt-node.json { background: linear-gradient(135deg, #d81b60, #880e4f); }
</style>

<div class="gbt-pipeline-container">
  <!-- Track 1: Project Init -->
  <div class="gbt-pipeline">
    <div class="gbt-node proj">
      <span class="gbt-node-icon">⚙️</span>
      <span>Project Init</span>
    </div>
    <div class="gbt-edge">
      <span class="gbt-edge-label">Parse Config 📍</span>
      <div class="gbt-edge-track"><div class="gbt-edge-flow"></div></div>
    </div>
    <div class="gbt-node loader">
      <span class="gbt-node-icon">🛠️</span>
      <span>Project Init<br>Engine Loader</span>
    </div>
    <div class="gbt-edge">
      <span class="gbt-edge-label">Load State 🚀</span>
      <div class="gbt-edge-track"><div class="gbt-edge-flow" style="animation-delay: 0.2s"></div></div>
    </div>
    <div class="gbt-node json">
      <span class="gbt-node-icon">📄</span>
      <span>Manifest Json</span>
    </div>
  </div>

  <!-- Track 2: Schema Models Init -->
  <div class="gbt-pipeline">
    <div class="gbt-node schema">
      <span class="gbt-node-icon">🗂️</span>
      <span>Schema/Models<br>Init</span>
    </div>
    <div class="gbt-edge">
      <span class="gbt-edge-label">Parse & Link 🔗</span>
      <div class="gbt-edge-track"><div class="gbt-edge-flow"></div></div>
    </div>
    <div class="gbt-node loader">
      <span class="gbt-node-icon">🛠️</span>
      <span>Schema/Models<br>Init Loader</span>
    </div>
    <div class="gbt-edge">
      <span class="gbt-edge-label">Load Models 🚀</span>
      <div class="gbt-edge-track"><div class="gbt-edge-flow" style="animation-delay: 0.2s"></div></div>
    </div>
    <div class="gbt-node json">
      <span class="gbt-node-icon">📄</span>
      <span>Manifest Json</span>
    </div>
  </div>
</div>

---

### Phase 1: Project Initialization Flow

This track focuses purely on digesting the environmental configuration and directory mappings so GBT natively understands how to navigate the workspace.

- **Project Init (`gbt_project.yaml`):** The absolute starting point. The workflow discovers the foundational configuration file situated at the root of your workspace.
- **Project Init Engine Loader (`ProjectLoader`):** The engine reads the raw YAML data, safely applies strict Pydantic model validation, and directly resolves crucial directory coordinates (e.g., scoping exactly where the `models/` or `target/` folders physically reside).
- **Manifest Json:** Integrated structural contexts and environment scopes mapped by the Loader are channeled actively to become the foundational blueprint of the generated `manifest.json`.

### Phase 2: Schema & Models Initialization Flow

Mirroring the path variables discovered in Phase 1, the engine actively walks down the directory paths to process physical data mappings.

- **Schema/Models Init (`models/*.yml`):** The engine systematically targets structural schema files within the model directions to capture constraints, properties, and entity labels.
- **Schema/Models Init Loader (`ManifestLoader` & `JinjaParser`):** It classifies all extracted models and forcefully links them onto their operational `.sql` or `.cypher` scripts via naming conventions. During this stage, the embedded `JinjaParser` dynamically evaluates and strips out native configuration macros (like `{{ config(...) }}`) to return purely executable strings.
- **Manifest Json:** Every schema property, table relationships, validation rules, and completely compiled query sets are heavily aggregated into dictionaries and written persistently into the absolute `target/manifest/manifest.json`.

> **Ultimate Goal:** Standardize both Global Project Settings and decoupled Schema Models into a single unified JSON block on the disk. Moving forward, during `--run` workflows, the `Core Engine` accesses this specific `manifest.json` exclusively, ensuring lightning-fast execution by preventing the need for repetitive local re-parsing.

---

## Architectural Data Flow Summary

To summarize structurally, GBT acts as a compiler translating YAML and SQL scripts cleanly into a single Source of Truth JSON node.

| Stage | Action Trigger | Artifact Target | Result Produced |
| :--- | :--- | :--- | :--- |
| **Project Parsing** | Locates Global Settings | `gbt_project.yaml` | `GbtProjectConfig Object` |
| **Model Registration** | Scans Schema Properties | `models/**/schema_*.yml` | `Dictionary array of models` |
| **Script Linking** | Links structure with queries | `.sql`, `.cypher`, `.txt` | `Compiled Scripts + Active Connectors` |
| **Manifest Loading** | Aggregates all parsed objects | `target/manifest/manifest.json` | **The Absolute Source of Truth** |
