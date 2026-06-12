"""External sensors (L1 environment: outside the station/platform boundary)."""

from src.sensors.external.astronomical import AstronomicalSensor
from src.sensors.external.communications import CommunicationsSensor
from src.sensors.external.deep_space import DeepSpaceSensor
from src.sensors.external.proximity import ProximitySensor
from src.sensors.external.salvage import SalvageCandidate, SalvageSensor

__all__ = [
    "AstronomicalSensor",
    "CommunicationsSensor",
    "DeepSpaceSensor",
    "ProximitySensor",
    "SalvageCandidate",
    "SalvageSensor",
]
