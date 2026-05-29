# Core Engine Architecture

<style>
  /* Global Pipeline CSS */
  .gbt-pipeline {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 2rem 0;
    padding: 1.5rem 1rem;
    background: var(--md-default-bg-color, #ffffff);
    border: 1px solid var(--md-default-fg-color--lightest, #e0e0e0);
    border-radius: 12px;
    overflow-x: auto;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
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
    width: 105px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    z-index: 2;
    font-size: 0.75rem;
    line-height: 1.2;
  }
  .gbt-node-icon { font-size: 1.5rem; margin-bottom: 0.3rem; }
  
  .gbt-edge {
    flex: 1 1 85px;
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
    min-width: 85px;
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
    animation: data-stream-flow 1.2s infinite linear;
  }
  @keyframes data-stream-flow {
    0% { left: -50%; }
    100% { left: 100%; }
  }
  
  /* Append Nodes */
  .gbt-node.trino { background: linear-gradient(135deg, #1e88e5, #0d47a1); }
  .gbt-node.append { background: linear-gradient(135deg, #fb8c00, #e65100); }
  .gbt-node.valid { background: linear-gradient(135deg, #e53935, #b71c1c); }
  .gbt-node.clean { background: linear-gradient(135deg, #43a047, #1b5e20); }
  .gbt-node.neo4j { background: linear-gradient(135deg, #8e24aa, #4a148c); }
  
  /* Delete Nodes & Flow */
  .delete-flow { background: linear-gradient(90deg, transparent, #ef5350, #b71c1c, transparent) !important; }
  .gbt-node.request { background: linear-gradient(135deg, #546e7a, #263238); }
  .gbt-node.parse { background: linear-gradient(135deg, #8d6e63, #4e342e); }
  .gbt-node.compile { background: linear-gradient(135deg, #ef5350, #c62828); }
</style>

The **Core Engine** is the computational heart of GBT. It efficiently moves data from your analytical storage to your target Graph Database. 

To ensure high performance, memory safety, and stability, the architecture is strictly decoupled into two components:

1. **Source Engine:** Extracts data.
2. **Destination Engine:** Loads data and manages the schema.

---

## 1. Source Engine (Data Extraction)

The **Source Engine** acts as the bridge to upstream analytical data. It manages connection states, executes SQL extraction queries, and yields data records continuously to the downstream pipeline. 

### The Trino Adapter

*Managed by:* `TrinoSourceAdapter`

GBT currently utilizes **Trino** as its primary extraction layer. The Trino Adapter bridges your declarative SQL model scripts (enhanced with Jinja) directly to the Trino distributed SQL engine. 

#### The Extraction Workflow

Data extraction in GBT is structured as a highly deterministic pipeline to ensure low latency and zero memory bottlenecks:

- **Step 1: Parse & Compile Context**<br>The engine reads your `.sql` file, parsing Jinja macros to compile the raw script into valid Trino SQL syntax. It verifies metadata (like ensuring the `connector` is strictly defined as `trino`).
- **Step 2: Connect & Execute**<br>It establishes a secure session with the Trino server (via `TrinoConnector`) and pushes the compiled query.
- **Step 3: Stream via Yield (Micro-batches)**<br>Rather than downloading the entire dataset into memory at once, the engine streams data in chunks. Utilizing iterative cursor fetching (`cursor.fetchmany()`) paired with native Python generators (`yield`), the payload is transmitted to the Destination Engine micro-batch by micro-batch.
- **Step 4: Dynamic Field Mapping**<br>Throughout the yielding process, the adapter inspects the cursor's column descriptions. It dynamically maps SQL column names directly to their row values, producing clean, structured Python dictionaries automatically.

> **Memory & Performance Note:**
> By default, the `batch_size` is configured to `1000`. This ensures that even when extraction queries encompass millions of rows, GBT strictly retains a maximum of 1,000 records in physical RAM at any exact microsecond, preventing Out-Of-Memory (OOM) failures.
>
> *(Additionally, the adapter provides a `count_total()` utility which silently wraps your query in a `SELECT count(*)` shell to calibrate progress bars before execution begins).*

#### Essential Configurations

To instruct the Source Engine on how to execute your model properly, your `.sql` files must declare specific Jinja configurations:

| Macro | Description | Requirement |
| :--- | :--- | :--- |
| `config(connector = 'trino')` | Declares the intended upstream extraction connector. The adapter validates this during the compile phase to prevent misrouted queries. | **Required** |
| `source('catalog', 'schema', 'table')` | Resolves the exact data source path to query within your Trino data warehouse / data lake. | **Required** |

**Example: Source Configuration & Extraction**

*Source Model Script (`models/neo4j/nodes/customer.sql`)*
```sql
{{ config(connector = 'trino') }}

SELECT 
    customer_id, 
    full_name, 
    email_address
FROM {{ source('crt_tdc', 'ns_tdc_customer_backend_public', 'customer') }}
WHERE status = 'ACTIVE'
```

*Execution Result:* The Source Engine compiles the query, submits it to Trino, and begins yielding dynamic batches of dictionaries:
```json
[
  { "customer_id": 1, "full_name": "John Doe", "email_address": "john.doe@ex.com" },
  { "customer_id": 2, "full_name": "Jane Smith", "email_address": "jane.smith@ex.com" }
]
```

---

## 2. Destination Engine (Data Loading & Schema)

The **Destination Engine** translates GBT's internal logic into native backend commands. 

**Core Responsibilities:**
- Execute schema definitions.
- Perform metadata checks.
- Safely mutate data against the Graph runtime.

### The Neo4j Adapter

Engineered specifically for the `bolt` protocol, the Neo4j Adapter manages the destination data lifecycle through a strict, three-stage execution pipeline. This architecture ensures that graph structural integrity is always prioritized before any physical data is transmitted.

#### Stage 1: System Meta Inspection

*Managed by:* `InspectorEngine`

Before mutating or defining any graph data, the engine actively surveys the existing database state. Graph databases often auto-generate complex hashes for internal constraints and indexes. Modifying these without prior reconnaissance can lead to orphaned artifacts or fatal execution collisions.

- **Step 1: Intelligent Scanning**<br>The engine queries internal system parameters (e.g., executing `SHOW CONSTRAINTS`) to map existing physical rules. It cross-references current graph labels and properties against the target topology.
- **Step 2: Metadata Routing**<br>It feeds this live reconnaissance mapping forward into GBT's internal state. This guarantees that subsequent operations—such as targeted full-refresh clean-ups—can accurately construct precise `DROP` commands using actual system-generated names, rather than attempting blind overwrite operations.

#### Stage 2: Schema Definition [DDL]

*Managed by:* `SchemaBuilderEngine`

This stage constructs the strict structural boundaries of the Graph explicitly before any records are inserted. Handling DDL at this stage ensures that database-level protections (like `IS UNIQUE` or `NOT NULL`) are locked in place, providing an unbreachable defense against downstream data anomalies.

- **Step 1: Extract**<br>The engine parses the `properties` map from your compiled YAML models. It systematically identifies all explicitly declared graph constraints assigned to specific node labels or relationship types.
- **Step 2: Compile**<br>It translates these declarative YAML rules into native Cypher DDL scripts. GBT leverages tailored Jinja templates to generate highly optimized structural definitions that Neo4j natively understands.
- **Step 3: Execute**<br>Finally, the engine deploys these compiled definitions directly into the Neo4j runtime, awaiting confirmation before advancing the pipeline.

**Example: Schema Definition Pipeline**

*Input Config (`schema_customer.yml`):*
```yaml
models:
  label: customer
  type: node
  properties:
    - name: customer_id
      data_type: string
      constraints:
        - IS UNIQUE
```

*Output Cypher:* 
```cypher
CREATE CONSTRAINT constraint_node_customer_customer_id_is_unique 
FOR (n:customer) 
REQUIRE n.customer_id IS UNIQUE;
```

#### Stage 3: Data Manipulation [DML]

*Managed by:* `AppendEngine` & `DeleteEngine`

The final stage of the data pipeline is Data Manipulation. The ultimate goal of this stage is to execute the injection of new data or the surgical removal of obsolete records with high precision, capable of processing millions of records at high speed without creating system memory bottlenecks.

**The Append Workflow**

*Managed by:* `AppendEngine`

In Graph Theory, Vertices (Nodes) and Edges (Relationships) possess fundamentally different natures. Consequently, the `AppendEngine` demands strictly defined configuration boundaries to ensure data is precisely routed.

**1. Configuration Boundaries**

| Graph Primitive     | Configuration Requirements |
|:--------------------| :--- |
| **Nodes**           | Requires only basic configuration: target `label` and a list of local `properties`. |
| **Relationships** | More complex. Requires 3 core elements:<br>1. `physical_name`: The physical name of the edge (e.g., `PURCHASED`).<br>2. `properties`: The attributes of the relationship.<br>3. **Directional Mapping**: Explicitly defined `source_node` and `target_node`, which must specify:<br> - `label`: The node label to scan in Neo4j.<br> - `key`: The primary lookup key on Neo4j.<br> - `ref`: The corresponding reference column from the incoming input payload. |

> **Example: Relationship Directional Mapping**
> ```yaml
> source_node:
>   label: customer       # Label on Neo4j
>   key: gid              # Primary key on Neo4j
>   ref: buyer_gid        # Corresponding column from Trino incoming data
> ```

**The Streaming Pipeline**

To guarantee high scalability and prevent graph fragmentation, records are injected into Neo4j through a strictly ordered streaming data pipeline:

<div class="gbt-pipeline">
  <div class="gbt-node trino">
    <span class="gbt-node-icon">🗄️</span>
    <span>Trino Source</span>
  </div>
  <div class="gbt-edge">
    <span class="gbt-edge-label">Yields Batch 📄</span>
    <div class="gbt-edge-track"><div class="gbt-edge-flow"></div></div>
  </div>
  <div class="gbt-node append">
    <span class="gbt-node-icon">⚙️</span>
    <span>Append Engine</span>
  </div>
  <div class="gbt-edge">
    <span class="gbt-edge-label">1000 Rows 📦</span>
    <div class="gbt-edge-track"><div class="gbt-edge-flow" style="animation-delay: 0.2s"></div></div>
  </div>
  <div class="gbt-node valid">
    <span class="gbt-node-icon">🛡️</span>
    <span>Validator</span>
  </div>
  <div class="gbt-edge">
    <span class="gbt-edge-label">Cast & Filter 🧹</span>
    <div class="gbt-edge-track"><div class="gbt-edge-flow" style="animation-delay: 0.4s"></div></div>
  </div>
  <div class="gbt-node clean">
    <span class="gbt-node-icon">✨</span>
    <span>Clean Array</span>
  </div>
  <div class="gbt-edge">
    <span class="gbt-edge-label">UNWIND 🚀</span>
    <div class="gbt-edge-track"><div class="gbt-edge-flow" style="animation-delay: 0.6s"></div></div>
  </div>
  <div class="gbt-node neo4j">
    <span class="gbt-node-icon">🎯</span>
    <span>Neo4j Dest</span>
  </div>
</div>

The data injection process follows a standardized 3-step routine:

- **Step 1: Receive**<br>Instead of loading millions of rows into RAM simultaneously, the `AppendEngine` acts as a buffer. It continuously receives micro-batches (defaulting to 1000 rows/batch) smoothly yielded by the Source Engine's generator mechanism.

- **Step 2: Validate**<br>Immediately upon receiving a Raw Batch, the data is forced through the `ValidationManager`—the ultimate gatekeeper of the Framework. Here, crucial operations occur:
  - *Data Contract Enforcement:* Executes physical memory type-casting (e.g., ensuring the string `"10"` is properly cast to an integer `10` in Python).
  - *Schema Error Isolation:* Intelligently detects corrupted rows and handles them according to configured severity (e.g., `on_schema_error: skip_row` will silently discard erroneous rows to protect the rest of the batch).
  *(For a deeper dive into this mechanism, refer to the [Validation & Contracts](validation/overview.md) documentation).*

- **Step 3: Inject**<br>Fully sanitized batch arrays are fired directly into Neo4j. Instead of suffering the brutal network latency of executing thousands of individual `CREATE` or `MERGE` statements, GBT capitalizes on Cypher's `UNWIND` optimization. It encapsulates the entire data array into a single Parameterized Bulk-Write query, forcing the Neo4j server's CPU to unpack and process the data at maximum velocity.

**The Wipe & Refresh Workflow**

*Managed by:* `DeleteEngine`

When data models undergo heavy structural changes or complete reloads, standard incremental appending is insufficient. The `DeleteEngine` handles the surgical removal of data and schemas, triggering primarily during `--full-refresh` pipeline executions.

**1. Supported Deletion Targets**

Because graph databases interconnect data intrinsically, blindly deleting objects can cause fatal collisions. The `DeleteEngine` intelligently targets four distinct graph entities:

| Target Type      | Objective | Cypher Outcome (Under the hood) |
|:-----------------| :--- | :--- |
| **Node**         | Deletes all node records matching the model label, along with all their connected edges to prevent stranded lines. | `MATCH (n:customer) DETACH DELETE n;` |
| **Relationship** | Exclusively severs edge connections referencing the `physical_name` without harming the underlying operational nodes. | `MATCH ()-[r:PURCHASED]->() DELETE r;` |
| **Constraint**   | Drops targeted structural rules securely by utilizing the exact system-generated name discovered by the `InspectorEngine`. | `DROP CONSTRAINT constraint_name_is_unique IF EXISTS;` |
| **Label**      | Wipes any object universally bearing a specific label across the database. | `MATCH (n:label) DETACH DELETE n;` |

**2. The Deletion Pipeline**

Safe object removal demands a highly deterministic flow to avoid corrupting the graph state. 

<div class="gbt-pipeline">
  <div class="gbt-node request">
    <span class="gbt-node-icon">🗑️</span>
    <span>Init Request</span>
  </div>
  <div class="gbt-edge">
    <span class="gbt-edge-label">Target Entity 🏷️</span>
    <div class="gbt-edge-track"><div class="gbt-edge-flow delete-flow"></div></div>
  </div>
  <div class="gbt-node parse">
    <span class="gbt-node-icon">🗂️</span>
    <span>Parse Context</span>
  </div>
  <div class="gbt-edge">
    <span class="gbt-edge-label">Jinja Template 📜</span>
    <div class="gbt-edge-track"><div class="gbt-edge-flow delete-flow" style="animation-delay: 0.2s"></div></div>
  </div>
  <div class="gbt-node compile">
    <span class="gbt-node-icon">🔨</span>
    <span>Compile Cypher</span>
  </div>
  <div class="gbt-edge">
    <span class="gbt-edge-label">Drop Query 🧨</span>
    <div class="gbt-edge-track"><div class="gbt-edge-flow delete-flow" style="animation-delay: 0.4s"></div></div>
  </div>
  <div class="gbt-node neo4j">
    <span class="gbt-node-icon">💥</span>
    <span>Neo4j Dest</span>
  </div>
</div>

- **Step 1: Initialization**<br>The engine receives the deletion request explicitly defining the operational `object_type` (e.g., `node`, `relationship`, `constraint`) while opening a secure Neo4j connection.
- **Step 2: Context Parsing**<br>It extracts relational boundaries from the Manifest. If deleting a constraint, it requires the precise `constraint_name`. If removing a relationship, it scopes the target using the config's `physical_name`.
- **Step 3: Compile**<br>Depending on the isolated `object_type`, the engine routes the metadata into the appropriate Jinja template (e.g., `delete_relation.cypher.j2` or `delete_constraint.cypher.j2`) to render surgical Cypher code.
- **Step 4: Execute**<br>The forcefully compiled Cypher query is pushed to the Neo4j destination, neutralizing the target data or schema securely. This guarantees an absolutely pristine slate prior to re-entering the schema and append phases.
