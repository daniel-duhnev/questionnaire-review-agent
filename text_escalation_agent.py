import json
import re
from typing import Any, Dict, List, Optional

# Patterns indicating ambiguity or potential issues
AMBIGUITY_PATTERNS = [
    r"\bvarious\b",
    r"\bTBD\b",
    r"\bunknown\b",
    r"\bunspecified\b",
    r"\bmiscellaneous\b",
]

# Fields to scan for ambiguous content
TEXT_FIELDS = [
    "source_of_funds_description",
    "accreditation_details",
]


def analyze_text_for_ambiguity(text: Optional[str]) -> Optional[str]:
    """
    Return a descriptive reason if any ambiguity pattern is found in text.
    """
    if not text:
        return None

    lower_text = text.lower()
    for pattern in AMBIGUITY_PATTERNS:
        if re.search(pattern, lower_text):
            # Extract the raw matched term for clarity
            match = re.search(pattern, lower_text)
            term = match.group(0) if match else pattern.strip('\\b')
            return f"Ambiguous term '{term}' found"
    return None


def review_with_text_analysis(q: Dict[str, Any]) -> Dict[str, Any]:
    """
    Review a single questionnaire focusing on text ambiguity escalation.
    Returns escalation if any pattern matched; otherwise Approve.
    """
    questionnaire_id = q.get("questionnaire_id")

    # Scan each free-text field
    for field in TEXT_FIELDS:
        reason = analyze_text_for_ambiguity(q.get(field))
        if reason:
            return {
                "questionnaire_id": questionnaire_id,
                "decision": "Escalate",
                "missing_fields": None,
                "escalation_reason": f"{reason} in {field}",
            }

    # No ambiguity detected
    return {
        "questionnaire_id": questionnaire_id,
        "decision": "Approve",
        "missing_fields": None,
        "escalation_reason": None,
    }


def process_file(input_path: str) -> None: # Removed output_path
    """
    Load questionnaires, apply text-based escalation logic, and print results to terminal.
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if isinstance(data, dict):
        records = [data]
    elif isinstance(data, list):
        records = data
    else:
        raise ValueError("Input JSON must be an object or array of objects.")

    results: List[Dict[str, Any]] = []
    for q in records:
        results.append(review_with_text_analysis(q))

    # Print results to terminal instead of saving to a file
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Text-ambiguity escalation for PE subscription questionnaires."
    )
    parser.add_argument("--input", required=True, help="Path to input JSON file")
    # Removed the --output argument as it's no longer needed
    args = parser.parse_args()

    process_file(args.input) # Removed args.output
    # Removed the print statement about writing to output file