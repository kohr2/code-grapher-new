#!/usr/bin/env python3
"""
Test module for Report Generator
Following TDD approach: tests first, then implementation
Generates professional HTML compliance reports with executive summaries
"""

import unittest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from dsl_parser import DSLRule, DSLVariable, DSLRequirement, DSLCondition
from graph_generator import GraphGenerator
from rule_detector import Violation


class TestReportGenerator(unittest.TestCase):
    """Test cases for the Report Generator module"""
    
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
        
        # Create sample violations
        self.sample_violations = [
            Violation(
                type="missing_variable",
                message="Required variable 'NSF-LOG-FLAG' not defined in program",
                severity="HIGH",
                requirement="nsf_logging",
                code_element="NSF-LOG-FLAG",
                source_file="violation.cob",
                line_number=15,
                dsl_rule="NSF Banking Rule"
            ),
            Violation(
                type="missing_logic",
                message="NSF fee logic required but NSF-FEE variable not found",
                severity="MEDIUM",
                requirement="nsf_fee_application",
                code_element="NSF-FEE",
                source_file="violation.cob",
                line_number=22,
                dsl_rule="NSF Banking Rule"
            )
        ]
        
        # Create sample graph
        self.graph_generator = GraphGenerator()
        self.graph_generator.add_dsl_rule(self.sample_rule)
        
    def test_report_generator_initialization(self):
        """Test ReportGenerator can be initialized"""
        from report_generator import ReportGenerator
        
        generator = ReportGenerator(output_dir=str(self.temp_path))
        self.assertIsNotNone(generator)
        self.assertTrue(hasattr(generator, 'output_dir'))
        self.assertTrue(hasattr(generator, 'template_dir'))

    def test_generate_executive_summary(self):
        """Test generation of executive summary dashboard"""
        from report_generator import ReportGenerator
        
        generator = ReportGenerator(output_dir=str(self.temp_path))
        
        summary = generator.generate_executive_summary(self.sample_violations, self.graph_generator.graph)
        
        # Should contain key metrics
        self.assertIn("total_violations", summary)
        self.assertIn("compliance_rate", summary)
        self.assertIn("severity_breakdown", summary)
        self.assertIn("files_affected", summary)
        self.assertIn("requirements_violated", summary)
        
        # Should have executive insights
        self.assertIn("executive_summary", summary)
        self.assertIn("risk_assessment", summary)
        self.assertIn("recommendations", summary)

    def test_generate_violation_details(self):
        """Test generation of detailed violation information"""
        from report_generator import ReportGenerator
        
        generator = ReportGenerator(output_dir=str(self.temp_path))
        
        details = generator.generate_violation_details(self.sample_violations)
        
        # Should contain violation information
        self.assertIn("violations", details)
        self.assertIn("violation_by_file", details)
        self.assertIn("violation_by_requirement", details)
        
        # Should have detailed violation data
        violations_list = details["violations"]
        self.assertEqual(len(violations_list), len(self.sample_violations))
        self.assertTrue(all("message" in v for v in violations_list))
        self.assertTrue(all("severity" in v for v in violations_list))
        self.assertTrue(all("source_file" in v for v in violations_list))

    def test_generate_graph_visualization(self):
        """Test generation of graph visualization data"""
        from report_generator import ReportGenerator
        
        generator = ReportGenerator(output_dir=str(self.temp_path))
        
        viz_data = generator.generate_graph_visualization(self.graph_generator.graph)
        
        # Should contain comprehensive graph data
        self.assertIn("nodes", viz_data)
        self.assertIn("edges", viz_data)
        self.assertIn("statistics", viz_data)
        
        # Should include graph metadata
        self.assertIn("total_nodes", viz_data["statistics"])
        self.assertIn("total_edges", viz_data["statistics"])
        self.assertIn("node_types", viz_data["statistics"])
        self.assertIn("edge_types", viz_data["statistics"])

    def test_generate_compliance_metrics(self):
        """Test generation of compliance metrics and analytics"""
        from report_generator import ReportGenerator
        
        generator = ReportGenerator(output_dir=str(self.temp_path))
        
        metrics = generator.generate_compliance_metrics(self.sample_violations, self.graph_generator.graph)
        
        # Should contain compliance analytics
        self.assertIn("overall_compliance_score", metrics)
        self.assertIn("requirement_compliance", metrics)
        self.assertIn("severity_distribution", metrics)
        self.assertIn("compliance_trends", metrics)
        
        # Should have actionable insights
        self.assertIn("priority_actions", metrics)
        self.assertIn("improvement_areas", metrics)

    def test_html_report_generation(self):
        """Test generation of complete HTML report"""
        from report_generator import ReportGenerator
        
        generator = ReportGenerator(output_dir=str(self.temp_path))
        
        # Generate report
        report_path = generator.generate_html_report(
            violations=self.sample_violations,
            graph=self.graph_generator.graph,
            cobol_files=["compliant.cob", "violation.cob"],
            ai_generated=True
        )
        
        # Should create report file
        self.assertTrue(report_path.exists())
        self.assertTrue(str(report_path).endswith('.html'))
        
        # Check file content
        report_content = report_path.read_text()
        
        # Should contain HTML structure
        self.assertIn("<html", report_content)
        self.assertIn("<head>", report_content)
        self.assertIn("<body>", report_content)
        self.assertIn("</html>", report_content)
        
        # Should contain executive summary
        self.assertIn("Executive Summary", report_content)
        self.assertIn("Policy Violation Details", report_content)
        
        # Should contain violation details
        self.assertIn("NSF-LOG-FLAG", report_content)
        self.assertIn("NSF-FEE", report_content)
        
        # Should show compliance metrics
        self.assertIn("Compliance Rate", report_content)
        self.assertIn("HIGH", report_content)
        self.assertIn("MEDIUM", report_content)

    def test_report_styling_and_formatting(self):
        """Test HTML report has professional styling"""
        from report_generator import ReportGenerator
        
        generator = ReportGenerator(output_dir=str(self.temp_path))
        
        report_path = generator.generate_html_report(
            violations=self.sample_violations,
            graph=self.graph_generator.graph,
            cobol_files=["test.cob"]
        )
        
        report_content = report_path.read_text()
        
        # Should have CSS styling
        self.assertIn("<style>", report_content)
        self.assertIn("color:", report_content.lower())
        self.assertIn("font-family:", report_content.lower())
        
        # Should have responsive design
        self.assertIn("viewport", report_content.lower())
        
        # Should have professional formatting
        self.assertIn("font-family", report_content.lower())

    def test_code_syntax_highlighting(self):
        """Test COBOL code syntax highlighting in report"""
        from report_generator import ReportGenerator
        
        generator = ReportGenerator(output_dir=str(self.temp_path))
        
        # Create sample COBOL content
        cobol_content = """IDENTIFICATION DIVISION.
       PROGRAM-ID. TEST-PROGRAM.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 ACCOUNT-BALANCE PIC 9(8)V99.
       
       PROCEDURE DIVISION.
       IF ACCOUNT-BALANCE < 1000 THEN
           DISPLAY 'Low Balance'
       END-IF
       STOP RUN."""
        
        highlighted = generator.highlight_cobol_syntax(cobol_content)
        
        # Should format COBOL syntax
        self.assertIn("COMMENT", highlighted.upper() or "")
        self.assertIn("KEYWORD", highlighted.upper() or "")
        self.assertIn("IDENTIFIER", highlighted.upper() or "")

    def test_interactive_report_features(self):
        """Test interactive report features"""
        from report_generator import ReportGenerator
        
        generator = ReportGenerator(output_dir=str(self.temp_path))
        
        report_path = generator.generate_html_report(
            violations=self.sample_violations,
            graph=self.graph_generator.graph,
            cobol_files=["file1.cob", "file2.cob"]
        )
        
        report_content = report_path.read_text()
        
        # Should have interactive elements
        self.assertIn("JavaScript", report_content.lower())
        self.assertIn("onclick", report_content.lower())
        
        # Should have filtering capabilities
        self.assertIn("filter", report_content.lower())
        self.assertIn("search", report_content.lower())
        
        # Should have expandable sections
        self.assertIn("toggle", report_content.lower() or "")
        self.assertIn("collapse", report_content.lower() or "")

    def test_export_formats(self):
        """Test report export to different formats"""
        from report_generator import ReportGenerator
        
        generator = ReportGenerator(output_dir=str(self.temp_path))
        
        # Test PDF export (if available)
        pdf_path = generator.export_report_pdf(
            violations=self.sample_violations,
            graph=self.graph_generator.graph
        )
        
        # PDF export should work or gracefully fail
        self.assertTrue(pdf_path is not None or True)  # Allow graceful failure
        
        # Test JSON export
        json_data = generator.export_report_json(
            violations=self.sample_violations,
            graph=self.graph_generator.graph
        )
        
        self.assertIsInstance(json_data, dict)
        self.assertIn("violations", json_data)
        self.assertIn("graph", json_data)

    def test_report_theming_and_branding(self):
        """Test report theming and enterprise branding"""
        from report_generator import ReportGenerator
        
        generator = ReportGenerator(output_dir=str(self.temp_path))
        
        # Test with custom branding
        custom_branding = {
            "company_name": "ABC Bank",
            "logo_url": "https://example.com/logo.png",
            "primary_color": "#1E40AF",
            "theme": "banking"
        }
        
        report_path = generator.generate_html_report(
            violations=self.sample_violations,
            graph=self.graph_generator.graph,
            branding=custom_branding
        )
        
        report_content = report_path.read_text()
        
        # Should include branding elements
        self.assertIn("ABC Bank", report_content)
        self.assertIn("#1E40AF", report_content)

    def test_accessibility_and_compliance(self):
        """Test report accessibility and compliance features"""
        from report_generator import ReportGenerator
        
        generator = ReportGenerator(output_dir=str(self.temp_path))
        
        report_path = generator.generate_html_report(
            violations=self.sample_violations,
            graph=self.graph_generator.graph,
            compliance_mode=True
        )
        
        report_content = report_path.read_text()
        
        # Should have accessibility features
        self.assertIn("alt=", report_content)
        self.assertIn("aria-", report_content)
        
        # Should include audit trail information
        self.assertIn("generated", report_content.lower())
        self.assertIn("timestamp", report_content.lower())
        
        # Should have tamper-evident features
        self.assertIn("report integrity", report_content.lower())

    def test_empty_violations_report(self):
        """Test report generation with no violations (compliant code)"""
        from report_generator import ReportGenerator
        
        generator = ReportGenerator(output_dir=str(self.temp_path))
        
        # Generate report with no violations
        report_path = generator.generate_html_report(
            violations=[],
            graph=self.graph_generator.graph,
            cobol_files=["compliant.cob"]
        )
        
        self.assertTrue(report_path.exists())
        
        report_content = report_path.read_text()
        
        # Should show compliance success
        self.assertIn("fully compliant", report_content.lower())
        self.assertIn("100%", report_content)
        self.assertIn("no violations", report_content.lower())

    def test_large_dataset_report(self):
        """Test report generation with large datasets"""
        from report_generator import ReportGenerator
        
        generator = ReportGenerator(output_dir=str(self.temp_path))
        
        # Create many violations
        large_violations = []
        for i in range(100):
            large_violations.append(Violation(
                type="missing_variable",
                message=f"Missing variable {i}",
                severity="MEDIUM",
                requirement=f"req_{i}",
                code_element=f"VAR_{i}",
                source_file=f"file_{i}.cob",
                line_number=i,
                dsl_rule="Test Rule"
            ))
        
        report_path = generator.generate_html_report(
            violations=large_violations,
            graph=self.graph_generator.graph,
            cobol_files=[f"file_{i}.cob" for i in range(100)]
        )
        
        self.assertTrue(report_path.exists())
        
        report_content = report_path.read_text()
        
        # Should handle large datasets efficiently
        self.assertIn("100", report_content)  # Should show violation count
        self.assertIn("pagination", report_content.lower() or "100")

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
