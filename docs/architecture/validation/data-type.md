# Data Type Validation

Maintaining pristine data types is essential for Neo4j query performance and index optimization. The **Data Type Validation** module intercepts raw payloads fetched from Source SQLs and forcibly casts them into uniform, expected Python memory objects before injecting them downstream.

---

## 1. The Validation Pipeline

When the Source Engine yields a micro-batch of data, it routes through the `ValidationManager` via a deterministic 3-tier pipeline.

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
    background: linear-gradient(90deg, transparent, #e53935, #b71c1c, transparent);
    animation: valid-flow 1.2s infinite linear;
  }
  @keyframes valid-flow {
    0% { left: -50%; }
    100% { left: 100%; }
  }

  .gbt-node.start { background: linear-gradient(135deg, #5c6bc0, #37474f); }
  .gbt-node.caster { background: linear-gradient(135deg, #00897b, #004d40); }
  .gbt-node.strategy { background: linear-gradient(135deg, #e53935, #b71c1c); }
  .gbt-node.clean { background: linear-gradient(135deg, #43a047, #1b5e20); }
</style>

<div class="gbt-pipeline-container">
  <div class="gbt-pipeline">
    <div class="gbt-node start">
      <span class="gbt-node-icon">📦</span>
      <span>Raw Batch</span>
    </div>
    <div class="gbt-edge">
      <span class="gbt-edge-label">Analyze Props ⚙️</span>
      <div class="gbt-edge-track"><div class="gbt-edge-flow"></div></div>
    </div>
    <div class="gbt-node caster">
      <span class="gbt-node-icon">🔄</span>
      <span>Type Caster</span>
    </div>
    <div class="gbt-edge">
      <span class="gbt-edge-label">Trap Errors 🛡️</span>
      <div class="gbt-edge-track"><div class="gbt-edge-flow" style="animation-delay: 0.2s"></div></div>
    </div>
    <div class="gbt-node strategy">
      <span class="gbt-node-icon">⚡</span>
      <span>Strategy Router</span>
    </div>
    <div class="gbt-edge">
      <span class="gbt-edge-label">Flush Data 🚀</span>
      <div class="gbt-edge-track"><div class="gbt-edge-flow" style="animation-delay: 0.4s"></div></div>
    </div>
    <div class="gbt-node clean">
      <span class="gbt-node-icon">✨</span>
      <span>Cleaned Array</span>
    </div>
  </div>
</div>

---

### Step 1: Payload Synchronization

*Managed by:* `ValidationManager`

The Engine immediately crosses the incoming raw dictionary fields against the strict `properties` defined in `models/**/*.yml`. 

- **Security Gate:** If a column exists in the data but is NOT declared in the model configuration, the Manager aggressively raises a `KeyError`. The framework enforces strict mappings to prevent random schema pollution.

### Step 2: Global Type Casting

*Managed by:* `TypeCaster`

Permitted properties are directed to the `TypeCaster` engine. This engine matches string definitions in YAML (e.g., `data_type: integer`) to physical Python operations.

| Supported Type (`YAML`) | Python Operator | Output Behavior Target |
| :--- | :--- | :--- |
| `string` | `str(...)` | Standard UTF-8 Text |
| `integer` | `int(...)` | Core numerical scalar |
| `float` | `float(...)` | Decimal precision numbers |
| `boolean` | `bool(...)` | True/False states |
| `date`, `datetime`, `timestamp` | `to_iso_format(...)` | Standardized ISO 8601 Strings compatible natively with Neo4j date functions. |

### Step 3: Error Strategy Routing

*Managed by:* `ValidationManager` & `BaseErrorStrategy`

What happens when `TypeCaster` tries to convert the string `"Not-a-Number"` into an `integer`? It inherently triggers a `ValueError`. The Validation Manager traps this Python exception and delegates authority to the **Schema Strategy Router**.

Based on the `on_schema_error` parameter globally configured in your `.yml` model settings, the system reacts systematically:

---

## 2. Configurable Error Strategies

GBT ensures that corrupted payloads do not destroy operational timelines blindly. We provide three tactical responses.

### 🔴 Fail Fast Strategy (`fail`)
**Objective:** The default behavior. Absolute paranoia. Halts pipeline immediately on the first conversion mistake.

- **How it works:** Whenever a cast fails, it immediately catches the underlying python exception and escalates it to a formatted, readable `DataTypeMismatchError`.
- **Use Case:** Financial data, crucial primary keys where data cleanliness is non-negotiable.

### 🟡 Nullify Strategy (`nullify`)
**Objective:** Passive tolerance. Drops the bad cell but saves the row.

- **How it works:** Catches the casting error, logs a runtime tactical warning, and actively returns `None` (Null in Neo4j) to the property cell while allowing the remainder of the row to be successfully flushed into the Graph Runtime.
- **Use Case:** Optional text descriptions, metadata tags, or incomplete source events.

### 🛡️ Skip Row Strategy (`skip_row`)
**Objective:** Cellular quarantine. Eliminates the affected row entirely without killing the entire 1000-row batch execution.

- **How it works:** Throws an internal `SkipRowException` which cleanly instructs the `ValidationManager` to eject that specific data row from the buffer and move straight to the next one.
- **Use Case:** Time-series events, click-streams, telemetry logs where volumetric speed overrides row-level completeness.

> **Example Configuration (`schema_customer.yml`):**
> ```yaml
> models:
>   label: customer
>   type: node
>   settings:
>     on_schema_error: skip_row
>   properties: ...
> ```
