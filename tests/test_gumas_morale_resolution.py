from __future__ import annotations
import copy
import pytest
from simulation.runtime.gumas_morale_resolution.constants import HARD_LIMIT_MS, WITHDRAWAL_BOUNDARY_UM
from simulation.runtime.gumas_morale_resolution.kernel import Phase8Error
from simulation.runtime.gumas_morale_resolution.test_support import baseline, commands, damage, decision, phase7_receipt, run, state, vessel
pytestmark=pytest.mark.unit


def test_quiet_replay_and_dissent_inert_without_shock():
    s=state(); c=commands(dissent=1000)
    a=run(s,phase7_receipt(s),c); b=run(copy.deepcopy(s),phase7_receipt(copy.deepcopy(s)),copy.deepcopy(c))
    assert a==b
    _,r,receipt=a
    assert receipt["morale_or_cohesion_mutated"] is False
    assert r["shock_by_side"]["loyalist"]["battle_shock_q1000"]==0
    assert r["dissent_by_side"]["loyalist"]["shock_coupled_dissent_q1000"]==0
    assert r["terminal_outcome"]["termination_mode"]=="ongoing"


def test_hull_loss_and_incapacity_reduce_morale_cohesion():
    s=state(vessels=[vessel("L1","loyalist","F-L",hull=700),vessel("L2","loyalist","F-L",disposition="disabled",hull=100,propulsion=100,weapons=100),vessel("R1","rebel","F-R"),vessel("R2","rebel","F-R")])
    dr=[damage("L1",hull_loss=300),damage("L2",hull_loss=900,before="degraded",after="disabled")]
    nxt,r,_=run(s,phase7_receipt(s,dr,2),commands())
    before={v["ship_id"]:v for v in s["vessels"]}; after={v["ship_id"]:v for v in nxt["vessels"]}
    assert after["L1"]["morale_q1000"]<before["L1"]["morale_q1000"]
    assert after["L1"]["cohesion_q1000"]<before["L1"]["cohesion_q1000"]
    assert r["shock_by_side"]["loyalist"]["new_incapacity_q1000"]>0


def test_ceasefire_offer_persists_press_rescinds_and_mutual_terminates():
    s=state(macrostep=5); _,r1,_=run(s,phase7_receipt(s),commands(lp="CEASEFIRE_PROBE",rp="HOLD"))
    assert r1["active_ceasefire_offer_by_side"]["loyalist"] and not r1["terminal_outcome"]["terminated"]
    s2=state(macrostep=6); _,r2,_=run(s2,phase7_receipt(s2),commands(),r1); assert r2["active_ceasefire_offer_by_side"]["loyalist"]
    s3=state(macrostep=7); _,r3,_=run(s3,phase7_receipt(s3),commands(lp="PRESS"),r2); assert not r3["active_ceasefire_offer_by_side"]["loyalist"]
    _,rm,_=run(c=commands(lp="CEASEFIRE_PROBE",rp="CEASEFIRE_PROBE"))
    assert rm["terminal_outcome"]["termination_mode"]=="mutual_ceasefire" and rm["terminal_outcome"]["victor_side_id"] is None
    assert len(rm["protected_ship_ids"])==4


def test_mutual_disengagement_requires_two_effect_free_steps():
    s=state(macrostep=10); _,r1,_=run(s,phase7_receipt(s),commands(lp="DISENGAGE",rp="DISENGAGE"))
    assert r1["mutual_disengage_streak"]==1 and not r1["terminal_outcome"]["terminated"]
    s2=state(macrostep=11); _,r2,_=run(s2,phase7_receipt(s2),commands(lp="DISENGAGE",rp="DISENGAGE"),r1)
    assert r2["terminal_outcome"]["termination_mode"]=="mutual_disengagement" and r2["terminal_outcome"]["victor_side_id"] is None


def test_withdrawal_requires_intent_boundary_outbound_threshold_no_false_winner():
    b=WITHDRAWAL_BOUNDARY_UM
    vs=[vessel("L1","loyalist","F-L",position=[b,0,0],velocity=[1,0,0]),vessel("L2","loyalist","F-L",position=[b+1,0,0],velocity=[1,0,0]),vessel("R1","rebel","F-R"),vessel("R2","rebel","F-R")]
    s=state(vessels=vs); _,hold,_=run(s,phase7_receipt(s),commands()); assert not hold["withdrawal_by_side"]["loyalist"]["success"]
    _,d,_=run(s,phase7_receipt(s),commands(lp="DISENGAGE")); o=d["terminal_outcome"]
    assert d["withdrawal_by_side"]["loyalist"]["withdrawn_mobile_fraction_q1000"]==1000
    assert o["termination_mode"]=="successful_withdrawal" and o["victor_side_id"] is None and o["local_control_side_id"]=="rebel"


def test_inward_or_insufficient_fraction_does_not_withdraw():
    b=WITHDRAWAL_BOUNDARY_UM
    s=state(vessels=[vessel("L1","loyalist","F-L",position=[b,0,0],velocity=[-1,0,0]),vessel("L2","loyalist","F-L",position=[b,0,0],velocity=[1,0,0]),vessel("R1","rebel","F-R"),vessel("R2","rebel","F-R")])
    _,r,_=run(s,phase7_receipt(s),commands(lp="DISENGAGE")); assert r["withdrawal_by_side"]["loyalist"]["withdrawn_mobile_fraction_q1000"]==500 and not r["terminal_outcome"]["terminated"]


def test_surrender_needs_posture_and_resolve_threshold_is_monotonic():
    s=state(vessels=[vessel("L1","loyalist","F-L",disposition="degraded",hull=400,morale=100,cohesion=100),vessel("L2","loyalist","F-L",disposition="disabled",hull=400,morale=100,cohesion=100,propulsion=100,weapons=100),vessel("R1","rebel","F-R"),vessel("R2","rebel","F-R")])
    _,press,_=run(s,phase7_receipt(s),commands(lp="PRESS",withdrawal_viability=0)); assert not press["surrender_by_side"]["loyalist"]["predicate"]
    low={"F-L":decision("loyalist","F-L","CEASEFIRE_PROBE",resolve="low",withdrawal_viability=0),"F-R":decision("rebel","F-R","HOLD")}
    high={"F-L":decision("loyalist","F-L","CEASEFIRE_PROBE",resolve="high",withdrawal_viability=0),"F-R":decision("rebel","F-R","HOLD")}
    _,rl,_=run(s,phase7_receipt(s),low); _,rh,_=run(s,phase7_receipt(s),high)
    assert rl["surrender_by_side"]["loyalist"]["surrender_threshold_q1000"]<rh["surrender_by_side"]["loyalist"]["surrender_threshold_q1000"]
    assert rl["surrender_by_side"]["loyalist"]["predicate"] and rl["terminal_outcome"]["victor_side_id"]=="rebel"


def test_incapacity_and_annihilation_are_distinct():
    inc=state(vessels=[vessel("L1","loyalist","F-L",disposition="disabled",hull=100,propulsion=100,weapons=100),vessel("L2","loyalist","F-L",disposition="disabled",hull=100,propulsion=100,weapons=100),vessel("R1","rebel","F-R"),vessel("R2","rebel","F-R")])
    _,ri,_=run(inc,phase7_receipt(inc),commands()); assert ri["terminal_outcome"]["termination_mode"]=="combat_incapacity" and not ri["terminal_outcome"]["annihilated_side_ids"]
    ann=state(vessels=[vessel("L1","loyalist","F-L",disposition="destroyed",hull=0,propulsion=0,weapons=0),vessel("L2","loyalist","F-L",disposition="destroyed",hull=0,propulsion=0,weapons=0),vessel("R1","rebel","F-R"),vessel("R2","rebel","F-R")])
    _,ra,_=run(ann,phase7_receipt(ann),commands()); assert ra["terminal_outcome"]["termination_mode"]=="annihilation" and ra["terminal_outcome"]["victor_side_id"]=="rebel"


def test_hard_limit_exact():
    early=state(elapsed=HARD_LIMIT_MS-1); _,r1,_=run(early,phase7_receipt(early),commands()); assert not r1["terminal_outcome"]["terminated"]
    exact=state(elapsed=HARD_LIMIT_MS); _,r2,_=run(exact,phase7_receipt(exact),commands()); assert r2["terminal_outcome"]["termination_mode"]=="hard_limit_stalemate" and r2["terminal_outcome"]["victor_side_id"] is None


def test_command_mapping_order_inert_and_bad_phase7_hash_fails_closed():
    s=state(); c=commands(); assert run(s,phase7_receipt(s),c)==run(s,phase7_receipt(s),dict(reversed(list(c.items()))))
    bad=phase7_receipt(s); bad["phase7_receipt_sha256"]="0"*64
    with pytest.raises(Phase8Error): run(s,bad,c)

def _lapse_step(sep_um, k, prior=None, effects=0, range_m=500_000):
    vs=[vessel("L1","loyalist","F-L",weapon_range_m=range_m),vessel("L2","loyalist","F-L",disposition="disabled",weapons=0),
        vessel("R1","rebel","F-R",position=[sep_um,0,0],weapon_range_m=range_m),vessel("R2","rebel","F-R",position=[sep_um,0,0],weapon_range_m=range_m)]
    s=state(elapsed=100000+k*10000,macrostep=10+k,vessels=vs)
    return run(s,phase7_receipt(s,(),effects),commands(),prior)[1]


def _drive(seps, effects=None):
    prior=None; out=[]
    for k,sep in enumerate(seps):
        prior=_lapse_step(sep,k,prior,(effects or {}).get(k,0)); out.append(prior)
        if prior["terminal_outcome"]["terminated"]: break
    return out


def test_contact_broken_after_sustained_out_of_reach_window():
    from simulation.runtime.gumas_morale_resolution.constants import CONTACT_LAPSE_WINDOW_MS
    steps=CONTACT_LAPSE_WINDOW_MS//10000
    far=600_000*1_000_000
    rs=_drive([far+k for k in range(steps+5)])
    assert rs[0]["contact_lapse"]["lapsed_this_step"] is False  # no prior separation yet
    assert all(not r["terminal_outcome"]["terminated"] for r in rs[:-1])
    last=rs[-1]; o=last["terminal_outcome"]
    assert len(rs)==steps+2 and last["contact_lapse"]["lapse_duration_ms"]==CONTACT_LAPSE_WINDOW_MS
    assert o["termination_mode"]=="contact_broken" and o["victor_side_id"] is None and o["stalemate"] is False
    assert set(last["engagement_status_by_side"].values())=={"disengaged"}
    assert last["protected_ship_ids"]==["L1","L2","R1","R2"]


def test_contact_lapse_resets_when_closing_in_reach_or_firing():
    far=600_000*1_000_000
    closing=_drive([far+100-k for k in range(10)])
    assert all(not r["contact_lapse"]["lapsed_this_step"] for r in closing)
    reach=_drive([400_000*1_000_000+k for k in range(10)])
    assert all(not r["contact_lapse"]["out_of_reach"] and not r["contact_lapse"]["lapsed_this_step"] for r in reach)
    fired=_drive([far+k for k in range(6)],effects={3:1})
    assert [r["contact_lapse"]["lapse_started_elapsed_ms"] for r in fired]==[None,110000,110000,None,140000,140000]


def test_contact_lapse_requires_integer_weapon_range():
    with pytest.raises(Phase8Error, match="effective weapon range"):
        _lapse_step(1,0,range_m=None)
