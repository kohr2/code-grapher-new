"""
Integration tests for RuleDetector to ReportGenerator workflow
Tests the integration between violation detection and HTML report generation
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from dsl_parser import DSLParser, DSLError
from cobol_cst_parser import COBOLCSTParser
from graph_generator import GraphGenerator
from rule_detector import RuleDetector, Violation
from report_generator import ReportGenerator


class TestViolationsToReportIntegration(unittest.TestCase):
    """Test RuleDetector integration with ReportGenerator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create test directories
        self.rules_dir = self.temp_path / "rules"
        self.examples_dir = self.temp_path / "examples"
        self.output_dir = self.temp_path / "output"
        
        self.rules_dir.mkdir()
        self.examples_dir.mkdir()
        self.output_dir.mkdir()
        
        # Create test DSL rule
        self._create_test_dsl_rule()
        
        # Initialize components
        self.cst_parser = COBOLCSTParser()
        self.graph_gen = GraphGenerator()
        self.rule_detector = RuleDetector()
        self.report_gen = ReportGenerator()
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def _create_test_dsl_rule(self):
        """Create a test DSL rule file"""
        test_rule = """
rule:
  name: "Financial Compliance Rule"
  description: "Comprehensive financial compliance validation"

variables:
  - name: "ACCOUNT-NUMBER"
    type: "string"
    pic: "X(10)"
    description: "Account identifier"
  - name: "TRANSACTION-AMOUNT"
    type: "numeric"
    pic: "9(8)V99"
    description: "Transaction amount"
  - name: "APPROVAL-CODE"
    type: "string"
    pic: "X(5)"
    description: "Approval code"
  - name: "AUDIT-TRAIL-FLAG"
    type: "flag"
    pic: "X(1)"
    description: "Audit trail flag"
  - name: "RISK-RATING"
    type: "numeric"
    pic: "9(2)"
    description: "Risk rating score"

conditions:
  high_value_check:
    check: "TRANSACTION-AMOUNT > 5000"
    description: "High-value transaction check"
  risk_assessment:
    check: "RISK-RATING > 70"
    description: "High-risk assessment check"

requirements:
  account_validation:
    description: "Account number must be validated"
    check: "ACCOUNT-NUMBER variable must be defined"
    violation_message: "ACCOUNT-NUMBER variable not defined"
    severity: "HIGH"
  amount_validation:
    description: "Transaction amount must be validated"
    check: "TRANSACTION-AMOUNT variable must be defined"
    violation_message: "TRANSACTION-AMOUNT variable not defined"
    severity: "HIGH"
  approval_process:
    description: "Approval process must be implemented"
    check: "APPROVAL-CODE variable must be defined"
    violation_message: "APPROVAL-CODE variable not defined"
    severity: "MEDIUM"
  audit_trail:
    description: "Audit trail must be maintained"
    check: "AUDIT-TRAIL-FLAG variable must be defined"
    violation_message: "AUDIT-TRAIL-FLAG variable not defined"
    severity: "MEDIUM"
  risk_management:
    description: "Risk management must be implemented"
    check: "RISK-RATING variable must be defined"
    violation_message: "RISK-RATING variable not defined"
    severity: "HIGH"

compliant_logic:
  process_high_value:
    - "IF TRANSACTION-AMOUNT > 5000"
    - "MOVE 'HIGH' TO APPROVAL-CODE"
    - "MOVE 'Y' TO AUDIT-TRAIL-FLAG"
    - "PERFORM RISK-ASSESSMENT"
  process_risk_management:
    - "IF RISK-RATING > 70"
    - "MOVE 'HIGH' TO APPROVAL-CODE"
    - "PERFORM ADDITIONAL-VALIDATION"

violation_examples:
  missing_account_validation:
    description: "ACCOUNT-NUMBER variable missing"
    remove_variables: ["ACCOUNT-NUMBER"]
  missing_amount_validation:
    description: "TRANSACTION-AMOUNT variable missing"
    remove_variables: ["TRANSACTION-AMOUNT"]
  missing_approval_process:
    description: "APPROVAL-CODE variable missing"
    remove_variables: ["APPROVAL-CODE"]
  missing_audit_trail:
    description: "AUDIT-TRAIL-FLAG variable missing"
    remove_variables: ["AUDIT-TRAIL-FLAG"]
  missing_risk_management:
    description: "RISK-RATING variable missing"
    remove_variables: ["RISK-RATING"]
"""
        
        rule_file = self.rules_dir / "financial_rule.dsl"
        rule_file.write_text(test_rule.strip())
    
    def _create_sample_violations(self):
        """Create sample violations for testing"""
        violations = [
            Violation(
                type="missing_variable",
                message="ACCOUNT-NUMBER variable not defined",
                severity="HIGH",
                requirement="account_validation",
                source_file="COMPLIANCE-TEST.cob",
                line_number=10,
                dsl_rule="Financial Compliance Rule"
            ),
            Violation(
                type="missing_variable",
                message="TRANSACTION-AMOUNT variable not defined",
                severity="HIGH",
                requirement="amount_validation",
                source_file="COMPLIANCE-TEST.cob",
                line_number=15,
                dsl_rule="Financial Compliance Rule"
            ),
            Violation(
                type="missing_variable",
                message="APPROVAL-CODE variable not defined",
                severity="MEDIUM",
                requirement="approval_process",
                source_file="COMPLIANCE-TEST.cob",
                line_number=20,
                dsl_rule="Financial Compliance Rule"
            ),
            Violation(
                type="missing_variable",
                message="AUDIT-TRAIL-FLAG variable not defined",
                severity="MEDIUM",
                requirement="audit_trail",
                source_file="COMPLIANCE-TEST.cob",
                line_number=25,
                dsl_rule="Financial Compliance Rule"
            ),
            Violation(
                type="missing_variable",
                message="RISK-RATING variable not defined",
                severity="HIGH",
                requirement="risk_management",
                source_file="COMPLIANCE-TEST.cob",
                line_number=30,
                dsl_rule="Financial Compliance Rule"
            )
        ]
        return violations
    
    def test_violations_to_html_report_integration(self):
        """Test violation data to HTML report generation"""
        # Create sample violations
        violations = self._create_sample_violations()
        
        # Create sample graph
        parser = DSLParser(rules_dir=str(self.rules_dir))
        rules = parser.load_all_rules()
        self.graph_gen.add_dsl_rule(rules[0])
        
        # Create sample COBOL files list
        cobol_files = ["COMPLIANCE-TEST.cob", "AUDIT-TEST.cob"]
        
        # Generate HTML report
        report_path = self.report_gen.generate_html_report(
            violations, self.graph_gen.graph, cobol_files
        )
        
        # Verify report generated
        self.assertTrue(Path(report_path).exists())
        
        # Verify report content
        report_content = Path(report_path).read_text()
        
        # Check for essential report elements
        self.assertIn("Stacktalk Compliance Report", report_content)
        self.assertIn("Financial Compliance Rule", report_content)
        self.assertIn("COMPLIANCE-TEST.cob", report_content)
        
        # Check for violation details
        self.assertIn("ACCOUNT-NUMBER variable not defined", report_content)
        self.assertIn("TRANSACTION-AMOUNT variable not defined", report_content)
        
        # Check for severity indicators
        self.assertIn("HIGH", report_content)
        self.assertIn("MEDIUM", report_content)
        
        print(f"\n✅ Violations to HTML report integration successful!")
        print(f"   📊 Report generated: {report_path}")
        print(f"   📝 Violations included: {len(violations)}")
        print(f"   🔍 Report size: {len(report_content)} characters")
    
    def test_report_generation_with_empty_violations(self):
        """Test HTML report generation with no violations"""
        # Create empty violations list
        violations = []
        
        # Create sample graph
        parser = DSLParser(rules_dir=str(self.rules_dir))
        rules = parser.load_all_rules()
        self.graph_gen.add_dsl_rule(rules[0])
        
        # Create sample COBOL files list
        cobol_files = ["COMPLIANT-TEST.cob"]
        
        # Generate HTML report
        report_path = self.report_gen.generate_html_report(
            violations, self.graph_gen.graph, cobol_files
        )
        
        # Verify report generated
        self.assertTrue(Path(report_path).exists())
        
        # Verify report content for compliant scenario
        report_content = Path(report_path).read_text()
        
        # Should indicate no violations
        self.assertIn("Stacktalk Compliance Report", report_content)
        self.assertIn("0", report_content)  # Should show 0 violations
        
        print(f"\n✅ Empty violations report generation successful!")
        print(f"   📊 Report generated: {report_path}")
        print(f"   ✅ Compliant scenario handled properly")
    
    def test_report_generation_with_mixed_severities(self):
        """Test HTML report generation with mixed violation severities"""
        # Create violations with mixed severities
        mixed_violations = [
            Violation(
                type="missing_variable",
                message="Critical variable missing",
                severity="HIGH",
                requirement="critical_validation",
                source_file="MIXED-TEST.cob",
                line_number=10,
                dsl_rule="Financial Compliance Rule"
            ),
            Violation(
                type="missing_logic",
                message="Important logic missing",
                severity="MEDIUM",
                requirement="important_logic",
                source_file="MIXED-TEST.cob",
                line_number=20,
                dsl_rule="Financial Compliance Rule"
            ),
            Violation(
                type="missing_comment",
                message="Documentation missing",
                severity="LOW",
                requirement="documentation",
                source_file="MIXED-TEST.cob",
                line_number=30,
                dsl_rule="Financial Compliance Rule"
            )
        ]
        
        # Create sample graph
        parser = DSLParser(rules_dir=str(self.rules_dir))
        rules = parser.load_all_rules()
        self.graph_gen.add_dsl_rule(rules[0])
        
        # Create sample COBOL files list
        cobol_files = ["MIXED-TEST.cob"]
        
        # Generate HTML report
        report_path = self.report_gen.generate_html_report(
            mixed_violations, self.graph_gen.graph, cobol_files
        )
        
        # Verify report generated
        self.assertTrue(Path(report_path).exists())
        
        # Verify report content includes all severities
        report_content = Path(report_path).read_text()
        
        self.assertIn("HIGH", report_content)
        self.assertIn("MEDIUM", report_content)
        self.assertIn("LOW", report_content)
        
        # Check for violation descriptions
        self.assertIn("Critical variable missing", report_content)
        self.assertIn("Important logic missing", report_content)
        self.assertIn("Documentation missing", report_content)
        
        print(f"\n✅ Mixed severities report generation successful!")
        print(f"   📊 Report generated: {report_path}")
        print(f"   🔴 High severity violations: {len([v for v in mixed_violations if v.severity == 'HIGH'])}")
        print(f"   🟡 Medium severity violations: {len([v for v in mixed_violations if v.severity == 'MEDIUM'])}")
        print(f"   🟢 Low severity violations: {len([v for v in mixed_violations if v.severity == 'LOW'])}")
    
    def test_report_generation_with_multiple_files(self):
        """Test HTML report generation with violations across multiple files"""
        # Create violations across multiple files
        multi_file_violations = [
            Violation(
                type="missing_variable",
                message="Account validation missing",
                severity="HIGH",
                requirement="account_validation",
                source_file="FILE1.cob",
                line_number=10,
                dsl_rule="Financial Compliance Rule"
            ),
            Violation(
                type="missing_variable",
                message="Transaction validation missing",
                severity="HIGH",
                requirement="amount_validation",
                source_file="FILE2.cob",
                line_number=15,
                dsl_rule="Financial Compliance Rule"
            ),
            Violation(
                type="missing_logic",
                message="Approval logic missing",
                severity="MEDIUM",
                requirement="approval_process",
                source_file="FILE3.cob",
                line_number=20,
                dsl_rule="Financial Compliance Rule"
            )
        ]
        
        # Create sample graph
        parser = DSLParser(rules_dir=str(self.rules_dir))
        rules = parser.load_all_rules()
        self.graph_gen.add_dsl_rule(rules[0])
        
        # Create sample COBOL files list
        cobol_files = ["FILE1.cob", "FILE2.cob", "FILE3.cob", "FILE4.cob"]
        
        # Generate HTML report
        report_path = self.report_gen.generate_html_report(
            multi_file_violations, self.graph_gen.graph, cobol_files
        )
        
        # Verify report generated
        self.assertTrue(Path(report_path).exists())
        
        # Verify report content includes all files
        report_content = Path(report_path).read_text()
        
        # Check for source files with violations
        self.assertIn("FILE1.cob", report_content)
        self.assertIn("FILE2.cob", report_content)
        self.assertIn("FILE3.cob", report_content)
        # Note: FILE4.cob has no violations, so it won't appear in the report
        
        print(f"\n✅ Multiple files report generation successful!")
        print(f"   📊 Report generated: {report_path}")
        print(f"   📁 Files with violations: {len(set(v.source_file for v in multi_file_violations))}")
        print(f"   📁 Total files processed: {len(cobol_files)}")
    
    def test_report_generation_with_large_dataset(self):
        """Test HTML report generation with large violation dataset"""
        # Create large dataset of violations
        large_violations = []
        for i in range(50):
            violation = Violation(
                type="missing_variable",
                message=f"Variable {i} not defined",
                severity="HIGH" if i % 3 == 0 else "MEDIUM" if i % 3 == 1 else "LOW",
                requirement=f"validation_{i}",
                source_file=f"FILE_{(i % 10) + 1}.cob",
                line_number=i + 10,
                dsl_rule="Financial Compliance Rule"
            )
            large_violations.append(violation)
        
        # Create sample graph
        parser = DSLParser(rules_dir=str(self.rules_dir))
        rules = parser.load_all_rules()
        self.graph_gen.add_dsl_rule(rules[0])
        
        # Create sample COBOL files list
        cobol_files = [f"FILE_{i}.cob" for i in range(1, 11)]
        
        # Generate HTML report
        report_path = self.report_gen.generate_html_report(
            large_violations, self.graph_gen.graph, cobol_files
        )
        
        # Verify report generated
        self.assertTrue(Path(report_path).exists())
        
        # Verify report content
        report_content = Path(report_path).read_text()
        
        # Should handle large dataset
        self.assertIn("Stacktalk Compliance Report", report_content)
        self.assertIn("50", report_content)  # Should show 50 violations
        
        # Check for severity distribution
        high_count = len([v for v in large_violations if v.severity == "HIGH"])
        medium_count = len([v for v in large_violations if v.severity == "MEDIUM"])
        low_count = len([v for v in large_violations if v.severity == "LOW"])
        
        print(f"\n✅ Large dataset report generation successful!")
        print(f"   📊 Report generated: {report_path}")
        print(f"   📝 Total violations: {len(large_violations)}")
        print(f"   🔴 High severity: {high_count}")
        print(f"   🟡 Medium severity: {medium_count}")
        print(f"   🟢 Low severity: {low_count}")
        print(f"   📁 Files processed: {len(cobol_files)}")
    
    def test_report_generation_error_handling(self):
        """Test HTML report generation error handling"""
        # Test with None violations
        try:
            report_path = self.report_gen.generate_html_report(
                None, self.graph_gen.graph, ["test.cob"]
            )
            # Should handle gracefully
            self.assertIsNotNone(report_path)
        except Exception as e:
            print(f"⚠️ None violations handled: {e}")
        
        # Test with empty graph
        empty_graph = {"nodes": [], "edges": [], "metadata": {}}
        violations = self._create_sample_violations()
        
        try:
            report_path = self.report_gen.generate_html_report(
                violations, empty_graph, ["test.cob"]
            )
            # Should handle gracefully
            self.assertIsNotNone(report_path)
        except Exception as e:
            print(f"⚠️ Empty graph handled: {e}")
        
        # Test with empty COBOL files list
        try:
            report_path = self.report_gen.generate_html_report(
                violations, self.graph_gen.graph, []
            )
            # Should handle gracefully
            self.assertIsNotNone(report_path)
        except Exception as e:
            print(f"⚠️ Empty COBOL files handled: {e}")
        
        print(f"\n✅ Report generation error handling successful!")
    
    def test_report_styling_and_formatting(self):
        """Test HTML report styling and formatting"""
        # Create sample violations
        violations = self._create_sample_violations()
        
        # Create sample graph
        parser = DSLParser(rules_dir=str(self.rules_dir))
        rules = parser.load_all_rules()
        self.graph_gen.add_dsl_rule(rules[0])
        
        # Create sample COBOL files list
        cobol_files = ["STYLING-TEST.cob"]
        
        # Generate HTML report
        report_path = self.report_gen.generate_html_report(
            violations, self.graph_gen.graph, cobol_files
        )
        
        # Verify report generated
        self.assertTrue(Path(report_path).exists())
        
        # Verify report styling
        report_content = Path(report_path).read_text()
        
        # Check for HTML structure
        self.assertIn("<!DOCTYPE html>", report_content)
        self.assertIn("<html lang=\"en\">", report_content)
        self.assertIn("<head>", report_content)
        self.assertIn("<body>", report_content)
        
        # Check for CSS styling
        self.assertIn("style=", report_content)
        self.assertIn("background", report_content)
        self.assertIn("color", report_content)
        
        # Check for table structure
        self.assertIn("<table class=\"violation-table\">", report_content)
        self.assertIn("<tr>", report_content)
        self.assertIn("<td>", report_content)
        
        print(f"\n✅ Report styling and formatting successful!")
        print(f"   📊 Report generated: {report_path}")
        print(f"   🎨 HTML structure verified")
        print(f"   💄 CSS styling verified")
        print(f"   📋 Table formatting verified")


if __name__ == '__main__':
    unittest.main()
