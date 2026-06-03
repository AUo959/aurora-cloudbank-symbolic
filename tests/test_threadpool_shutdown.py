"""Tests for ThreadPoolExecutor lifecycle management (Issue #804).

Both AuroraDiffOptimizer and DistributedConsciousnessMesh must expose
close() and a context-manager interface so callers can guarantee the
executor is shut down on process exit.
"""

import pytest


@pytest.mark.unit
class TestAuroraDiffOptimizerExecutorLifecycle:
    """AuroraDiffOptimizer.close() and context-manager support."""

    def _make_optimizer(self):
        from modules.opal2.aurora_diff_optimizer import AuroraDiffOptimizer
        return AuroraDiffOptimizer()

    def test_close_shuts_down_executor(self):
        opt = self._make_optimizer()
        opt.close()
        # After shutdown, submitting work raises RuntimeError.
        with pytest.raises(RuntimeError):
            opt.executor.submit(lambda: None)

    def test_context_manager_calls_close(self):
        with self._make_optimizer() as opt:
            assert not opt.executor._shutdown
        with pytest.raises(RuntimeError):
            opt.executor.submit(lambda: None)

    def test_context_manager_returns_self(self):
        opt_outer = self._make_optimizer()
        with opt_outer as opt_inner:
            assert opt_inner is opt_outer
        opt_outer.close()  # idempotent — second call is harmless


@pytest.mark.unit
class TestDistributedConsciousnessMeshExecutorLifecycle:
    """DistributedConsciousnessMesh.close() and context-manager support."""

    def _make_mesh(self):
        from modules.nexus.scale.distributed_consciousness import DistributedConsciousnessMesh
        return DistributedConsciousnessMesh()

    def test_close_shuts_down_executor(self):
        mesh = self._make_mesh()
        mesh.close()
        with pytest.raises(RuntimeError):
            mesh.executor.submit(lambda: None)

    def test_context_manager_calls_close(self):
        with self._make_mesh() as mesh:
            assert not mesh.executor._shutdown
        with pytest.raises(RuntimeError):
            mesh.executor.submit(lambda: None)

    def test_context_manager_returns_self(self):
        mesh_outer = self._make_mesh()
        with mesh_outer as mesh_inner:
            assert mesh_inner is mesh_outer
        mesh_outer.close()
