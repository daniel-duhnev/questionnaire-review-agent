# POC: Questionnaire Review Agent

## 1. Setup & Dependencies

1. **Clone the repo** (or copy files into a directory)

2. **Run the combined agent using python on an input JSON file**:

   ```bash
   python combined_agent.py --input sample_input.json
   ```

   The script will print a JSON array of decision objects to your terminal.

## 2. Architecture & Design Choices

- **Two-stage pipeline**
  - **Stage 1 (`rules_agent.py`)**: deterministic, rule-based checks for required fields, positive amount, and accreditation.
  - **Stage 2 (`text_escalation_agent.py`)**: regex-based ambiguity detection on free-text fields.
  - `combined_agent.py` imports both functions and only invokes Stage 2 if Stage 1 yields Approve.

- **Why two scripts?**
  - Keeps the core rule logic separated from the text analysis which can later be extended to include an ML classifier instead of the current POC approach.

## 3. Decision Logic

- **Return**
  - Any of the required fields (`investor_name`, `investor_address`, `investment_amount`, `is_accredited_investor`, `signature_present`, `tax_id_provided`) is missing, null, or empty.
  - `investment_amount` is not a positive number.

- **Escalate**
  - `is_accredited_investor` is explicitly false.
  - Or, in Stage 2, any free-text field (`source_of_funds_description` or `accreditation_details`) contains one of our ambiguity patterns.

- **Approve**
  - Passes all Stage 1 rules and then all Stage 2 text checks.

- **Each decision object includes**:

   ```json
   {
     "questionnaire_id": "...",
     "decision": "Approve"/"Return"/"Escalate",
     "missing_fields": [...],         // only for Return
     "escalation_reason": "..."       // only for Escalate
   }
   ```

## 4. Handling Ambiguity in Text

- A small list of regex patterns was defined that flag vague or placeholder language:

   ```python
   AMBIGUITY_PATTERNS = [
     r"\bvarious\w*\b",
     r"\bTBD\b",
     r"\bunknown\w*\b",
     r"\bunspecified\b",
     r"\bmiscellaneous\b",
   ]
   ```

- Each pattern is applied case-insensitive to the raw text.
- On match, the questionnaire is escalated with a message like:

   ```
   Ambiguous term 'various' found in source_of_funds_description
   ```

## 5. Proposed extensions and feedback mechanism to be implemented

- **Decision and Feedback Logging**: Log every agent decision (Approve, Return, Escalate) along with the input data (full questionnaire JSON payload) and decision rationale. Provide a simple interface, such as a web form or spreadsheet, for human analysts to review these logs and override decisions with corrected outcomes and reasons.
- Using this data improve on approach by:
  - **Rule Refinement**: Analyze feedback where human corrections differ from agent decisions to improve the rule-based system:
    - **False Negatives**: Identify missed escalations and update `AMBIGUITY_PATTERNS` with new regex or keywords.
    - **False Positives**: Address unnecessary escalations by refining or adding exceptions to existing patterns.
    - Version-control rule updates and test them against historical feedback data before deployment.
  - **Machine Learning Integration**: Use human corrected feedback to train a classifier for ambiguity detection. Periodically retrain the model with new data, evaluate its performance, and deploy it if it meets predefined thresholds. A hybrid system could combine rule-based logic with model predictions for better decision-making.
- **Continuous Improvement & Monitoring**: Track system performance over time with metrics like human override rates and the percentage of forms auto-approved, returned, or escalated. Conduct regular reviews to refine rules or update the model based on new feedback, ensuring ongoing accuracy improvements.

## 6. Assumptions & Limitations

- Flat JSON: input is either one object or an array of objects.
- Limited ambiguity patterns: may miss novel vague phrases.
- No spelling correction or fuzzy matching beyond simple `\w*` suffixes.
- Prototype only: no logging, error handling, or UI.
