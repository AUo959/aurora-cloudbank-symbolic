# GUMAS/Orion Status Module v2 - CLI Command Reference

## Quick Status Check
```bash
# Get comprehensive system status
python modules/nexus/gumas/gumas_orion_status_v2.py --status

# Display visual glyphcard
python modules/nexus/gumas/gumas_orion_status_v2.py --glyphcard

# Verify 12-anchor thread continuity
python modules/nexus/gumas/gumas_orion_status_v2.py --verify-thread

# Detect entropy drift patterns (including OSCILLATING)
python modules/nexus/gumas/gumas_orion_status_v2.py --detect-drift

# Export snapshot for zero-knowledge hand-off
python modules/nexus/gumas/gumas_orion_status_v2.py --export-snapshot

# Show help and available commands
python modules/nexus/gumas/gumas_orion_status_v2.py --help
```

## Python API Usage
```python
import asyncio
from modules.nexus.gumas.gumas_orion_status_v2 import StatusOrchestrator

# Initialize orchestrator
orchestrator = StatusOrchestrator()
print(f"✅ Initialized: {orchestrator.anchor}")

# Get comprehensive status (async)
async def get_status():
    status = await orchestrator.get_comprehensive_status()
    print(f"🎯 System Health: {status['manifest']['anchor']}")
    print(f"📊 Entropy Drift: {status['entropy_analysis']['drift']:.3f}")
    print(f"🔗 Thread Verified: {status['thread_continuity']['verified']}")
    return status

# Run async status check
status = asyncio.run(get_status())
```

## Test Suite Execution
```bash
# Run complete test suite (23 tests)
python3 -m pytest modules/nexus/gumas/test_gumas_orion_status_v2_corrected.py -v

# Run specific test categories
python3 -m pytest modules/nexus/gumas/test_gumas_orion_status_v2_corrected.py::TestPerformanceV2 -v
python3 -m pytest modules/nexus/gumas/test_gumas_orion_status_v2_corrected.py::TestEntropyMonitorV2 -v
python3 -m pytest modules/nexus/gumas/test_gumas_orion_status_v2_corrected.py::TestStatusOrchestratorV2 -v
```

## Performance Verification
```python
# Test initialization performance (< 2s target)
import time
start = time.time()
orchestrator = StatusOrchestrator()
init_time = time.time() - start
print(f"⚡ Init Time: {init_time:.2f}s {'✅' if init_time < 2.0 else '❌'}")

# Test status generation performance (< 1s target)
async def test_performance():
    start = time.time()
    status = await orchestrator.get_comprehensive_status()
    gen_time = time.time() - start
    print(f"🚀 Status Gen: {gen_time:.2f}s {'✅' if gen_time < 1.0 else '❌'}")

asyncio.run(test_performance())
```

## Entropy Monitoring
```python
# Monitor entropy with OSCILLATING detection
monitor = orchestrator.entropy_monitor

# Take measurements
snapshot1 = monitor.measure(0.05)  # Normal
snapshot2 = monitor.measure(0.08)  # Slight increase
snapshot3 = monitor.measure(0.03)  # Decrease
snapshot4 = monitor.measure(0.09)  # Increase again

# Check for OSCILLATING pattern
trend = monitor._detect_trend()
print(f"📈 Entropy Trend: {trend}")

if trend == "OSCILLATING":
    print("⚠️ OSCILLATING entropy detected - requires attention")
    # Check arbitration flags
    flags = monitor.divergent_truths
    for flag in flags[-3:]:  # Last 3 flags
        if flag.get('requires_arbitration'):
            print(f"🚨 Arbitration Required: {flag['message']}")
```

## Thread Chain Verification
```python
# Verify complete 12-anchor chain
async def verify_chain():
    status = await orchestrator.get_comprehensive_status()
    chain = status['thread_continuity']['chain']
    
    expected_anchors = [
        "NEXUS-BOOTSTRAP-2025",
        "T1-NEXUS-INIT-20250925",
        "T2-MULTIAGENT-2025", 
        "T3-QUANTUM-2025",
        "T4-MEMORY-WEAVE-2025",
        "T5-REALITY-FORK-2025",
        "T6-EMERGENCE-2025",
        "T7-SCALE-2025",
        "T7-GUMAS-ORION-2025",
        "T8-TRANSCENDENT-2025",
        "T8-STATUS-GUMAS-2025",
        "T8-STATUS-GUMAS-V2-2025"
    ]
    
    print(f"🔗 Chain Length: {len(chain)}/12")
    print(f"✅ Chain Valid: {status['thread_continuity']['verified']}")
    
    for i, (expected, actual) in enumerate(zip(expected_anchors, chain)):
        status_icon = "✅" if expected == actual else "❌"
        print(f"   {i+1:2d}. {actual} {status_icon}")

asyncio.run(verify_chain())
```

## Meta-Agent Status Check
```python
async def check_agents():
    status = await orchestrator.get_comprehensive_status()
    agents = status['meta_agents']
    
    for agent_name, agent_data in agents.items():
        print(f"🤖 {agent_name}")
        print(f"   Role: {agent_data.get('role', 'Unknown')}")
        print(f"   Clearance: {agent_data.get('clearance', 'N/A')}")
        print(f"   Status: {agent_data.get('status', 'Unknown')}")
        print()

asyncio.run(check_agents())
```

## Snapshot Export & Recovery
```python
# Create immutable snapshot
snapshot = monitor.measure()
print(f"📸 Snapshot: {snapshot.snapshot_id}")
print(f"🔒 Sealed: {snapshot.verify_integrity()}")
print(f"⚠️ Arbitration: {snapshot.requires_arbitration()}")

# Export for hand-off
async def export_snapshot():
    status = await orchestrator.get_comprehensive_status()
    
    export_data = {
        "anchor": status['manifest']['anchor'],
        "timestamp": status['manifest']['timestamp'],
        "entropy_state": status['entropy_analysis'],
        "thread_chain": status['thread_continuity']['chain'],
        "seal": status['entropy_analysis']['seal']
    }
    
    # Save to file (in production)
    import json
    export_json = json.dumps(export_data, indent=2)
    print(f"📋 Export Size: {len(export_json)} bytes")
    return export_data

export = asyncio.run(export_snapshot())
```

## Troubleshooting Commands
```bash
# Debug entropy issues
python3 -c "
from modules.nexus.gumas.gumas_orion_status_v2 import EntropyMonitor
monitor = EntropyMonitor()
snapshot = monitor.measure()
print(f'Current: {snapshot.current}')
print(f'Drift: {snapshot.drift}')
print(f'Trend: {snapshot.trend}')
print(f'Arbitration: {snapshot.requires_arbitration()}')
"

# Verify module import
python3 -c "
from modules.nexus.gumas.gumas_orion_status_v2 import StatusOrchestrator, EntropyMonitor, EntropySnapshot
print('✅ All classes imported successfully')
orchestrator = StatusOrchestrator()
print(f'✅ Orchestrator anchor: {orchestrator.anchor}')
"

# Check performance quickly
python3 -c "
import time, asyncio
from modules.nexus.gumas.gumas_orion_status_v2 import StatusOrchestrator

async def quick_test():
    start = time.time()
    orchestrator = StatusOrchestrator()
    init_time = time.time() - start
    
    start = time.time()
    status = await orchestrator.get_comprehensive_status()
    status_time = time.time() - start
    
    print(f'⚡ Init: {init_time:.2f}s (target < 2s)')
    print(f'🚀 Status: {status_time:.2f}s (target < 1s)')
    print(f'✅ Performance: {\"PASS\" if init_time < 2 and status_time < 1 else \"NEEDS ATTENTION\"}')

asyncio.run(quick_test())
"
```

---

**Enhanced GUMAS/Orion Status Module v2 - CLI Reference Complete**  
*All commands validated and ready for production use* 🚀