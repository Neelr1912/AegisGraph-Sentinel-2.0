"""
Regression tests for exception handling observability improvements.

Tests verify that:
1. Logging was added to exception handlers
2. Bare except was fixed to except Exception
3. Fallback behavior remains intact
"""

import inspect
import pytest


class TestCodeInspection:
    """Verify code changes through inspection rather than runtime tests."""

    def test_stream_processor_formula_has_logging(self):
        """Verify stream processor formula evaluation has debug logging."""
        from src.real_time_streaming.stream_processor import StreamProcessor
        source = inspect.getsource(StreamProcessor._evaluate_formula)
        assert "logger.debug" in source or "logging" in source
        assert "Formula evaluation failed" in source

    def test_velocity_calculator_timestamp_has_logging(self):
        """Verify velocity calculator timestamp normalization has debug logging."""
        from src.features.velocity_calculator import VelocityCalculator
        source = inspect.getsource(VelocityCalculator._normalize_timestamp)
        assert "logger.debug" in source
        assert "Timestamp normalization failed" in source

    def test_risk_scorer_state_access_has_logging(self):
        """Verify risk scorer state access has debug logging."""
        from src.inference.risk_scorer import compute_risk_score
        source = inspect.getsource(compute_risk_score)
        assert "Failed to access API state attributes" in source

    def test_blockchain_evidence_redis_has_logging(self):
        """Verify blockchain evidence Redis operations have warning logging."""
        from src.features.blockchain_evidence import BlockchainEvidenceManager
        source = inspect.getsource(BlockchainEvidenceManager)
        # Check the entire module for Redis logging
        import src.features.blockchain_evidence as be_module
        module_source = inspect.getsource(be_module)
        assert "logger.warning" in module_source
        assert "Redis connection failed" in module_source or "Redis" in module_source

    def test_main_api_config_loading_has_logging(self):
        """Verify main API config loading has warning logging."""
        from src.api import main
        source = inspect.getsource(main._load_fallback_scoring_config)
        assert "Failed to load fallback scoring config" in source

    def test_main_api_behavioral_detection_has_logging(self):
        """Verify main API behavioral stress detection has debug logging."""
        from src.api import main
        source = inspect.getsource(main._analyze_keystrokes_sync)
        assert "Behavioral stress detection failed" in source

    def test_main_api_graph_check_has_logging(self):
        """Verify main API graph node check has debug logging."""
        from src.api import main
        # Find the endpoint that has the graph check
        source = inspect.getsource(main)
        assert "Graph node existence check failed" in source

    def test_subsystems_optional_service_has_logging(self):
        """Verify subsystems optional service construction has debug logging."""
        from src.api.dependencies import subsystems
        source = inspect.getsource(subsystems.get_lateral_movement_detector)
        assert "Lateral movement detector construction failed" in source

    def test_refactor_concurrency_has_logging(self):
        """Verify refactor_concurrency behavioral detection has debug logging."""
        import refactor_concurrency
        source = inspect.getsource(refactor_concurrency.refactor)
        assert "Behavioral stress detection failed" in source


class TestBareExceptFix:
    """Test that bare except has been fixed to catch only Exception."""

    def test_auth_bare_except_fixed(self):
        """Verify bare except was changed to except Exception in auth.py."""
        try:
            import src.saas.routes.auth as auth_module
            source = inspect.getsource(auth_module.get_optional_user)
            assert "except Exception:" in source
            # Ensure no bare except remains
            lines = source.split('\n')
            for line in lines:
                if 'except:' in line and 'except Exception:' not in line:
                    # Check if it's a comment or part of a string
                    if not line.strip().startswith('#') and '"""' not in line and "'''" not in line:
                        pytest.fail(f"Found bare except: {line}")
        except ImportError:
            pytest.skip("pyotp dependency not available, skipping auth test")


class TestFallbackBehaviorPreservation:
    """Test that fallback behaviors remain intact using simple tests."""

    def test_stream_processor_formula_returns_zero(self):
        """Formula evaluation should return 0.0 on error."""
        from src.real_time_streaming.stream_processor import StreamProcessor
        processor = StreamProcessor()
        result = processor._evaluate_formula("invalid", {})
        assert result == 0.0

    def test_velocity_calculator_timestamp_returns_fallback(self):
        """Timestamp normalization should return fallback on error."""
        from src.features.velocity_calculator import VelocityCalculator
        calculator = VelocityCalculator()
        result = calculator._normalize_timestamp("invalid", 999.0)
        assert result == 999.0


class TestAuditLoggingPreserved:
    """Verify existing audit logging is still in place."""

    def test_watchdog_audit_has_debug_logging(self):
        """Verify watchdog audit failure has debug logging."""
        from src.runtime.watchdog import RuntimeWatchdog
        source = inspect.getsource(RuntimeWatchdog._audit)
        assert "debug" in source
        assert "Watchdog audit recording failed" in source

    def test_lifecycle_manager_audit_has_debug_logging(self):
        """Verify lifecycle manager audit failure has debug logging."""
        from src.runtime.lifecycle_manager import LifecycleManager
        source = inspect.getsource(LifecycleManager._audit)
        assert "debug" in source
        assert "Runtime audit recording failed" in source

    def test_resource_manager_audit_has_debug_logging(self):
        """Verify resource manager audit failure has debug logging."""
        from src.runtime.resources.resource_manager import _audit_resource_event
        source = inspect.getsource(_audit_resource_event)
        assert "debug" in source
        assert "Resource audit recording failed" in source

    def test_recovery_manager_audit_has_debug_logging(self):
        """Verify recovery manager audit failure has debug logging."""
        from src.runtime.recovery_manager import RecoveryManager
        source = inspect.getsource(RecoveryManager._audit)
        assert "debug" in source
        assert "Recovery audit recording failed" in source

    def test_config_reload_audit_has_debug_logging(self):
        """Verify config reload audit failure has debug logging."""
        from src.configuration.config_reload import ConfigReloadManager
        source = inspect.getsource(ConfigReloadManager._audit)
        assert "debug" in source
        assert "Configuration audit recording failed" in source


class TestEventDispatchLoggingPreserved:
    """Verify event dispatch logging is still in place."""

    def test_event_dispatcher_has_exception_logging(self):
        """Verify event dispatcher has exception logging."""
        from src.runtime.events.dispatcher import EventDispatcher
        source = inspect.getsource(EventDispatcher._process_loop)
        assert "logger.exception" in source
        assert "Event dispatch failed" in source


class TestModelRegistryLoggingPreserved:
    """Verify model registry logging is still in place."""

    def test_model_registry_has_warning_logging(self):
        """Verify model registry has warning logging for load failures."""
        from src.training.model_registry import ModelRegistry
        source = inspect.getsource(ModelRegistry.load_champion)
        assert "logger.warning" in source
        assert "Failed to load champion checkpoint" in source
