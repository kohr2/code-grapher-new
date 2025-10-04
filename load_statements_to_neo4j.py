#!/usr/bin/env python3
"""
Script to load the working CST graph (with statements) into Neo4j
"""

import sys
sys.path.insert(0, 'src')
import json
import os

def load_working_graph_to_neo4j():
    """Load the working graph with statements into Neo4j"""
    
    # Check if working graph exists
    working_graph_file = 'output/working_cst_graph.json'
    if not os.path.exists(working_graph_file):
        print(f'❌ Working graph file not found: {working_graph_file}')
        return False
    
    # Load the working graph
    with open(working_graph_file, 'r') as f:
        graph = json.load(f)
    
    nodes = graph.get('nodes', [])
    print(f'📊 Loading working graph: {len(nodes)} nodes')
    
    # Count node types
    node_types = {}
    for node in nodes:
        node_type = node.get('type', 'unknown')
        node_types[node_type] = node_types.get(node_type, 0) + 1
    
    print('Node types to load:')
    for node_type, count in node_types.items():
        print(f'   - {node_type}: {count}')
    
    # Check for statements
    stmt_count = node_types.get('cobol_statement', 0)
    if stmt_count == 0:
        print('❌ No statement nodes found in working graph!')
        return False
    
    print(f'\\n🎯 Found {stmt_count} statement nodes to load into Neo4j!')
    
    # Try to load into Neo4j
    try:
        from neo4j_adapter import Neo4jAdapter
        adapter = Neo4jAdapter()
        
        if not adapter.is_available():
            print('❌ Neo4j not available - cannot load statements')
            print('   Please ensure Neo4j is running and configured')
            return False
        
        print('✅ Neo4j connection available')
        
        # Clear existing data
        print('🗑️ Clearing existing Neo4j data...')
        adapter.run_query('MATCH (n) DETACH DELETE n')
        
        # Load nodes
        print('📥 Loading nodes into Neo4j...')
        for i, node in enumerate(nodes):
            if i % 100 == 0:
                print(f'   Loading node {i+1}/{len(nodes)}...')
            
            node_id = node.get('id', f'node_{i}')
            node_type = node.get('type', 'unknown')
            properties = node.get('data', {})
            
            # Add basic properties
            properties['name'] = node.get('name', '')
            properties['description'] = node.get('description', '')
            
            adapter.create_node(
                node_id=node_id,
                labels=[node_type.title()],
                properties=properties
            )
        
        print(f'✅ Successfully loaded {len(nodes)} nodes into Neo4j!')
        print(f'🎯 Including {stmt_count} cobol_statement nodes!')
        
        # Verify the load
        print('\\n🔍 Verifying load...')
        result = adapter.run_query('MATCH (n:cobol_statement) RETURN count(n) as count')
        actual_stmt_count = result[0]['count'] if result else 0
        print(f'   cobol_statement nodes in Neo4j: {actual_stmt_count}')
        
        if actual_stmt_count == stmt_count:
            print('✅ All statement nodes successfully loaded!')
        else:
            print(f'⚠️ Expected {stmt_count}, got {actual_stmt_count}')
        
        return True
        
    except Exception as e:
        print(f'❌ Error loading to Neo4j: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print('🚀 Loading CST Graph with Statements to Neo4j')
    print('=' * 50)
    
    success = load_working_graph_to_neo4j()
    
    if success:
        print('\\n🎉 SUCCESS! Statement nodes are now in Neo4j!')
        print('   You can now query: MATCH (n:cobol_statement) RETURN n LIMIT 10')
    else:
        print('\\n❌ Failed to load statement nodes to Neo4j')
        print('   Check Neo4j connection and try again')
