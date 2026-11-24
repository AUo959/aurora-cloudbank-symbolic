"""Tolkien-style diachronic phonology for GUMAS names.

Layers (each separately testable):

* ``segments``  - phonemes as feature bundles; parsing and feature shifts
* ``syllables`` - onset-maximizing syllabification and phonotactic checks
* ``rules``     - words as segment/boundary streams, stress, data-defined sound laws
* ``lexicon``   - roots, radicals with ablaut grades, suffixes, lineage classes
* ``engine``    - profile loading, chronology and dialects, orthography, generation
* ``phonaesthetics`` - a bigram sound model trained on canon names
* ``analysis``  - reverse derivation, loan classification, blind recovery

Language data lives in ``profiles/<name>/`` as JSON (inventory, chronology,
lexicon, attested). The engine is language-neutral; Velari is the first profile.
"""

from .engine import COMMON, ENGINE_VERSION, Derivation, Engine, Profile, load_profile, shared_roots

__all__ = ["COMMON", "ENGINE_VERSION", "Derivation", "Engine", "Profile", "load_profile", "shared_roots"]
