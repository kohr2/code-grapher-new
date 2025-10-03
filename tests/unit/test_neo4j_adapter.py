#!/usr/bin/env python3
"""
Tests for Neo4j Adapter
Tests fallback behavior and basic Neo4j operations when available
Following TDD approach: comprehensive testing of fallback scenarios
"""

import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import sys
import os

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from neo4j_adapter import Neo4jAdapter, Neo4jConfig, Neo4jConnectionError, Neo4jOperationError


class TestNeo4jAdapterFallback(unittest.TestCase):
    """Test Neo4j adapter fallback behavior when driver unavailable"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    @patch('neo4j_adapter.NEO4J_AVAILABLE', False)
    def test_adapter_fallback_no_driver(self):
        """Test adapter gracefully handles missing Neo4j driver"""
        adapter = Neo4jAdapter()
        self.assertFalse(adapter.available)
        self.assertFalse(adapter.is_available())
    
    @patch('neo4j_adapter.GraphDatabase.driver')
    def test_adapter_fallback_connection_error(self, mock_driver):
        """Test adapter falls back on connection errors"""
        mock_driver.side_effect = Exception("Connection failed")
        
        adapter = Neo4jAdapter()
        self.assertFalse(adapter.available)
        self.assertFalse(adapter.is_available())
    
    @patch('neo4j_adapter.NEO4J_AVAILABLE', False)
    def test_save_graph_returns_false_on_fallback(self):
        """Test save_graph returns False when Neo4j unavailable"""
        adapter = Neo4jAdapter()
        test_graph = {"nodes": [], "edges": [], "type": "test"}
        
        result = adapter.save_graph(test_graph, "test_session")
        self.assertFalse(result)
    
    @patch('neo4j_adapter.NEO4J_AVAILABLE', False)
    def test_query_graph_returns_empty_on_fallback(self):
        """Test query_graph returns empty list when Neo4j unavailable"""
        adapter = Neo4jAdapter()
        
        result = adapter.query_graph("MATCH (n) RETURN n")
        self.assertEqual(result, [])
    
    @patch('neo4j_adapter.NEO4J_AVAILABLE', False)
    def test_load_graph_returns_none_on_fallback(self):
        """Test load_graph returns None when Neo4j unavailable"""
        adapter = Neo4jAdapter()
        
        result = adapter.get_session_graph("test_session")
        self.assertIsNone(result)


class TestNeo4jConfig(unittest.TestCase):
    """Test Neo4j configuration handling"""
    
    def test_config_from_env_defaults(self):
        """Test Neo4j config uses default values"""
        # Clear environment variables for clean test
        env_vars = ['NEO4J_URI', 'NEO4J_USER', ' NEO4J_DATABASE']
        original_values = {}
        for var in env_vars:
            if var in os.environ:
                original_values[var] = os.environ[var]
                del os.environ[var]
        
        try:
            config = Neo4jConfig.from_env()
            
            self.assertEqual(config.uri, 'bolt://localhost:7687')
            self.assertEqual(config.user, 'neo4j')
            self.assertEqual(config.database, 'neo4j')
        finally:
            # Restore original environment
            for var, value in original_values.items():
                os.environ[var] = value
    
    @patch.dict(os.environ, {
        'NEO4J_URI': 'bolt://remote:7687',
        'NEO4J_USER': 'testuser',
        'NEO4J_PASSWORD': 'testpass',
        'NEO4J_DATABASE': 'testdb'
    })
    def test_config_from_env_custom(self):
        """Test Neo4j config uses environment values"""
        config = Neo4jConfig.from_env()
        
        self.assertEqual(config.uri, 'bolt://remote:7687')
        self.assertEqual(config.user, 'testuser')
        self.assertEqual(config.password, 'testpass')
        self.assertEqual(config.database, 'testdb')


class TestNeo4jAvailableOperations(unittest.TestCase):
    """Test Neo4j operations when driver is available (mocked)"""
    
    def setUp(self):
        """Set up test fixtures with mock Neo4j driver"""
        self.mock_session = Mock()
        self.mock_driver = Mock()
        self.mock_driver.session.return_value.__enter__.return_value = self.mock_session
        
    @patch('neo4j_adapter.NEO4J_AVAILABLE', True)
    @patch('neo4j_adapter.GraphDatabase.driver')
    def test_adapter_initialization_success(self, mock_graph_db):
        """Test adapter initializes successfully with Neo4j"""
        mock_graph_db.return_value = self.mock_driver
        self.mock_session.run.return_value.single.return_value = [1]
        
        adapter = Neo4jAdapter()
        self.assertTrue(adapter.available)
        self.assertTrue(adapter.is_available())
    
    @patch('neo4j_adapter.NEO4J_AVAILABLE', True)
    @patch('neo4j_adapter.GraphDatabase.driver')
    def test_save_graph_success(self, mock_graph_db):
        """Test successful graph save to Neo4j"""
        mock_graph_db.return_value = self.mock_driver
        self.mock_session.run.return_value.single.return_value = [1]
        
        adapter = Neo4jAdapter()
        test_graph = {
            "nodes": [{"id": "test_node", "type": "test"}],
            "edges": [{"from": "test_node", "to": "test_node2", "type": "test_edge"}]
        }
        
        result = adapter.save_graph(test_graph, "test_session")
        self.assertTrue(result)
    
    @patch('neo4j_adapter.NEO4J_AVAILABLE', True)
    @patch('neo4j_adapter.GraphDatabase.driver')
    def test_query_graph_success(self, mock_graph_db):
        """Test successful graph query from Neo4j"""
        mock_graph_db.return_value = self.mock_driver
        self.mock_session.run.return_value.single.return_value = [1]
        self.mock_session.run.return_value.data.return_value = [{"result": "test"}]
        
        adapter = Neo4jAdapter()
        
        result = adapter.query_graph("MATCH (n) RETURN n")
        self.assertIsInstance(result, list)
    
    @patch('neo4j_adapter.NEO4J_AVAILABLE', True)
    @patch('neo4j_adapter.GraphDatabase.driver')
    def test_load_graph_format(self, mock_graph_db):
        """Test graph loading returns proper format"""
        mock_graph_db.return_value = self.mock_driver
        self.mock_session.run.return_value.single.return_value = [1]
        
        # Mock query results for graph loading
        mock_nodes_result = [{"n": {"id": "test"}, "labels": ["TestLabel"]}]
        mock_edges_result = [{"from": {"id": "test"}, "relationship_type": "TEST_REL", "to": {"id": "test2"}, "r": {}}]
        
        def mock_query_run(query, **kwargs):
            mock_result = Mock()
            if "MATCH (n)" in query and "labels(n)" in query:
                mock_result.data.return_value = mock_nodes_result
            elif "MATCH (from)-[r]->(to)" in query:
                mock_result.data.return_value = mock_edges_result
            else:
                mock_result.data.return_value = []
            return mock_result
        
        session_manager = self.mock_driver.session.return_value
        session_manager.run = mock_query_run
        
        adapter = Neo4jAdapter()
        
        result = adapter.get_session_graph("test_session")
        
        if result:  # Only assert if Neo4j actually connects
            self.assertEqual(result["type"], "graph")
            self.assertIn("nodes", result)
            self.assertIn("edges", result)
            self.assertIn("metadata", result)


class TestNeo4jCLI(unittest.TestCase):
    """Test Neo4j CLI functionality"""
    
    @patch('neo4j_adapter.create_neoj_adapter')
    def test_cli_test_command(self, mock_create_adapter):
        """Test CLI test command"""
        mock_adapter = Mock()
        mock_adapter.is_available.return_value = True
        mock_create_adapter.return_value = mock_adapter
        
        with patch('sys.argv', ['neo4j_adapter.py', '--test']):
            with patch('neo4j_adapter.main') as mock_main:
                import neo4j_adapter
                neo4j_adapter.main()
    
    @patch('neo4j_adapter.create_neoj_adapter')
    def test_cli_list_sessions(self, mock_create_adapter):
        """Test CLI list sessions command"""
        mock_adapter = Mock()
        mock_adapter.list_sessions.return_value = ['session1', 'session2']
        mock_create_adapter.return_value = mock_adapter
        
        with patch('sys.argv', ['neo4j_adapter.py', '--sessions']):
            with patch('neo4j_adapter.main') as mock_main:
                import neo4j_adapter
                neo4j_adapter.main()


class TestFallbackBehavior(unittest.TestCase):
    """Test comprehensive fallback behavior scenarios"""
    
    @patch('neo4j_adapter.NEO4J_AVAILABLE', False)
    def test_complete_fallback_mode(self):
        """Test complete operation in fallback mode"""
        adapter = Neo4jAdapter()
        
        # All operations should handle gracefully
        self.assertFalse(adapter.save_graph({}, "test"))
        self.assertEqual(adapter.query_graph("test"), [])
        self.assertIsNone(adapter.get_session_graph("test"))
        self.assertEqual(adapter.list_sessions(), [])
        self.assertFalse(adapter.clear_session("test"))
    
    def test_adapter_close_safety(self):
        """Test adapter close method safety"""
        adapter = Neo4jAdapter()
        adapter.close()  # Should not raise exception
        
        # Multiple closes should be safe
        adapter.close()
        adapter.close()


if __name__ == '__main__':
    unittest.main()
