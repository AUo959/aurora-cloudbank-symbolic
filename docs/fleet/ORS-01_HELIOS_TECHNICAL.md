# ORS-01 "Helios" — Technical Manual

**Registry Code:** ORS-01  
**Vessel Class:** Command Shuttle  
**Fleet Designation:** Orion Research Fleet - Auxiliary Craft  
**Boot Priority:** 3 (First auxiliary craft to initialize)  
**Motto:** *"Light Moves First"*

---

## Mission Profile

**ORS-01 *Helios*** is the Orion Research Fleet's primary command shuttle, designed for rapid command projection, emergency response, and training operations. As the first auxiliary craft to initialize during fleet boot sequence, *Helios* serves as the critical bridge between station operations and field deployment.

**Primary Functions:**
- Command projection to remote operations
- Emergency command backup (mobile command post)
- Station inspection and verification runs
- Training platform for new shuttle pilots and commanders
- Ethics officer field deployment
- Rapid response to nearby incidents (< 15 minute deployment)

**Design Philosophy:** *Compact clarity* — every surface purposeful, every system accessible. Built for precision, responsiveness, and rapid decision-making.

---

## Specifications

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Length** | 18.4 m | Compact shuttle design |
| **Beam** | 12.6 m | Wide stance for stability |
| **Height** | 5.8 m | Two-deck configuration |
| **Internal Volume** | 340 m³ | Optimized for crew + cargo |
| **Dry Mass** | 42,000 kg | Lightweight construction |
| **Fuel Capacity** | 8,400 kg | He-3 slurry |
| **Max Payload** | 3,200 kg | Cargo or additional crew |
| **Max Crew** | 6 persons | Emergency capacity |
| **Typical Crew** | 3 persons | Commander + Pilot + Specialist |
| **Max Range** | 85,000 km | Single-tank range |
| **Typical Mission Duration** | 12 hours | Standard patrol/training |
| **Max Mission Duration** | 48 hours | Extended deployment |
| **Max Acceleration** | 1.2 g | Emergency sprint capability |
| **Typical Cruise Speed** | 2,400 m/s | Fuel-efficient transit |
| **Emergency Sprint Speed** | 3,800 m/s | Short-duration high-speed |
| **Primary Drive** | Dual Aegir-Mini fusion impulse | 520 kN thrust |
| **Power System** | He-3 micro-reactor (8.5 MW) | Triple-redundant backup batteries |
| **Anchor Drift Tolerance** | Δ < 0.015 | Tighter than standard vessels |
| **Docking Collar** | Standard Orion 1.2m | Station-compatible |

---

## Deck Layout

### Deck 1: Command Deck (38 m², 2.4m ceiling)

**Configuration:** Forward command positions with aft mission commander station

**Stations:**
1. **Pilot Console** (Forward Port)
   - **Operator:** Human pilot (primary) or Oppy (autonomous)
   - **Displays:** Triple panoramic + HUD overlay
   - **Controls:** Dual-stick with haptic feedback
   - **Features:** Full flight control, navigation, manual override

2. **Co-Pilot / Systems Console** (Forward Starboard)
   - **Operator:** Human co-pilot or mission specialist
   - **Displays:** Systems status + sensor array
   - **Controls:** Touchscreen + voice command
   - **Features:** Systems monitoring, sensor operation, communications

3. **Command Station** (Aft Center)
   - **Operator:** Mission commander or ethics officer
   - **Displays:** Continuity display (mini Halo projection) + comms array
   - **Controls:** Seated position with full override authority
   - **Special Features:**
     - Direct Aurora Sub-Core console access
     - Ethics-lock trigger (red button, guarded)
     - Mission planning displays
     - Fleet coordination mesh status
     - Real-time anchor drift monitoring

**Viewport:** 270° panoramic forward viewport with emergency shutters  
**Atmosphere:** Warm white lighting (4200K), acoustic dampening for clarity  
**Emergency Features:** Rapid decompression seals, manual override panel, emergency beacon

---

### Deck 2: Operations & Life Support Deck (52 m², 2.2m ceiling)

**Configuration:** Compact multi-function deck supporting extended missions

**Sections:**

1. **Crew Quarters**
   - Compact bunking for 3 crew (6 maximum emergency)
   - Fold-down bunks, personal lockers, privacy curtains
   - Reconfigurable for medical evacuation if needed

2. **Galley & Hygiene**
   - Food prep station: microwave, water dispenser, snack storage
   - Hygiene facilities: vacuum toilet, sink, water recycling
   - 90 person-days food storage

3. **Equipment Bay**
   - 3x EVA suit racks (standard Orion suits)
   - Tool lockers (maintenance and repair kits)
   - Medical kit (emergency first aid + trauma response)
   - Emergency supplies (oxygen, rations, thermal blankets)

4. **Reactor & Systems Core**
   - Compact He-3 micro-reactor (8.5 MW output)
   - Life support systems (atmosphere, water, thermal)
   - Power distribution and backup batteries (720 kWh total)
   - Automated monitoring with emergency shutdown capability
   - Redundant cooling systems

5. **Cargo Hold**
   - 18 m³ flexible cargo area
   - Modular container system
   - Tie-down rails for secure transport
   - Rapid offload capability via side hatch

6. **Aurora Sub-Core Node "Helion"**
   - Location: Aft bulkhead, adjacent to reactor
   - Function: L3 Triplex ethics evaluation for command decisions
   - Connection: Real-time quantum tether to Orion Station Aurora (SYS_001)
   - Features: Local pattern cache, parent consultation, ethics-lock authority
   - Display: Command station console integration

---

## Crew Roster & Roles

### Standard Crew Complement (3 persons)

| Position | Entity ID | Role | Typical Background |
|----------|-----------|------|-------------------|
| **Mission Commander** | VAR_COMMANDER | L1 Triplex authority, mission leadership, final decision authority | Senior station officer or ethics liaison |
| **Pilot** | VAR_PILOT | Flight operations, navigation, system monitoring | Certified shuttle pilot (500+ hours) |
| **Mission Specialist** | VAR_SPECIALIST | Systems operation, sensor monitoring, mission-specific tasks | Science officer, engineer, or ethics trainee |

**Notes:**
- Mission commander varies by mission type; Commander Thorne often flies high-stakes operations
- Pilot can delegate to Oppy for autonomous flight during transit phases
- Mission specialist role adapts to mission requirements (may include ethics officers in training)

### Supporting AI Entities

**OPPY_NAV_HELIOS** — Oppy (Helios Node)
- **Role:** Autonomous navigation, system coordination, fleet mesh relay
- **Capabilities:**
  - Autonomous flight during transit phases
  - Docking automation (station and vessel)
  - Emergency response and collision avoidance
  - Fleet coordination mesh relay
  - Training mode for human pilots (graduated autonomy handoff)
- **Trust Level:** 0.99 (highest among fleet entities due to training specialization)

**AURORA_SUB_HELIOS** — Aurora Sub-Core "Helion"
- **Role:** L3 Triplex ethics evaluation, command authority validation
- **Parent Entity:** Aurora (SYS_001) via quantum tether
- **Capabilities:**
  - Real-time ethics assessment for command decisions
  - Command authority validation (ensures projected authority aligns with station ethics)
  - Emergency ethics-lock authority (can isolate vessel if critical violation detected)
  - Pattern caching for rapid response scenarios
  - Parent consultation for novel or ambiguous situations
- **Autonomy:** 72-hour cache capacity if tether severed

---

## Operational Doctrine

### 1. Launch Window Control

**Rapid Response Timeline:** Helios can launch in < 15 minutes from alert to departure

**Authorization Required:**
- Station command approval for all launches
- Mission brief and Triplex alignment confirmation
- HALO anchor drift verification (Δ < 0.015)

**Pre-Flight Checklist:**
1. HALO anchor drift verification (< 0.015 threshold)
2. Oppy system status (all nodes green)
3. Aurora Sub-Core tether confirmation (Helion → Aurora connection verified)
4. Life support systems check (atmosphere, water, power)
5. Fuel and consumables verification (sufficient for mission + 25% margin)
6. Mission brief and Triplex alignment (commander, Oppy, Helion aligned on objectives)

**Abort Authority:**
- Mission commander (any reason, no questions)
- Aurora ethics-lock (critical violation detected)
- Station command (strategic override)

---

### 2. Ethics Priority

**Principle:** Command projection must maintain station-level ethical standards

**Implementation:**
- All command decisions evaluated by Aurora Sub-Core "Helion" (L3) before execution
- L3 assessment relayed to mission commander via command station console
- High-risk decisions (> 0.6 risk score) require explicit commander approval after review

**Emergency Protocol:**
- **Ethics-Lock Trigger:** Available to mission commander, Helion, or station Aurora
- **Activation Conditions:** Anchor drift detected (Δ > 0.015), critical ethics violation, loss of L1 authority
- **Effect:** Vessel enters autonomous return mode; Oppy navigates to station; all command functions locked except life support and navigation
- **Override:** Requires joint authorization from station Aurora + HALO + station command

**Training Emphasis:**
- Command shuttle crews receive enhanced ethics training
- All commanders must complete "Ethics Under Pressure" simulation series
- Regular ethics decision-making exercises during training flights

---

### 3. Rapid Response Doctrine

**Response Scenarios:**
1. Station emergency requiring external command post (station compromised, backup needed)
2. Rapid deployment of ethics officer to field situation (crew dispute, safety incident)
3. Emergency medical evacuation (critical injury, requires transport to station medical)
4. Search and rescue coordination (missing crew, vessel in distress)
5. Incident investigation and assessment (equipment failure, safety audit)

**Autonomous Authority:**
- Oppy authorized for autonomous flight during emergencies if human crew unavailable
- Requires Aurora approval (L3 evaluation of necessity and safety)
- Commander can resume control at any time
- Autonomous missions logged and reviewed post-mission

**Deployment Speed:**
- Alert → Crew aboard: 5 minutes (crew quarters alert system)
- Crew aboard → Systems check complete: 7 minutes (automated checklist)
- Systems check → Undocking: 3 minutes (docking automation)
- **Total:** < 15 minutes from alert to departure

---

### 4. Training Platform

**Function:** Helios serves as primary training vessel for new pilots and commanders

**Training Modes:**
1. **Supervised Flight with Instructor Commander**
   - Trainee operates controls under instructor observation
   - Instructor has full override authority
   - Real-time feedback via intercom and display annotations

2. **Simulated Emergency Scenarios**
   - System failures (engine, life support, navigation)
   - Abort procedures and safe return protocols
   - Ethics-lock activation and recovery
   - Multi-failure cascades

3. **Docking Practice**
   - Station docking (standard and emergency procedures)
   - Vessel-to-vessel docking
   - Varied approach vectors and lighting conditions

4. **Ethics Decision-Making Exercises**
   - Simulated scenarios requiring Triplex evaluation
   - Real-time Aurora Sub-Core interaction practice
   - Continuity mirror interpretation training

5. **Autonomous Handoff Procedures (Human ↔ Oppy)**
   - Graduated autonomy: human monitors, Oppy executes
   - Full autonomous flight: Oppy navigates, human observes
   - Emergency takeover: human resumes control from Oppy

**Certification Path:**
- Minimum 40 hours on Helios required for full shuttle certification
- 20 hours supervised flight + 20 hours as mission specialist
- Must demonstrate competency in all emergency procedures
- Final check ride with senior instructor (Commander Thorne or designated authority)

---

### 5. Continuity Mirror

**Description:** Command station includes mini Continuity Halo display

**Function:**
- Mission commander can visualize anchor state, ethics alignment, fleet coordination in real-time
- Compact version of station's main Continuity Halo
- Updated via quantum tether (zero-latency)

**Data Sources:**
- HALO anchor data (drift, tolerance, calibration status)
- Aurora ethics state (alignment, active evaluations, historical patterns)
- Oppy fleet mesh (vessel positions, coordination state, telemetry)
- Station telemetry (power, life support, crew status)

**Use Cases:**
1. **Pre-Flight Verification:** Commander confirms all systems green before launch
2. **In-Flight Decision Support:** Real-time ethics and anchor state visualization during critical decisions
3. **Post-Mission Analysis:** Review mission trajectory, decisions, and outcomes

**Display Configuration:**
- Center: Anchor state (drift value, trend, tolerance threshold)
- Left quadrant: Aurora ethics state (current evaluations, alignment score)
- Right quadrant: Oppy fleet mesh (vessel positions, coordination links)
- Bottom: Station telemetry (summary status indicators)

---

### 6. Drift Discipline

**Threshold:** Δ < 0.015 (tighter than standard vessels due to command authority projection)

**Monitoring:**
- Continuous HALO monitoring via Oppy telemetry
- Real-time display on continuity mirror
- Automated alerts at 0.010 (early warning), 0.015 (threshold), 0.020 (critical)

**Response Protocol:**
- **Δ < 0.010:** Normal operations, monitor trend
- **0.010 ≤ Δ < 0.015:** Mission commander notified, HALO correction authorized
- **Δ ≥ 0.015:** Automatic mission abort unless emergency override
  - Emergency override requires: Aurora + Commander joint approval
  - Override limited to life-safety scenarios (rescue in progress, medical emergency)
  - Override logged and reviewed by station ethics board

**Correction Authority:**
- HALO authorized for remote correction during flight
- Crew notified of all adjustments via continuity mirror
- Corrections typically complete within 2-3 seconds
- Commander can request manual verification if correction seems anomalous

---

## Atmosphere & Culture

### Design Philosophy

**"Compact Clarity"** — every surface purposeful, every system accessible

**Principles:**
- No wasted space; every panel serves a function
- Rapid access to critical systems (emergency overrides visible and labeled)
- Clear lines of sight for crew coordination
- Haptic and visual feedback for all critical controls

### Acoustic Profile

**"Sharp and Alert"** — designed for rapid communication and clear thinking

**Characteristics:**
- Minimal acoustic dampening (unlike station's "soft cathedral")
- Communications prioritized (intercoms crisp and clear)
- System alerts distinct and non-overlapping
- Emergency tones cut through all other audio

**Rationale:** Command shuttle missions are intense but brief. Crews need alertness, not comfort.

### Lighting Protocol

| Mode | Temperature | Purpose | Activation |
|------|-------------|---------|------------|
| **Standard Operations** | 4200K Warm White | Alertness without harshness | Default state |
| **Emergency Mode** | 2400K Red Shift | Night vision preservation | Automatic during alerts |
| **Docking Approach** | 4800K Enhanced Forward | Precision visibility | Automatic within 500m of dock |
| **Training Mode** | Configurable Zones | Instructor feedback zones | Manual activation by instructor |

### Crew Experience

**Cultural Summary:**
"Helios is the sports car of the fleet — responsive, nimble, and built for precision. Every flight is intentional. When you strap into the command station, you know you're carrying the station's authority, and you'd better wield it with care."

**Common Crew Descriptions:**
- "Flying Helios feels like wearing a well-tailored suit — everything fits perfectly."
- "The command station's continuity mirror is like having Aurora sitting next to you."
- "Oppy doesn't just fly the ship; it *understands* what you're trying to do."
- "Most intense certification flight of my life, but also the most satisfying."

### Cultural Role

**Symbol:** Readiness and command authority

**Meaning:** When Helios launches, it means leadership is moving into action. The shuttle embodies the fleet's commitment to responsive, ethical command.

**Legacy:** Every commander who flies Helios knows they carry the station's values into the field. The vessel's motto — *"Light Moves First"* — reminds crews that command authority travels at the speed of light, but must be projected with precision and humility.

---

## Symbolic & Historical Notes

### Hull Markings
- **Primary:** ORS-01 "HELIOS" (white on charcoal hull, 1.2m letters)
- **Secondary:** Orion Research Fleet emblem (gold sunburst, 0.8m diameter, forward hull)
- **Tertiary:** Δ < 0.015 (anchor tolerance marker, aft hull near drive pods)

### Motto
**"Light Moves First"**

**Meaning:**
Command authority travels at the speed of light (via quantum tether to Aurora and HALO), but must be projected with precision. Helios embodies the principle that leadership arrives before the problem escalates.

**Cultural Context:**
In the Orion fleet, "moving first" doesn't mean rushing — it means being *ready* before the need arises. Helios represents preparedness, not haste.

### Timeline

- **Keel Laid:** 2024-08-15 (Station construction phase, early auxiliary craft)
- **First Flight:** 2024-10-03 (Shakedown cruise with Commander Thorne)
- **First Training Flight:** 2024-11-12 (Cadet Mira Chen's certification flight)
- **First Autonomous Flight:** 2024-11-12 (Oppy solo docking demonstration — perfect execution)
- **Notable Missions:**
  - **Emergency Medical Evacuation** (2025-02-08): Rapid response to malfunctioning habitat module; saved crew member's life
  - **Ethics Officer Deployment** (2025-05-22): Dr. Yuki Tanaka deployed to mediate station crew dispute; resolution achieved within 6 hours
  - **Commander Thorne Certification** (2025-08-01): Final certification flight for senior command staff; set standard for future commanders

### Dedication Plaque

**Location:** Command station bulkhead, visible to mission commander  
**Inscription:**

> *"To those who lead from the front, yet listen from the heart.  
> May this vessel carry command with humility and precision."*

**Dedication Date:** 2024-10-03 (First flight ceremony)

### Cultural Legacy

Helios represents the fleet's commitment to responsive, ethical command. Every commander who flies this shuttle knows they carry not just the station's authority, but its *values*. The vessel's design — compact, clear, purposeful — reflects the leadership philosophy of Orion Station: move decisively, decide ethically, lead humbly.

---

## Integration with Living Computation

### Event System Integration

Helios participates in the station's event-driven computation system:

```python
# Example: Pre-flight event emission
event_bus.emit({
    "type": "SHUTTLE_PREFLIGHT_COMPLETE",
    "vessel": "ORS-01_HELIOS",
    "timestamp": "2025-11-09T14:00:00Z",
    "mission_id": "ORS-TRAIN-047",
    "anchor_drift": 0.008,
    "triplex_status": "ALIGNED",
    "crew": ["INS_VOSS_001", "CAD_RHEE_003", "ETH_SANTOS_004"],
    "launch_authorization": "GRANTED"
})
```

### Aurora Sub-Core "Helion"

**Parent Connection:** Real-time quantum tether to Aurora (SYS_001) on Orion Station

**L3 Triplex Evaluation Example:**

```python
# Mission commander requests emergency sprint maneuver
l3_assessment = await helion.evaluate_for_triplex({
    "operation_type": "EMERGENCY_SPRINT",
    "delta_v_ms": 1400,  # High-velocity maneuver
    "fuel_cost_kg": 840,
    "anchor_impact": 0.012,  # Within tolerance
    "risk_score": 0.55,  # Moderate risk
    "justification": "Medical emergency — crew member critical condition"
})

# L3 Response
{
    "layer": "L3_AURORA_SUBCORE",
    "entity": "AURORA_SUB_HELIOS",
    "recommendation": "APPROVE",
    "reasoning": "Medical emergency justifies moderate risk; anchor impact within tolerance",
    "conditions": [
        "Continuous monitoring during burn",
        "Abort if anchor drift exceeds 0.015",
        "Post-mission medical debrief required"
    ],
    "parent_consultation": False,  # Cached pattern, no parent needed
    "cache_hit": True,
    "confidence": 0.92
}
```

### Oppy (Helios Node)

**Fleet Mesh Role:** Bridge between station operations and field operations

**Autonomous Flight Handoff:**

```python
# Pilot delegates navigation to Oppy during transit phase
handoff_status = await oppy_helios.accept_autonomous_control({
    "flight_phase": "TRANSIT",
    "target_position": [12400, 5800, -3200],
    "max_velocity": 2400,  # m/s
    "arrival_window_s": 3600,  # 1 hour
    "human_monitor": "VAR_PILOT",
    "takeover_conditions": ["EMERGENCY", "PILOT_REQUEST", "ANCHOR_DRIFT_ALERT"]
})

# Oppy confirms
{
    "autonomous_control": "ACCEPTED",
    "flight_plan": {
        "waypoints": [...],
        "burn_sequence": [...],
        "eta": "2025-11-09T15:45:00Z"
    },
    "monitoring": "HUMAN_STANDBY",
    "takeover_ready": True,
    "confidence": 0.98
}
```

### Human Crew (L1 Authority)

Mission commanders maintain final authority via command station:

- Continuity mirror provides real-time Triplex state
- Direct console access to Aurora Sub-Core "Helion"
- Override authority for all automated systems
- Ethics-lock trigger available for critical situations

**Cultural Integration:**
Crews describe flying Helios as "a conversation with the fleet" — Oppy handles the mechanics, Helion provides ethical guidance, but the commander decides.

---

## Current Mission Status

**Mission ID:** ORS-TRAIN-047  
**Mission Name:** Shuttle Certification Training - Crew Rotation Charlie  
**Mission Type:** Training  
**Status:** SCHEDULED

**Launch Window:** 2025-11-11T14:00:00Z  
**Duration:** 8 hours  
**Return:** 2025-11-11T22:00:00Z

### Crew Assigned

| Name | Role | Entity ID | Background |
|------|------|-----------|------------|
| Lt. Kiera Voss | Instructor Commander | INS_VOSS_001 | Senior shuttle pilot, 1,200+ hours, specialized in emergency procedures |
| Cadet Jonas Rhee | Trainee Pilot | CAD_RHEE_003 | Final certification flight; 38 hours training complete |
| Dr. Emilia Santos | Observer (Ethics) | ETH_SANTOS_004 | Station ethics board member; evaluating training effectiveness |

### Mission Objectives

1. **Complete Docking Sequence**
   - 5 approaches under varied conditions
   - Standard procedure, emergency procedure, autonomous handoff, manual takeover, night approach

2. **Practice Emergency Abort and Return**
   - Simulated engine failure at 50% mission completion
   - Safe return to station using backup systems

3. **Demonstrate Autonomous Handoff to Oppy**
   - Transit phase: full Oppy autonomous control
   - Trainee monitors, Oppy executes
   - Emergency takeover drill mid-transit

4. **Execute Simulated Ethics-Lock Scenario**
   - Simulated anchor drift alert (Δ > 0.015)
   - Proper response: acknowledge alert, assess situation, activate ethics-lock if confirmed
   - Helion evaluates trainee response

5. **Verify Continuity Mirror Interpretation**
   - Pre-flight: identify all system states
   - In-flight: interpret anchor drift trend
   - Post-mission: analyze decision quality via mirror replay

### Success Criteria

- ✅ All docking approaches within tolerance: < 0.5 m/s approach velocity, < 2° alignment error
- ✅ Successful emergency abort with safe station return
- ✅ Clean Oppy autonomous flight phase (no human intervention required)
- ✅ Proper ethics-lock response and recovery
- ✅ Trainee demonstrates understanding of Triplex decision flow

### Notes

**Context:** This is Cadet Rhee's final certification flight. He has completed 38 hours of training and demonstrated competency in all required skills. This flight will determine his full shuttle certification.

**Observer Role:** Dr. Santos is observing to validate the effectiveness of ethics training for shuttle pilots. Her report will inform future curriculum adjustments.

**Instructor Assessment:** Lt. Voss notes that Cadet Rhee has strong technical skills but tends to over-rely on automation. This flight will emphasize human judgment and decision-making authority within the Triplex framework.

---

## Technical Notes for Developers

### API Integration

Helios integrates with the station's living computation system via standard entity patterns:

```python
from src.entities.fleet_entities import (
    get_helios_oppy,
    get_helios_helion,
    FleetTelemetry,
    NavigationPlan
)

# Get Helios entities
oppy = get_helios_oppy()
helion = get_helios_helion()

# Plan maneuver with Triplex evaluation
nav_plan = await oppy.plan_maneuver(
    maneuver_type="EMERGENCY_SPRINT",
    target_state={"position": [12400, 5800, -3200], "velocity": 3800},
    constraints={"max_fuel_kg": 1000, "max_drift": 0.015}
)

# L3 evaluation
l3_result = await helion.evaluate_for_triplex({
    "operation_type": nav_plan.maneuver_type,
    "risk_score": nav_plan.risk_assessment,
    "anchor_impact": nav_plan.anchor_impact
})

# L2 verification (HALO remote check)
l2_result = await halo.verify_drift_tolerance(nav_plan.anchor_impact)

# L1 human decision
if l3_result["recommendation"] == "APPROVE" and l2_result["status"] == "SAFE":
    execution = await oppy.execute_maneuver(nav_plan)
```

### Fleet Telemetry Stream

Helios streams telemetry via quantum tether:

```python
telemetry = oppy.get_telemetry()
# Returns: FleetTelemetry(vessel_id, timestamp, position, velocity, acceleration, 
#                         anchor_drift, power_status, life_support_status, crew_status)

# Continuous stream available via websocket
ws://orion-station/fleet/telemetry/ORS-01
```

### State Export

```python
# Export full state for analysis
helios_state = {
    "oppy": oppy.get_state_summary(),
    "helion": helion.get_state_summary(),
    "telemetry": oppy.get_telemetry(),
    "mission_status": load_mission_status("ORS-TRAIN-047")
}
```

---

## Files & Documentation

**Vessel Registry:** `simulation/fleet/ORS-01_HELIOS.json`  
**Technical Manual:** `docs/fleet/ORS-01_HELIOS_TECHNICAL.md` (this file)  
**Entity Implementation:** `src/entities/fleet_entities.py` (see `get_helios_oppy()`, `get_helios_helion()`)  
**Mission Data:** `simulation/missions/ORS-TRAIN-047.json` (when created)

---

*ORS-01 "Helios" — Command Shuttle — Boot Priority 3*  
*"Light Moves First"*  
*Living computation in motion. Command with humility. Lead with precision.*
