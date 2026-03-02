"""Robust JSON parser that handles multi-block and malformed LLM responses."""

import ast
import json
import re
from typing import Dict


def parse_llm_json(raw: str) -> Dict:
    """
    Parse JSON from LLM output, handling common issues:
    1. Markdown code fences (```json ... ```)
    2. Multiple separate JSON objects (merges them)
    3. Multiline strings inside values
    4. Python dict syntax (single quotes instead of double quotes)

    Parameters
    ----------
    raw : str
        Raw LLM output string.

    Returns
    -------
    dict
        Merged dictionary of all parsed JSON objects.
    """
    raw = raw.strip()

    # Strip markdown code fences
    raw = re.sub(r"```(?:json)?\s*", "", raw)
    raw = re.sub(r"```", "", raw)
    raw = raw.strip()

    # Try direct JSON parse first (fast path)
    try:
        result = json.loads(raw)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass

    # Try Python dict syntax (single quotes) via ast.literal_eval
    try:
        result = ast.literal_eval(raw)
        if isinstance(result, dict):
            return result
    except (ValueError, SyntaxError):
        pass

    # Try converting single quotes to double quotes
    try:
        fixed = _single_to_double_quotes(raw)
        result = json.loads(fixed)
        if isinstance(result, dict):
            return result
    except (json.JSONDecodeError, ValueError):
        pass

    # Find ALL JSON objects in the text
    objects = _extract_all_json_objects(raw)

    if not objects:
        # Last resort: try to fix multiline strings
        fixed = _fix_multiline_strings(raw)
        try:
            result = json.loads(fixed)
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass

        # Final fallback: try ast.literal_eval on fixed text
        try:
            result = ast.literal_eval(fixed)
            if isinstance(result, dict):
                return result
        except (ValueError, SyntaxError):
            pass

        raise ValueError(f"No valid JSON found in LLM output:\n{raw[:500]}")

    # Merge all objects into one dict
    merged = {}
    for obj in objects:
        merged.update(obj)

    return merged


def _single_to_double_quotes(text: str) -> str:
    """
    Convert Python dict syntax (single quotes) to JSON (double quotes).
    Handles apostrophes inside values by being careful about replacements.
    """
    # Match the outermost { ... } first
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return text

    content = match.group(0)

    # Replace single-quoted keys and values with double-quoted ones
    # This regex finds: 'some text' patterns
    result = re.sub(
        r"'([^'\\]*(?:\\.[^'\\]*)*)'",
        r'"\1"',
        content,
    )

    return result


def _extract_all_json_objects(text: str) -> list:
    """
    Extract all top-level JSON objects from a string using brace matching.
    Handles nested braces correctly. Falls back to ast.literal_eval for
    Python dict syntax.
    """
    objects = []
    i = 0
    while i < len(text):
        if text[i] == "{":
            # Find the matching closing brace
            depth = 0
            start = i
            in_string = False
            escape_next = False
            quote_char = None

            for j in range(i, len(text)):
                char = text[j]

                if escape_next:
                    escape_next = False
                    continue

                if char == "\\":
                    escape_next = True
                    continue

                # Handle both single and double quote strings
                if char in ('"', "'") and not escape_next:
                    if not in_string:
                        in_string = True
                        quote_char = char
                    elif char == quote_char:
                        in_string = False
                        quote_char = None
                    continue

                if in_string:
                    continue

                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth == 0:
                        block = text[start : j + 1]
                        obj = _try_parse_block(block)
                        if obj is not None:
                            objects.append(obj)
                        i = j + 1
                        break
            else:
                i += 1
        else:
            i += 1

    return objects


def _try_parse_block(block: str) -> dict | None:
    """Try multiple strategies to parse a JSON/dict block."""
    # Strategy 1: direct JSON
    try:
        obj = json.loads(block)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass

    # Strategy 2: Python dict (single quotes)
    try:
        obj = ast.literal_eval(block)
        if isinstance(obj, dict):
            return obj
    except (ValueError, SyntaxError):
        pass

    # Strategy 3: single→double quote conversion
    try:
        fixed = _single_to_double_quotes(block)
        obj = json.loads(fixed)
        if isinstance(obj, dict):
            return obj
    except (json.JSONDecodeError, ValueError):
        pass

    # Strategy 4: fix multiline strings
    try:
        fixed = _fix_multiline_strings(block)
        obj = json.loads(fixed)
        if isinstance(obj, dict):
            return obj
    except (json.JSONDecodeError, ValueError):
        pass

    return None


def _fix_multiline_strings(text: str) -> str:
    """Escape literal newlines inside JSON string values."""

    def escape_newlines(match):
        value = match.group(1).replace("\n", "\\n")
        return f'"{value}"'

    return re.sub(r'"(.*?)"', escape_newlines, text, flags=re.DOTALL)
