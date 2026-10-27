# Ontology-grounded LLM risk discovery for autonomous-driving corner cases

Course project for CECS 571 (Semantic Web Technologies) at California State University, Long Beach, Spring 2026.

Vision-language models look at driving scenes (27 corner-case scenarios, 6 weather conditions each) and describe the risks they see as RDF/Turtle. I ran every scene twice per model: once with a plain prompt (baseline) and once with a prompt that includes the vocabulary of an ontology I built in Protege (grounded). Same images, same models, same scoring code, so the only difference is the ontology.

162 image groups x 3 models x 2 modes = 972 LLM calls. Models: Gemini 3.1 Flash Lite Preview, GPT-4o-mini and Pixtral-12B.

## Results

| Metric | Baseline | Grounded |
|---|---|---|
| Valid Turtle (RDF parse success) | 60.1% | 96.9% |
| Risk discovery precision | 0.161 | 0.234 |
| Risk discovery recall | 0.244 | 0.143 |
| Risk discovery F1 | 0.173 | 0.149 |

Grounding mostly fixed the output format: Pixtral-12B went from 23.5% to 94.4% valid Turtle. Precision went up on all three models, but recall dropped, because grounded answers were shorter and the keyword-overlap scorer rewards longer lists of risks. Net F1 fell 14%. Full tables are in [docs/results-tables.md](docs/results-tables.md) and the write-up is in [docs/report.md](docs/report.md).

## Layout

- `ontology/corner_case_ontology.ttl`: the ontology (CornerCase with StateAnomaly, BehaviorAnomaly and EvidenceBasedAnomaly, plus Actor, Obstacle, Scene, Risk and supporting classes)
- `main.py`: runs both modes over the dataset
- `ontology_parser.py`: reads the ontology and builds the vocabulary block for the grounded prompt
- `llm_clients.py`, `prompt.py`, `config.py`: model clients, prompts and settings
- `evaluator.py`, `comparison_evaluator.py`, `ground_truth.py`: scoring
- `rdf_baseline/`, `rdf_grounded/`: the Turtle files the models produced
- `docs/`: report, result tables, ontology notes and Protege screenshots

## Running it

```
pip install -r requirements.txt
```

Put API keys in a `.env` file (OPENAI_API_KEY, GEMINI_API_KEY, GROQ_API_KEY, MISTRAL_API_KEY). The image dataset was provided for the course and is not included; place it in `./Dataset/` and run `python main.py`.
