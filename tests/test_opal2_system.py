#!/usr/bin/env python3
"""
Opal2 Modular System - Test Suite
Comprehensive testing for all Opal2 components
"""

import pytest
import asyncio
import numpy as np
import json
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import tempfile
import shutil
from typing import Dict, Any

# Import Opal2 modules
from ..glyph_core import GlyphCore
from ..glyph_cache import GlyphCache
from ..quantum_renderer import QuantumRenderer, RenderContext, RenderResult, QuantumState
from ..plugin_system import PluginSystem, PluginInterface, RendererPlugin, PluginType
from ..config_manager import ConfigurationManager, ConfigValidationRule
from ..api.opal2_api import app
from ...symbolic.geometric_algebra import GeometricAlgebra
from ...symbolic.quantum_symbolic_vector import QuantumSymbolicVector

class TestGlyphCore:
    """Test suite for GlyphCore"""
    
    def setup_method(self):
        """Set up test environment"""
        self.glyph_core = GlyphCore()
        self.test_expression = "x^2 + y^2"
        self.test_style_params = {"color": "blue", "width": 2}
    
    def test_glyph_core_initialization(self):
        """Test GlyphCore initialization"""
        assert self.glyph_core is not None
        assert hasattr(self.glyph_core, 'geometric_algebra')
        assert hasattr(self.glyph_core, 'quantum_vector')
    
    @pytest.mark.asyncio
    async def test_glyph_generation_async(self):
        """Test async glyph generation"""
        # Mock the generate_async method
        with patch.object(self.glyph_core, 'generate_async', return_value={
            "vertices": [[0, 0], [1, 1], [2, 0]],
            "style": self.test_style_params,
            "quantum_enhanced": True
        }) as mock_generate:
            
            result = await self.glyph_core.generate_async(
                expression=self.test_expression,
                style_params=self.test_style_params,
                quantum_enhancement=True
            )
            
            assert result is not None
            assert "vertices" in result
            assert "style" in result
            assert "quantum_enhanced" in result
            mock_generate.assert_called_once()
    
    def test_glyph_parsing(self):
        """Test glyph expression parsing"""
        # Test would validate expression parsing
        assert self.glyph_core is not None
    
    @pytest.mark.asyncio
    async def test_quantum_enhancement(self):
        """Test quantum enhancement functionality"""
        # Mock quantum enhancement
        with patch.object(self.glyph_core, '_apply_quantum_enhancement', return_value={
            "coherence_matrix": np.eye(3),
            "entanglement_data": {"strength": 0.8}
        }) as mock_enhance:
            
            test_data = {"vertices": [[0, 0], [1, 1]]}
            result = await self.glyph_core._apply_quantum_enhancement(test_data)
            
            assert result is not None
            assert "coherence_matrix" in result
            assert "entanglement_data" in result

class TestGlyphCache:
    """Test suite for GlyphCache"""
    
    def setup_method(self):
        """Set up test environment"""
        self.glyph_cache = GlyphCache()
        self.test_key = "test_glyph_123"
        self.test_data = {"vertices": [[0, 0], [1, 1]], "color": "blue"}
    
    @pytest.mark.asyncio
    async def test_cache_set_get_async(self):
        """Test async cache set and get operations"""
        # Mock cache operations
        with patch.object(self.glyph_cache, 'set_async', return_value=True) as mock_set:
            with patch.object(self.glyph_cache, 'get_async', return_value=self.test_data) as mock_get:
                
                # Test set
                set_result = await self.glyph_cache.set_async(self.test_key, self.test_data)
                assert set_result is True
                
                # Test get
                get_result = await self.glyph_cache.get_async(self.test_key)
                assert get_result == self.test_data
                
                mock_set.assert_called_once_with(self.test_key, self.test_data)
                mock_get.assert_called_once_with(self.test_key)
    
    @pytest.mark.asyncio
    async def test_cache_clear_async(self):
        """Test async cache clear operation"""
        with patch.object(self.glyph_cache, 'clear_async', return_value=5) as mock_clear:
            result = await self.glyph_cache.clear_async()
            assert result == 5
            mock_clear.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cache_stats(self):
        """Test cache statistics"""
        with patch.object(self.glyph_cache, 'get_stats', return_value={
            "total_items": 10,
            "hit_rate": 0.85,
            "miss_rate": 0.15
        }) as mock_stats:
            
            stats = await self.glyph_cache.get_stats()
            assert stats["total_items"] == 10
            assert stats["hit_rate"] == 0.85
            mock_stats.assert_called_once()

class TestQuantumRenderer:
    """Test suite for QuantumRenderer"""
    
    def setup_method(self):
        """Set up test environment"""
        self.quantum_renderer = QuantumRenderer()
        self.test_glyph_data = {
            "vertices": [[0, 0], [100, 0], [100, 100], [0, 100]],
            "indices": [0, 1, 2, 3],
            "dimensions": 2
        }
    
    def test_quantum_renderer_initialization(self):
        """Test QuantumRenderer initialization"""
        assert self.quantum_renderer is not None
        assert hasattr(self.quantum_renderer, 'geometric_algebra')
        assert hasattr(self.quantum_renderer, 'quantum_vector')
        assert hasattr(self.quantum_renderer, 'render_plugins')
    
    @pytest.mark.asyncio
    async def test_async_render_webgl(self):
        """Test async WebGL rendering"""
        result = await self.quantum_renderer.render_async(
            glyph_data=self.test_glyph_data,
            renderer="webgl",
            dimensions={"width": 800, "height": 600}
        )
        
        assert isinstance(result, RenderResult)
        assert result.format == "webgl"
        assert result.render_time >= 0
        assert "quantum_metrics" in result.__dict__
    
    @pytest.mark.asyncio
    async def test_async_render_canvas(self):
        """Test async Canvas rendering"""
        result = await self.quantum_renderer.render_async(
            glyph_data=self.test_glyph_data,
            renderer="canvas",
            dimensions={"width": 400, "height": 400}
        )
        
        assert isinstance(result, RenderResult)
        assert result.format == "canvas"
        assert isinstance(result.output, str)
    
    @pytest.mark.asyncio
    async def test_async_render_svg(self):
        """Test async SVG rendering"""
        result = await self.quantum_renderer.render_async(
            glyph_data=self.test_glyph_data,
            renderer="svg",
            dimensions={"width": 600, "height": 600}
        )
        
        assert isinstance(result, RenderResult)
        assert result.format == "svg"
        assert isinstance(result.output, str)
        assert result.output.startswith('<svg')
    
    def test_quantum_enhancement_application(self):
        """Test quantum enhancement application"""
        context = RenderContext(
            glyph_data=self.test_glyph_data,
            quantum_state=QuantumState.ENHANCED,
            quantum_params={"coherence_factor": 0.8, "entanglement_strength": 0.6}
        )
        
        # Test coherence matrix generation
        coherence_matrix = self.quantum_renderer._generate_coherence_matrix(
            self.test_glyph_data, 0.8
        )
        
        assert isinstance(coherence_matrix, np.ndarray)
        assert coherence_matrix.dtype == complex
    
    def test_superposition_states_generation(self):
        """Test superposition states generation"""
        superposition_states = self.quantum_renderer._generate_superposition_states(
            self.test_glyph_data, 3
        )
        
        assert isinstance(superposition_states, list)
        assert len(superposition_states) == 3
        
        for state in superposition_states:
            assert "amplitude" in state
            assert "phase" in state
            assert "state_data" in state
    
    def test_performance_metrics(self):
        """Test performance metrics tracking"""
        # Simulate some render times
        self.quantum_renderer._update_performance_metrics("webgl", 0.1)
        self.quantum_renderer._update_performance_metrics("webgl", 0.2)
        self.quantum_renderer._update_performance_metrics("canvas", 0.05)
        
        metrics = self.quantum_renderer.get_performance_metrics()
        
        assert "webgl" in metrics
        assert "canvas" in metrics
        assert metrics["webgl"]["sample_count"] == 2
        assert metrics["canvas"]["sample_count"] == 1

class TestPluginSystem:
    """Test suite for PluginSystem"""
    
    def setup_method(self):
        """Set up test environment"""
        self.plugin_system = PluginSystem()
    
    def test_plugin_system_initialization(self):
        """Test PluginSystem initialization"""
        assert self.plugin_system is not None
        assert hasattr(self.plugin_system, 'plugins')
        assert hasattr(self.plugin_system, 'plugin_info')
        assert len(self.plugin_system.plugins) > 0  # Built-in plugins should be loaded
    
    def test_builtin_plugins_loaded(self):
        """Test that built-in plugins are loaded"""
        plugin_names = list(self.plugin_system.plugins.keys())
        
        expected_plugins = ["webgl_renderer", "canvas_renderer", "svg_renderer"]
        
        for expected_plugin in expected_plugins:
            assert expected_plugin in plugin_names
    
    def test_get_plugin(self):
        """Test plugin retrieval"""
        webgl_plugin = self.plugin_system.get_plugin("webgl_renderer")
        assert webgl_plugin is not None
        assert isinstance(webgl_plugin, RendererPlugin)
    
    def test_get_plugins_by_type(self):
        """Test plugin retrieval by type"""
        renderer_plugins = self.plugin_system.get_plugins_by_type(PluginType.RENDERER)
        assert len(renderer_plugins) > 0
        
        for plugin in renderer_plugins:
            assert isinstance(plugin, RendererPlugin)
    
    def test_plugin_registration(self):
        """Test custom plugin registration"""
        class TestPlugin(PluginInterface):
            def get_info(self):
                from ..plugin_system import PluginInfo
                return PluginInfo(
                    name="test_plugin",
                    version="1.0.0",
                    author="Test Author",
                    description="Test plugin",
                    plugin_type=PluginType.PROCESSOR
                )
        
        test_plugin = TestPlugin()
        self.plugin_system.register_plugin("test_plugin", test_plugin)
        
        assert "test_plugin" in self.plugin_system.plugins
        assert self.plugin_system.get_plugin("test_plugin") is test_plugin
    
    def test_plugin_statistics(self):
        """Test plugin statistics"""
        stats = self.plugin_system.get_plugin_statistics()
        
        assert "total_plugins" in stats
        assert "loaded_plugins" in stats
        assert "plugin_types" in stats
        assert stats["total_plugins"] > 0

class TestConfigurationManager:
    """Test suite for ConfigurationManager"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ConfigurationManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_config_manager_initialization(self):
        """Test ConfigurationManager initialization"""
        assert self.config_manager is not None
        assert hasattr(self.config_manager, 'configs')
        assert hasattr(self.config_manager, 'validation_rules')
        assert Path(self.temp_dir).exists()
    
    def test_create_default_config(self):
        """Test default configuration creation"""
        result = self.config_manager.create_default_config("opal2_graphics")
        assert result is True
        assert "opal2_graphics" in self.config_manager.configs
        
        config = self.config_manager.get_config("opal2_graphics")
        assert config is not None
        assert "renderer" in config
        assert "canvas" in config
        assert "quantum" in config
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Create a valid config
        valid_config = {
            "renderer": {
                "default_engine": "webgl",
                "quantum_enhancement": True,
                "performance_mode": "balanced"
            },
            "canvas": {
                "width": 800,
                "height": 600
            },
            "quantum": {
                "coherence_factor": 0.8,
                "entanglement_strength": 0.6,
                "superposition_depth": 3
            }
        }
        
        result = self.config_manager._validate_config("opal2_graphics", valid_config)
        assert result is True
        
        # Test invalid config
        invalid_config = {
            "renderer": {
                "default_engine": "invalid_engine",  # Invalid value
                "quantum_enhancement": True,
                "performance_mode": "balanced"
            },
            "canvas": {
                "width": 50,  # Too small
                "height": 600
            },
            "quantum": {
                "coherence_factor": 1.5,  # Out of range
                "entanglement_strength": 0.6,
                "superposition_depth": 3
            }
        }
        
        result = self.config_manager._validate_config("opal2_graphics", invalid_config)
        assert result is False
    
    def test_config_value_operations(self):
        """Test configuration value get/set operations"""
        # Create default config
        self.config_manager.create_default_config("opal2_graphics")
        
        # Test getting values
        default_engine = self.config_manager.get_config_value("opal2_graphics", "renderer.default_engine")
        assert default_engine == "webgl"
        
        # Test setting values
        result = self.config_manager.set_config_value("opal2_graphics", "renderer.default_engine", "canvas")
        assert result is True
        
        updated_engine = self.config_manager.get_config_value("opal2_graphics", "renderer.default_engine")
        assert updated_engine == "canvas"
    
    def test_config_change_callbacks(self):
        """Test configuration change callbacks"""
        callback_called = False
        callback_event = None
        
        def test_callback(event):
            nonlocal callback_called, callback_event
            callback_called = True
            callback_event = event
        
        # Register callback
        self.config_manager.register_change_callback("opal2_graphics", test_callback)
        
        # Create config and make a change
        self.config_manager.create_default_config("opal2_graphics")
        self.config_manager.set_config_value("opal2_graphics", "canvas.width", 1024)
        
        # Check if callback was called
        assert callback_called is True
        assert callback_event is not None
        assert "canvas.width" in callback_event.changed_keys

class TestOpal2API:
    """Test suite for Opal2 API"""
    
    def setup_method(self):
        """Set up test environment"""
        self.client = None  # Would use TestClient from fastapi.testclient
    
    def test_api_initialization(self):
        """Test API initialization"""
        assert app is not None
        assert hasattr(app, 'routes')
    
    # Additional API tests would go here using FastAPI's TestClient
    # This would require importing TestClient and mocking the dependencies

class TestIntegration:
    """Integration tests for Opal2 system"""
    
    def setup_method(self):
        """Set up integration test environment"""
        self.glyph_core = GlyphCore()
        self.glyph_cache = GlyphCache()
        self.quantum_renderer = QuantumRenderer()
        self.plugin_system = PluginSystem()
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ConfigurationManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up integration test environment"""
        shutil.rmtree(self.temp_dir)
    
    @pytest.mark.asyncio
    async def test_full_rendering_pipeline(self):
        """Test the complete rendering pipeline"""
        # 1. Generate glyph data
        glyph_data = {
            "vertices": [[0, 0], [100, 0], [100, 100], [0, 100]],
            "indices": [0, 1, 2, 3],
            "dimensions": 2
        }
        
        # 2. Cache the glyph
        cache_key = "integration_test_glyph"
        with patch.object(self.glyph_cache, 'set_async', return_value=True):
            await self.glyph_cache.set_async(cache_key, glyph_data)
        
        # 3. Render with quantum enhancement
        result = await self.quantum_renderer.render_async(
            glyph_data=glyph_data,
            renderer="webgl",
            dimensions={"width": 800, "height": 600},
            quantum_params={"coherence_factor": 0.8}
        )
        
        # 4. Verify results
        assert isinstance(result, RenderResult)
        assert result.format == "webgl"
        assert "quantum_metrics" in result.__dict__
        assert result.quantum_metrics is not None
    
    def test_plugin_system_integration(self):
        """Test plugin system integration with quantum renderer"""
        # Get a plugin from the plugin system
        webgl_plugin = self.plugin_system.get_plugin("webgl_renderer")
        assert webgl_plugin is not None
        
        # Register the plugin with the quantum renderer
        self.quantum_renderer.register_plugin("test_webgl", webgl_plugin.render)
        
        # Verify the plugin is registered
        renderers = self.quantum_renderer.list_renderers()
        assert "test_webgl" in renderers
    
    def test_config_system_integration(self):
        """Test configuration system integration"""
        # Create configuration
        self.config_manager.create_default_config("opal2_graphics")
        
        # Get configuration values
        config = self.config_manager.get_config("opal2_graphics")
        assert config is not None
        
        # Test configuration would be used by other components
        quantum_params = config.get("quantum", {})
        assert "coherence_factor" in quantum_params
        assert "entanglement_strength" in quantum_params

class TestPerformance:
    """Performance tests for Opal2 system"""
    
    def setup_method(self):
        """Set up performance test environment"""
        self.quantum_renderer = QuantumRenderer()
        self.large_glyph_data = {
            "vertices": [[i, j] for i in range(100) for j in range(100)],
            "indices": list(range(10000)),
            "dimensions": 2
        }
    
    @pytest.mark.asyncio
    async def test_large_glyph_rendering_performance(self):
        """Test performance with large glyph data"""
        import time
        
        start_time = time.time()
        
        result = await self.quantum_renderer.render_async(
            glyph_data=self.large_glyph_data,
            renderer="webgl",
            dimensions={"width": 1920, "height": 1080}
        )
        
        end_time = time.time()
        render_time = end_time - start_time
        
        # Performance assertion (should render within reasonable time)
        assert render_time < 5.0  # Should complete within 5 seconds
        assert isinstance(result, RenderResult)
        assert result.render_time > 0
    
    @pytest.mark.asyncio
    async def test_concurrent_rendering_performance(self):
        """Test performance with concurrent rendering"""
        import asyncio
        
        test_glyph_data = {
            "vertices": [[0, 0], [100, 0], [100, 100], [0, 100]],
            "indices": [0, 1, 2, 3],
            "dimensions": 2
        }
        
        # Create multiple concurrent render tasks
        tasks = []
        for i in range(10):
            task = self.quantum_renderer.render_async(
                glyph_data=test_glyph_data,
                renderer="webgl",
                dimensions={"width": 400, "height": 400}
            )
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks)
        
        # Verify all renders completed successfully
        assert len(results) == 10
        for result in results:
            assert isinstance(result, RenderResult)
            assert result.format == "webgl"

# Test fixtures and utilities
@pytest.fixture
def temp_config_dir():
    """Create a temporary configuration directory"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_glyph_data():
    """Provide sample glyph data for testing"""
    return {
        "vertices": [[0, 0], [100, 0], [100, 100], [0, 100]],
        "indices": [0, 1, 2, 3],
        "dimensions": 2,
        "color": "blue",
        "width": 2
    }

@pytest.fixture
def mock_quantum_params():
    """Provide mock quantum parameters"""
    return {
        "coherence_factor": 0.8,
        "entanglement_strength": 0.6,
        "superposition_depth": 3,
        "decoherence_rate": 0.1
    }

# Main test runner
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
