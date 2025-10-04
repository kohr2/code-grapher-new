#!/usr/bin/env python3
"""
Test script to verify statements are stored in the graph
"""

import sys
sys.path.insert(0, 'src')
import json

from cobol_cst_parser import COBOLCSTParser
from graph_generator import GraphGenerator

# Test CST parser
parser = COBOLCSTParser()
analysis = parser.analyze_cobol_comprehensive('programs/vasu/vasu_fraud_management_cobol_reformatted.cbl')

print('✅ CST Analysis Complete:')
print(f'   Divisions: {len(analysis.get("divisions", []))}')
print(f'   Variables: {len(analysis.get("variables", []))}')
print(f'   Procedures: {len(analysis.get("procedures", []))}')

# Test graph generator
graph_gen = GraphGenerator()
program_name = 'VASU-FRAUD-MGMT'

try:
    cobol_nodes = graph_gen.generate_cobol_nodes_from_cst(analysis, program_name)
    print(f'\n✅ Generated {len(cobol_nodes)} COBOL nodes for graph')
    
    # Count node types
    node_types = {}
    for node in cobol_nodes:
        node_type = node.get('type', 'unknown')
        node_types[node_type] = node_types.get(node_type, 0) + 1
    
    print('\n📊 Node types in graph:')
    for node_type, count in node_types.items():
        print(f'   - {node_type}: {count}')
    
    # Check for statements specifically
    statement_nodes = [n for n in cobol_nodes if n.get('type') == 'cobol_statement']
    print(f'\n🎯 Statement nodes: {len(statement_nodes)}')
    
    if statement_nodes:
        print('✅ STATEMENTS ARE NOW IN THE GRAPH!')
        print('\nFirst few statement types:')
        stmt_types = {}
        for stmt in statement_nodes[:10]:
            stmt_type = stmt.get('data', {}).get('statement_type', 'UNKNOWN')
            stmt_types[stmt_type] = stmt_types.get(stmt_type, 0) + 1
        print(f'   {stmt_types}')
    else:
        print('❌ No statement nodes found')
        
except Exception as e:
    print(f'❌ Graph generation failed: {e}')
    import traceback
    traceback.print_exc()
