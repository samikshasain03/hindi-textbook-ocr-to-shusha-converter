"""Convert Hindi to the project's Shusha profile, preserving unsupported text.

A font run is a piece of text that needs one font. This lets the screen and
Word download keep English and unsupported Hindi readable alongside Shusha.
"""

from dataclasses import dataclass, field
import unicodedata

from shusha_map import (
    HALF_FORMS, HALF_JOINED_FORMS, JOINED_FORMS, NUKTA_FORMS,
    SPECIAL_SYLLABLES, UNICODE_TO_SHUSHA,
)


@dataclass
class TextRun:
    text: str
    font: str  # "shusha" or "unicode"


@dataclass
class ConversionResult:
    text: str = ""
    runs: list[TextRun] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    unsupported: list[str] = field(default_factory=list)


def _is_consonant(char):
    return "\u0915" <= char <= "\u0939" or "\u0958" <= char <= "\u095f"


def _is_hindi(char):
    return "\u0900" <= char <= "\u097f"


def _syllable_end(text, start):
    """Keep a consonant group and its matras together for safe conversion."""
    end = start + 1
    while end < len(text):
        char = text[end]
        if char == "़":
            end += 1
        elif char == "्":
            end += 1
            if end < len(text) and text[end] in ("\u200c", "\u200d"):
                joiner = text[end]
                end += 1
                if joiner == "\u200c":  # ZWNJ asks for a visible halant.
                    break
            if end < len(text) and _is_consonant(text[end]):
                end += 1
            else:
                break
        elif _is_hindi(char) and unicodedata.category(char).startswith("M"):
            end += 1
        else:
            break
    return end


def _encode_syllable(original):
    """Return Shusha keys, or None when the whole syllable needs review."""
    syllable = unicodedata.normalize("NFD", original)

    # We cannot safely invent a key for reph from the available reference.
    if syllable.startswith("र्") and len(syllable) > 2 and syllable[2] not in "\u200c\u200d":
        return None

    if syllable in SPECIAL_SYLLABLES:
        return SPECIAL_SYLLABLES[syllable]

    # Keep a dedicated vowel glyph when nasal/visarga marks follow it.
    for special, glyph in SPECIAL_SYLLABLES.items():
        if syllable.startswith(special):
            ending = syllable[len(special):]
            if ending and all(mark in "ँंः" for mark in ending):
                return glyph + "".join(UNICODE_TO_SHUSHA[mark] for mark in ending)

    # Independent vowels do not need consonant-group reordering.
    if not _is_consonant(syllable[0]):
        if any(char not in UNICODE_TO_SHUSHA for char in syllable):
            return None
        return "".join(UNICODE_TO_SHUSHA[char] for char in syllable)

    units = []
    index = 0
    terminal_halant = False
    explicit_half = False
    while index < len(syllable) and _is_consonant(syllable[index]):
        unit = syllable[index]
        index += 1
        if index < len(syllable) and syllable[index] == "़":
            unit += "़"
            index += 1
        units.append(unit)
        if index >= len(syllable) or syllable[index] != "्":
            break
        index += 1
        joiner = ""
        if index < len(syllable) and syllable[index] in "\u200c\u200d":
            joiner = syllable[index]
            index += 1
        if joiner == "\u200c" or index == len(syllable) or not _is_consonant(syllable[index]):
            terminal_halant = True
            explicit_half = joiner == "\u200d"
            break

    marks = syllable[index:]
    # Preserve unusual or malformed combinations for human review.
    vowels = "ािीुूृॅेैॉोौ"
    if any(char not in vowels + "ँंः" for char in marks):
        return None
    if sum(char in vowels for char in marks) > 1 or (terminal_halant and any(char in vowels for char in marks)):
        return None

    keys = ""
    position = 0
    # An internal ZWJ explicitly requests a half form instead of a ligature.
    requested_half = any(syllable[i] == "\u200d" and _is_consonant(syllable[i + 1])
                         for i in range(len(syllable) - 1))
    while position < len(units):
        remainder = "्".join(units[position:])
        if not terminal_halant and not requested_half and remainder in JOINED_FORMS:
            keys += JOINED_FORMS[remainder]
            break
        if terminal_halant and explicit_half and remainder in HALF_JOINED_FORMS:
            keys += HALF_JOINED_FORMS[remainder]
            break
        unit = units[position]
        needs_half = position < len(units) - 1 or (terminal_halant and explicit_half)
        if needs_half:
            if unit not in HALF_FORMS:
                return None
            keys += HALF_FORMS[unit]
        else:
            value = NUKTA_FORMS.get(unit) if "़" in unit else UNICODE_TO_SHUSHA.get(unit)
            if value is None:
                return None
            keys += value
            if terminal_halant:
                keys += "\\"
        position += 1

    # Short-i is typed before the entire joined group in this legacy font.
    if "ि" in marks:
        keys = "i" + keys
    for mark in marks:
        if mark != "ि":
            keys += UNICODE_TO_SHUSHA[mark]
    return keys


def convert_to_shusha(text):
   
    result = ConversionResult()

    def append(value, font):
        # Merge neighbouring pieces that need the same font.
        if result.runs and result.runs[-1].font == font:
            result.runs[-1].text += value
        else:
            result.runs.append(TextRun(value, font))

    index = 0
    while index < len(text):
        char = text[index]
        if _is_consonant(char) or ("\u0904" <= char <= "\u0914"):
            end = _syllable_end(text, index)
            original = text[index:end]
            encoded = _encode_syllable(original)
            if encoded is None:
                append(original, "unicode")
                if original not in result.unsupported:
                    result.unsupported.append(original)
            else:
                append(encoded, "shusha")
            index = end
        elif char in "।॥ॐ" or "०" <= char <= "९":
            append(UNICODE_TO_SHUSHA[char], "shusha")
            index += 1
        else:
            # English, ASCII punctuation, digits, and whitespace stay readable.
            append(char, "unicode")
            if _is_hindi(char) or char in "\u200c\u200d":
                if char not in result.unsupported:
                    result.unsupported.append(char)
            index += 1

    result.text = "".join(run.text for run in result.runs)
    if result.unsupported:
        result.warnings.append(
            "Some Hindi groups were kept in Unicode because this font profile "
            "has no verified conversion for them: " + ", ".join(result.unsupported)
        )
    return result
