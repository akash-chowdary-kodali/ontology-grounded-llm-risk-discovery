# Ontology Documentation Summary

**Ontology:** Corner Case Ontology for Autonomous Driving
**File:** `Corner Case Ontology for Autonomous Driving.ttl`
**Namespace:** `http://cecs571.csulb.edu/ontology/cornercase#`
**Author:** Akash Chowdary Kodali, CECS 571 Project 2

## Scope

The ontology includes self-driving corner cases: the scenes they appear in, the actors and obstacles in those scenes, the weather and lighting, the safety risks that come out of them, and the visible hints that a hazard is imminent. Other things that I did not model: vehicle dynamics, sensor models, route planning, traffic laws, and image-level boxes or masks.

## Key Classes

The ontology has 34 classes. The top class is `CornerCase`, and the three subclasses that the assignment requested are taken from the 3CSim paper:

- `StateAnomaly`: when an object is made to appear to be one thing when in reality it is another (such as a billboard that shows a STOP sign).
- `BehaviorAnomaly`: a thing on the road does something that you do not anticipate (a wrong-way driver, a police chase).
- `EvidenceBasedAnomaly`: an observable signal that a hazard is about to happen (a ball rolling into the road, a barrel falling off a truck).

The supporting classes are: `Actor` (with `Vehicle`, `Pedestrian`, `Cyclist` under it), `Obstacle` (with `RoadObject` under it), `Scene`, `Risk`, `SeverityScore`, `EvidenceIndicator`, `WeatherCondition`, `TrafficSign`, `TrafficLight`, `Billboard`.

## Key Properties

There are nine object properties: `hasActor`, `hasObstacle`, `hasWeatherCondition`, `hasRisk`, `hasSeverityScore`, `hasEvidence`, `occursInScene`, `indicatesPotentialRisk`, `hasCornerCaseType`. They all have a clear domain and range.

There are four datatype properties: `severityValue` (xsd:float on `SeverityScore`), `confidenceScore` (xsd:float on `Risk`), `description` (xsd:string), `scenarioName` (xsd:string on `Scene`).

Each class and each property has a label and a comment. That makes 48 labels and 48 comments in total.

## Major Modeling Decisions

1. I have given `CornerCase` as the sole top class, therefore all the scenes must fall into one of the three sub-types. It is what causes the output to be a real knowledge graph rather than free text.
2. I put each risk as a separate object with a separate severity rating, rather than simply slapping a number on the corner case. It is now possible for a tool to sort or filter risks without reading English.
3. I divide the cue and the risk that the cue is warning about, using `indicatesPotentialRisk`. The paper considers them a single entity. Separating them allows the same cue to point at different risks in different scenes.
4. I had `WeatherCondition` as a class hierarchy, not a string property. In such a manner, some future version will be able to mix subclasses (Day + Foggy) without changing the schema.
5. I made `SeverityScore` a separate class rather than a simple float field. That allows me to add additional things such as a confidence range or a source to a score later, without breaking older data.

## Extensions Out of the Paper

The three top types are listed and a brief list of side concepts is provided in the paper. I added them in more detail because I needed the ontology to fit the data. Each of them is recorded in the TTL with a comment which explains why it is there:

- **Subclasses of Risk:** `CollisionRisk` parent, with `PedestrianCollisionRisk` and `RearEndCollisionRisk` as sub-children. In addition to `OcclusionRisk`, `LaneIntrusionRisk`, `DistractionRisk`, `RoadConditionRisk`, `WeatherRisk`. The Project 1 ground truth labels these risks with the following names, and thus I needed to find ontology terms that coincide with these names.
- **Subclasses of evidence indicators:** `RollingBallIndicator`, `OpenDoorIndicator`, `FallingObjectIndicator`. The paper refers to rolling balls and falling objects in the text but leaves it at that.
- **Weather subclasses:** `ClearCondition`, `RainyCondition`, `FoggyCondition`, `DayCondition`, `NightCondition`. Required to ensure that the six weather × time mixes of the dataset are real ontology words and not strings.
- **Cyclist, Billboard, TrafficLight:** the paper lumps cyclists in with general actors and does not name billboards or traffic lights, but the dataset has UnpredictableBicycle, the StaticHighwayAd scenes, and BlinkingYellowIntersection.
- **Additions to datatypes:** `confidenceScore` on `Risk`, so the LLM can display the level of confidence it has. `scenarioName` on `Scene`, to be able to trace a scene to its dataset name.

## Reasoner Verification

Before exporting, I ran HermiT in Protégé. It worked through the class hierarchy, object property hierarchy, data property hierarchy, class assertions, object property assertions, and same-individuals checks in 85 ms. No mistakes and no inconsistencies. As a second check, I loaded the TTL into `rdflib` and ran an OWL RL closure with `owlrl`. The graph grew from 192 to 634 triples, and no `owl:Nothing` instances were found. No broken domain or range references either.
