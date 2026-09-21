#!/usr/bin/env python3
"""Load the full ontology network + demo ABox and run all CQ queries.

Usage:  python scripts/run_queries.py
Requires: rdflib  (pip install rdflib)
"""
from pathlib import Path
import rdflib

ROOT = Path(__file__).resolve().parent.parent
FILES = (sorted((ROOT / "dppo").glob("*.ttl"))
         + [ROOT / "ontology" / "zx-core.ttl",
            ROOT / "ontology" / "zx-dppo-conn.ttl",
            ROOT / "examples" / "demo.ttl"])

g = rdflib.Graph()
for f in FILES:
    g.parse(f, format="turtle")
print(f"Loaded {len(FILES)} files, {len(g)} triples\n")

for qf in sorted((ROOT / "queries").glob("*.rq")):
    print("=" * 70)
    print(qf.name)
    print("=" * 70)
    res = g.query(qf.read_text())
    header = [str(v) for v in res.vars]
    print(" | ".join(header))
    for row in res:
        print(" | ".join("-" if v is None else str(v) for v in row))
    print()
