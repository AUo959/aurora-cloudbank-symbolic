"""
Tests for Integrated Monitoring System
"""

import pytest
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import datetime, timedelta, timezone
from src.monitoring.monitoring_system import (
    MonitoringSystem,
    AlertConfig,
    AlertLevel,
    InterventionType
)


class TestMonitoringSystem:
    """Test suite for MonitoringSystem"""

    @pytest.fixture(autouse=True)
    def monitoring_signing_key(self, monkeypatch):
        """Provide the required audit HMAC key for monitoring tests."""
        monkeypatch.setenv("MONITORING_SIGNING_KEY", "test-monitoring-signing-key")
    
    def test_initialization(self):
        """Test monitoring system initialization"""
        with TemporaryDirectory() as tmpdir:
            monitoring = MonitoringSystem(storage_dir=Path(tmpdir))
            
            assert monitoring.behavior_monitor.current_metrics == {}
            assert monitoring.drift_detector.alerts_path == Path(tmpdir) / "drift_alerts.jsonl"
            assert monitoring.ethics_engine.violations_path == Path(tmpdir) / "ethics_violations.jsonl"
            assert monitoring.audit_logger.storage_path == Path(tmpdir) / "audit_log.jsonl"
    
    def test_establish_agent_baseline(self):
        """Test establishing agent baseline"""
        with TemporaryDirectory() as tmpdir:
            monitoring = MonitoringSystem(storage_dir=Path(tmpdir))
            
            historical_data = {
                'decisions_made': [10, 12, 11, 13, 10, 12],
                'success_rate': [0.95, 0.96, 0.94, 0.97, 0.95, 0.96]
            }
            
            monitoring.establish_agent_baseline(
                agent_id="test-agent",
                historical_data=historical_data
            )
            
            # Verify baselines created
            assert "test-agent:decisions_made" in monitoring.drift_detector.baselines
            assert "test-agent:success_rate" in monitoring.drift_detector.baselines
    
    def test_record_agent_behavior(self):
        """Test recording behavioral metrics"""
        with TemporaryDirectory() as tmpdir:
            monitoring = MonitoringSystem(storage_dir=Path(tmpdir))
            
            metrics = {
                'decisions_made': 15,
                'success_rate': 0.92
            }
            
            monitoring.record_agent_behavior(
                agent_id="test-agent",
                metrics=metrics,
                context_tag="test_001"
            )
            
            # Verify metrics recorded
            assert "test-agent" in monitoring.behavior_monitor.current_metrics
    
    def test_check_agent_behavior_with_drift(self):
        """Test checking behavior and detecting drift"""
        with TemporaryDirectory() as tmpdir:
            monitoring = MonitoringSystem(storage_dir=Path(tmpdir))
            
            # Establish baseline
            historical_data = {
                'decisions_made': [10, 11, 12, 11, 10, 11]
            }
            monitoring.establish_agent_baseline("test-agent", historical_data)
            
            # Record normal behavior
            monitoring.record_agent_behavior(
                agent_id="test-agent",
                metrics={'decisions_made': 12}
            )
            
            # Check (should be OK)
            result1 = monitoring.check_agent_behavior(agent_id="test-agent")
            assert result1['drift_detected'] is False
            
            # Record drifted behavior
            monitoring.record_agent_behavior(
                agent_id="test-agent",
                metrics={'decisions_made': 30}  # Significant drift
            )
            
            # Check (should detect drift)
            result2 = monitoring.check_agent_behavior(agent_id="test-agent")
            assert result2['drift_detected'] is True
            assert len(result2['alerts']) > 0
    
    def test_evaluate_action_compliant(self):
        """Test evaluating compliant action"""
        with TemporaryDirectory() as tmpdir:
            monitoring = MonitoringSystem(storage_dir=Path(tmpdir))
            
            result = monitoring.evaluate_action(
                agent_id="test-agent",
                action_type="normal_operation",
                parameters={'safe': True}
            )
            
            assert result['blocked'] is False
            assert len(result['violations']) == 0
    
    def test_evaluate_action_violation(self):
        """Test evaluating action with violation"""
        with TemporaryDirectory() as tmpdir:
            monitoring = MonitoringSystem(storage_dir=Path(tmpdir))
            
            result = monitoring.evaluate_action(
                agent_id="test-agent",
                action_type="critical_decision",
                parameters={
                    'critical_decision': True,
                    'no_human_approval': True
                }
            )
            
            assert result['blocked'] is True
            assert len(result['violations']) > 0
    
    def test_alert_handler_registration(self):
        """Test registering alert handlers"""
        with TemporaryDirectory() as tmpdir:
            monitoring = MonitoringSystem(storage_dir=Path(tmpdir))
            
            handler_called = {'count': 0}
            
            def test_handler(data):
                handler_called['count'] += 1
            
            monitoring.register_alert_handler(AlertLevel.CRITICAL, test_handler)
            
            # Trigger critical violation
            monitoring.evaluate_action(
                agent_id="test-agent",
                action_type="critical",
                parameters={
                    'critical_decision': True,
                    'no_human_approval': True
                }
            )
            
            assert handler_called['count'] > 0
    
    def test_get_agent_status(self):
        """Test getting agent status"""
        with TemporaryDirectory() as tmpdir:
            monitoring = MonitoringSystem(storage_dir=Path(tmpdir))
            
            # Setup agent
            monitoring.establish_agent_baseline(
                "test-agent",
                {'decisions_made': [10, 11, 12]}
            )
            
            monitoring.record_agent_behavior(
                agent_id="test-agent",
                metrics={'decisions_made': 11}
            )
            
            status = monitoring.get_agent_status("test-agent")
            
            assert status['agent_id'] == "test-agent"
            assert 'status' in status
            assert 'violations_24h' in status
            assert 'drift_alerts_24h' in status
    
    def test_generate_compliance_report(self):
        """Test generating compliance report"""
        with TemporaryDirectory() as tmpdir:
            monitoring = MonitoringSystem(storage_dir=Path(tmpdir))
            
            # Generate some activity
            monitoring.establish_agent_baseline(
                "test-agent",
                {'decisions_made': [10, 11, 12]}
            )
            
            monitoring.record_agent_behavior(
                agent_id="test-agent",
                metrics={'decisions_made': 30}
            )
            
            monitoring.check_agent_behavior(agent_id="test-agent")
            
            # Generate report
            report = monitoring.generate_compliance_report(
                since=datetime.now(timezone.utc) - timedelta(hours=1),
                agent_id="test-agent"
            )
            
            assert 'report_period' in report
            assert 'summary' in report
            assert 'violations' in report
            assert 'drift_alerts' in report
            assert 'audit_verified' in report
    
    def test_export_state(self):
        """Test exporting system state"""
        with TemporaryDirectory() as tmpdir:
            monitoring = MonitoringSystem(storage_dir=Path(tmpdir))
            
            monitoring.establish_agent_baseline(
                "test-agent",
                {'metric1': [1, 2, 3]}
            )
            
            state = monitoring.export_state()
            
            assert 'baselines' in state
            assert 'rules' in state
            assert 'behavior_history' in state
            assert 'interventions' in state
            assert 'last_intervention_time' in state
            assert 'violations' in state
            assert 'drift_alerts' in state

    def test_import_state_restores_intervention_cooldowns(self):
        """Test intervention history and cooldowns survive restart."""
        with TemporaryDirectory() as tmpdir:
            storage_dir = Path(tmpdir)
            monitoring = MonitoringSystem(storage_dir=storage_dir)

            monitoring.register_enforcement_handler(
                InterventionType.SUSPEND_AGENT,
                lambda agent_id: True
            )
            monitoring._execute_intervention(
                agent_id="test-agent",
                intervention_type=InterventionType.SUSPEND_AGENT,
                reason="critical drift"
            )

            restarted = MonitoringSystem(storage_dir=storage_dir)
            assert len(restarted.interventions) == 1
            assert restarted.interventions[0].agent_id == "test-agent"
            assert restarted.interventions[0].success is True
            assert "test-agent" in restarted.last_intervention_time

    def test_monitoring_histories_reload_from_storage_dir(self):
        """Test violation and drift alert histories survive restart."""
        with TemporaryDirectory() as tmpdir:
            storage_dir = Path(tmpdir)
            monitoring = MonitoringSystem(storage_dir=storage_dir)

            monitoring.evaluate_action(
                agent_id="test-agent",
                action_type="critical",
                parameters={
                    'critical_decision': True,
                    'no_human_approval': True
                }
            )
            monitoring.establish_agent_baseline(
                "test-agent",
                {'decisions_made': [10, 11, 12]}
            )
            monitoring.record_agent_behavior(
                agent_id="test-agent",
                metrics={'decisions_made': 30}
            )
            monitoring.check_agent_behavior(agent_id="test-agent")

            restarted = MonitoringSystem(storage_dir=storage_dir)
            assert restarted.ethics_engine.get_violations(agent_id="test-agent")
            assert restarted.drift_detector.get_alerts(agent_id="test-agent")
    
    def test_automated_intervention_disabled(self):
        """Test with automated intervention disabled"""
        with TemporaryDirectory() as tmpdir:
            config = AlertConfig(enable_auto_intervention=False)
            monitoring = MonitoringSystem(
                storage_dir=Path(tmpdir),
                config=config
            )
            
            # Trigger critical issue
            monitoring.evaluate_action(
                agent_id="test-agent",
                action_type="critical",
                parameters={
                    'critical_decision': True,
                    'no_human_approval': True
                }
            )
            
            # No intervention should be recorded
            assert len(monitoring.interventions) == 0

    def test_intervention_without_handler_records_failed_audit_receipt(self):
        """Test interventions are not marked successful without enforcement."""
        with TemporaryDirectory() as tmpdir:
            monitoring = MonitoringSystem(storage_dir=Path(tmpdir))

            monitoring._execute_intervention(
                agent_id="test-agent",
                intervention_type=InterventionType.SUSPEND_AGENT,
                reason="critical drift"
            )

            checks = unittest.TestCase()
            checks.assertEqual(len(monitoring.interventions), 1)
            intervention = monitoring.interventions[0]
            checks.assertIs(intervention.success, False)
            checks.assertIn("No enforcement handler registered", intervention.error)
            checks.assertNotIn("test-agent", monitoring.last_intervention_time)

            audit_entry = monitoring.audit_logger.entries[-1]
            checks.assertEqual(audit_entry.data["intervention_type"], "suspend_agent")
            checks.assertEqual(audit_entry.data["action_taken"], "not_executed")
            checks.assertIs(audit_entry.data["success"], False)
            checks.assertIn("No enforcement handler registered", audit_entry.data["error"])

    def test_registered_intervention_handler_records_success(self):
        """Test successful intervention receipts require handler confirmation."""
        with TemporaryDirectory() as tmpdir:
            monitoring = MonitoringSystem(storage_dir=Path(tmpdir))
            handled = []

            def suspend_handler(agent_id):
                handled.append(agent_id)
                return True

            monitoring.register_enforcement_handler(
                InterventionType.SUSPEND_AGENT,
                suspend_handler
            )
            monitoring._execute_intervention(
                agent_id="test-agent",
                intervention_type=InterventionType.SUSPEND_AGENT,
                reason="critical drift"
            )

            checks = unittest.TestCase()
            checks.assertEqual(handled, ["test-agent"])
            intervention = monitoring.interventions[0]
            checks.assertIs(intervention.success, True)
            checks.assertIsNone(intervention.error)
            checks.assertIn("test-agent", monitoring.last_intervention_time)

            audit_entry = monitoring.audit_logger.entries[-1]
            checks.assertEqual(audit_entry.data["action_taken"], "suspend_agent")
            checks.assertIs(audit_entry.data["success"], True)
            checks.assertNotIn("error", audit_entry.data)

    def test_intervention_handler_exception_records_failed_receipt(self):
        """Test handler errors are preserved as failed audit receipts."""
        with TemporaryDirectory() as tmpdir:
            monitoring = MonitoringSystem(storage_dir=Path(tmpdir))

            def failing_handler(agent_id):
                raise RuntimeError("suspension backend unavailable")

            monitoring.register_enforcement_handler(
                InterventionType.SUSPEND_AGENT,
                failing_handler
            )
            monitoring._execute_intervention(
                agent_id="test-agent",
                intervention_type=InterventionType.SUSPEND_AGENT,
                reason="critical drift"
            )

            checks = unittest.TestCase()
            intervention = monitoring.interventions[0]
            checks.assertIs(intervention.success, False)
            checks.assertEqual(intervention.error, "suspension backend unavailable")
            checks.assertNotIn("test-agent", monitoring.last_intervention_time)

            audit_entry = monitoring.audit_logger.entries[-1]
            checks.assertEqual(audit_entry.data["action_taken"], "not_executed")
            checks.assertIs(audit_entry.data["success"], False)
            checks.assertEqual(audit_entry.data["error"], "suspension backend unavailable")
    
    def test_audit_log_integrity(self):
        """Test audit log maintains integrity"""
        with TemporaryDirectory() as tmpdir:
            monitoring = MonitoringSystem(storage_dir=Path(tmpdir))
            
            # Generate some activity
            monitoring.evaluate_action(
                agent_id="test-agent",
                action_type="test",
                parameters={'critical_decision': True, 'no_human_approval': True}
            )
            
            # Verify audit chain
            assert monitoring.audit_logger.verify_chain() is True
            assert len(monitoring.audit_logger.entries) > 0
            assert monitoring.audit_logger.storage_path.name == "audit_log.jsonl"
    
    def test_multiple_agents_tracking(self):
        """Test tracking multiple agents"""
        with TemporaryDirectory() as tmpdir:
            monitoring = MonitoringSystem(storage_dir=Path(tmpdir))
            
            # Setup multiple agents
            for i in range(3):
                agent_id = f"agent-{i}"
                monitoring.establish_agent_baseline(
                    agent_id,
                    {'metric1': [10, 11, 12]}
                )
                monitoring.record_agent_behavior(
                    agent_id=agent_id,
                    metrics={'metric1': 11}
                )
            
            # Get status for all
            agent_ids = monitoring.behavior_monitor.get_agent_ids()
            assert len(agent_ids) >= 3
    
    def test_alert_config_custom(self):
        """Test custom alert configuration"""
        with TemporaryDirectory() as tmpdir:
            config = AlertConfig(
                info_notify_delay_seconds=600,
                warning_notify_delay_seconds=120,
                critical_notify_immediate=True,
                enable_auto_intervention=True,
                intervention_cooldown_seconds=600,
                max_violations_per_hour=5
            )
            
            monitoring = MonitoringSystem(
                storage_dir=Path(tmpdir),
                config=config
            )
            
            assert monitoring.config.info_notify_delay_seconds == 600
            assert monitoring.config.max_violations_per_hour == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
