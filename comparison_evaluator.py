"""
Part F comparison metrics: baseline vs grounded.
Reads outputs/rdf_baseline/ + outputs/rdf_grounded/ and computes:
  - semantic_consistency: % of unique terms used that exist in ontology
  - rdf_quality: triples parseable by rdflib, plus parse-success bool
  - grounding_fidelity: count of ontology classes/properties referenced
  - hallucinated_terms: ontology-prefixed terms NOT in ontology
"""

import os
import re
import json
from rdflib import Graph
from ontology_parser import parse_ontology, ONTOLOGY_NS

BASELINE_DIR = "outputs/rdf_baseline"
GROUNDED_DIR = "outputs/rdf_grounded"
RESULTS_PATH = "outputs/results/comparison_results.json"


def _ontology_vocab(onto):
    vocab = set(onto["classes"].keys())
    vocab.update(onto["object_properties"].keys())
    vocab.update(onto["data_properties"].keys())
    return vocab


def extract_ontology_terms(text):
    """Find tokens used as ontology terms (after `:` prefix or full IRI)."""
    if not text:
        return []
    terms = []
    # Prefixed form: :TermName
    terms.extend(re.findall(r'(?<![\w])(?<!:):([A-Za-z][A-Za-z0-9_]*)', text))
    # Full IRI form
    iri_re = re.escape(ONTOLOGY_NS) + r'([A-Za-z][A-Za-z0-9_]*)'
    terms.extend(re.findall(iri_re, text))
    return terms


def semantic_consistency(text, vocab):
    used = set(extract_ontology_terms(text))
    if not used:
        return {"used_terms": 0, "valid_terms": 0, "consistency": 0.0}
    valid = used & vocab
    return {
        "used_terms": len(used),
        "valid_terms": len(valid),
        "consistency": len(valid) / len(used)
    }


def grounding_fidelity(text, vocab):
    used = set(extract_ontology_terms(text))
    if not vocab:
        return 0.0
    overlap = used & vocab
    return {
        "ontology_terms_referenced": len(overlap),
        "ontology_total": len(vocab),
        "fidelity": len(overlap) / len(vocab)
    }


def hallucinated_terms(text, vocab):
    used = set(extract_ontology_terms(text))
    return sorted(used - vocab)


def rdf_quality(text):
    """Try parse RDF block(s) from text. Strip Turtle code fences if present."""
    if not text:
        return {"parseable": False, "triples": 0, "error": "empty"}

    # Extract code-fence blocks regardless of language tag (turtle, ttl, plaintext, etc.)
    blocks = re.findall(r"```[a-zA-Z0-9_-]*\s*\n?(.*?)```", text, re.DOTALL)
    if blocks:
        candidate = "\n".join(blocks)
    else:
        # No fences — strip prose preamble (before @prefix) and prose epilogue (Identified Risks etc.)
        idx = text.find("@prefix")
        candidate = text[idx:] if idx > 0 else text
        # Cut off trailing prose markers
        for marker in ["\nIdentified Risks", "\nRisk 1:", "\n### ", "\n## ", "\n**Risk"]:
            cut = candidate.find(marker)
            if cut > 0:
                candidate = candidate[:cut]

    # Ensure prefix declared so parse succeeds
    if "@prefix :" not in candidate:
        candidate = f"@prefix : <{ONTOLOGY_NS}> .\n@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n" + candidate

    g = Graph()
    try:
        g.parse(data=candidate, format="turtle")
        return {"parseable": True, "triples": len(g), "error": None}
    except Exception as e:
        return {"parseable": False, "triples": 0, "error": str(e)[:120]}


def evaluate_file(path, vocab):
    with open(path, "r") as f:
        text = f.read()
    return {
        "file": os.path.basename(path),
        "semantic_consistency": semantic_consistency(text, vocab),
        "grounding_fidelity": grounding_fidelity(text, vocab),
        "rdf_quality": rdf_quality(text),
        "hallucinated_terms": hallucinated_terms(text, vocab),
    }


def evaluate_dir(dirpath, vocab):
    results = []
    if not os.path.isdir(dirpath):
        return results
    for fname in sorted(os.listdir(dirpath)):
        if fname.endswith(".ttl"):
            results.append(evaluate_file(os.path.join(dirpath, fname), vocab))
    return results


def aggregate(results):
    if not results:
        return {}
    n = len(results)
    return {
        "n_files": n,
        "avg_semantic_consistency": sum(r["semantic_consistency"]["consistency"] for r in results) / n,
        "avg_grounding_fidelity": sum(r["grounding_fidelity"]["fidelity"] for r in results) / n,
        "parse_success_rate": sum(1 for r in results if r["rdf_quality"]["parseable"]) / n,
        "avg_triples": sum(r["rdf_quality"]["triples"] for r in results) / n,
        "avg_hallucinated_terms": sum(len(r["hallucinated_terms"]) for r in results) / n,
    }


def print_comparison(baseline_agg, grounded_agg):
    metrics = [
        ("Semantic Consistency", "avg_semantic_consistency", "{:.3f}"),
        ("Grounding Fidelity", "avg_grounding_fidelity", "{:.3f}"),
        ("RDF Parse Success", "parse_success_rate", "{:.2%}"),
        ("Avg Triples / file", "avg_triples", "{:.1f}"),
        ("Avg Hallucinated Terms", "avg_hallucinated_terms", "{:.2f}"),
    ]
    print("\n" + "="*70)
    print("Part F: Baseline vs Grounded — Aggregate Metrics")
    print("="*70)
    print(f"{'Metric':<28} {'Baseline':<15} {'Grounded':<15} {'Δ':<10}")
    print("-"*70)
    for label, key, fmt in metrics:
        b = baseline_agg.get(key, 0)
        g = grounded_agg.get(key, 0)
        delta = g - b
        print(f"{label:<28} {fmt.format(b):<15} {fmt.format(g):<15} {fmt.format(delta):<10}")


if __name__ == "__main__":
    onto = parse_ontology()
    vocab = _ontology_vocab(onto)
    print(f"Ontology vocab size: {len(vocab)}")

    baseline = evaluate_dir(BASELINE_DIR, vocab)
    grounded = evaluate_dir(GROUNDED_DIR, vocab)

    baseline_agg = aggregate(baseline)
    grounded_agg = aggregate(grounded)

    out = {
        "vocab_size": len(vocab),
        "baseline": {"per_file": baseline, "aggregate": baseline_agg},
        "grounded": {"per_file": grounded, "aggregate": grounded_agg},
    }
    os.makedirs("outputs/results", exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Per-file + aggregate written to {RESULTS_PATH}")

    print_comparison(baseline_agg, grounded_agg)
