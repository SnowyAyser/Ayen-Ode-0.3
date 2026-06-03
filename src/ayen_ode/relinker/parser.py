import re
import json
from typing import Any

_INV_RE = re.compile(r"<investigate\s+([^>]*?)>(.*?)</investigate>", re.DOTALL)


def are_names_equivalent(a: str, b: str) -> bool:
    """Robust, article-aware equivalence checking for proper nouns and entity names.
    Supports case-insensitivity, article-stripping, plurals, and significant name stem matching.
    """
    def strip_article(name: str) -> str:
        s = name.strip().lower()
        for art in ("the ", "a ", "an "):
            if s.startswith(art):
                return s[len(art):].strip()
        return s

    a_clean = strip_article(a)
    b_clean = strip_article(b)
    if not a_clean or not b_clean:
        return False
        
    if a_clean == b_clean:
        return True
        
    def get_variants(name: str) -> set[str]:
        vars_set = {name}
        if name.endswith("s"):
            if name.endswith("es"):
                vars_set.add(name[:-2])
            vars_set.add(name[:-1])
        else:
            vars_set.add(name + "s")
            vars_set.add(name + "es")
        return vars_set
        
    if get_variants(a_clean).intersection(get_variants(b_clean)):
        return True
        
    if " " not in a_clean and " " in b_clean:
        tokens = [t.strip() for t in b_clean.split() if t.strip()]
        if a_clean in tokens and a_clean not in {"the", "of", "and", "in", "at", "to", "for", "with", "by", "from", "on", "a", "an", "authority"}:
            return True
            
    return False


def text_needs_relinking(text: str, already_investigated: list[str] | dict[str, str]) -> bool:
    if not text or not text.strip():
        return False
    text_lower = text.lower()
    for name in already_investigated:
        name_clean = name.strip()
        if not name_clean:
            continue
        if name_clean.lower() in text_lower:
            keys = [
                f"item='{name_clean}'", f'item="{name_clean}"',
                f"npc='{name_clean}'", f'npc="{name_clean}"',
                f"location='{name_clean}'", f'location="{name_clean}"',
                f"faction='{name_clean}'", f'faction="{name_clean}"',
                f"event='{name_clean}'", f'event="{name_clean}"'
            ]
            if any(k.lower() in text_lower for k in keys):
                continue
            try:
                if re.search(r'\b' + re.escape(name_clean) + r'\b', text, re.IGNORECASE):
                    return True
            except Exception:
                pass
    return False


def get_all_linkable_entities(service: Any, world_id: str) -> dict[str, str]:
    already_investigated = {}
    try:
        with service.connect() as conn:
            for row in conn.execute("SELECT name, entity_type FROM entities WHERE world_id = ?", (world_id,)).fetchall():
                if row["name"]:
                    already_investigated[row["name"]] = row["entity_type"]
            for row in conn.execute("SELECT entity_name, entity_type FROM pregenerated_investigations WHERE world_id = ?", (world_id,)).fetchall():
                if row["entity_name"] and row["entity_name"] not in already_investigated:
                    already_investigated[row["entity_name"]] = row["entity_type"]
    except Exception:
        pass
    return already_investigated


def extract_proper_nouns_with_llm(client: Any, text: str) -> list[str]:
    """Query the local Qwen model to parse out all proper nouns, named entities,
    or unique fantasy jargon that might need a compendium entry.
    """
    if not client or not text or not text.strip():
        return []
    
    prompt = f"""You are a narrative RPG assistant. Analyze the following story text and identify all key characters, locations, factions, items, lore events, or mysterious concepts that are central to the narrative or might need an explanatory compendium entry for the player.

CRITICAL RULES:
1. Extract the EXACT, full names or noun phrases as they appear in the text (e.g. "Tessaly Vorn", "Citadel Vane", "Mark of Treachery"). Do NOT split them into separate words.
2. Only extract terms that are proper nouns, unique names, or unique fantasy jargon. Do NOT extract standard vocabulary words, verbs, pronouns, or common nouns (e.g. do NOT extract "hope", "eyes", "teeth", "face", "sympathy", "silence", "corners", "words", "carriage", "horse", "sword", "rock", "sky").
3. Return a clean, valid JSON list of strings, for example: ["Tessaly Vorn", "Citadel Vane", "Mark of Treachery"].
4. Do NOT include any markdown code fences, reasoning, explanation, or other text outside of the JSON array.

Text to analyze:
\"\"\"{text}\"\"\"
"""
    try:
        from ..config import HAIKU_MODEL
        response = client.messages.create(
            model=HAIKU_MODEL,
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}],
        )
        response_text = "".join(b.text for b in response.content if b.type == "text").strip()
        cleaned = response_text
        if "```json" in cleaned:
            cleaned = cleaned.split("```json", 1)[1].split("```")[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```", 1)[1].split("```")[0].strip()
        
        try:
            data = json.loads(cleaned)
            if isinstance(data, list):
                return [str(item).strip() for item in data if item and str(item).strip()]
        except Exception:
            pass
            
        matches = re.findall(r'["\']([^"\']+)["\']', response_text)
        if matches:
            return [m.strip() for m in matches if m.strip()]
    except Exception as e:
        print(f"Error extracting proper nouns with local AI: {e}")
    return []


def relink_text_with_llm(client: Any, text: str, already_investigated: dict[str, str] | list[str], use_llm: bool = True) -> str:
    """Dynamic AI-driven relinking pass:
    1. Scan narrative using local AI parser to extract all unique named proper nouns.
    2. Check each extracted noun against existing investigated entities/links (using are_names_equivalent).
    3. If matched, connect them. If not, it is registered as a new candidate for pregeneration.
    4. Programmatically apply exact-phrase linkification.
    """
    if not text or not text.strip():
        return text

    # Standardize already_investigated into a clean dict
    vocab = {}
    if isinstance(already_investigated, list):
        for name in already_investigated:
            if name.strip():
                vocab[name.strip()] = "object"
    else:
        for name, etype in already_investigated.items():
            if name.strip():
                vocab[name.strip()] = etype

    # Step 1: Noun extraction pass
    extracted_terms = []
    if use_llm and client is not None:
        try:
            extracted_terms = extract_proper_nouns_with_llm(client, text)
        except Exception as e:
            print(f"Fallback to heuristic proper noun extraction due to: {e}")
            
    if not extracted_terms:
        extracted_terms = extract_heuristic_proper_nouns(text, vocab)

    # Step 2: Separate Connection Checking & Candidate building
    matched_candidates = {}
    for term in extracted_terms:
        term_clean = term.strip()
        if not term_clean:
            continue
            
        matched_canonical = None
        matched_type = "object"
        
        for name, etype in vocab.items():
            if are_names_equivalent(term_clean, name):
                matched_canonical = name
                matched_type = etype
                break
                
        if matched_canonical:
            matched_candidates[term_clean.lower()] = (matched_canonical, matched_type)
        elif use_llm:
            matched_candidates[term_clean.lower()] = (term_clean, "object")

    # Step 3: Targeted Exact-phrase linkification
    if not matched_candidates:
        return text

    sorted_candidates = sorted(matched_candidates.items(), key=lambda x: len(x[0]), reverse=True)
    tag_pattern = re.compile(r"(<investigate\s+[^>]*?>.*?</investigate>)", re.DOTALL)
    type_attr_map = {"character": "npc", "location": "location", "faction": "faction", "object": "item", "event": "event"}

    for match_phrase, (canonical, etype) in sorted_candidates:
        attr = type_attr_map.get(etype, "item")
        escaped = re.escape(match_phrase)
        
        # Match plurals/singulars
        base = (escaped[:-2] + '(?:es)?') if match_phrase.endswith('es') else ((escaped[:-1] + 's?') if match_phrase.endswith('s') else escaped)
        has_art = any(match_phrase.startswith(art) for art in ["the ", "a ", "an "])
        prefix = "" if has_art else r"(?:[Tt]he\s+|[Aa]\s+|[Aa]n\s+)??"
        
        if " " in match_phrase:
            pattern = re.compile(r"\b(" + prefix + base + r"(?:s|es)?)\b", re.IGNORECASE)
        else:
            base_capitalized = match_phrase[0].upper() + match_phrase[1:]
            base_escaped = re.escape(base_capitalized)
            base_final = (base_escaped[:-2] + '(?:es)?') if base_capitalized.endswith('es') else ((base_escaped[:-1] + 's?') if base_capitalized.endswith('s') else base_escaped)
            pattern = re.compile(r"\b(" + prefix + base_final + r"(?:s|es)?)\b")

        parts = tag_pattern.split(text)
        for i in range(len(parts)):
            if not parts[i].startswith("<investigate"):
                parts[i] = pattern.sub(f"<investigate {attr}='{canonical.lower()}' cost='1'>\\1</investigate>", parts[i])
        text = "".join(parts)

    return text


def relink_text_programmatically(text: str, already_investigated: dict[str, str] | list[str]) -> str:
    """Exact-phrase programmatic relinker mapping text references to compendium entity cards.
    Fully gets rid of the stop-words system and leverages the targeted extraction/checking pass.
    """
    return relink_text_with_llm(None, text, already_investigated, use_llm=False)


def extract_heuristic_proper_nouns(text: str, already_investigated: dict[str, str] | None = None) -> list[str]:
    """Scan text to extract potential proper nouns (Title Case sequences) left untagged by LLM."""
    if not text or not text.strip():
        return []
    
    tag_pattern = re.compile(r"<investigate\s+[^>]*?>.*?</investigate>", re.DOTALL)
    clean_text = tag_pattern.sub(" ", text)
    sentences = re.split(r'(?<=[.!?])\s+', clean_text)
    proper_nouns = []
    
    vocab_lower = {name.lower() for name in already_investigated} if already_investigated else set()
    
    for sentence in sentences:
        if not sentence.strip():
            continue
        matches = re.findall(r'\b([A-Z][a-zA-Z]+(?:\s+(?:of|on|at|the|and)\s+[A-Z][a-zA-Z]+|\s+[A-Z][a-zA-Z]+)*)\b', sentence)
        for m in matches:
            m_clean = m.strip()
            
            # If it's a multi-word sequence, also extract individual capitalized words that do not start the sentence
            if " " in m_clean:
                words = [w.strip() for w in re.split(r'\s+', m_clean) if w.strip()]
                for w in words[1:]:
                    if w and w[0].isupper() and len(w) >= 3:
                        proper_nouns.append(w)
            
            if m_clean.lower() in {
                "the", "this", "that", "there", "when", "then", "what", "where", "how", "who", "whom", "you", 
                "they", "some", "here", "with", "from", "once", "and", "but", "for", "yet", "soon",
                "suddenly", "meanwhile", "finally", "eventually"
            }:
                continue
            
            sentence_start = re.sub(r'^[^a-zA-Z]+', '', sentence.strip())
            if sentence_start.startswith(m_clean):
                if " " not in m_clean and m_clean.lower() not in vocab_lower:
                    continue
                    
            if len(m_clean) >= 3:
                proper_nouns.append(m_clean)
    return list(set(proper_nouns))


def extract_investigate_tags(text: str) -> list[tuple[str, str]]:
    if not text:
        return []
    results = []
    for m in _INV_RE.finditer(text):
        attrs, display = m.group(1), m.group(2).strip()
        item_name, entity_type = "", "object"
        item_matches = list(re.finditer(r"(item|npc|location|faction|event)=(['\"])(.*?)\2", attrs)) or list(re.finditer(r"(item|npc|location|faction|event)=([^\s'\">]+)", attrs))
        for am in item_matches:
            grp_cnt = len(am.groups())
            item_name = am.group(3) if grp_cnt >= 3 else am.group(2)
            t = am.group(1)
            entity_type = "character" if t == "npc" else (t if t in ("location", "faction", "event") else "object")
        name = (item_name or display).strip()
        if name:
            results.append((name, entity_type))
    return results


def get_name_variants(name: str) -> list[str]:
    name_clean = name.strip().lower()
    variants = {name_clean}
    if name_clean.endswith("s"):
        if name_clean.endswith("es"):
            variants.add(name_clean[:-2])
        variants.add(name_clean[:-1])
    else:
        variants.add(name_clean + "s")
        variants.add(name_clean + "es")
    return list(variants)
