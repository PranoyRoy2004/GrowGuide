# backend/nlp/parser.py

import os
import re
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

# ─────────────────────────────────────────
# Feature value ranges (for reference)
# N: 0-140, P: 5-145, K: 5-205
# temperature: 8-44°C, humidity: 14-100%
# ph: 3.5-9.9, rainfall: 20-300mm
# ─────────────────────────────────────────

# ── Rule-based keyword mappings ───────────────────────────────────────────────

RAINFALL_RULES = {
    r"\bno rain\b|\barid\b|\bdesert\b"                        : 30,
    r"\bvery low rain\b|\bvery little rain\b"                 : 50,
    r"\blow rain\b|\blight rain\b|\bdry\b"                    : 75,
    r"\bmoderate rain\b|\baverage rain\b|\bmedium rain\b"     : 120,
    r"\bgood rain\b|\bregular rain\b"                         : 160,
    r"\bheavy rain\b|\bhigh rain\b|\blots of rain\b"          : 220,
    r"\bvery heavy rain\b|\bextreme rain\b|\btropical rain\b" : 280,
}

HUMIDITY_RULES = {
    r"\bvery dry\b|\bvery low humidity\b"                     : 20,
    r"\bdry\b|\blow humidity\b"                               : 35,
    r"\bmoderately humid\b|\bmoderate humidity\b"             : 55,
    r"\bhumid\b|\bhigh humidity\b"                            : 75,
    r"\bvery humid\b|\bextremely humid\b|\btropical\b"        : 90,
}

TEMPERATURE_RULES = {
    r"\bvery cold\b|\bfreezing\b|\bsnowy\b"                   : 10,
    r"\bcold\b|\bcool\b|\bwinter\b"                           : 16,
    r"\bmild\b|\bwarm\b|\bmoderate temp\b"                    : 24,
    r"\bhot\b|\bwarm climate\b|\bsummer\b"                    : 32,
    r"\bvery hot\b|\bscorching\b|\bextreme heat\b"            : 40,
}

PH_RULES = {
    r"\bvery acidic\b|\bstrongly acidic\b"                    : 4.0,
    r"\bacidic\b|\blow ph\b"                                  : 5.5,
    r"\bslightly acidic\b|\bmildly acidic\b"                  : 6.2,
    r"\bneutral\b|\bneutral ph\b|\bbalanced ph\b"             : 7.0,
    r"\bslightly alkaline\b|\bmildly alkaline\b"              : 7.5,
    r"\balkaline\b|\bhigh ph\b"                               : 8.5,
    r"\bvery alkaline\b|\bstrongly alkaline\b"                : 9.0,
}

NITROGEN_RULES = {
    r"\bno nitrogen\b|\bnitrogen depleted\b"                  : 5,
    r"\blow nitrogen\b|\bnitrogen deficient\b"                : 25,
    r"\bmoderate nitrogen\b|\bmedium nitrogen\b"              : 60,
    r"\bhigh nitrogen\b|\bnitrogen rich\b"                    : 100,
    r"\bvery high nitrogen\b|\bexcellent nitrogen\b"          : 130,
}

PHOSPHORUS_RULES = {
    r"\blow phosphorus\b|\bphosphorus deficient\b"            : 15,
    r"\bmoderate phosphorus\b|\bmedium phosphorus\b"          : 50,
    r"\bhigh phosphorus\b|\bphosphorus rich\b"                : 100,
    r"\bvery high phosphorus\b"                               : 135,
}

POTASSIUM_RULES = {
    r"\blow potassium\b|\bpotassium deficient\b"              : 15,
    r"\bmoderate potassium\b|\bmedium potassium\b"            : 70,
    r"\bhigh potassium\b|\bpotassium rich\b"                  : 140,
    r"\bvery high potassium\b"                                : 195,
}

SOIL_TYPE_HINTS = {
    r"\bsandy\b"   : {"ph": 6.0, "N": 20,  "humidity": 30},
    r"\bclay\b"    : {"ph": 6.5, "N": 60,  "humidity": 70},
    r"\bloamy\b"   : {"ph": 6.8, "N": 80,  "humidity": 55},
    r"\bsilty\b"   : {"ph": 6.5, "N": 70,  "humidity": 65},
    r"\bpeaty\b"   : {"ph": 4.5, "N": 100, "humidity": 80},
    r"\bchalky\b"  : {"ph": 8.0, "N": 30,  "humidity": 35},
    r"\bblack soil\b|\bregur\b" : {"ph": 7.2, "N": 85, "K": 110},
    r"\bred soil\b"             : {"ph": 6.0, "N": 40, "P": 30},
    r"\balluvial\b"             : {"ph": 7.0, "N": 90, "P": 60, "K": 80},
}

REGION_HINTS = {
    r"\btropical\b"     : {"temperature": 30, "humidity": 85, "rainfall": 250},
    r"\bsubtropical\b"  : {"temperature": 26, "humidity": 70, "rainfall": 180},
    r"\barid\b"         : {"temperature": 35, "humidity": 20, "rainfall": 40},
    r"\bsemi.?arid\b"   : {"temperature": 30, "humidity": 35, "rainfall": 70},
    r"\btemperate\b"    : {"temperature": 18, "humidity": 60, "rainfall": 120},
    r"\bmediterranean\b": {"temperature": 22, "humidity": 50, "rainfall": 90},
    r"\bcoastal\b"      : {"temperature": 25, "humidity": 80, "rainfall": 170},
}


# ─────────────────────────────────────────────────────────────────────────────
# LAYER 1 — Rule-based extractor
# ─────────────────────────────────────────────────────────────────────────────

def _apply_rules(text: str, rules: dict) -> float | None:
    """Checks text against regex rules and returns the matched value."""
    text = text.lower()
    for pattern, value in rules.items():
        if re.search(pattern, text):
            return value
    return None


def rule_based_extract(text: str) -> dict:
    """
    Extracts as many features as possible using keyword/rule matching.
    Returns a dict — missing features will have None values.
    """
    features = {
        "N"          : _apply_rules(text, NITROGEN_RULES),
        "P"          : _apply_rules(text, PHOSPHORUS_RULES),
        "K"          : _apply_rules(text, POTASSIUM_RULES),
        "temperature": _apply_rules(text, TEMPERATURE_RULES),
        "humidity"   : _apply_rules(text, HUMIDITY_RULES),
        "ph"         : _apply_rules(text, PH_RULES),
        "rainfall"   : _apply_rules(text, RAINFALL_RULES),
    }

    # Apply soil type hints for missing features
    for pattern, hints in SOIL_TYPE_HINTS.items():
        if re.search(pattern, text.lower()):
            for key, val in hints.items():
                if features.get(key) is None:
                    features[key] = val

    # Apply region hints for missing features
    for pattern, hints in REGION_HINTS.items():
        if re.search(pattern, text.lower()):
            for key, val in hints.items():
                if features.get(key) is None:
                    features[key] = val

    return features


# ─────────────────────────────────────────────────────────────────────────────
# LAYER 2 — LLM-based extractor (fills gaps left by rules)
# ─────────────────────────────────────────────────────────────────────────────

def llm_extract(text: str, partial_features: dict) -> dict:
    """
    Sends the user text + already-extracted features to Groq LLM.
    Asks it to fill in only the missing values.
    Returns updated features dict.
    """
    missing = [k for k, v in partial_features.items() if v is None]

    if not missing:
        return partial_features  # nothing to fill

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""You are an agriculture data extraction assistant.

A farmer described their farm as:
"{text}"

From this description, some soil and climate features have already been extracted:
{json.dumps({k: v for k, v in partial_features.items() if v is not None}, indent=2)}

Please estimate ONLY these missing features based on the description:
{missing}

Feature reference ranges:
- N (Nitrogen in soil): 0–140
- P (Phosphorus in soil): 5–145  
- K (Potassium in soil): 5–205
- temperature: 8–44 (°C)
- humidity: 14–100 (%)
- ph: 3.5–9.9
- rainfall: 20–300 (mm)

Rules:
1. Use median/typical values if the description is vague.
2. If truly impossible to estimate, use the midpoint of the range.
3. Return ONLY a valid JSON object with the missing keys and numeric values.
4. Do NOT include explanations, markdown, or extra text.

Example output format:
{{"N": 60, "ph": 6.5}}"""

    try:
        response = client.chat.completions.create(
            model    = "llama-3.3-70b-versatile",
            messages = [{"role": "user", "content": prompt}],
            temperature = 0.1,   # low temp = more consistent/factual
            max_tokens  = 200,
        )

        raw = response.choices[0].message.content.strip()

        # Clean up in case LLM wraps in markdown code block
        raw = re.sub(r"```json|```", "", raw).strip()

        llm_values = json.loads(raw)

        # Merge LLM values into features (only for missing ones)
        for key in missing:
            if key in llm_values and llm_values[key] is not None:
                partial_features[key] = float(llm_values[key])

    except Exception as e:
        print(f"[WARNING] LLM extraction failed: {e}. Using fallback defaults.")
        # Fallback: use dataset midpoint values for any still-missing features
        FALLBACKS = {
            "N": 70, "P": 53, "K": 48,
            "temperature": 25, "humidity": 71,
            "ph": 6.5, "rainfall": 103
        }
        for key in missing:
            if partial_features[key] is None:
                partial_features[key] = FALLBACKS[key]

    return partial_features


# ─────────────────────────────────────────────────────────────────────────────
# MAIN PUBLIC FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def parse_natural_language(text: str) -> dict:
    """
    Main entry point. Converts a natural language farm description
    into a structured feature dictionary ready for ML prediction.

    Args:
        text (str): User's natural language input

    Returns:
        dict: {
            "features": {N, P, K, temperature, humidity, ph, rainfall},
            "extraction_method": "rule_based" | "hybrid" | "llm_fallback",
            "missing_before_llm": [list of features filled by LLM]
        }
    """
    print(f"\n[NLP] Input: '{text}'")

    # Layer 1 — rule-based
    features = rule_based_extract(text)
    missing_before_llm = [k for k, v in features.items() if v is None]

    print(f"[NLP] After rule-based extraction: {features}")
    print(f"[NLP] Features still missing: {missing_before_llm}")

    # Layer 2 — LLM fills gaps
    if missing_before_llm:
        features = llm_extract(text, features)
        method = "hybrid" if len(missing_before_llm) < 7 else "llm_fallback"
    else:
        method = "rule_based"

    print(f"[NLP] Final features ({method}): {features}")

    return {
        "features"           : features,
        "extraction_method"  : method,
        "missing_before_llm" : missing_before_llm
    }


# ─────────────────────────────────────────────────────────────────────────────
# Quick tests when run directly
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_inputs = [
        "I live in a tropical region with loamy soil and heavy rainfall.",
        "My farm has high nitrogen content, acidic soil, and moderate temperature.",
        "Hot and dry region with sandy soil and very little rain.",
        "I have alluvial soil near a river with moderate humidity.",
    ]

    for text in test_inputs:
        print("\n" + "─" * 60)
        result = parse_natural_language(text)
        print(f"\n  Method : {result['extraction_method']}")
        print(f"  LLM filled : {result['missing_before_llm']}")
        print(f"  Features   : {result['features']}")