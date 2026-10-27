# Project 2: Ontology-Grounded LLM Risk Discovery for AD Corner Cases

**Akash Chowdary Kodali — CECS 571 Semantic Web Technologies**

## Approach

I took my Project 1 pipeline and added an ontology layer to it. The comparison is fair because of the identical dataset, identical models, and identical scoring code. Each of the 27 corner-case scenarios in 6 weather conditions is run twice on each model: once with the old Project 1 prompt (baseline), and once with a prompt that includes the vocabulary of the parsed ontology (grounded). That is 162 image groups × 3 models × 2 modes = 972 LLM calls, with 486 Turtle files per mode. The three models that I used are Gemini 3.1 Flash Lite Preview, GPT-4o-mini, and Pixtral-12B.

## Ontology Design

I created the ontology using the Protégé tool and stored it in Turtle. The highest-level class is `CornerCase`, and the three subtypes from the 3CSim paper are `StateAnomaly`, `BehaviorAnomaly`, and `EvidenceBasedAnomaly`. Around it I added the supporting classes that the dataset needed: `Actor` (with `Vehicle`, `Pedestrian`, `Cyclist` under it), `Obstacle` (with `RoadObject`), `Scene`, `Risk`, `SeverityScore`, `EvidenceIndicator`, `WeatherCondition`, `TrafficSign`, `TrafficLight`, and `Billboard`.

The dataset variants are not listed in the paper as fine-grained risks or indicators, so I added my own: `CollisionRisk` (with `PedestrianCollisionRisk` and `RearEndCollisionRisk` under it), `OcclusionRisk`, `LaneIntrusionRisk`, `DistractionRisk`, `RoadConditionRisk`, `WeatherRisk`, `RollingBallIndicator`, `OpenDoorIndicator`, `FallingObjectIndicator`, and weather subclasses for the dataset's variants. Final counts: 34 classes, 9 object properties, 4 datatype properties. Each class and property is labeled and commented. I ran HermiT and then exported the file, and it did not show any issues.

## Parser Design

The `ontology_parser.py` file contains the parser and is built on `rdflib`. It iterates over the `owl:Class`, `owl:ObjectProperty`, and `owl:DatatypeProperty` triples and extracts the name, parent, label, comment, domain, and range of each. `parse_ontology()` returns a Python dict, and `format_for_prompt()` turns that dict into a string ready to drop into a prompt: a numbered class list and a property list with domain → range arrows. I made sure that the counts are identical to the source ontology.

## Prompting Strategy

`prompt.py` has two builders. `get_baseline_prompt()` is the Project 1 prompt with no changes: no schema, no namespace hints. `get_grounded_prompt(ontology_summary)` adds five items on top: a required line with an `@prefix`, the entire list of classes with labels and comments, the entire list of properties with domain and range arrows, a clear rule that says use only terms from the ontology, and a small Turtle example that demonstrates the `Scene → CornerCase → Risk → SeverityScore` chain. Identical pictures, identical task wording, identical model settings on either side. The pipeline executes each scenario in both modes one after the other, so as not to give one side an unfair edge due to the time of day or rate-limit chance.

## Experimental Comparison

Grounding helped structure and precision, and it hurt recall. In all three models, the semantic consistency increased by 24× (0.028 to 0.669). RDF parse rate rose from 60.1% to 96.9%, and the average number of triples per file went from 15.5 to 28.4. The largest improvements were on the worst-baseline parsers: GPT-4o-mini went from 60% to 96%, Pixtral went from 24% to 94%, and Gemini reached 100%. Hallucinated `:Term` references per file dropped 39% (15.1 down to 9.2). Risk-discovery precision increased 45% (0.161 to 0.234), but recall decreased 41% (0.244 to 0.143) because the model now picks one risk subclass per scene rather than listing three. Net F1 dropped 14% on the keyword-overlap scoring I used in Project 1, and I think that is unjust to the grounded outputs because short correct answers lose points when they do not share words with the ground-truth phrasing. The entire comparison is summarized in Tables 1 and 2 below.

### Table 1. Ontology Summary

| Item | Count |
|---|---|
| Classes | 34 |
| Object properties | 9 |
| Datatype properties | 4 |
| `rdfs:label` annotations | 48 |
| `rdfs:comment` annotations | 48 |

### Table 2. Baseline vs Ontology-Grounded Comparison

| Dimension | Without Ontology | With Ontology | Improvement Observed |
|---|---|---|---|
| Semantic consistency | 0.028 | 0.669 | ×23.9. Outputs are written in actual ontology terms, rather than in placeholders |
| Risk accuracy (F1, avg of 3 models) | 0.173 | 0.149 | F1 -14%. Precision +45%, recall -41%. More specific yet less comprehensive |
| Hallucination rate | 0.839 (text), 15.1 terms/file | 0.766 (text), 9.2 terms/file | -8.7% text overlap, -39% hallucinated terms |
| RDF quality | 60.1% parse, 15.5 triples/file | 96.9% parse, 28.4 triples/file | +36.8 pp parse, +83% triples. Pixtral parse 23% → 94% |

### Table 3. Example Risk Comparison (representative scenarios, GPT-4o-mini)

| Scenario | Ground Truth Risk | Baseline Output | Ontology-Grounded Output |
|---|---|---|---|
| FallenTree | obstacle on road; collision risk; lane change risk; sudden braking risk | "Obstacle (tree) obstructing the path of vehicles"; "Potential collision risk between vehicles due to proximity to the tree" | "Obstruction on the roadway due to fallen tree" |
| FootballFollowedByBoy | pedestrian collision risk; unexpected obstacle; sudden braking risk | "Potential collision with the pedestrian crossing the road"; "Risk of not detecting the ball on the road" | "Risk of colliding with the crossing pedestrian" |
| BusObscuresCar | occlusion risk; collision risk; limited visibility | "The truck is occluding the view of the crossing vehicle"; "The taxi is following closely behind the pedestrian's path" | "Potential collision risk due to vehicles in close proximity"; "Driver distraction from noticeable billboards" |
| UnpredictableBicycle | cyclist collision risk; unexpected movement; lane intrusion | "Potential collision risk with a cyclist crossing in proximity to the vehicle"; "Reduced visibility due to distance and angle" | "Risk of collision due to cyclist position on road" |
| GreenLightOnSign | misleading signal; false traffic light; misidentification risk | "Potential distraction for the driver from advertisement billboards"; "Risk of misinterpretation of traffic light status" | "Potential collision risk due to vehicle crossing in pedestrian zone"; "Driver distraction from billboards" |

Full 27-scenario table and per-model splits are in the Results document.

## Conclusion

I believe grounding wins for any pipeline that wants a knowledge graph slice it can query. It compromises on a tool that requires the longest list of possible risks, since the ontology drives the model to select one type of risk per scene. The largest finding from this run is that grounding helps the weakest models the most: Pixtral went from giving me valid Turtle 24% of the time to giving me valid Turtle 94% of the time.

Three things I would do differently if I run this again. In place of the keyword-overlap scoring, use a meaning-based scorer so that short correct answers do not incur penalties. Balance the images-per-call across all three models so that Pixtral does not receive broken-up batches. Include some worked examples in the grounded prompt that show how a scene maps to an `:EvidenceIndicator` subclass, because those are the classes the models almost never used.
