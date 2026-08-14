"""Synthetic fixtures for focused Phase-8 deterministic acceptance tests."""
from __future__ import annotations
import copy, hashlib
from simulation.runtime.gumas_command_policy import policy as cp
from simulation.runtime.gumas_damage_disposition import kernel as p7
from simulation.runtime.gumas_damage_disposition.normalization import normalizer_source_identity
from simulation.runtime.gumas_movement_geometry.kernel import _hash_without_field as state_hash
from simulation.runtime.gumas_morale_resolution.kernel import canonical_json_bytes, step_phase8_state


def baseline():
    return {"baseline_id":"test-phase8","version":"1.0","sides":{"loyalist":{"fleet_id":"F-L"},"rebel":{"fleet_id":"F-R"}}}


def vessel(ship, side, fleet, *, disposition="combat_capable", hull=1000, morale=900, cohesion=900, position=None, velocity=None, propulsion=1000, weapons=1000):
    return {"ship_id":ship,"side_id":side,"fleet_id":fleet,"position_um":list(position or [0,0,0]),"velocity_um_s":list(velocity or [0,0,0]),"physical":{"shield_capacity_milliunits":1000,"shield_current_milliunits":1000,"armor_integrity_milliunits":1000,"armor_current_milliunits":1000,"hull_integrity_milliunits":1000,"hull_current_milliunits":hull},"readiness_q1000":{"overall":1000,"sensors":1000,"ew":1000,"propulsion":propulsion,"weapons":weapons,"damage_control":1000},"morale_q1000":morale,"cohesion_q1000":cohesion,"damage_state":"undamaged" if hull==1000 else "major_damage","disposition":disposition}


def state(*, elapsed=100000, macrostep=10, vessels=None):
    s={"schema":"aurora://simulation/gumas/phase7-test-state/v1","macrostep_index":macrostep,"elapsed_ms":elapsed,"vessels":vessels or [vessel("L1","loyalist","F-L"),vessel("L2","loyalist","F-L"),vessel("R1","rebel","F-R"),vessel("R2","rebel","F-R")]}
    s["vessels"]=sorted(s["vessels"],key=lambda x:x["ship_id"]); s["state_sha256"]=state_hash(s,"state_sha256"); return s


def damage(ship, *, hull_loss=0, before="combat_capable", after="combat_capable"):
    return {"target_ship_id":ship,"hull":{"lost":hull_loss,"new_hull_loss_q1000":hull_loss},"physical_disposition":{"before":before,"after":after}}


def phase7_receipt(s, receipts=(), effect_count=0):
    core=p7._source_identity(); norm=normalizer_source_identity(); composite=hashlib.sha256(canonical_json_bytes({"damage_core_source_identity":core,"semantic_normalizer_source_identity":norm})).hexdigest()
    r={"schema":"aurora://simulation/gumas/phase7_step_receipt/v1.0","phase7_source_identity":core,"phase7_semantic_normalizer_source_identity":norm,"phase7_composite_source_sha256":composite,"next_state_sha256":s["state_sha256"],"effect_count":effect_count,"target_damage_receipts":list(receipts),"morale_mutated":False,"cohesion_mutated":False,"termination_decision_made":False}
    r["phase7_receipt_sha256"]=p7._hash_without_field(r,"phase7_receipt_sha256"); return r


def decision(side, fleet, posture="HOLD", *, dissent=0, resolve="mid", withdrawal_viability=500):
    src=cp._source_identity()
    cmd={"command_skill":500,"discipline":500,"casualty_aversion":500,"negotiation_openness":500}
    if resolve=="high": cmd={"command_skill":1000,"discipline":1000,"casualty_aversion":0,"negotiation_openness":0}
    if resolve=="low": cmd={"command_skill":0,"discipline":0,"casualty_aversion":1000,"negotiation_openness":1000}
    p={"policy_source_sha256":src["bundle_sha256"],"policy_module_sha256":src["policy_module_sha256"],"coefficient_table_sha256":src["coefficient_table_sha256"],"baseline_identity":{"baseline_id":"test-phase8","baseline_version":"1.0"},"side_id":side,"fleet_id":fleet,"observation":{"withdrawal_viability":withdrawal_viability},"command_team_numeric":{"commander":{"attributes_q1000":cmd}},"specialists":{role:{"dissent_q1000":dissent} for role in cp.ROLE_ORDER},"orders":{"strategic_posture":posture,"specialist_intents":{}}}
    p["decision_sha256"]=cp.sha256_canonical(p); return p


def commands(lp="HOLD", rp="HOLD", **kw):
    return {"F-L":decision("loyalist","F-L",lp,**kw),"F-R":decision("rebel","F-R",rp,**kw)}


def run(s=None, r=None, c=None, prior=None):
    s=s or state(); r=r or phase7_receipt(s); c=c or commands(); return step_phase8_state(s,r,c,baseline(),prior)
