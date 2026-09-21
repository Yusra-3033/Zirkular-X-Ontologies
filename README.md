# Digital Product Passports for Building Services in Existing Buildings Using DPPO Ontology

Application of the **Digital Product Passport Ontology (DPPO 0.1)** to the German
research project **ZIRKULAR-X**: a modular extension for building-services (HVAC)
products in existing buildings, a fully worked demo passport for an air handling
unit, and reproducible SPARQL competency-question queries.

> DPPO is developed by Jansen et al. See: (https://github.com/LiUSemWeb/DPPO).

![DPPO 0.1 module structure] ()
---

## 1. Why a Digital Product Passport, and why an ontology?

The EU Ecodesign for Sustainable Products Regulation (ESPR, Regulation (EU)
2024/1781) introduces the Digital Product Passport (DPP) as a mandatory
instrument. In July 2026 the European Commission published the references of six
harmonised DPP system standards (Implementing Decision (EU) 2026/1736), among
them **EN 18219:2026 (unique identifiers)** and **EN 18220:2026 (data
carriers)**. For construction products, the new Construction Products Regulation
(EU) 2024/3110 adds its own passport requirements.

ZIRKULAR-X targets a hard variant of this problem: passports for products that
are **already installed in existing buildings**, where documentation is
incomplete, identifiers are legacy codes, and information is collected
incrementally by different actors over decades. That calls for a data model in
which every single piece of information is:

- attributable (*who* recorded it),
- dated (*when* it was recorded),
- typed and referenced to a defined characteristic (*what* it means),
- and separable from unverified claims (*stored text is not evidence*).

An ontology-based knowledge graph provides exactly this, and DPPO's generic
statement pattern (`dpp-info:DPPInformation` + value + unit + provenance) fits
the incremental-capture scenario better than a fixed schema.

## 2. What DPPO provides

DPPO 0.1 is a small, modular ontology network (26 classes, 20 object
properties, 6 datatype properties across five modules):

| Module | Role in this project |
|---|---|
| `dpp-odp` | Core pattern: a `DPP` `describes` a `Product`; products decompose via `hasPart` |
| `dpp-core` | Product types (Component, Material, Substance, ConsumerProduct) and their passport types |
| `dpp-info` | The information pattern: passport contents as individual statements with `value`, `unit`, validity and versioning |
| `dpp-comp` | Composition: `aboutWhole` / `aboutPart` relations and substance classes |
| `dpp-prov` | Actors and accountability: `dppOwner`, `responsibleActor`, `creationTimeStamp` |

The five module files are vendored unmodified in [`dppo/`](dppo/).

## 3. The ZIRKULAR-X extension

DPPO deliberately contains no building or HVAC domain knowledge. The extension
follows a strict three-layer architecture (see
[docs/zx_extension_architecture.svg](docs/zx_extension_architecture.svg)):

```
DPPO 0.1 (5 reused modules)   <--- zx-dppo-conn.ttl --->   zx-core.ttl
        unchanged                  alignment only           domain model
```

**[`ontology/zx-core.ttl`](ontology/zx-core.ttl)** — the domain model, usable on
its own:

- Product classes: `zx:BuildingProduct`, `zx:VentilationUnit`, `zx:Fan`.
  A fan is **not** a subclass of the ventilation unit; the part-of relation
  holds between *instances* via `dpp-odp:hasPart`.
- Identification (EN 18219 context): `zx:Identifier` with `identifierValue`,
  `legacyIdentifierValue` and `granularity` (item / model / batch), attached to
  the **product** via `zx:hasIdentifier`; the passport carries
  `zx:uniqueProductIdentifier` and `zx:dppStatus`.
- A statement hierarchy: `zx:Statement` with `ParameterStatement`,
  `MaterialStatement`, `ClassificationStatement`, `LifeCycleEventStatement`,
  plus `zx:elementId` as a stable key that links statements to CQ IDs and
  parameter-list rows.

**[`ontology/zx-dppo-conn.ttl`](ontology/zx-dppo-conn.ttl)** — the connector.
All alignment axioms live here and nowhere else:

| ZIRKULAR-X term | aligned to DPPO |
|---|---|
| `zx:BuildingProduct` | `rdfs:subClassOf dpp-core:Component` |
| `zx:Statement` | `rdfs:subClassOf dpp-info:DPPInformation` |
| `zx:ParameterStatement` | `rdfs:subClassOf dpp-info:ProductCharacteristic` |
| `zx:MaterialStatement` | `rdfs:subClassOf dpp-info:CompositionInformation` |

Import strategy: the connector imports `odp`, `core`, `info` and `prov`, but
**deliberately not `comp`** — the published comp module references versioned
`dpp-info/0.1/` IRIs, which breaks a mixed unversioned import closure. The demo
still uses `dpp-comp:aboutWhole` / `aboutPart`; for reasoning or validation over
comp terms, load `dppo/dpp-comp.ttl` explicitly and keep the version deviation
documented rather than silently normalised.

Why subclassing instead of equivalence? It keeps the extension conservative:
every ZIRKULAR-X statement *is* a DPPO information item (so all DPPO tooling,
queries and future SHACL shapes written against `dpp-info:DPPInformation`
apply), while DPPO itself remains untouched and upgradeable.

## 4. The demo: passport of an existing air handling unit

[`examples/demo.ttl`](examples/demo.ttl) models **RLT-01**, a ventilation unit
manufactured in 1998, with one documented component (a fan) and 15 passport
statements. It shows the full pattern end to end (see
[docs/statement_pattern.svg](docs/statement_pattern.svg)):

```
ex:dpp-rlt-01 (dpp-odp:DPP)
  ├─ dpp-odp:describes ─────────────► ex:rlt-01 (zx:VentilationUnit)
  │                                     ├─ dpp-odp:hasPart ► ex:fan-01 (zx:Fan)
  │                                     └─ zx:hasIdentifier ► ex:id-rlt-01
  │                                          value, legacy "RLT-1998-0042", granularity: item
  ├─ dpp-prov:dppOwner ─────────────► ex:muster-gmbh
  └─ dpp-info:containsInformation ──► 15 statements, e.g.:

ex:st-airflow (zx:ParameterStatement)
  dpp-info:isAbout          ex:rlt-01
  dpp-info:characteristic   zxd:AirflowRate      # dictionary reference
  dpp-info:value            5000.0               # unit intentionally absent!
  zx:elementId              "rlt-01.airflow.1"
  dpp-prov:responsibleActor ex:facility-manager
  dpp-prov:creationTimeStamp "2026-09-10T08:31:00Z"
```

Deliberate modelling decisions, visible in the data:

1. **Every statement is attributable.** All 15 statements carry
   `responsibleActor` and `creationTimeStamp`. (Queries verify: none is
   missing either.)
2. **Material composition is checkable.** Six `zx:MaterialStatement`s connect
   the unit (`aboutWhole`) to material individuals (`aboutPart`) with explicit
   `unit:PERCENT` values: 68 + 14 + 3 + 9 + 4 + 2 = 100. Derived masses
   (578 kg steel at 850 kg total) are *calculations*, not stored triples.
3. **Gaps stay visible.** The airflow value 5000.0 has **no unit triple** —
   a real, documented gap in the captured data. Queries use
   `OPTIONAL { ?st dpp-info:unit ?unit }` so the gap shows up as an unbound
   variable instead of a silently dropped row.
4. **Claims are not evidence.** The substance classification
   ("Keine Gefahrstoffe; REACH/RoHS-konform") is modelled as a
   `zx:ClassificationStatement` with an explicit note that no evidence
   document is attached. It must not be read as verified conformity.
5. **Events belong to the right subject.** Production (1998-04-30) is about
   the unit; the disassembly (2019-03-11) is about the **fan** and is reached
   from the unit only via `hasPart`.
6. **Percent semantics.** `0.1 unit:PERCENT` for recycled content means
   0.1 %, not 10 %.
7. **Dictionary references.** `zxd:` characteristic IRIs point to the project
   dictionary (ISO 23386 / ISOProps alignment); the definitions are maintained
   separately and are not part of this repository yet.

All identifiers, company names and URLs in the demo are fictitious.

## 5. Competency-question queries

Three CQs, chosen so that together they touch every reused module — see
[`queries/README.md`](queries/README.md) for the queries with their actual
results:

- **CQ-A — material composition** (`dpp-comp` + `dpp-info`): materials and
  shares of RLT-01, ordered by share.
- **CQ-B — life-cycle events including components** (`dpp-odp:hasPart+`):
  finds the fan's disassembly through the decomposition path.
- **CQ-C — traceable characteristics** (`dpp-info` + `dpp-prov`): value,
  optional unit, responsible actor and timestamp per parameter; exposes the
  missing airflow unit.

Run everything locally (no triple store needed):

```bash
pip install rdflib
python scripts/run_queries.py
```

## 6. Loading the network into GraphDB

1. Create a repository (e.g. `zirkular-x-dppo`; ruleset "RDFS-Plus (optimized)"
   is enough for the subclass alignment to take effect).
2. *Import → Server files / Upload RDF files*: upload all **eight** Turtle
   files — the five files in `dppo/`, the two in `ontology/`, and
   `examples/demo.ttl`. Import into the default graph (or one named graph per
   file if you want per-file provenance).
3. Open *SPARQL* and paste any query from `queries/`.
4. With RDFS reasoning enabled, `?st a dpp-info:DPPInformation` also returns
   the ZIRKULAR-X statements — that is the connector doing its job.
5. *Explore → Visual graph* on `ex:dpp-rlt-01` renders the passport
   neighbourhood (passport → product → part, statements, actors).

Note on `owl:imports`: GraphDB does not automatically resolve imports on file
upload, which is why all eight files are uploaded explicitly. This also keeps
the offline setup fully reproducible.

## 7. Repository layout

```
├── dppo/                  DPPO 0.1 modules, unmodified (CC BY 4.0, see NOTICE.md)
├── ontology/
│   ├── zx-core.ttl        ZIRKULAR-X domain extension (HVAC in existing buildings)
│   └── zx-dppo-conn.ttl   alignment to DPPO (imports; subclass axioms only)
├── examples/
│   └── demo.ttl           RLT-01 demo passport (15 statements)
├── queries/               3 CQ queries + documented results
├── scripts/run_queries.py rdflib runner
├── docs/                  diagrams (SVG editable, PNG for viewing)
├── NOTICE.md              DPPO attribution
└── LICENSE                CC BY 4.0
```

## 8. Status, known gaps and roadmap

This repository is a **small, verifiable working state**, not the finished
project model. Open points, in priority order:

- add the missing `dpp-info:unit` for the airflow statement (m³/h) once the
  source is confirmed;
- assert an explicit manufacturer role relation (currently only a passport
  owner is present);
- data carrier / resolver modelling (EN 18220) and building-topology links;
- publish the `zxd:` dictionary with ISO 23386 / ISOProps property
  definitions, datatypes and units;
- SHACL shapes for mandatory-field validation (subclassing enables shapes
  written against DPPO classes, but OWL alone does not enforce them);
- extend the ABox (further components and parameters) and run the full
  project CQ suite against it.

## 9. How to cite / contact

ZIRKULAR-X, work package 2 "Semantic Data Platform", Ruhr University Bochum,
Chair of Computing in Engineering, and project partners. 
For DPPO itself, cite Jansen et al. (see [NOTICE.md](NOTICE.md) and
https://liusemweb.github.io/DPPO/).
