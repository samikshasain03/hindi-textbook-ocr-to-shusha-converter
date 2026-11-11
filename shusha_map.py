"""Starter Unicode-to-Shusha mapping for the Shusha 1.5 font.

Reference: James Kass's table for Shusha 1.5, dated 25 May 1997:
https://www.unicode.org/mail-arch/unicode-ml/y2001-m11/0258.html

This is a reference-based starting map, not a complete converter. It has not
been visually checked against the font used by the intended user yet.
"""

# Record the version so we do not accidentally mix different Shusha layouts.
SHUSHA_VERSION = "1.5 (25 May 1997)"

# Left side: Unicode Hindi. Right side: characters to display in Shusha.
# For example, UNICODE_TO_SHUSHA["ग"] returns "ga".
# These are font keys, not English spellings or pronunciations.
UNICODE_TO_SHUSHA = {
    # Vowels: these can stand on their own, unlike matras.
    "अ": "A",
    "आ": "Aa",
    "इ": "[",
    # The source gives byte 154 for ई. Here we assume Windows-1252 (š).
    # This extended character especially needs a check with the actual font.
    "ई": "š",
    "उ": "]",
    "ऊ": "}",
    "ऋ": "?",
    "ऍ": "e^",
    "ए": "e",
    "ऐ": "eo",
    "ऑ": "Aa^",
    "ओ": "Aao",
    "औ": "AaO",

    # Consonants: some full letters need more than one Shusha character.
    "क": "k",
    "ख": "K",
    "ग": "ga",
    "घ": "Ga",
    "ङ": "=",
    "च": "ca",
    "छ": "C",
    "ज": "ja",
    "झ": "Ja",
    "ञ": "Ha",
    "ट": "T",
    "ठ": "z",
    "ड": "D",
    "ढ": "Z",
    "ण": "Na",
    "त": "t",
    "थ": "qa",
    "द": "d",
    "ध": "Qa",
    "न": "na",
    "प": "p",
    "फ": "f",
    "ब": "ba",
    "भ": "Ba",
    "म": "ma",
    "य": "ya",
    "र": "r",
    "ल": "la",
    "व": "va",
    # The source gives characters 207 + 97 for श: Ï + a.
    "श": "Ïa",
    "ष": "Ya",
    "स": "sa",
    "ह": "h",

    # Matras: converter.py will decide where to place them.
    # In particular, ि must move before the relevant letter or joined group.
    "ा": "a",
    "ि": "i",
    "ी": "I",
    "ु": "u",
    "ू": "U",
    "ृ": "R",
    "ॅ": "^",
    "े": "o",
    "ै": "O",
    # These three are assembled from the component matra keys above.
    "ॉ": "a^",
    "ो": "ao",
    "ौ": "aO",

    # Marks: ़ adds a dot, while ् removes the consonant's vowel sound.
    # The converter must handle their position and context before using them.
    "ँ": "Ð",
    "ं": "M",
    "ः": "Á",
    "़": ",",
    "्": "\\",
    "ॐ": "!",

    # Common joined letters with their own documented Shusha sequences.
    # Later, the converter must check these before matching single letters.
    "क्ष": "xa",
    "त्र": "~",
    "ज्ञ": "&",
    "श्र": "Ea",

    # Hindi numbers: these keys display Devanagari digits in the target font.
    "०": "0",
    "१": "1",
    "२": "2",
    "३": "3",
    "४": "4",
    "५": "5",
    "६": "6",
    "७": "7",
    "८": "8",
    "९": "9",

    # Hindi sentence-ending marks.
    "।": ".",
    "॥": "..",

    # Keep gaps and line breaks between words and paragraphs.
    " ": " ",
    "\n": "\n",
    "\t": "\t",
}

# These half-letter keys come from the same reference's C + halant + ZWJ rows.
# The converter uses them inside ordinary joined groups as well.
HALF_FORMS = {
    "क": "@", "ख": "#", "ग": "g", "घ": "G", "च": "c",
    "ज": "j", "झ": "J", "ञ": "H", "ण": "N", "त": "%",
    "थ": "q", "ध": "Q", "न": "n", "प": "P", "फ": "F",
    "ब": "b", "भ": "B", "म": "m", "य": "y", "ल": "l",
    "व": "v", "श": "Ï", "ष": "Y", "स": "s", "ह": "*",
}

# Whole joined groups with documented glyphs. We omit ambiguous placeholder rows.
JOINED_FORMS = {
    "क्ष": "xa", "त्र": "~", "ज्ञ": "&", "श्र": "Ea",
    "क्त": ">", "क्र": "Ë", "ख्र": "K`", "त्त": "<a",
    "द्द": "_", "द्ध": "w", "द्य": "V", "द्व": "W",
    "न्न": "Ù", "प्र": "p`", "फ्र": "Í", "ह्य": "(",
}
HALF_JOINED_FORMS = {"क्ष": "x", "त्त": "<", "श्र": "E"}

# Nukta letters supported explicitly by the reference (stored decomposed).
# Other nukta combinations stay Unicode rather than being guessed.
NUKTA_FORMS = {"ख़": "Ó", "ग़": "ga,", "ज़": "ja,", "फ़": "Ô"}

# These special vowel combinations have their own documented glyphs.
SPECIAL_SYLLABLES = {"रु": "É", "रू": "$", "हृ": ")"}

# Reph (र् at the start of a syllable) is not documented reliably in this
# reference. The converter keeps those syllables in Unicode with a warning.
