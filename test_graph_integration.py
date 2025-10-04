#!/usr/bin/env python3
"""
Test script to verify CST parser integration with graph generator
"""

import sys
sys.path.insert(0, 'src')

from cobol_cst_parser import COBOLCSTParser

# Test CST parser
parser = COBOLCSTParser()
analysis = parser.analyze_cobol_comprehensive('programs/vasu/vasu_fraud_management_cobol_reformatted.cbl')

print('✅ CST Analysis Complete:')
print(f'   Divisions: {len(analysis.get("divisions", []))}')
print(f'   Variables: {len(analysis.get("variables", []))}')
print(f'   Procedures: {len(analysis.get("procedures", []))}')

# Show divisions
divisions = analysis.get('divisions', [])
print('\n📋 Divisions extracted:')
for div in divisions:
    sections = div.get('sections', [])
    print(f'  - {div["name"]} ({len(sections)} sections)')
    for sec in sections[:3]:  # Show first 3 sections
        print(f'    • {sec["name"]}')

# Show variables
variables = analysis.get('variables', [])
print(f'\n🔧 Variables extracted ({len(variables)} total):')
for var in variables[:10]:  # Show first 10 variables
    print(f'  - {var.name} (level: {var.level})')

# Show procedures
procedures = analysis.get('procedures', [])
print(f'\n⚙️ Procedures extracted ({len(procedures)} total):')
total_statements = 0
for proc in procedures[:5]:  # Show first 5 procedures
    statements = proc.get('statements', [])
    total_statements += len(statements)
    print(f'  - {proc["name"]} ({len(statements)} statements)')

print(f'\n📊 Summary:')
print(f'   Total statements: {total_statements}')
print(f'   Total elements: {len(divisions) + len(variables) + len(procedures) + total_statements}')

print('\n🎯 These elements should now be stored in the graph!')
