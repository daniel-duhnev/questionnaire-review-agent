import json
from typing import Any, Dict, List, Optional

# Define the required fields and basic checks
REQUIRED_FIELDS = [
    "investor_name",
    "investor_address",
    "investment_amount",
    "is_accredited_investor",
    "signature_present",
    "tax_id_provided",
]


def review_questionnaire(q: Dict[str, Any]) -> Dict[str, Any]:
    """
    Review a single questionnaire record and return decision structure.
    """
    questionnaire_id = q.get("questionnaire_id")
    missing_fields: List[str] = []
    escalation_reason: Optional[str] = None

    # Check for missing or null/empty required fields
    for field in REQUIRED_FIELDS:
        value = q.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            missing_fields.append(field)

    # If any missing, return 'Return'
    if missing_fields:
        return {
            "questionnaire_id": questionnaire_id,
            "decision": "Return",
            "missing_fields": missing_fields,
            "escalation_reason": None,
        }

    # Check investment_amount > 0
    amount = q.get("investment_amount")
    if not isinstance(amount, (int, float)) or amount <= 0:
        return {
            "questionnaire_id": questionnaire_id,
            "decision": "Return",
            "missing_fields": ["investment_amount"],
            "escalation_reason": None,
        }

    # Escalate if not accredited
    if q.get("is_accredited_investor") is False:
        return {
            "questionnaire_id": questionnaire_id,
            "decision": "Escalate",
            "missing_fields": None,
            "escalation_reason": "Investor is not accredited",
        }

    # All basic checks passed -> Approve
    return {
        "questionnaire_id": questionnaire_id,
        "decision": "Approve",
        "missing_fields": None,
        "escalation_reason": None,
    }


def process_file(input_path: str, output_path: str) -> None:
    """
    Load a JSON file of questionnaires, review each, and write results to output JSON.
    Handles both a single object and a list of objects.
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Ensure we have a list of questionnaires
    if isinstance(data, dict):
        questionnaires = [data]
    elif isinstance(data, list):
        questionnaires = data
    else:
        raise ValueError("Input JSON must be an object or array of objects.")

    results: List[Dict[str, Any]] = []
    for q in questionnaires:
        result = review_questionnaire(q)
        results.append(result)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Review PE subscription questionnaires.")
    parser.add_argument("--input", required=True, help="Path to input JSON file")
    parser.add_argument("--output", required=True, help="Path to output JSON file")
    args = parser.parse_args()

    process_file(args.input, args.output)
    print(f"Processed {args.input} and wrote results to {args.output}")
