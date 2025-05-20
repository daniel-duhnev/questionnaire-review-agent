# combined_agent.py
import json
from typing import Any, Dict, List, Optional
from rules_agent import review_questionnaire
from text_escalation_agent import review_with_text_analysis

def main(input_path: str):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    qs = data if isinstance(data, list) else [data]

    final: List[Dict[str, Any]] = []
    for q in qs:
        rule_res = review_questionnaire(q)
        if rule_res["decision"] == "Approve":
            # only escalate text if rules gave Approve
            text_res = review_with_text_analysis(q)
            final.append(text_res)
        else:
            final.append(rule_res)

    print(json.dumps(final, indent=2))


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    args = p.parse_args()
    main(args.input)
