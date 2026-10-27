def get_baseline_prompt():
    return """
You are an autonomous driving safety analyst.
Your task is to analyze the following scene images and produce a
semantic interpretation of the environment. The images represent
a potential corner case scenario.
Please perform the following tasks:
1. Identify the main entities in the scene
(vehicles, pedestrians, cyclists, road infrastructure,
obstacles, weather conditions).
2. Identify relationships between entities
(approaching, following, crossing, occluding, near).
3. Generate RDF triples describing the scene using Turtle
format.
4. Identify potential safety risks present in the scene
in RDF risk class.
5. Assign a severity score between 0 and 1 for each risk.
Return the results in the following format:
Scene Description in RDF Triples (Turtle Format)
Identified Risks for each risk class
Risk 1:
Description:
Severity Score:

"""


def get_grounded_prompt(ontology_summary):
    return f"""
You are an autonomous driving safety analyst working with a fixed OWL ontology.
Your task is to analyze the following scene images and produce a
semantic interpretation grounded in the ontology vocabulary below.

{ontology_summary}

STRICT RULES:
- Use ONLY the classes and properties listed in the vocabulary above.
- Do NOT invent new class names or property names.
- Every RDF subject/object that is a class instance must be typed with one of the listed classes.
- Every predicate must be one of the listed object or data properties.
- Use the prefix `:` declared below for all ontology terms.

Perform the following tasks:
1. Identify entities in the scene and type them using ontology Actor / Obstacle / TrafficSign / TrafficLight / Billboard / WeatherCondition subclasses.
2. Classify the corner case as one of: StateAnomaly, BehaviorAnomaly, EvidenceBasedAnomaly.
3. Generate RDF triples in Turtle format using the ontology vocabulary.
4. Identify potential safety risks using the Risk subclasses from the ontology.
5. Assign a severity score between 0.0 and 1.0 to each risk via SeverityScore + severityValue.

Required Turtle prefix declaration (include verbatim at top of RDF output):
@prefix : <http://cecs571.csulb.edu/ontology/cornercase#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

Example structure (follow this shape):
:scene1 a :Scene ;
    :scenarioName "ExampleScenario" ;
    :hasCornerCaseType :cc1 .
:cc1 a :StateAnomaly ;
    :hasActor :actor1 ;
    :hasWeatherCondition :weather1 ;
    :hasRisk :risk1 .
:actor1 a :Pedestrian .
:weather1 a :ClearCondition .
:risk1 a :PedestrianCollisionRisk ;
    :description "Pedestrian crossing in vehicle path" ;
    :hasSeverityScore :sev1 .
:sev1 a :SeverityScore ;
    :severityValue "0.85"^^xsd:float .

Return results in the following format:

Scene Description in RDF Triples (Turtle Format)
<your turtle here>

Identified Risks for each risk class
Risk 1:
Description:
Severity Score:

"""
