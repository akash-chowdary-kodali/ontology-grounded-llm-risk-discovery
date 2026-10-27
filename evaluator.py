import re


def parse_risks(response_text):
    risks = []
    if not response_text:
        return risks

    # Split on various Risk header formats: "Risk 1:", "**Risk 1:**", "*Risk 1*", etc.
    risk_blocks = re.split(r'\*{0,2}Risk\s*\d+\s*:?\*{0,2}:?', response_text)

    for block in risk_blocks[1:]:
        description = ""
        severity = 0.0

        # Match Description with optional markdown bold
        desc_match = re.search(r'\*{0,2}Description:?\*{0,2}\s*(.+)', block)
        if desc_match:
            description = desc_match.group(1).strip().strip('*').strip()

        # Match Severity Score with optional markdown bold
        sev_match = re.search(r'\*{0,2}Severity\s*Score:?\*{0,2}\s*([\d.]+)', block)
        if sev_match:
            severity = float(sev_match.group(1))

        if description:
            risks.append({"description": description, "severity": severity})

    return risks


def _keyword_match(gt_risk, identified_desc):
    """Check if ground truth risk keywords appear in the identified risk description."""
    gt_lower = gt_risk.lower()
    desc_lower = identified_desc.lower()

    # Direct substring match
    if gt_lower in desc_lower:
        return True

    # Check if all significant keywords from ground truth appear in description
    keywords = [w for w in gt_lower.split() if w not in ("risk", "of", "on", "the", "a", "an", "in")]
    if len(keywords) > 0 and all(kw in desc_lower for kw in keywords):
        return True

    return False


def compute_metrics(identified_risks, ground_truth_risks):
    tp = 0
    matched_gt = set()

    for risk in identified_risks:
        for j, gt in enumerate(ground_truth_risks):
            if j not in matched_gt and _keyword_match(gt, risk["description"]):
                tp += 1
                matched_gt.add(j)
                break

    fp = len(identified_risks) - tp
    fn = len(ground_truth_risks) - tp

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    hallucination_rate = fp / len(identified_risks) if len(identified_risks) > 0 else 0.0

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "hallucination_rate": hallucination_rate
    }
