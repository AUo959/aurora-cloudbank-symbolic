"""Vessel registry accessors (modularized)."""
from __future__ import annotations

from typing import Optional

from .oppy import OPPYNavigator
from .aurora_subcore import AuroraSubCore

__all__ = [
    "get_constancy_oppy",
    "get_constancy_athena",
    "get_helios_oppy",
    "get_helios_helion",
    "get_liora_oppy",
    "get_liora_ai",
    "get_archimedes_oppy",
    "get_archimedes_daedalus",
    "get_pioneer_oppy",
    "get_pioneer_mercury",
    "get_lacewing_oppy",
    "get_lacewing_lyra",
]


# Global instances for Constancy
_constancy_oppy: Optional[OPPYNavigator] = None
_constancy_athena: Optional[AuroraSubCore] = None


def get_constancy_oppy() -> OPPYNavigator:
    global _constancy_oppy
    if _constancy_oppy is None:
        _constancy_oppy = OPPYNavigator(vessel_id="ORF-01")
    return _constancy_oppy



def get_constancy_athena() -> AuroraSubCore:
    global _constancy_athena
    if _constancy_athena is None:
        _constancy_athena = AuroraSubCore(subcore_id="AURORA_SUB_B", vessel_id="ORF-01")
    return _constancy_athena


# Global instances for Helios
_helios_oppy: Optional[OPPYNavigator] = None
_helios_helion: Optional[AuroraSubCore] = None


def get_helios_oppy() -> OPPYNavigator:
    global _helios_oppy
    if _helios_oppy is None:
        _helios_oppy = OPPYNavigator(vessel_id="ORS-01")
    return _helios_oppy



def get_helios_helion() -> AuroraSubCore:
    global _helios_helion
    if _helios_helion is None:
        _helios_helion = AuroraSubCore(subcore_id="AURORA_SUB_HELIOS", vessel_id="ORS-01")
    return _helios_helion


# Global instances for Liora
_liora_oppy: Optional[OPPYNavigator] = None
_liora_ai: Optional[AuroraSubCore] = None


def get_liora_oppy() -> OPPYNavigator:
    global _liora_oppy
    if _liora_oppy is None:
        _liora_oppy = OPPYNavigator(vessel_id="ORS-02")
    return _liora_oppy



def get_liora_ai() -> AuroraSubCore:
    global _liora_ai
    if _liora_ai is None:
        _liora_ai = AuroraSubCore(subcore_id="AURORA_SUB_LIORA", vessel_id="ORS-02")
    return _liora_ai


# Global instances for Archimedes
_archimedes_oppy: Optional[OPPYNavigator] = None
_archimedes_daedalus: Optional[AuroraSubCore] = None


def get_archimedes_oppy() -> OPPYNavigator:
    global _archimedes_oppy
    if _archimedes_oppy is None:
        _archimedes_oppy = OPPYNavigator(vessel_id="ORS-03")
    return _archimedes_oppy



def get_archimedes_daedalus() -> AuroraSubCore:
    global _archimedes_daedalus
    if _archimedes_daedalus is None:
        _archimedes_daedalus = AuroraSubCore(subcore_id="AURORA_SUB_DAEDALUS", vessel_id="ORS-03")
    return _archimedes_daedalus


# Global instances for Pioneer
_pioneer_oppy: Optional[OPPYNavigator] = None
_pioneer_mercury: Optional[AuroraSubCore] = None


def get_pioneer_oppy() -> OPPYNavigator:
    global _pioneer_oppy
    if _pioneer_oppy is None:
        _pioneer_oppy = OPPYNavigator(vessel_id="ORS-04")
    return _pioneer_oppy



def get_pioneer_mercury() -> AuroraSubCore:
    global _pioneer_mercury
    if _pioneer_mercury is None:
        _pioneer_mercury = AuroraSubCore(subcore_id="AURORA_SUB_MERCURY", vessel_id="ORS-04")
    return _pioneer_mercury


# Global instances for Lacewing
_lacewing_oppy: Optional[OPPYNavigator] = None
_lacewing_lyra: Optional[AuroraSubCore] = None


def get_lacewing_oppy() -> OPPYNavigator:
    global _lacewing_oppy
    if _lacewing_oppy is None:
        _lacewing_oppy = OPPYNavigator(vessel_id="ORS-05")
    return _lacewing_oppy



def get_lacewing_lyra() -> AuroraSubCore:
    global _lacewing_lyra
    if _lacewing_lyra is None:
        _lacewing_lyra = AuroraSubCore(subcore_id="AURORA_SUB_LYRA", vessel_id="ORS-05")
    return _lacewing_lyra
