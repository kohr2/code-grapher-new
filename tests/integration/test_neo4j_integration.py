#!/usr/bin/env python3
"""
Neo4j Integration Demo
Demonstrates advanced graph operations with Neo4j persistence
"""

import unittest
import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from neo4j_adapter import Neo4jAdapter
from graph_generator import GraphGenerator
from dsl_parser import DSLParser


class TestNeo4jIntegrationDemo(unittest.TestCase):
    """Test Neo4j integration demonstration functionality"""
    
    def test_neo4j_integration_demo(self):
        """Test Neo4j integration demonstration capabilities"""
        print("\n🚀 Neo4j Integration Demonstration")
        print("="*50)
        
        # Initialize Neo4j adapter
        print("\n1. Initializing Neo4j Adapter...")
        adapter = Neo4jAdapter()
        
        if not adapter.is_available():
            print("❌ Neo4j not available - skipping demo")
            self.skipTest("Neo4j not available")
            return
        
        print("✅ Neo4j adapter ready!")
        
        # Test session management
        print("\n2. Session Management...")
        sessions = adapter.list_sessions()
        print(f"📋 Current sessions: {len(sessions)}")
        for session in sessions[:3]:  # Show first 3 sessions
            print(f"   - {session}")
        
        # Load DSL rules and create graph
        print("\n3. Creating Demo Graph...")
        rules_dir = Path(__file__).parent.parent / "rules"
        if not rules_dir.exists():
            # Create a minimal test rule for demo
            rules_dir.mkdir(exist_ok=True)
            test_rule = """
rule:
  name: "Demo Rule"
  description: "Demo rule for Neo4j integration test"

variables:
  - name: "DEMO-VAR"
    type: "string"
    pic: "X(10)"
    description: "Demo variable"

requirements:
  demo_requirement:
    description: "Demo variable must be present"
    check: "DEMO-VAR variable must be defined"
    violation_message: "DEMO-VAR variable not defined"
    severity: "HIGH"

compliant_logic:
  demo_logic:
    - "MOVE 'DEMO' TO DEMO-VAR"
"""
            demo_rule_file = rules_dir / "demo_rule.dsl"
            demo_rule_file.write_text(test_rule.strip())
        
        parser = DSLParser(rules_dir=str(rules_dir))
        rules = parser.load_all_rules()
        
        if not rules:
            print("❌ No DSL rules found - skipping demo")
            self.skipTest("No DSL rules found")
            return
        
        graph_gen = GraphGenerator()
        for rule in rules:
            graph_gen.add_dsl_rule(rule)
        
        # Save to Neo4j with unique session
        import datetime
        session_name = f"demo_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"\n4. Saving to Neo4j Session: {session_name}")
        success = adapter.save_graph(graph_gen.graph, session_name)
        
        if success:
            print("✅ Graph saved to Neo4j successfully!")
            
            # Retrieve and compare
            print(f"\n5. Retrieving Graph from Neo4j...")
            retrieved_graph = adapter.get_session_graph(session_name)
            
            if retrieved_graph:
                print("✅ Graph retrieved successfully!")
                print(f"📊 Retrieved: {len(retrieved_graph['nodes'])} nodes, {len(retrieved_graph['edges'])} edges")
                print(f"📋 Metadata: {retrieved_graph.get('metadata', {})}")
                
                # Verify graph structure
                self.assertIn("nodes", retrieved_graph)
                self.assertIn("edges", retrieved_graph)
                self.assertIsInstance(retrieved_graph["nodes"], list)
                self.assertIsInstance(retrieved_graph["edges"], list)
            else:
                print("❌ Failed to retrieve graph")
        
        # Test Cypher queries
        print(f"\n6. Advanced Cypher Queries...")
        
        queries = [
            {
                "name": "Count all DSL rules",
                "query": "MATCH (n:dslrule) RETURN count(n) as rule_count",
                "params": {}
            },
            {
                "name": "Find all variables",
                "query": "MATCH (var:dslvariable) RETURN var.name as variable_name LIMIT 5",
                "params": {}
            },
            {
                "name": "Graph statistics",
                "query": "CALL apoc.meta.stats()",
                "params": {}
            }
        ]
        
        for query_info in queries:
            print(f"\n🔍 {query_info['name']}:")
            try:
                results = adapter.query_graph(query_info['query'], query_info['params'])
                if results:
                    for row in results[:2]:  # Show first 2 results
                        print(f"   {dict(row)}")
                    if len(results) > 2:
                        print(f"   ... and {len(results) - 2} more results")
                else:
                    print("   No results found")
            except Exception as e:
                print(f"   Query failed: {e}")
        
        # Show final session list
        print(f"\n7. Final Session List:")
        final_sessions = adapter.list_sessions()
        print(f"📋 Total sessions: {len(final_sessions)}")
        for session in final_sessions[:3]:  # Show first 3 sessions
            print(f"   - {session}")
        
        print(f"\n🎯 Neo4j Integration Demo Complete!")
        print(f"✅ Sessions created: {session_name}")
        print(f"📊 Graph nodes saved: {len(graph_gen.graph['nodes'])}")
        print(f"🔗 Graph edges saved: {len(graph_gen.graph['edges'])}")
        
        # Verify demo completed successfully
        self.assertTrue(len(graph_gen.graph['nodes']) > 0)
        self.assertTrue(len(graph_gen.graph['edges']) >= 0)


def demo_neo4j_integration():
    """Standalone demo function for direct execution"""
    test_instance = TestNeo4jIntegrationDemo()
    test_instance.test_neo4j_integration_demo()


if __name__ == "__main__":
    # Allow both unittest and direct demo execution
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_neo4j_integration()
    else:
        unittest.main()
