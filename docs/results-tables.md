# Project 2 Results — Tables and Per-Scenario Examples

Companion document to `report.md`. Contains the full per-model breakdown, the spec-form Table 2, the extended Table 2, the per-model RDF parse-rate split, and the 27-scenario Table 3.

## Table 2 (extended). Baseline vs Ontology-Grounded — Full Aggregate

| Metric | Without Ontology | With Ontology | Change |
|---|---|---|---|
| Semantic consistency | 0.028 | 0.669 | ×23.9 |
| Grounding fidelity | 0.031 | 0.376 | ×12.1 |
| RDF parse success | 60.1% | 96.9% | +36.8 pp |
| Avg triples per file | 15.5 | 28.4 | +83% |
| Avg hallucinated `:Term` per file | 15.1 | 9.2 | -39% |
| Risk discovery precision | 0.161 | 0.234 | +45% |
| Risk discovery recall | 0.244 | 0.143 | -41% |
| Risk discovery F1 | 0.173 | 0.149 | -14% |
| Hallucination rate (text overlap) | 0.839 | 0.766 | -8.7% |

## Table 2b. RDF Parse Success — Per Model

The aggregate parse rate hides the most interesting effect: grounding rescues the models that were worst at producing valid Turtle.

| Model | Baseline parse | Grounded parse | Δ |
|---|---|---|---|
| Gemini 3.1 Flash Lite Preview | 96.9% | 100.0% | +3.1 pp |
| GPT-4o-mini | 59.9% | 96.3% | +36.4 pp |
| Pixtral-12B | 23.5% | 94.4% | +70.9 pp |

## Per-Model Risk Discovery Breakdown

| Model | Mode | Precision | Recall | F1 | Hallucination | Risks/scene | Time/batch |
|---|---|---|---|---|---|---|---|
| Gemini 3.1 Flash Lite Preview | baseline | 0.234 | 0.215 | 0.219 | 0.766 | 2.98 | 26.0s |
| Gemini 3.1 Flash Lite Preview | grounded | 0.386 | 0.127 | 0.190 | 0.614 | 1.04 | 16.1s |
| GPT-4o-mini | baseline | 0.171 | 0.180 | 0.173 | 0.829 | 3.37 | 9.0s |
| GPT-4o-mini | grounded | 0.224 | 0.096 | 0.130 | 0.776 | 1.33 | 7.2s |
| Pixtral-12B | baseline | 0.078 | 0.337 | 0.126 | 0.922 | 13.44 | 10.9s |
| Pixtral-12B | grounded | 0.093 | 0.206 | 0.127 | 0.907 | 6.67 | 7.8s |

Across all three models, grounded mode raises precision and lowers hallucination, at the cost of recall.

## Table 3. Example Risk Comparison — All 27 Scenarios (GPT-4o-mini, DayClear)

Risks are quoted from the model's Turtle output. Truncated to the first two risks per cell for readability.

| Scenario | Ground Truth | Baseline | Grounded |
|---|---|---|---|
| AheadAndRightSign | misleading sign; confusing signage; collision risk | "Potential collision risk with pedestrians crossing the road as the car approaches"; "Risk of misjudgment of traffic signals or indicators at the intersection" | "Vehicle approaching intersection with unclear lane markings" |
| BlinkingYellowIntersection | intersection collision risk; unclear traffic signal; sudden braking risk | "Potential collision between red car and gold car at the intersection due to proximity and unclear traffic signal indications"; "Presence of vacant buildings along the road may distract drivers" | "Potential rear-end collision due to sudden stopping"; "Other vehicle encroaching into lane" |
| BusObscuresCar | occlusion risk; collision risk; limited visibility | "The truck is occluding the view of the crossing vehicle"; "The taxi is following closely behind the pedestrian's path" | "Potential collision risk due to vehicles in close proximity"; "Driver distraction from noticeable billboards" |
| BusStopNearPlayground | pedestrian collision risk; occlusion risk; children on road risk | "Pedestrians crossing the road in front of a large vehicle (bus) while running"; "The bus may not be able to stop in time" | "Pedestrians crossing in vehicle path" |
| CarDropoff | rear-end collision risk; door opening risk; sudden braking risk | "The black vehicle is approaching a stationary white truck at an intersection"; "Nearby buildings may obstruct the driver's view" | "Potential rear-end collision due to vehicle interaction"; "Potential distraction due to multiple visual stimuli" |
| CarOppositeDirectionHIT | head-on collision risk; lane intrusion; sudden braking risk | "Potential collision due to Vehicle1 following closely behind Vehicle2"; "Risk of obstruction with deteriorated overpass above" | "Potential rear-end collision due to sudden stop" |
| CarOppositeDirectionMISTAKE | head-on collision risk; lane intrusion; sudden braking risk | "Potential collision due to the black vehicle maneuvering near the intersection"; "Obstruction of view from the overpass" | "Vehicle near intersection poses risk of collision" |
| FallenTree | obstacle on road; collision risk; lane change risk; sudden braking risk | "Obstacle (tree) obstructing the path of vehicles"; "Potential collision risk between vehicles due to proximity to the tree" | "Obstruction on the roadway due to fallen tree" |
| FallingBarrel | obstacle on road; collision risk; sudden braking risk | "Pedestrian is pulling a cart near obstacles in the roadway"; "Obstacles (traffic cone and container) are obstructing the road" | "Potential collision with pedestrian due to rolling barrel" |
| FallingVendingMachine | obstacle on road; collision risk; sudden braking risk | "The flag is obstructing the road, potentially leading to a collision"; "The pedestrian near the white van may not be visible to drivers" | "Potential risk of collision due to falling billboard" |
| FootballFollowedByBoy | pedestrian collision risk; unexpected obstacle; sudden braking risk | "Potential collision with the pedestrian crossing the road while the vehicles are approaching"; "Risk of not detecting the ball on the road" | "Risk of colliding with the crossing pedestrian" |
| FootballOnHighway | unexpected obstacle; distraction risk; sudden braking risk | "A vehicle is approaching an area where a pedestrian is present"; "Buildings can obstruct the driver's view" | "A soccer ball rolling onto the street may distract drivers" |
| GreenLightOnSign | misleading signal; false traffic light; misidentification risk | "Potential distraction for the driver from advertisement billboards"; "Risk of misinterpretation of traffic light status" | "Potential collision risk due to vehicle crossing in pedestrian zone"; "Driver distraction from billboards" |
| HaybaleOnHighway | obstacle on road; collision risk; lane change risk | "Risk of collision due to the hay bale rolling into the roadway"; "Risk of pedestrian visibility obstruction due to the hay bale" | "Risk of collision with rolling hay bale" |
| LooseZooAnimals | unexpected obstacle; collision risk; sudden braking risk | "Presence of large elephants on the roadway may obstruct the vehicle's path"; "Upside-down vehicle may indicate a prior accident" | "Risk of collision with pedestrians due to unexpected animal presence"; "Distraction from unconventional road objects" |
| PedestrianCallingDog | pedestrian collision risk; animal on road; sudden braking risk | "Dog running across the street, potentially creating a hazard for vehicles"; "Multiple vehicles closely parked, creating potential for collisions" | "Dog crossing in vehicle path, potential collision risk" |
| PoliceCarChase1 | high speed collision risk; unexpected vehicle movement; obstacle on road | "The red vehicle is approaching a white vehicle positioned in its path"; "The tunnel environment may affect visibility" | "Potential for rear-end collision due to unexpected vehicle behavior" |
| PoliceCarChase2 | high speed collision risk; obstacle on road; unexpected vehicle movement | "Potential collision risk between Black Sedan and White Mini in adjacent lanes"; "Risk of obstruction due to Steel Overpass blocking view" | "Vehicle crossing over lane markings" |
| RoadWithExcavator | obstacle on road; lane intrusion; reduced road width | "Potential collision with construction equipment (excavator)"; "Reduced visibility caused by the overpass" | "Potential collision with construction equipment" |
| StaticHighwayAd1 | misleading sign; driver distraction; misidentification risk | "Potential collision with pedestrians at the bus stop"; "Driver distraction due to billboards displaying advertisements" | "Potential distraction from the billboard while driving" |
| StaticHighwayAd2 | misleading sign; driver distraction; misidentification risk | "Potential collision risk due to vehicle near the road side"; "Distraction from billboards could divert driver attention" | "Potential lane intrusion risk due to nearby road users" |
| StaticHighwayAd3 | misleading sign; driver distraction; misidentification risk | "Potential failure to recognize a stopping signal at the traffic light"; "Proximity to pedestrians waiting at the bus stop may lead to a collision risk" | "Billboards may distract drivers"; "Multiple billboards in view could distract drivers" |
| StaticHighwayAd4 | misleading sign; driver distraction; misidentification risk | "Potential collision with pedestrians at bus stop due to vehicle approaching at speed"; "Driver distraction from nearby advertisements and signage" | "Multiple billboards may distract drivers" |
| UnpredictableBicycle | cyclist collision risk; unexpected movement; lane intrusion | "Potential collision risk with a cyclist crossing in proximity to the vehicle"; "Reduced visibility due to distance and angle from which the cyclist is observed" | "Risk of collision due to cyclist position on road" |
| UnpredictableTaxi | collision risk; unexpected movement; sudden lane change risk | "The yellow taxi is very close to the red car"; "The interaction between the two vehicles suggests a possibility of sudden braking or lane changes" | "Risk of rear-end collision due to close proximity" |
| WorkersBlockedByVan | pedestrian risk; occlusion risk; construction zone risk | "Pedestrian crossing in proximity to moving vehicles"; "Obstacles (traffic cones and large rock) present on the road" | "Pedestrian crossing the road without visible awareness of the vehicle"; "Obstacles placed in the roadway may obstruct vehicle path" |
| WorkersNoVan | pedestrian risk; construction zone risk; obstacle on road | "Pedestrian near traffic cones while crossing the road"; "Construction obstacles (traffic cones) limit vehicle maneuverability" | "Pedestrian walking near moving vehicles"; "Obstruction on the road with traffic cones" |

## Qualitative Observations

**Q1. Did ontology grounding improve scene interpretation quality?** Yes, structurally. Every grounded output uses ontology vocabulary instead of placeholder namespaces. Semantic consistency went from 0.028 to 0.669, so two-thirds of `:Term` references in grounded output map to real ontology terms versus essentially zero in baseline.

**Q2. Did ontology grounding reduce hallucinated risks or entities?** Yes. Hallucinated `:Term` references per file dropped from 15.1 to 9.2. Risks per scenario fell from ~3 (Gemini, GPT) and ~13 (Pixtral) to 1.0–6.7. Text-overlap hallucination rate dropped 0.766 → 0.614 for Gemini and 0.829 → 0.776 for GPT-4o-mini. Pixtral barely moved (0.92 → 0.91), partly because its 2-image batch limit produces fragmented outputs.

**Q3. Were RDF outputs more structured?** Yes. Parse rate jumped 60.1% → 96.9%. The biggest gains were on the worst baseline parsers: GPT 60% → 96%, Pixtral 24% → 94%. Gemini reached 100%. Triples per file rose 15.5 → 28.4.

**Q4. Which ontology concepts were most useful?** Heavy hitters: `:Scene`, `:CornerCase`, `:Risk`, `:hasRisk`, `:SeverityScore`, `:severityValue`. The `:CollisionRisk` subclass family did most of the discriminating work. The three anomaly classes (`:StateAnomaly`, `:BehaviorAnomaly`, `:EvidenceBasedAnomaly`) had the highest leverage per token because they force a taxonomic commitment. Underused: `:EvidenceIndicator` subclasses; `:hasCornerCaseType` and `:occursInScene` were used inconsistently because the two-way scene-corner-case link confused some models.

**Q5. Did the ontology over-constrain the model?** Yes. Recall dropped uniformly: Gemini 0.215 → 0.127, GPT 0.180 → 0.096, Pixtral 0.337 → 0.206. The grounded prompt nudges the model toward one risk subclass per scenario, so on multi-risk scenarios (FallenTree: 4 ground-truth risks) the grounded model picks one and misses the others.

**Q6. Did grounding make the output more constrained and explainable?** Yes on both counts. Risks per scene fell sharply (Gemini 2.98 → 1.04, GPT 3.37 → 1.33, Pixtral 13.44 → 6.67). Explainability improved because grounded outputs name a specific subclass like `:RearEndCollisionRisk` or `:OcclusionRisk` instead of a freeform sentence. A reviewer answers "what kind of risk is this?" by looking at `rdf:type`.

**Q7. Limitations.**
1. The text-overlap evaluator is inherited from Project 1 and penalizes terse correct grounded outputs that use ontology labels instead of ground-truth wording. A semantic-similarity scorer would shift these numbers.
2. Pixtral's free tier rejected requests with more than 2 images, so Pixtral ran at batch size 2 while the others handled all 5 images per scenario in one call. Pixtral's three concatenated mini-analyses inflated its risk count and hallucination rate.
3. Free-tier rate limits dominated runtime. Gemini's 500-RPD limit plus 503 storms required exponential backoff with up to 5 retries, occasionally costing six minutes per affected batch.
4. Each scenario has only one weather × anomaly pairing, so some Part C extensions had real triggers in the dataset (CarDropoff for `:OpenDoorIndicator`, FallingBarrel for `:FallingObjectIndicator`) but were rarely invoked under grounded prompting. Stronger prompts with explicit scenario-to-indicator examples would probably fix this.
