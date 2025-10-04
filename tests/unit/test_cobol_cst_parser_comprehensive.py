#!/usr/bin/env python3
"""
Comprehensive test for COBOL CST Parser with real-world COBOL file
Tests the parser against the vasu_fraud_management_cobol_reformatted.cbl file
"""

import unittest
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cobol_cst_parser import COBOLCSTParser, COBOLParsingError


class TestCOBOLCSTParserComprehensive(unittest.TestCase):
    """Comprehensive test for COBOL CST Parser with real COBOL file"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parser = COBOLCSTParser()
        
        # Load the real COBOL file
        cobol_file = Path(__file__).parent.parent.parent / "programs" / "vasu" / "vasu_fraud_management_cobol_reformatted.cbl"
        self.assertTrue(cobol_file.exists(), f"COBOL file not found: {cobol_file}")
        
        with open(cobol_file, 'r') as f:
            self.cobol_text = f.read()
        
        # Parse the COBOL text
        self.cst = self.parser.parse_cobol_text(self.cobol_text)
        
        # Extract all elements
        self.program_info = self.parser.extract_program_info(self.cst)
        self.variables = self.parser.extract_variables(self.cst)
        self.procedures = self.parser.extract_procedures(self.cst)
        self.divisions = self.parser.extract_divisions(self.cst)
    
    def test_cobol_file_parsing(self):
        """Test that the COBOL file can be parsed successfully"""
        self.assertIsNotNone(self.cst, "CST should be created successfully")
        self.assertIsNotNone(self.cobol_text, "COBOL text should be loaded")
        self.assertTrue(len(self.cobol_text) > 1000, "COBOL file should be substantial")
    
    def test_program_extraction(self):
        """Test program information extraction"""
        # Should extract program info
        self.assertIsNotNone(self.program_info, "Program info should be extracted")
        self.assertIsInstance(self.program_info, dict, "Program info should be a dictionary")
        
        # Should have program ID
        self.assertIn('program_id', self.program_info, "Program info should contain program_id")
    
    def test_divisions_extraction(self):
        """Test that all 4 divisions are extracted"""
        # Target: 4 divisions (IDENTIFICATION, ENVIRONMENT, DATA, PROCEDURE)
        self.assertGreaterEqual(len(self.divisions), 4, 
                               f"Should extract at least 4 divisions, got {len(self.divisions)}")
        
        # Check for specific divisions
        division_names = [div['name'] for div in self.divisions]
        expected_divisions = ['IDENTIFICATION', 'ENVIRONMENT', 'DATA', 'PROCEDURE']
        
        for expected_div in expected_divisions:
            # Allow for partial matches due to line number prefixes
            found = any(expected_div in name for name in division_names)
            self.assertTrue(found, f"Should find {expected_div} division")
    
    def test_sections_extraction(self):
        """Test that sections within divisions are extracted"""
        total_sections = sum(len(div.get('sections', [])) for div in self.divisions)
        
        # Target: 19 sections total
        self.assertGreaterEqual(total_sections, 10, 
                               f"Should extract multiple sections, got {total_sections}")
        
        # Check for specific sections
        all_sections = []
        for div in self.divisions:
            all_sections.extend(div.get('sections', []))
        
        section_names = [sec['name'] for sec in all_sections]
        expected_sections = ['CONFIGURATION', 'INPUT-OUTPUT', 'FILE', 'WORKING-STORAGE']
        
        for expected_sec in expected_sections:
            found = any(expected_sec in name for name in section_names)
            self.assertTrue(found, f"Should find {expected_sec} section")
    
    def test_variables_extraction(self):
        """Test that COBOL variables are extracted from DATA DIVISION"""
        # Should extract variables
        self.assertGreater(len(self.variables), 0, "Should extract COBOL variables")
        
        # Check for specific variables from the fraud management system
        variable_names = [var.name for var in self.variables]
        expected_variables = ['WS-TOTAL-RISK-SCORE', 'FRAUD-LOG-RECORD', 'RULE-01-TRIGGERED']
        
        found_variables = []
        for expected_var in expected_variables:
            found = any(expected_var in name for name in variable_names)
            if found:
                found_variables.append(expected_var)
        
        self.assertGreater(len(found_variables), 0, 
                          f"Should find some expected variables, found: {found_variables}")
    
    def test_procedures_extraction(self):
        """Test that procedures and paragraphs are extracted"""
        # Should extract procedures
        self.assertGreater(len(self.procedures), 0, "Should extract COBOL procedures")
        
        # Check for specific procedures from the fraud management system
        procedure_names = [proc['name'] for proc in self.procedures]
        expected_procedures = ['MAIN-CONTROL', 'INITIALIZE-PROGRAM', 'PROCESS-TRANSACTIONS']
        
        found_procedures = []
        for expected_proc in expected_procedures:
            found = any(expected_proc in name for name in procedure_names)
            if found:
                found_procedures.append(expected_proc)
        
        self.assertGreater(len(found_procedures), 0, 
                          f"Should find some expected procedures, found: {found_procedures}")
    
    def test_statements_extraction(self):
        """Test that statements within procedures are extracted"""
        total_statements = sum(len(proc.get('statements', [])) for proc in self.procedures)
        
        # Target: 708 statements (approximate)
        self.assertGreater(total_statements, 100, 
                          f"Should extract many statements, got {total_statements}")
        
        # Check for specific statement types
        all_statements = []
        for proc in self.procedures:
            all_statements.extend(proc.get('statements', []))
        
        statement_types = [stmt.get('type', 'UNKNOWN') for stmt in all_statements]
        expected_types = ['MOVE', 'IF', 'PERFORM', 'COMPUTE', 'ADD']
        
        found_types = []
        for expected_type in expected_types:
            if expected_type in statement_types:
                found_types.append(expected_type)
        
        self.assertGreater(len(found_types), 0, 
                          f"Should find various statement types, found: {found_types}")
    
    def test_hierarchical_structure(self):
        """Test that hierarchical relationships are preserved"""
        # Variables should have proper level hierarchy
        level_01_vars = [var for var in self.variables if var.level == '01']
        self.assertGreater(len(level_01_vars), 0, "Should have 01-level variables")
        
        # Procedures should have statements
        procedures_with_statements = [proc for proc in self.procedures if proc.get('statements')]
        self.assertGreater(len(procedures_with_statements), 0, 
                          "Should have procedures with statements")
    
    def test_line_number_handling(self):
        """Test that line-numbered COBOL format is handled correctly"""
        # Should handle line numbers like "000100 IDENTIFICATION DIVISION."
        # without treating them as variable names
        variable_names = [var.name for var in self.variables]
        
        # Should not have variables starting with "000"
        line_number_vars = [name for name in variable_names if name.startswith('000')]
        self.assertEqual(len(line_number_vars), 0, 
                        f"Should not have variables starting with '000', found: {line_number_vars}")
    
    def test_comprehensive_coverage(self):
        """Test overall coverage of the COBOL file structure"""
        # Summary test - verify we're extracting a reasonable amount of structure
        total_elements = (len(self.divisions) + 
                         len(self.variables) + 
                         len(self.procedures) + 
                         sum(len(proc.get('statements', [])) for proc in self.procedures))
        
        # Should extract hundreds of elements from a real COBOL file
        self.assertGreater(total_elements, 500, 
                          f"Should extract many elements from real COBOL file, got {total_elements}")
        
        print(f"\n📊 Comprehensive CST Parser Results:")
        print(f"   Divisions: {len(self.divisions)}")
        print(f"   Variables: {len(self.variables)}")
        print(f"   Procedures: {len(self.procedures)}")
        print(f"   Total Statements: {sum(len(proc.get('statements', [])) for proc in self.procedures)}")
        print(f"   Total Elements: {total_elements}")


if __name__ == '__main__':
    unittest.main()
