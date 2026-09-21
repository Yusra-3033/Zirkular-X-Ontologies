# Competency-question queries

Three representative CQs, chosen so that together they exercise every
reused DPPO module plus the ZIRKULAR-X extension. Run them all with:

```bash
python scripts/run_queries.py
```

or paste them into the GraphDB SPARQL editor after loading the eight
Turtle files (see main README).

## CQ-A `cq1_material_composition.rq`
*What materials is the product composed of, and in what shares?*
Exercises: `dpp-comp` (aboutWhole/aboutPart), `dpp-info` (value/unit), `zx:MaterialStatement`.

Result on `examples/demo.ttl`:

| material | share | unit |
|---|---|---|
| Galvanised sheet steel | 68 | unit:PERCENT |
| Aluminium | 14 | unit:PERCENT |
| Mineral wool | 9 | unit:PERCENT |
| Plastics / elastomers | 4 | unit:PERCENT |
| Copper | 3 | unit:PERCENT |
| Electronics / power semiconductors | 2 | unit:PERCENT |

The shares sum to 100 %. Derived masses (e.g. 578 kg steel at 850 kg
total) are calculations on top of these triples, not stored data.

## CQ-B `cq2_lifecycle_events.rq`
*Which life-cycle events are documented for the product, including its
components?*
Exercises: `dpp-odp:hasPart+` (product decomposition), `zx:LifeCycleEventStatement`.

Result:

| subject | eventType | date |
|---|---|---|
| ex:rlt-01 | zx:production | 1998-04-30 |
| ex:fan-01 | zx:disassembly | 2019-03-11 |

Note that the disassembly belongs to the **fan**, not to the whole unit;
the query reaches it through the part-of path.

## CQ-C `cq3_traceable_characteristic.rq`
*For each characteristic: what is the value, its unit, who recorded it,
and when?*
Exercises: `dpp-info` (containsInformation, characteristic, value, unit),
`dpp-prov` (responsibleActor, creationTimeStamp), `zx:elementId`.

Result (6 rows): every parameter comes back with actor and timestamp.
The airflow row returns **no unit** — this is a documented gap in the
demo data, made visible by the `OPTIONAL { ?st dpp-info:unit ?unit }`
pattern. A mandatory join would have silently dropped the row.
