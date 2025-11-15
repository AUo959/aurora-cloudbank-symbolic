"""
Thread Transfer Bridge v2 - API Endpoint Testing

Manual testing script for all 21 v2 endpoints.

Thread: T1→BRIDGE_V2→API_TESTING
DLP: context_tag=bridge_v2_api_manual_test
Anchor: EOS_SEED_ORION_v2
"""
import asyncio
import httpx
import pytest

BASE_URL = "http://localhost:8000"
TIMEOUT = 30.0

# Exclude this manual runner from pytest's automated suite
pytest.skip("Manual v2 API tester; excluded from pytest suite", allow_module_level=True)

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name, status, details=""):
    """Print test result with color coding"""
    if status == "PASS":
        print(f"{Colors.GREEN}✓{Colors.END} {name}")
    elif status == "FAIL":
        print(f"{Colors.RED}✗{Colors.END} {name}")
        if details:
            print(f"  {Colors.RED}Error: {details}{Colors.END}")
    elif status == "SKIP":
        print(f"{Colors.YELLOW}⊘{Colors.END} {name} (skipped)")
    if details and status == "PASS":
        print(f"  {Colors.BLUE}{details}{Colors.END}")

async def test_endpoint(client, method, path, data=None, expected_status=200, name=""):
    """Test a single endpoint"""
    try:
        if method == "GET":
            response = await client.get(path)
        elif method == "POST":
            response = await client.post(path, json=data)
        elif method == "DELETE":
            response = await client.delete(path)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        if response.status_code == expected_status:
            result = response.json() if response.text else {}
            success = result.get("success", True)
            if success:
                print_test(name, "PASS", f"Status: {response.status_code}")
                return True, result
            else:
                print_test(name, "FAIL", f"Success=False: {result.get('message', 'Unknown error')}")
                return False, result
        else:
            print_test(name, "FAIL", f"Expected {expected_status}, got {response.status_code}")
            return False, {}
    except Exception as e:
        print_test(name, "FAIL", str(e))
        return False, {}

async def main():
    """Run all endpoint tests"""
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}Thread Transfer Bridge v2 - API Endpoint Testing{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}\n")
    
    # Check if server is running
    try:
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
            response = await client.get("/health")
            if response.status_code != 200:
                print(f"{Colors.RED}❌ Server not responding at {BASE_URL}{Colors.END}")
                return
            print(f"{Colors.GREEN}✓ Server is running at {BASE_URL}{Colors.END}\n")
    except Exception as e:
        print(f"{Colors.RED}❌ Cannot connect to server: {e}{Colors.END}")
        print(f"{Colors.YELLOW}💡 Start server with: python aurora_api.py{Colors.END}")
        return
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT) as client:
        results = {"passed": 0, "failed": 0, "skipped": 0}
        
        # ================================================================
        # Phase 1: Distributed Node Management (6 endpoints)
        # ================================================================
        print(f"\n{Colors.BLUE}Phase 1: Distributed Node Management{Colors.END}")
        print("-" * 70)
        
        # 1. Register a node
        node_data = {
            "hostname": "test-node-1",
            "port": 8080,
            "region": "us-east-1",
            "capacity": 100,
            "version": "2.0.0"
        }
        success, result = await test_endpoint(
            client, "POST", "/api/v2/nodes/register",
            data=node_data,
            name="POST /api/v2/nodes/register"
        )
        node_id = result.get("node", {}).get("node_id") if success else None
        results["passed" if success else "failed"] += 1
        
        # 2. List all nodes
        success, result = await test_endpoint(
            client, "GET", "/api/v2/nodes",
            name="GET /api/v2/nodes"
        )
        results["passed" if success else "failed"] += 1
        
        # 3. Get node health (only if we have a node_id)
        if node_id:
            success, result = await test_endpoint(
                client, "GET", f"/api/v2/nodes/{node_id}/health",
                name=f"GET /api/v2/nodes/{node_id}/health"
            )
            results["passed" if success else "failed"] += 1
        else:
            print_test("GET /api/v2/nodes/{node_id}/health", "SKIP")
            results["skipped"] += 1
        
        # 4. Get cluster health
        success, result = await test_endpoint(
            client, "GET", "/api/v2/cluster/health",
            name="GET /api/v2/cluster/health"
        )
        results["passed" if success else "failed"] += 1
        
        # 5. Trigger consensus election
        success, result = await test_endpoint(
            client, "POST", "/api/v2/consensus/elect",
            name="POST /api/v2/consensus/elect"
        )
        results["passed" if success else "failed"] += 1
        
        # 6. Unregister node (only if we have a node_id)
        if node_id:
            success, result = await test_endpoint(
                client, "DELETE", f"/api/v2/nodes/{node_id}",
                name=f"DELETE /api/v2/nodes/{node_id}"
            )
            results["passed" if success else "failed"] += 1
        else:
            print_test("DELETE /api/v2/nodes/{node_id}", "SKIP")
            results["skipped"] += 1
        
        # ================================================================
        # Phase 2: Cross-Repository Sync (4 endpoints)
        # ================================================================
        print(f"\n{Colors.BLUE}Phase 2: Cross-Repository Sync{Colors.END}")
        print("-" * 70)
        
        # Note: These require actual Git repositories, so we'll test the API calls
        # but expect some to fail gracefully
        
        # 7. Register repository
        repo_data = {
            "repo_id": "test-repo-1",
            "repo_path": "/tmp/test-repo",
            "branch": "main"
        }
        success, result = await test_endpoint(
            client, "POST", "/api/v2/repos/register",
            data=repo_data,
            expected_status=500,  # Expected to fail without real repo
            name="POST /api/v2/repos/register (expects failure)"
        )
        results["passed" if not success else "failed"] += 1  # Inverted - we expect failure
        
        # 8. Sync repository
        success, result = await test_endpoint(
            client, "POST", "/api/v2/repos/test-repo-1/sync?direction=pull",
            expected_status=500,  # Expected to fail
            name="POST /api/v2/repos/{repo_id}/sync (expects failure)"
        )
        results["passed" if not success else "failed"] += 1
        
        # 9. Create cross-repo bridge
        success, result = await test_endpoint(
            client, "POST", "/api/v2/bridges/cross-repo?source_repo=repo1&target_repo=repo2&thread_id=test_thread",
            expected_status=500,  # Expected to fail
            name="POST /api/v2/bridges/cross-repo (expects failure)"
        )
        results["passed" if not success else "failed"] += 1
        
        # 10. Execute cross-repo handshake
        success, result = await test_endpoint(
            client, "POST", "/api/v2/bridges/test-bridge/handshake",
            expected_status=500,  # Expected to fail
            name="POST /api/v2/bridges/{bridge_id}/handshake (expects failure)"
        )
        results["passed" if not success else "failed"] += 1
        
        # ================================================================
        # Phase 3: Drift Prediction (5 endpoints)
        # ================================================================
        print(f"\n{Colors.BLUE}Phase 3: Drift Prediction{Colors.END}")
        print("-" * 70)
        
        # 11. Predict drift
        drift_data = {
            "drift_velocity": 0.001,
            "drift_acceleration": 0.0001,
            "handshake_count": 10,
            "average_handshake_duration": 0.5,
            "failed_handshake_ratio": 0.05,
            "time_of_day": 14.0,
            "day_of_week": 1,
            "thread_age_hours": 24.0,
            "anchor_changes": 2,
            "sync_frequency": 2.0,
            "node_count": 3,
            "thread_id": "test_thread_001"
        }
        success, result = await test_endpoint(
            client, "POST", "/api/v2/drift/predict",
            data=drift_data,
            name="POST /api/v2/drift/predict"
        )
        results["passed" if success else "failed"] += 1
        
        # 12. Analyze patterns
        success, result = await test_endpoint(
            client, "GET", "/api/v2/drift/patterns",
            name="GET /api/v2/drift/patterns"
        )
        results["passed" if success else "failed"] += 1
        
        # 13. Record observation
        success, result = await test_endpoint(
            client, "POST", "/api/v2/drift/observe?drift=0.002",
            name="POST /api/v2/drift/observe"
        )
        results["passed" if success else "failed"] += 1
        
        # 14. Get prediction accuracy
        success, result = await test_endpoint(
            client, "GET", "/api/v2/drift/accuracy",
            name="GET /api/v2/drift/accuracy"
        )
        results["passed" if success else "failed"] += 1
        
        # 15. Apply correction
        success, result = await test_endpoint(
            client, "POST", "/api/v2/corrections/apply?thread_id=test_thread&predicted_drift=0.003&current_drift=0.001",
            name="POST /api/v2/corrections/apply"
        )
        results["passed" if success else "failed"] += 1
        
        # ================================================================
        # Phase 4: Layer Management (6 endpoints)
        # ================================================================
        print(f"\n{Colors.BLUE}Phase 4: Layer Management{Colors.END}")
        print("-" * 70)
        
        # 16. Create layer bridge
        layer_data = {
            "bridge_id": "test_l1_bridge",
            "layer": "L1",
            "source_id": "thread_a",
            "target_id": "thread_b",
            "thread_id": "test_thread_layer"
        }
        success, result = await test_endpoint(
            client, "POST", "/api/v2/layers/bridge",
            data=layer_data,
            name="POST /api/v2/layers/bridge"
        )
        bridge_created = success
        results["passed" if success else "failed"] += 1
        
        # 17. Execute layered handshake
        if bridge_created:
            success, result = await test_endpoint(
                client, "POST", "/api/v2/layers/test_l1_bridge/handshake",
                name="POST /api/v2/layers/{bridge_id}/handshake"
            )
            results["passed" if success else "failed"] += 1
        else:
            print_test("POST /api/v2/layers/{bridge_id}/handshake", "SKIP")
            results["skipped"] += 1
        
        # 18. Validate hierarchy
        success, result = await test_endpoint(
            client, "POST", "/api/v2/layers/validate?thread_id=test_thread_layer&strict_mode=false",
            name="POST /api/v2/layers/validate"
        )
        results["passed" if success else "failed"] += 1
        
        # 19. List layer bridges
        success, result = await test_endpoint(
            client, "GET", "/api/v2/layers/bridges",
            name="GET /api/v2/layers/bridges"
        )
        results["passed" if success else "failed"] += 1
        
        # 20. Get layer statistics
        success, result = await test_endpoint(
            client, "GET", "/api/v2/layers/statistics",
            name="GET /api/v2/layers/statistics"
        )
        results["passed" if success else "failed"] += 1
        
        # 21. Cascade validate
        success, result = await test_endpoint(
            client, "POST", "/api/v2/layers/cascade-validate?thread_id=test_thread_layer",
            name="POST /api/v2/layers/cascade-validate"
        )
        results["passed" if success else "failed"] += 1
        
        # ================================================================
        # Summary
        # ================================================================
        print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
        print(f"{Colors.BLUE}Test Summary{Colors.END}")
        print(f"{Colors.BLUE}{'='*70}{Colors.END}")
        
        total = results["passed"] + results["failed"] + results["skipped"]
        pass_rate = (results["passed"] / total * 100) if total > 0 else 0
        
        print(f"\n{Colors.GREEN}Passed: {results['passed']}{Colors.END}")
        print(f"{Colors.RED}Failed: {results['failed']}{Colors.END}")
        print(f"{Colors.YELLOW}Skipped: {results['skipped']}{Colors.END}")
        print(f"Total: {total}")
        print(f"Pass Rate: {pass_rate:.1f}%\n")
        
        if results["failed"] == 0:
            print(f"{Colors.GREEN}✓ All tests passed!{Colors.END}\n")
        else:
            print(f"{Colors.YELLOW}⚠ Some tests failed (may be expected for endpoints requiring external resources){Colors.END}\n")

if __name__ == "__main__":
    asyncio.run(main())
