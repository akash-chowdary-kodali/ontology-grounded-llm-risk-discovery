from rdflib import Graph, RDF, RDFS, OWL, URIRef
from rdflib.namespace import XSD


ONTOLOGY_PATH = "Project-2/Corner Case Ontology for Autonomous Driving.ttl"
ONTOLOGY_NS = "http://cecs571.csulb.edu/ontology/cornercase#"


def _local_name(uri):
    s = str(uri)
    if "#" in s:
        return s.split("#")[-1]
    return s.rsplit("/", 1)[-1]


def parse_ontology(path=ONTOLOGY_PATH):
    g = Graph()
    g.parse(path, format="turtle")

    classes = {}
    for cls in g.subjects(RDF.type, OWL.Class):
        if isinstance(cls, URIRef) and str(cls).startswith(ONTOLOGY_NS):
            name = _local_name(cls)
            label = next(g.objects(cls, RDFS.label), None)
            comment = next(g.objects(cls, RDFS.comment), None)
            parents = [
                _local_name(p) for p in g.objects(cls, RDFS.subClassOf)
                if isinstance(p, URIRef) and str(p).startswith(ONTOLOGY_NS)
            ]
            classes[name] = {
                "label": str(label) if label else name,
                "comment": str(comment) if comment else "",
                "parents": parents,
            }

    object_properties = _parse_properties(g, OWL.ObjectProperty)
    data_properties = _parse_properties(g, OWL.DatatypeProperty, datatype=True)

    return {
        "classes": classes,
        "object_properties": object_properties,
        "data_properties": data_properties,
    }


def _parse_properties(g, prop_type, datatype=False):
    props = {}
    for p in g.subjects(RDF.type, prop_type):
        if not (isinstance(p, URIRef) and str(p).startswith(ONTOLOGY_NS)):
            continue
        name = _local_name(p)
        label = next(g.objects(p, RDFS.label), None)
        comment = next(g.objects(p, RDFS.comment), None)
        domains = [_local_name(d) for d in g.objects(p, RDFS.domain) if isinstance(d, URIRef)]
        ranges = [
            (str(r) if datatype and str(r).startswith(str(XSD)) else _local_name(r))
            for r in g.objects(p, RDFS.range) if isinstance(r, URIRef)
        ]
        props[name] = {
            "label": str(label) if label else name,
            "comment": str(comment) if comment else "",
            "domain": domains,
            "range": ranges,
        }
    return props


def format_for_prompt(ontology):
    lines = []
    lines.append("ONTOLOGY VOCABULARY (use ONLY these terms in RDF output):")
    lines.append("")
    lines.append("CLASSES (with hierarchy):")
    roots = [n for n, d in ontology["classes"].items() if not d["parents"]]
    for root in sorted(roots):
        _render_class(root, ontology["classes"], lines, depth=0)

    lines.append("")
    lines.append("OBJECT PROPERTIES (subject -> predicate -> object):")
    for name, d in sorted(ontology["object_properties"].items()):
        dom = ", ".join(d["domain"]) or "?"
        rng = ", ".join(d["range"]) or "?"
        lines.append(f"  - {name}: {dom} -> {rng}")

    lines.append("")
    lines.append("DATA PROPERTIES (subject -> predicate -> literal):")
    for name, d in sorted(ontology["data_properties"].items()):
        dom = ", ".join(d["domain"]) or "Any"
        rng = ", ".join(d["range"]) or "string"
        lines.append(f"  - {name}: {dom} -> {rng}")

    return "\n".join(lines)


def _render_class(name, classes, lines, depth):
    info = classes.get(name, {})
    label = info.get("label", name)
    indent = "  " * depth
    lines.append(f"{indent}- {name} ({label})")
    children = sorted([n for n, d in classes.items() if name in d["parents"]])
    for c in children:
        _render_class(c, classes, lines, depth + 1)


if __name__ == "__main__":
    onto = parse_ontology()
    print(f"Classes: {len(onto['classes'])}")
    print(f"Object properties: {len(onto['object_properties'])}")
    print(f"Data properties: {len(onto['data_properties'])}")
    print()
    print(format_for_prompt(onto))
