#!/usr/bin/env python3
"""
Tests for Kubernetes deployment scripts.
Chain Notation: #TESTS//K8S//DEPLOY//
DLP Tag: test_k8s_deploy_v1

These tests validate the deployment scripts' structure and behavior
without requiring an actual Kubernetes cluster.
"""

import os
import subprocess
import pytest
from pathlib import Path


# Get project root
PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


class TestK8sDeployScripts:
    """Test suite for Kubernetes deployment scripts."""

    @pytest.fixture
    def deploy_relays_script(self):
        """Path to the relay deployment script."""
        return SCRIPTS_DIR / "k8s_deploy_relays.sh"

    @pytest.fixture
    def deploy_firewall_script(self):
        """Path to the firewall deployment script."""
        return SCRIPTS_DIR / "k8s_deploy_firewall.sh"

    @pytest.fixture
    def deploy_mcp_script(self):
        """Path to the MCP deployment script."""
        return SCRIPTS_DIR / "k8s_deploy_mcp.sh"

    def test_relay_script_exists(self, deploy_relays_script):
        """Verify relay deployment script exists."""
        assert deploy_relays_script.exists(), \
            f"Relay deployment script not found: {deploy_relays_script}"

    def test_firewall_script_exists(self, deploy_firewall_script):
        """Verify firewall deployment script exists."""
        assert deploy_firewall_script.exists(), \
            f"Firewall deployment script not found: {deploy_firewall_script}"

    def test_mcp_script_exists(self, deploy_mcp_script):
        """Verify MCP deployment script exists."""
        assert deploy_mcp_script.exists(), \
            f"MCP deployment script not found: {deploy_mcp_script}"

    def test_relay_script_is_executable(self, deploy_relays_script):
        """Verify relay deployment script is executable."""
        assert os.access(deploy_relays_script, os.X_OK), \
            "Relay deployment script should be executable"

    def test_firewall_script_is_executable(self, deploy_firewall_script):
        """Verify firewall deployment script is executable."""
        assert os.access(deploy_firewall_script, os.X_OK), \
            "Firewall deployment script should be executable"

    def test_mcp_script_is_executable(self, deploy_mcp_script):
        """Verify MCP deployment script is executable."""
        assert os.access(deploy_mcp_script, os.X_OK), \
            "MCP deployment script should be executable"

    def test_relay_script_syntax(self, deploy_relays_script):
        """Verify relay deployment script has valid bash syntax."""
        result = subprocess.run(
            ["bash", "-n", str(deploy_relays_script)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"Relay script syntax error: {result.stderr}"

    def test_firewall_script_syntax(self, deploy_firewall_script):
        """Verify firewall deployment script has valid bash syntax."""
        result = subprocess.run(
            ["bash", "-n", str(deploy_firewall_script)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"Firewall script syntax error: {result.stderr}"

    def test_mcp_script_syntax(self, deploy_mcp_script):
        """Verify MCP deployment script has valid bash syntax."""
        result = subprocess.run(
            ["bash", "-n", str(deploy_mcp_script)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"MCP script syntax error: {result.stderr}"

    def test_relay_script_has_help(self, deploy_relays_script):
        """Verify relay deployment script has help option."""
        content = deploy_relays_script.read_text()
        assert "--help" in content or "-h" in content, \
            "Script should have help option"

    def test_firewall_script_has_help(self, deploy_firewall_script):
        """Verify firewall deployment script has help option."""
        content = deploy_firewall_script.read_text()
        assert "--help" in content or "-h" in content, \
            "Script should have help option"

    def test_mcp_script_has_help(self, deploy_mcp_script):
        """Verify MCP deployment script has help option."""
        content = deploy_mcp_script.read_text()
        assert "--help" in content or "-h" in content, \
            "Script should have help option"

    def test_relay_script_has_dry_run(self, deploy_relays_script):
        """Verify relay deployment script has dry-run option."""
        content = deploy_relays_script.read_text()
        assert "--dry-run" in content, \
            "Script should have dry-run option"

    def test_firewall_script_has_dry_run(self, deploy_firewall_script):
        """Verify firewall deployment script has dry-run option."""
        content = deploy_firewall_script.read_text()
        assert "--dry-run" in content, \
            "Script should have dry-run option"

    def test_mcp_script_has_dry_run(self, deploy_mcp_script):
        """Verify MCP deployment script has dry-run option."""
        content = deploy_mcp_script.read_text()
        assert "--dry-run" in content, \
            "Script should have dry-run option"

    def test_relay_script_has_chain_notation(self, deploy_relays_script):
        """Verify relay script includes chain notation comment."""
        content = deploy_relays_script.read_text()
        assert "Chain Notation" in content or "#K8S//" in content, \
            "Script should include chain notation"

    def test_relay_script_has_dlp_tag(self, deploy_relays_script):
        """Verify relay script includes DLP tag comment."""
        content = deploy_relays_script.read_text()
        assert "DLP" in content, \
            "Script should include DLP tag"

    def test_relay_script_references_correct_manifests(self, deploy_relays_script):
        """Verify relay script references correct K8s manifest files."""
        content = deploy_relays_script.read_text()
        expected_manifests = [
            "aurora-namespace-rbac.yaml",
            "aurora-configmap-secrets.yaml",
            "aurora-gui-cloudhub-deployment.yaml"
        ]
        for manifest in expected_manifests:
            assert manifest in content, \
                f"Script should reference {manifest}"


class TestK8sManifests:
    """Test suite for Kubernetes manifest files."""

    @pytest.fixture
    def k8s_dir(self):
        """Path to the k8s directory."""
        return PROJECT_ROOT / "k8s"

    def test_k8s_directory_exists(self, k8s_dir):
        """Verify k8s directory exists."""
        assert k8s_dir.exists(), "k8s directory should exist"

    def test_namespace_rbac_exists(self, k8s_dir):
        """Verify namespace RBAC manifest exists."""
        manifest = k8s_dir / "aurora-namespace-rbac.yaml"
        assert manifest.exists(), "Namespace RBAC manifest should exist"

    def test_configmap_secrets_exists(self, k8s_dir):
        """Verify ConfigMap and Secrets manifest exists."""
        manifest = k8s_dir / "aurora-configmap-secrets.yaml"
        assert manifest.exists(), "ConfigMap/Secrets manifest should exist"

    def test_deployment_manifest_exists(self, k8s_dir):
        """Verify deployment manifest exists."""
        manifest = k8s_dir / "aurora-gui-cloudhub-deployment.yaml"
        assert manifest.exists(), "Deployment manifest should exist"

    def test_service_manifest_exists(self, k8s_dir):
        """Verify service manifest exists."""
        manifest = k8s_dir / "aurora-gui-cloudhub-service.yaml"
        assert manifest.exists(), "Service manifest should exist"

    def test_dockerfile_exists(self, k8s_dir):
        """Verify Dockerfile exists in k8s directory."""
        dockerfile = k8s_dir / "Dockerfile"
        assert dockerfile.exists(), "Dockerfile should exist in k8s directory"


class TestWorkflowFile:
    """Test suite for GitHub Actions workflow file."""

    @pytest.fixture
    def workflow_file(self):
        """Path to the k8s-deploy workflow."""
        return PROJECT_ROOT / ".github" / "workflows" / "k8s-deploy.yml"

    def test_workflow_exists(self, workflow_file):
        """Verify workflow file exists."""
        assert workflow_file.exists(), "k8s-deploy.yml workflow should exist"

    def test_workflow_has_valid_yaml(self, workflow_file):
        """Verify workflow file has valid YAML syntax."""
        import yaml
        try:
            with open(workflow_file) as f:
                yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"Workflow YAML is invalid: {e}")

    def test_workflow_has_trigger_on_push(self, workflow_file):
        """Verify workflow triggers on push to main/develop."""
        content = workflow_file.read_text()
        assert "push:" in content, "Workflow should trigger on push"
        assert "main" in content, "Workflow should include main branch"
        assert "develop" in content, "Workflow should include develop branch"

    def test_workflow_has_build_job(self, workflow_file):
        """Verify workflow has a build job."""
        content = workflow_file.read_text()
        assert "build:" in content.lower() or "Build" in content, \
            "Workflow should have a build job"

    def test_workflow_has_deploy_job(self, workflow_file):
        """Verify workflow has a deploy job."""
        content = workflow_file.read_text()
        assert "deploy" in content.lower(), \
            "Workflow should have a deploy job"

    def test_workflow_uses_ghcr(self, workflow_file):
        """Verify workflow uses GitHub Container Registry."""
        content = workflow_file.read_text()
        assert "ghcr.io" in content, \
            "Workflow should use GitHub Container Registry"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
