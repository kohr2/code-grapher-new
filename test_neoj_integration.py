#!/usr/bin/env python3
"""
Neo4j Integration Demo
Demonstrates advanced graph operations with Neo4j persistence
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from neo4j_adapter import Neo4jAdapter
from graph_generator import GraphGenerator
from dsl_parser import DSLParser

def demo_neo4j_integration():
    """Demonstrate Neo4j integration capabilities"""
    
    print("🚀 Neo4j Integration Demonstration")
    print("="*50)
    
    # Initialize Neo4j adapter
    print("\n1. Initializing Neo4j Adapter...")
    adapter = Neo4jAdapter()
    
    if not adapter.is_available():
        print("❌ Neo4j not available - cannot demonstrate")
        return
    
    print("✅ Neo4j adapter ready!")
    
    # Test session management
    print("\n2. Session Management...")
    sessions = adapter.list_sessions()
    print(f"📋 Current sessions: {len(sessions)}")
    for session in sessions:
        print(f"   - {session}")
    
    # Load DSL rules and create graph
    print("\n3. Creating Demo Graph...")
    parser = DSLParser(rules_dir="rules")
    rules = parser.load_all_rules()
    
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
            "name": "Find all variables connected to NSF rule",
            "query": """MATCH (rule:dslrule)-[:DEFINES_VARIABLE]->(var:dslvariable) 
                       WHERE rule.name CONTAINS 'NSF'
                       RETURN rule.name, var.name, var.description""",
            "params": {}
        },
        {
            "name": "Graph schema",
            "query": "CALL db.schema.visualization()",
            "params": {}
        }
    ]
    
    for query_info in queries:
        print(f"\n🔍 {query_info['name']}:")
        try:
            results = adapter.query_graph(query_info['query'], query_info['params'])
            if results:
                for row in results[:3]:  # Show first 3 results
                    print(f"   {dict(row)}")
                if len(results) > 3:
                    print(f"   ... and {len(results) - 3} more results")
            else:
                print("   No results found")
        except Exception as e:
            print(f"   Query failed: {e}")
    
    # Show final session list
    print(f"\n7. Final Session List:")
    final_sessions = adapter.list_sessions()
    print(f"📋 Total sessions: {len(final_sessions)}")
    for session in final_sessions:
        print(f"   - {session}")
    
    print(f"\n🎯 Neo4j Integration Demo Complete!")
    print(f"✅ Sessions created: {session_name}")
    print(f"📊 Graph nodes saved: {len(graph_gen.graph['nodes'])}")
    print(f"🔗 Graph edges saved: {len(graph_gen.graph['edges'])}")

if __name__ == "__main__":
    demo_neo4j_integration()
