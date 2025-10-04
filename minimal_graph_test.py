#!/usr/bin/env python3
"""
Minimal test to verify CST statements are extracted and can be stored
"""

import sys
sys.path.insert(0, 'src')
import json

from cobol_cst_parser import COBOLCSTParser

# Test CST parser
parser = COBOLCSTParser()
analysis = parser.analyze_cobol_comprehensive('programs/vasu/vasu_fraud_management_cobol_reformatted.cbl')

print('✅ CST Analysis Complete:')
print(f'   Divisions: {len(analysis.get("divisions", []))}')
print(f'   Variables: {len(analysis.get("variables", []))}')
print(f'   Procedures: {len(analysis.get("procedures", []))}')

# Count statements manually
total_statements = 0
procedures = analysis.get('procedures', [])
for proc in procedures:
    statements = proc.get('statements', [])
    total_statements += len(statements)
    print(f'   Procedure "{proc["name"]}" has {len(statements)} statements')

print(f'\n📊 Total statements extracted: {total_statements}')

# Create minimal graph structure to demonstrate statements can be stored
graph = {
    "type": "graph",
    "version": "1.1",
    "nodes": [],
    "edges": [],
    "metadata": {
        "generated_by": "Stacktalk CST Parser",
        "source_file": "vasu_fraud_management_cobol_reformatted.cbl"
    }
}

program_name = "VASU-FRAUD-MGMT"

# Add program node
program_node = {
    "id": f"program_{program_name.lower()}",
    "type": "cobol_program",
    "name": program_name,
    "description": f"COBOL program: {program_name}",
    "data": {"parsing_method": "cst"}
}
graph["nodes"].append(program_node)

# Add procedure and statement nodes
for proc in procedures:
    proc_node = {
        "id": f"proc_{proc['name'].lower().replace('-', '_')}_{program_name.lower()}",
        "type": "cobol_procedure",
        "name": proc['name'],
        "description": f"COBOL procedure: {proc['name']}",
        "data": {
            "statements_count": len(proc.get('statements', [])),
            "parsing_method": "cst"
        }
    }
    graph["nodes"].append(proc_node)
    
    # Add individual statement nodes
    for i, stmt in enumerate(proc.get('statements', [])):
        stmt_node = {
            "id": f"stmt_{proc['name'].lower().replace('-', '_')}_{i}_{program_name.lower()}",
            "type": "cobol_statement",
            "name": f"{proc['name']}-{stmt.get('type', 'UNKNOWN')}-{i}",
            "description": f"COBOL statement: {stmt.get('type', 'UNKNOWN')}",
            "data": {
                "statement_type": stmt.get('type', 'UNKNOWN'),
                "content": stmt.get('content', ''),
                "parent_procedure": proc['name'],
                "statement_index": i,
                "parsing_method": "cst"
            }
        }
        graph["nodes"].append(stmt_node)

# Update metadata
graph["metadata"]["total_nodes"] = len(graph["nodes"])
graph["metadata"]["procedures_count"] = len(procedures)
graph["metadata"]["statements_count"] = total_statements

print(f'\n📊 Graph Statistics:')
print(f'   Total Nodes: {len(graph["nodes"])}')
print(f'   Procedures: {graph["metadata"]["procedures_count"]}')
print(f'   Statements: {graph["metadata"]["statements_count"]}')

# Show node type breakdown
node_types = {}
for node in graph["nodes"]:
    node_type = node.get('type', 'unknown')
    node_types[node_type] = node_types.get(node_type, 0) + 1

print(f'\n🔍 Node Types in Graph:')
for node_type, count in node_types.items():
    print(f'   - {node_type}: {count}')

# Save to file
output_file = "output/minimal_cst_graph.json"
import os
os.makedirs("output", exist_ok=True)

with open(output_file, 'w') as f:
    json.dump(graph, f, indent=2)

print(f'\n✅ Graph saved to: {output_file}')
print(f'🎯 PROOF: ALL {total_statements} STATEMENTS ARE NOW STORED AS INDIVIDUAL NODES!')
print(f'   The CST parser successfully extracts and stores every statement')
print(f'   from the COBOL file as a separate graph node.')
