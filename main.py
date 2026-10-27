from image_loader import load_scenarios
import config
from prompt import get_baseline_prompt, get_grounded_prompt
from ontology_parser import parse_ontology, format_for_prompt
import time
import os
import json
from llm_clients import call_gemini, call_ollama, call_openai, call_mistral
from evaluator import parse_risks, compute_metrics
from ground_truth import GROUND_TRUTH

scenarios = load_scenarios(config.DATASET_PATH)

LLM_FUNCTIONS = {
    "gemini-3.1-flash-lite-preview": call_gemini,
    "llama3.2-vision": call_ollama,
    "gpt-4o-mini": call_openai,
    "pixtral-12b-2409": call_mistral,
}

# Load ontology once and build grounded prompt
ontology = parse_ontology()
ontology_summary = format_for_prompt(ontology)

PROMPT_MODES = {
    "baseline": get_baseline_prompt(),
    "grounded": get_grounded_prompt(ontology_summary),
}

for mode in PROMPT_MODES:
    os.makedirs(f"outputs/rdf_{mode}/batches", exist_ok=True)
os.makedirs("outputs/results", exist_ok=True)


def safe_model_name(name):
    return name.replace("/", "_")


def call_with_retry(fn, batch, prompt, model_name, scenario_label):
    """Call LLM with exponential backoff on rate-limit and network errors."""
    delays = [0] + config.RETRY_DELAYS
    last_err = None
    for attempt, delay in enumerate(delays):
        if delay > 0:
            time.sleep(delay)
        try:
            return fn(batch, prompt=prompt)
        except Exception as e:
            last_err = e
            err = str(e)
            err_lower = err.lower()
            is_rate = "429" in err or "rate" in err_lower or "tpd" in err_lower or "tpm" in err_lower or "quota" in err_lower
            is_net = any(x in err_lower for x in ["timeout", "connection", "network", "unreachable", "reset", "broken pipe", "eof", "ssl"])
            is_server = any(x in err for x in ["500", "502", "503", "504"]) or any(x in err_lower for x in ["unavailable", "overloaded", "high demand", "spikes in demand", "internal", "service_unavailable"])
            recoverable = is_rate or is_net or is_server

            if attempt == len(delays) - 1:
                print(f"  GAVE UP after {attempt+1} attempts | {model_name} | {scenario_label} | {err[:120]}")
                return None
            if not recoverable:
                print(f"  NON-RECOVERABLE | {model_name} | {scenario_label} | {err[:120]}")
                return None
            next_delay = delays[attempt + 1]
            kind = 'rate' if is_rate else ('server' if is_server else 'net')
            print(f"  RETRY {attempt+1}/{len(delays)-1} ({kind}) | wait {next_delay}s | {err[:80]}")
    return None


Model_results = {}
evaluation_results = []
results_log_path = "outputs/results/evaluation_results.json"

# Resume previous evaluation_results if file exists
if os.path.exists(results_log_path):
    try:
        with open(results_log_path) as f:
            evaluation_results = json.load(f)
        print(f"Resumed {len(evaluation_results)} prior eval rows")
    except Exception:
        evaluation_results = []


def already_evaluated(model_name, scenario_name, weather, mode):
    return any(
        r["model"] == model_name and r["scenario"] == scenario_name
        and r["weather"] == weather and r.get("mode") == mode
        for r in evaluation_results
    )


for model in config.MODELS:
    if not model["enabled"]:
        continue

    llm_function = LLM_FUNCTIONS[model["name"]]
    throttle = config.THROTTLE_SECONDS.get(model["name"], 0)
    batch_size = config.BATCH_SIZE_OVERRIDE.get(model["name"], config.BATCH_SIZE)
    Model_results[model["name"]] = {}

    for scenario in scenarios:
        key = f"{scenario['scenario_name']}_{scenario['weather']}"
        Model_results[model["name"]][key] = {}
        images = scenario["images"]

        for mode_name, prompt_text in PROMPT_MODES.items():
            scenario_label = f"{scenario['scenario_name']}/{scenario['weather']}/{mode_name}"

            if already_evaluated(model["name"], scenario["scenario_name"], scenario["weather"], mode_name):
                print(f"SKIP (already evaluated): {model['name']} | {scenario_label}")
                continue

            Model_results[model["name"]][key][mode_name] = []
            batch_dir = f"outputs/rdf_{mode_name}/batches"
            scenario_rdf_path = f"outputs/rdf_{mode_name}/{safe_model_name(model['name'])}_{key}.ttl"

            # Apply per-scenario image cap (last N most-informative frames)
            scenario_images = images[-config.IMAGES_PER_SCENARIO:] if config.IMAGES_PER_SCENARIO else images

            for i in range(0, len(scenario_images), batch_size):
                batch = scenario_images[i:i + batch_size]
                batch_idx = i // batch_size
                batch_path = f"{batch_dir}/{safe_model_name(model['name'])}_{key}_b{batch_idx}.ttl"

                # Resume: skip batch if file already saved with content
                if os.path.exists(batch_path) and os.path.getsize(batch_path) > 0:
                    with open(batch_path, "r") as f:
                        response = f.read()
                    print(f"RESUME batch | {model['name']} | {scenario_label} | b{batch_idx}")
                    Model_results[model["name"]][key][mode_name].append(
                        {"response": response, "execution_time": 0, "batch_index": i, "resumed": True})
                    continue

                if throttle > 0:
                    time.sleep(throttle)

                start_time = time.time()
                response = call_with_retry(llm_function, batch, prompt_text, model["name"], scenario_label)
                execution_time = time.time() - start_time

                # Always write batch file (even empty) so we don't retry forever on persistent failures
                with open(batch_path, "w") as f:
                    f.write(response or "")

                print(f"{model['name']} | {mode_name} | {scenario['scenario_name']} | {scenario['weather']} | b{batch_idx} | {execution_time:.2f}s | {'OK' if response else 'FAIL'}")
                Model_results[model["name"]][key][mode_name].append(
                    {"response": response, "execution_time": execution_time, "batch_index": i})

            # Aggregate per-batch responses → scenario-level RDF file
            all_responses = " ".join(
                [b["response"] for b in Model_results[model["name"]][key][mode_name] if b["response"]]
            )
            with open(scenario_rdf_path, "w") as f:
                f.write(all_responses)

            # Risks + metrics
            identified_risks = parse_risks(all_responses)
            gt_risks = GROUND_TRUTH.get(scenario["scenario_name"], [])

            if gt_risks:
                metrics = compute_metrics(identified_risks, gt_risks)
            else:
                metrics = {"precision": None, "recall": None, "f1": None, "hallucination_rate": None}

            batch_times = [b["execution_time"] for b in Model_results[model["name"]][key][mode_name] if not b.get("resumed")]
            avg_runtime_per_batch = sum(batch_times) / len(batch_times) if batch_times else 0
            total_scenario_time = sum(batch_times)

            evaluation_results.append({
                "model": model["name"],
                "mode": mode_name,
                "scenario": scenario["scenario_name"],
                "weather": scenario["weather"],
                "batch_size": batch_size,
                "num_batches": len(Model_results[model["name"]][key][mode_name]),
                "avg_runtime_per_batch": round(avg_runtime_per_batch, 2),
                "total_scenario_time": round(total_scenario_time, 2),
                "num_risks_found": len(identified_risks),
                "precision": metrics["precision"],
                "recall": metrics["recall"],
                "f1": metrics["f1"],
                "hallucination_rate": metrics["hallucination_rate"]
            })

            # Persist after every scenario+mode (cheap insurance)
            with open(results_log_path, "w") as f:
                json.dump(evaluation_results, f, indent=2)

            print(f"  -> [{mode_name}] Risks: {len(identified_risks)} | F1: {metrics['f1']} | Halluc: {metrics['hallucination_rate']}")

# Final summary tables
print("\n" + "="*110)
print("TABLE 1: Risk Discovery (Baseline vs Grounded)")
print("="*110)
print(f"{'Model':<28} {'Mode':<10} {'Scenario':<25} {'Weather':<12} {'F1':<8} {'Halluc':<8}")
print("-"*110)
for r in evaluation_results:
    if r["f1"] is not None:
        print(f"{r['model']:<28} {r['mode']:<10} {r['scenario']:<25} {r['weather']:<12} {r['f1']:<8.3f} {r['hallucination_rate']:<8.3f}")

print("\n" + "="*110)
print("TABLE 2: Performance")
print("="*110)
print(f"{'Model':<28} {'Mode':<10} {'Scenario':<25} {'Weather':<12} {'Avg/Batch':<12} {'Total':<10}")
print("-"*110)
for r in evaluation_results:
    print(f"{r['model']:<28} {r['mode']:<10} {r['scenario']:<25} {r['weather']:<12} {r['avg_runtime_per_batch']:<12.2f} {r['total_scenario_time']:<10.2f}")
