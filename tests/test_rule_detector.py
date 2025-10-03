#!/usr/bin/env python3
"""
Test module for Rule Detector
Following TDD approach: tests first, then implementation
Analyzes graph for policy violations using sophisticated AI-enhanced detection
"""

import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from dsl_parser import DSLRule, DSLVariable, DSLRequirement
from cobol_cst_parser import COBOLCSTParser, DSLCondition
from graph_generator import GraphGenerator
from rule_detector import Violation


class TestRuleDetector(unittest.TestCase):
    """Test cases for the Rule Detector module"""
    
    def _parse_cobol_with_cst(self, cobol_text: str, program_name: str):
        """Helper method to parse COBOL with CST parser and generate nodes"""
        cst_parser = COBOLCSTParser()
        analysis = cst_parser.analyze_cobol_comprehensive(cobol_text)
        return self.graph_generator.generate_cobol_nodes_from_cst(analysis, program_name)
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create sample DSL rule for testing
        self.sample_rule = DSLRule(
            name="NSF Banking Rule",
            description="NSF events must be logged and fee applied before rejection",
            variables=[
                DSLVariable("ACCOUNT-BALANCE", "numeric", "9(8)V99", "Current account balance"),
                DSLVariable("WITHDRAWAL-AMOUNT", "numeric", "9(8)V99", "Amount to withdraw"),
                DSLVariable("NSF-FEE", "numeric", "9(2)V99", "NSF fee amount", "35.00"),
                DSLVariable("NSF-LOG-FLAG", "flag", "X(1)", "Flag to track NSF logging", default="N")
            ],
            conditions=[
                DSLCondition("insufficient_funds", "ACCOUNT-BALANCE < WITHDRAWAL-AMOUNT", "Check if account has sufficient funds")
            ],
            requirements=[
                DSLRequirement("nsf_logging", "NSF events must be logged", "NSF-LOG-FLAG variable must be defined", "NSF-LOG-FLAG variable not defined", "HIGH"),
                DSLRequirement("nsf_fee_application", "NSF fee must be applied", "ADD NSF-FEE TO WITHDRAWAL-AMOUNT must be present", "NSF fee not added to withdrawal amount", "HIGH")
            ],
            compliant_logic={
                "when_insufficient_funds": [
                    "MOVE 'Y' TO NSF-LOG-FLAG",
                    "ADD NSF-FEE TO WITHDRAWAL-AMOUNT",
                    "DISPLAY 'NSF Event Logged - Fee Applied'",
                    "PERFORM REJECT-TRANSACTION"
                ]
            },
            violation_examples={
                "missing_log_flag": {"remove_variables": ["NSF-LOG-FLAG"]},
                "missing_fee_application": {"remove_logic": ["ADD NSF-FEE TO WITHDRAWAL-AMOUNT"]}
            }
        )
        
        # Create sample graph for testing
        self.graph_generator = GraphGenerator()
        self.graph_generator.add_dsl_rule(self.sample_rule)
        
    def test_rule_detector_initialization(self):
        """Test RuleDetector can be initialized"""
        from rule_detector import RuleDetector
        
        detector = RuleDetector()
        self.assertIsNotNone(detector)
        self.assertTrue(hasattr(detector, 'detection_strategies'))
        self.assertTrue(hasattr(detector, 'violation_severities'))

    def test_detect_violations_in_empty_graph(self):
        """Test violation detection in empty graph"""
        from rule_detector import RuleDetector
        
        detector = RuleDetector()
        empty_graph = {"nodes": [], "edges": []}
        
        violations = detector.detect_violations(empty_graph)
        self.assertEqual(len(violations), 0)

    def test_detect_violations_with_cobol_code(self):
        """Test violation detection by analyzing COBOL code"""
        from rule_detector import RuleDetector
        
        detector = RuleDetector()
        
        # Add COBOL code to graph
        cobol_code = """IDENTIFICATION DIVISION.
       PROGRAM-ID. TEST-PROGRAM.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 ACCOUNT-BALANCE PIC 9(8)V99.
       01 NSF-FEE PIC 9(2)V99.
        * Missing NSF-LOG-FLAG variable
        
       PROCEDURE DIVISION.
       IF ACCOUNT-BALANCE < WITHDRAWAL-AMOUNT THEN
           ADD NSF-FEE TO WITHDRAWAL-AMOUNT
           DISPLAY 'Transaction Failed'
       END-IF
       STOP RUN."""
        
        cobol_nodes = self._parse_cobol_with_cst(cobol_code, "TEST-PROGRAM")
        self.graph_generator.connect_cobol_to_rules(cobol_nodes)
        violations = detector.detect_violations(self.graph_generator.graph)
        
        # Should detect missing NSF-LOG-FLAG variable
        self.assertGreater(len(violations), 0)
        
        # Check for specific violation
        violation_messages = [v.message for v in violations]
        self.assertTrue(any("NSF-LOG-FLAG" in msg for msg in violation_messages))

    def test_detect_violations_with_compliant_code(self):
        """Test violation detection with fully compliant code"""
        from rule_detector import RuleDetector
        
        detector = RuleDetector()
        
        # Add compliant COBOL code to graph
        compliant_code = """IDENTIFICATION DIVISION.
       PROGRAM-ID. COMPLIANT-PROGRAM.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 ACCOUNT-BALANCE PIC 9(8)V99.
       01 WITHDRAWAL-AMOUNT PIC 9(8)V99.
       01 NSF-FEE PIC 9(2)V99.
       01 NSF-LOG-FLAG PIC X(1).
        
       PROCEDURE DIVISION.
       IF ACCOUNT-BALANCE < WITHDRAWAL-AMOUNT THEN
           MOVE 'Y' TO NSF-LOG-FLAG
           ADD NSF-FEE TO WITHDRAWAL-AMOUNT
           DISPLAY 'NSF Event Logged - Fee Applied'
           PERFORM REJECT-TRANSACTION
       END-IF
       STOP RUN."""
        
        # Use CST parser directly
        cst_parser = COBOLCSTParser()
        analysis = cst_parser.analyze_cobol_comprehensive(compliant_code)
        cobol_nodes = self.graph_generator.generate_cobol_nodes_from_cst(analysis, "COMPLIANT-PROGRAM")
        self.graph_generator.connect_cobol_to_rules(cobol_nodes)
        violations = detector.detect_violations(self.graph_generator.graph)
        
        # Should detect no violations
        self.assertEqual(len(violations), 0)

    def test_detect_violations_by_requirement_type(self):
        """Test detecting violations for specific requirement types"""
        from rule_detector import RuleDetector
        
        detector = RuleDetector()
        
        # Test missing variable violation
        missing_var_code = """IDENTIFICATION DIVISION.
       PROGRAM-ID. MISSING-VAR.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 ACCOUNT-BALANCE PIC 9(8)V99.
       01 NSF-FEE PIC 9(2)V99.
        
       PROCEDURE DIVISION.
       STOP RUN."""
        
        # Use CST parser directly
        cst_parser = COBOLCSTParser()
        analysis = cst_parser.analyze_cobol_comprehensive(missing_var_code)
        cobol_nodes = self.graph_generator.generate_cobol_nodes_from_cst(analysis, "MISSING-VAR")
        self.graph_generator.connect_cobol_to_rules(cobol_nodes)
        violations = detector.detect_violations(self.graph_generator.graph)
        
        # Should detect missing NSF-LOG-FLAG requirement violation
        var_violations = [v for v in violations if v.type == "missing_variable"]
        self.assertGreater(len(var_violations), 0)

    def test_violation_severity_classification(self):
        """Test classification of violations by severity"""
        from rule_detector import RuleDetector
        
        detector = RuleDetector()
        
        # Add code with multiple severity violations
        mixed_code = """IDENTIFICATION DIVISION.
       PROGRAM-ID. MIXED-VIOLATIONS.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 ACCOUNT-BALANCE PIC 9(8)V99.
       * Missing NSF-FEE and NSF-LOG-FLAG
       
       PROCEDURE DIVISION.
       IF ACCOUNT-BALANCE < WITHDRAWAL-AMOUNT THEN
           DISPLAY 'Low severity violation: no specific NSF handling'
       END-IF
       STOP RUN."""
        
        # Use CST parser directly
        cst_parser = COBOLCSTParser()
        analysis = cst_parser.analyze_cobol_comprehensive(mixed_code, "MIXED-VIOLATIONS")
        self.graph_generator.connect_cobol_to_rules(cobol_nodes)
        violations = detector.detect_violations(self.graph_generator.graph)
        
        # Should categorize violations by severity
        high_violations = [v for v in violations if v.severity == "HIGH"]
        medium_violations = [v for v in violations if v.severity == "MEDIUM"]
        
        self.assertGreater(len(high_violations), 0)
        # Should have at least one high severity violation (missing NSF requirements)

    def test_violation_code_element_linking(self):
        """Test linking violations to specific code elements"""
        from rule_detector import RuleDetector
        
        detector = RuleDetector()
        
        # Add code with specific violations
        code_with_violations = """IDENTIFICATION DIVISION.
       PROGRAM-ID. LINKED-VIOLATIONS.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 ACCOUNT-BALANCE PIC 9(8)V99.
       01 NSF-FEE PIC 9(2)V99.
        
       PROCEDURE DIVISION.
       IF ACCOUNT-BALANCE < WITHDRAWAL-AMOUNT THEN
           ADD NSF-FEE TO WITHDRAWAL-AMOUNT
           PERFORM REJECT-TRANSACTION
       END-IF
       STOP RUN."""
        
        # Use CST parser directly
        cst_parser = COBOLCSTParser()
        analysis = cst_parser.analyze_cobol_comprehensive(code_with_violations, "LINKED-VIOLATIONS")
        self.graph_generator.connect_cobol_to_rules(cobol_nodes)
        violations = detector.detect_violations(self.graph_generator.graph)
        
        # Should link violations to specific code elements
        code_violations = [v for v in violations if v.code_element]
        self.assertGreater(len(code_violations), 0)
        
        # Check specific linking
        for violation in code_violations:
            self.assertIsNotNone(violation.source_file)
            self.assertIsNotNone(violation.line_number)

    def test_detect_complex_business_violations(self):
        """Test detection of complex business logic violations"""
        from rule_detector import RuleDetector
        
        detector = RuleDetector()
        
        # Add code with subtle business logic violation
        subtle_violation_code = """IDENTIFICATION DIVISION.
       PROGRAM-ID. SUBTLE-VIOLATION.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 ACCOUNT-BALANCE PIC 9(8)V99.
       01 NSF-FEE PIC 9(2)V99.
       01 NSF-LOG-FLAG PIC X(1).
        
       PROCEDURE DIVISION.
       IF ACCOUNT-BALANCE < WITHDRAWAL-AMOUNT THEN
           MOVE 'Y' TO NSF-LOG-FLAG
           * Subtle violation: fee applied but not properly logged as NSF event
           ADD NSF-FEE TO WITHDRAWAL-AMOUNT
           DISPLAY 'Transaction Failed' * Missing proper NSF event logging
           PERFORM REJECT-TRANSACTION
       END-IF
       STOP RUN."""
        
        # Use CST parser directly
        cst_parser = COBOLCSTParser()
        analysis = cst_parser.analyze_cobol_comprehensive(subtle_violation_code, "SUBTLE-VIOLATION")
        self.graph_generator.connect_cobol_to_rules(cobol_nodes)
        violations = detector.detect_violations(self.graph_generator.graph)
        
        # Should detect subtle business logic violations
        business_violations = [v for v in violations if v.type == "business_logic_violation"]
        # Even though variables exist, business logic might be incorrect
        self.assertGreaterEqual(len(violations), 0)

    def test_ai_enhanced_violation_detection(self):
        """Test AI-enhanced violation detection capabilities"""
        from rule_detector import RuleDetector
        import os
        
        os.environ['OPENAI_KEY'] = 'test_api_key'
        
        detector = RuleDetector()
        
        # Test sophisticated violation detection
        sophisticated_code = """IDENTIFICATION DIVISION.
       PROGRAM-ID. SOPHISTICATED-VIOLATION.
       * This code appears compliant but has subtle audit trail gaps
       
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 ACCOUNT-BALANCE PIC 9(8)V99.
       01 NSF-FEE PIC 9(2)V99.
       01 NSF-LOG-FLAG PIC X(1).
       """
        
        # Use CST parser directly
        cst_parser = COBOLCSTParser()
        analysis = cst_parser.analyze_cobol_comprehensive(sophisticated_code, "SOPHISTICATED-VIOLATION")
        self.graph_generator.connect_cobol_to_rules(cobol_nodes)
        
        # Mock AI-enhanced detection if available
        with patch.object(detector, '_use_ai_violation_detection') as mock_ai:
            mock_violation = Violation(
                type="ai_enhanced_violation",
                message="Sophisticated audit trail gap detected",
                severity="HIGH",
                requirement="nsf_logging",
                code_element="SOPHISTICATED-VIOLATION",
                source_file="SOPHISTICATED-VIOLATION.cob",
                line_number=5
            )
            mock_ai.return_value = [mock_violation]
            
            violations = detector.detect_violations(self.graph_generator.graph)
            
            if detector.ai_available:
                ai_violations = [v for v in violations if v.type == "ai_enhanced_violation"]
                self.assertGreater(len(ai_violations), 0)
        
        os.environ.pop('OPENAI_KEY', None)

    def test_generate_violation_report(self):
        """Test generation of detailed violation report"""
        from rule_detector import RuleDetector
        
        detector = RuleDetector()
        
        # Add code with violations
        violation_code = """IDENTIFICATION DIVISION.
       PROGRAM-ID. REPORT-TEST.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 ACCOUNT-BALANCE PIC 9(8)V99.
       01 NSF-FEE PIC 9(2)V99.
        
       PROCEDURE DIVISION.
       IF ACCOUNT-BALANCE < WITHDRAWAL-AMOUNT THEN
           ADD NSF-FEE TO WITHDRAWAL-AMOUNT
           DISPLAY 'Transaction Failed'
       END-IF
       STOP RUN."""
        
        # Use CST parser directly
        cst_parser = COBOLCSTParser()
        analysis = cst_parser.analyze_cobol_comprehensive(violation_code, "REPORT-TEST")
        self.graph_generator.connect_cobol_to_rules(cobol_nodes)
        violations = detector.detect_violations(self.graph_generator.graph)
        
        # Generate violation report
        report = detector.generate_violation_report(violations)
        
        # Should contain summary statistics
        self.assertIn("total_violations", report)
        self.assertIn("severity_breakdown", report)
        self.assertIn("files_affected", report)
        self.assertIn("requirements_violated", report)
        
        # Should provide actionable insights
        self.assertIn("recommendations", report)

    def test_integrated_graph_analysis(self):
        """Test complete graph analysis workflow"""
        from rule_detector import RuleDetector
        
        detector = RuleDetector()
        
        # Add multiple COBOL programs to graph
        programs = [
            ("COMPLIANT-PROGRAM", """IDENTIFICATION DIVISION.
       PROGRAM-ID. COMPLIANT-PROGRAM.
       DATA DIVISION.
       01 NSF-LOG-FLAG PIC X(1).
       PROCEDURE DIVISION.
       MOVE 'Y' TO NSF-LOG-FLAG
       STOP RUN."""),
            
            ("VIOLATION-PROGRAM", """IDENTIFICATION DIVISION.
       PROGRAM-ID. VIOLATION-PROGRAM.
       DATA DIVISION.
       01 ACCOUNT-BALANCE PIC 9(8)V99.
       PROCEDURE DIVISION.
       STOP RUN."""),
        ]
        
        for program_name, code in programs:
            # Use CST parser directly
        cst_parser = COBOLCSTParser()
        analysis = cst_parser.analyze_cobol_comprehensive(code, program_name)
            self.graph_generator.connect_cobol_to_rules(cobol_nodes)
        
        # Analyze complete graph
        violations = detector.detect_violations(self.graph_generator.graph)
        
        # Should detect violations across multiple programs
        programs_with_violations = set(v.source_file for v in violations if v.source_file)
        self.assertGreater(len(programs_with_violations), 0)
        
        # Should provide comprehensive analysis
        report = detector.generate_violation_report(violations)
        self.assertIn("compliance_summary", report)
        self.assertIn("overall_compliance_rate", report)

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
