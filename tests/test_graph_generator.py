#!/usr/bin/env python3
"""
Test module for Graph Generator
Following TDD approach: tests first, then implementation
"""

import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from dsl_parser import DSLRule, DSLVariable, DSLRequirement


class TestGraphGenerator(unittest.TestCase):
    """Test cases for the Graph Generator module"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create sample DSL rule for testing
        self.sample_rule = DSLRule(
            name="Test Rule",
            description="Test banking rule",
            variables=[
                DSLVariable("ACCOUNT-BALANCE", "numeric", "9(8)V99", "Account balance"),
                DSLVariable("NSF-FEE", "numeric", "9(2)V99", "NSF fee", "35.00")
            ],
            conditions=[],
            requirements=[
                DSLRequirement("test_req", "Test requirement", "ACCOUNT-BALANCE > 0", "Balance too low", "HIGH")
            ],
            compliant_logic={"when_valid": ["MOVE 'Y' TO NSF-FLAG"]},
            violation_examples={"missing_flag": {"remove_variables": ["NSF-FLAG"]}}
        )
        
        # Expected graph structure
        self.expected_graph_structure = {
            "type": "graph",
            "version": "1.0",
            "nodes": [],
            "edges": [],
            "metadata": {}
        }

    def test_graph_generator_initialization(self):
        """Test GraphGenerator can be initialized"""
        # self.skipTest("Implementation not yet created")
        
        from graph_generator import GraphGenerator
        
        graph_gen = GraphGenerator()
        self.assertIsNotNone(graph_gen)
        self.assertIsInstance(graph_gen.graph, dict)
        self.assertEqual(graph_gen.graph["type"], "graph")
        self.assertEqual(graph_gen.graph["version"], "1.1")

    def test_add_dsl_rule_to_graph(self):
        """Test adding DSL rule to graph creates proper nodes and edges"""
        # self.skipTest("Implementation not yet created")
        
        from graph_generator import GraphGenerator
        
        graph_gen = GraphGenerator()
        graph_gen.add_dsl_rule(self.sample_rule)
        
        # Should have 4 nodes: 1 rule + 2 variables + 1 requirement + 0 conditions
        self.assertEqual(len(graph_gen.graph["nodes"]), 4)
        
        # Should have 3 edges: rule->var1, rule->var2, rule->requirement
        self.assertEqual(len(graph_gen.graph["edges"]), 3)
        
        # Check rule node exists
        rule_nodes = [n for n in graph_gen.graph["nodes"] if n["type"] == "dsl_rule"]
        self.assertEqual(len(rule_nodes), 1)
        self.assertEqual(rule_nodes[0]["name"], "Test Rule")

    def test_generate_cobol_nodes_from_text(self):
        """Test parsing COBOL text into graph nodes"""
        # self.skipTest("Implementation not yet created")
        
        from graph_generator import GraphGenerator
        
        cobol_text = """
       IDENTIFICATION DIVISION.
       PROGRAM-ID. WITHDRAWAL-PROCESS.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 ACCOUNT-BALANCE PIC 9(8)V99.
       01 NSF-FEE PIC 9(2)V99 VALUE 35.00.
       PROCEDURE DIVISION.
           IF ACCOUNT-BALANCE < 1000
              MOVE 'Y' TO NSF-FLAG
           END-IF.
       STOP RUN.
        """
        
        graph_gen = GraphGenerator()
        nodes = graph_gen.generate_cobol_nodes(cobol_text, "test_program")
        
        # Should have program node + 2 variables + 1 procedure
        self.assertEqual(len(nodes), 4)
        
        # Check node types
        node_types = [n["type"] for n in nodes]
        self.assertIn("cobol_program", node_types)
        self.assertIn("cobol_variable", node_types)
        self.assertIn("cobol_procedure", node_types)

    def test_connect_cobol_to_dsl_rules(self):
        """Test connecting COBOL elements to applicable DSL rules"""
        # self.skipTest("Implementation not yet created")
        
        from graph_generator import GraphGenerator
        
        graph_gen = GraphGenerator()
        graph_gen.add_dsl_rule(self.sample_rule)
        
        cobol_text = "01 ACCOUNT-BALANCE PIC 9(8)V99."
        cobol_nodes = graph_gen.generate_cobol_nodes(cobol_text, "test_program")
        
        # This should create connections between COBOL variables and DSL variables
        graph_gen.connect_cobol_to_rules(cobol_nodes)
        
        # Count connection edges
        connection_edges = [e for e in graph_gen.graph["edges"] 
                          if e["type"] == "variable_match"]
        self.assertGreater(len(connection_edges), 0)

    def test_detect_violations_in_graph(self):
        """Test violation detection across connected graph"""
        # self.skipTest("Implementation not yet created")
        
        from graph_generator import GraphGenerator
        
        graph_gen = GraphGenerator()
        graph_gen.add_dsl_rule(self.sample_rule)
        
        # COBOL with missing variable (should cause violation)
        cobol_text = """
       PROGRAM-ID. INCOMPLETE-TEST.
       DATA DIVISION.
       01 ACCOUNT-BALANCE PIC 9(8)V99.
       PROCEDURE DIVISION.
           STOP RUN.
        """
        
        cobol_nodes = graph_gen.generate_cobol_nodes(cobol_text, "test_program")
        graph_gen.connect_cobol_to_rules(cobol_nodes)
        
        violations = graph_gen.detect_violations()
        
        # Should detect missing NSF-FEE variable
        self.assertGreater(len(violations), 0)
        self.assertTrue(any("NSF-FEE" in str(v) for v in violations))

    def test_save_graph_to_file(self):
        """Test saving graph to JSON file"""
        # self.skipTest("Implementation not yet created")
        
        from graph_generator import GraphGenerator
        
        graph_gen = GraphGenerator()
        graph_gen.add_dsl_rule(self.sample_rule)
        
        output_file = self.temp_path / "test_graph.json"
        graph_gen.save_graph(str(output_file))
        
        self.assertTrue(output_file.exists())
        
        # Verify file content
        with open(output_file, 'r') as f:
            saved_graph = json.load(f)
        
        self.assertEqual(saved_graph["type"], "graph")
        self.assertEqual(len(saved_graph["nodes"]), 4)

    def test_load_graph_from_file(self):
        """Test loading graph from JSON file"""
        # self.skipTest("Implementation not yet created")
        
        from graph_generator import GraphGenerator
        
        # Create a test graph file
        test_graph = {
            "type": "graph",
            "version": "1.1",
            "nodes": [{"id": "test_node", "type": "test", "name": "Test"}],
            "edges": [],
            "metadata": {"test": True}
        }
        
        test_file = self.temp_path / "test_graph.json"
        with open(test_file, 'w') as f:
            json.dump(test_graph, f)
        
        graph_gen = GraphGenerator()
        graph_gen.load_graph(str(test_file))
        
        self.assertEqual(graph_gen.graph["type"], "graph")
        self.assertEqual(len(graph_gen.graph["nodes"]), 1)

    def test_graph_statistics(self):
        """Test graph statistics calculation"""
        # self.skipTest("Implementation not yet created")
        
        from graph_generator import GraphGenerator
        
        graph_gen = GraphGenerator()
        graph_gen.add_dsl_rule(self.sample_rule)
        
        stats = graph_gen.get_statistics()
        
        self.assertIn("total_nodes", stats)
        self.assertIn("total_edges", stats)
        self.assertIn("dsl_rules", stats)
        self.assertIn("cobol_programs", stats)
        
        self.assertEqual(stats["dsl_rules"], 1)
        self.assertEqual(stats["total_nodes"], 4)

    def test_graph_query_by_type(self):
        """Test querying graph nodes by type"""
        # self.skipTest("Implementation not yet created")
        
        from graph_generator import GraphGenerator
        
        graph_gen = GraphGenerator()
        graph_gen.add_dsl_rule(self.sample_rule)
        
        variables = graph_gen.query_nodes_by_type("dsl_variable")
        self.assertEqual(len(variables), 2)
        
        requirements = graph_gen.query_nodes_by_type("dsl_requirement")
        self.assertEqual(len(requirements), 1)

    def test_graph_traversal_connections(self):
        """Test graph traversal to find connections"""
        # self.skipTest("Implementation not yet created")
        
        from graph_generator import GraphGenerator
        
        graph_gen = GraphGenerator()
        graph_gen.add_dsl_rule(self.sample_rule)
        
        # Get connections from sample rule
        rule_id = "rule_test_rule"
        connections = graph_gen.get_connected_nodes(rule_id)
        
        # Should have connections to variables and requirements
        self.assertGreater(len(connections), 0)
        connection_types = [c["to_node_type"] for c in connections]
        self.assertIn("dsl_variable", connection_types)

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
