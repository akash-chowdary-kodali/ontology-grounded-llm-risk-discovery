import os

def load_scenarios(dataset_path):
    scenarios = []

    for weather in sorted(os.listdir(dataset_path)):
        weather_path = os.path.join(dataset_path, weather)
        if not os.path.isdir(weather_path):
            continue

        for anomaly_type in sorted(os.listdir(weather_path)):
            anomaly_path = os.path.join(weather_path, anomaly_type)
            if not os.path.isdir(anomaly_path):
                continue

            for scenario_name in sorted(os.listdir (anomaly_path)):
                scenario_path = os.path.join(anomaly_path, scenario_name)
                if not os.path.isdir(scenario_path):
                    continue

                images = sorted ([os.path.join(scenario_path, f) for f in os.listdir(scenario_path) if f.endswith(".png")])

                if images:
                    scenarios.append({"weather": weather, 
                                      "anomaly_type": anomaly_type,
                                      "scenario_name": scenario_name,
                                      "images": images})
    
    return scenarios

