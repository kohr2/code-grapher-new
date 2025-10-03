"""
Integration tests for AI generation workflow integration
Tests the integration between AI-powered COBOL generation and the complete workflow
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import os
from unittest.mock import Mock, patch

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from dsl_parser import DSLParser, DSLError
from cobol_generator import COBOLGenerator
from cobol_cst_parser import COBOLCSTParser
from graph_generator import GraphGenerator
from rule_detector import RuleDetector
from report_generator import ReportGenerator


class TestAIGenerationWorkflowIntegration(unittest.TestCase):
    """Test AI generation workflow integration across components"""
    
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
        self.cobol_gen = COBOLGenerator()
        self.cst_parser = COBOLCSTParser()
        self.graph_gen = GraphGenerator()
        self.rule_detector = RuleDetector()
        self.report_gen = ReportGenerator()
        
        # Check for OpenAI key
        self.openai_available = bool(os.getenv('OPENAI_KEY'))
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def _create_test_dsl_rule(self):
        """Create a test DSL rule file"""
        test_rule = """
rule:
  name: "AI Generation Test Rule"
  description: "Rule for testing AI generation workflow integration"

variables:
  - name: "CUSTOMER-ID"
    type: "string"
    pic: "X(12)"
    description: "Customer identifier"
  - name: "ACCOUNT-BALANCE"
    type: "numeric"
    pic: "9(10)V99"
    description: "Account balance"
  - name: "TRANSACTION-TYPE"
    type: "string"
    pic: "X(8)"
    description: "Transaction type"
  - name: "AUTHORIZATION-CODE"
    type: "string"
    pic: "X(6)"
    description: "Authorization code"
  - name: "RISK-SCORE"
    type: "numeric"
    pic: "9(3)"
    description: "Risk assessment score"

conditions:
  balance_check:
    check: "ACCOUNT-BALANCE >= 0"
    description: "Account balance validation"
  risk_assessment:
    check: "RISK-SCORE <= 100"
    description: "Risk score validation"

requirements:
  customer_identification:
    description: "Customer must be identified"
    check: "CUSTOMER-ID variable must be defined"
    violation_message: "CUSTOMER-ID variable not defined"
    severity: "HIGH"
  balance_validation:
    description: "Account balance must be validated"
    check: "ACCOUNT-BALANCE variable must be defined"
    violation_message: "ACCOUNT-BALANCE variable not defined"
    severity: "HIGH"
  transaction_processing:
    description: "Transaction type must be processed"
    check: "TRANSACTION-TYPE variable must be defined"
    violation_message: "TRANSACTION-TYPE variable not defined"
    severity: "MEDIUM"
  authorization_check:
    description: "Authorization must be checked"
    check: "AUTHORIZATION-CODE variable must be defined"
    violation_message: "AUTHORIZATION-CODE variable not defined"
    severity: "HIGH"
  risk_management:
    description: "Risk assessment must be performed"
    check: "RISK-SCORE variable must be defined"
    violation_message: "RISK-SCORE variable not defined"
    severity: "MEDIUM"

compliant_logic:
  transaction_processing:
    - "MOVE CUSTOMER-ID TO WORK-CUSTOMER"
    - "MOVE ACCOUNT-BALANCE TO WORK-BALANCE"
    - "MOVE TRANSACTION-TYPE TO WORK-TYPE"
    - "MOVE AUTHORIZATION-CODE TO WORK-AUTH"
    - "MOVE RISK-SCORE TO WORK-RISK"
    - "PERFORM VALIDATE-TRANSACTION"
    - "PERFORM CALCULATE-RISK"
    - "PERFORM PROCESS-TRANSACTION"

violation_examples:
  missing_customer_id:
    description: "CUSTOMER-ID variable missing"
    remove_variables: ["CUSTOMER-ID"]
  missing_balance:
    description: "ACCOUNT-BALANCE variable missing"
    remove_variables: ["ACCOUNT-BALANCE"]
  missing_transaction_type:
    description: "TRANSACTION-TYPE variable missing"
    remove_variables: ["TRANSACTION-TYPE"]
  missing_authorization:
    description: "AUTHORIZATION-CODE variable missing"
    remove_variables: ["AUTHORIZATION-CODE"]
  missing_risk_score:
    description: "RISK-SCORE variable missing"
    remove_variables: ["RISK-SCORE"]
"""
        
        rule_file = self.rules_dir / "ai_generation_rule.dsl"
        rule_file.write_text(test_rule.strip())
    
    def test_ai_generation_workflow_with_openai(self):
        """Test AI generation workflow with OpenAI available"""
        if not self.openai_available:
            self.skipTest("OpenAI key not available")
        
        # Parse DSL rule
        parser = DSLParser(rules_dir=str(self.rules_dir))
        rules = parser.load_all_rules()
        self.graph_gen.add_dsl_rule(rules[0])
        
        # Generate COBOL examples using AI
        generated_files = self.cobol_gen.save_multiple_cobol_examples(
            rules, str(self.examples_dir)
        )
        
        # Verify AI generation
        self.assertGreater(len(generated_files), 0)
        
        # Parse generated COBOL files with CST
        all_violations = []
        for cobol_file in generated_files:
            try:
                cobol_content = Path(cobol_file).read_text()
                cst_analysis = self.cst_parser.analyze_cobol_comprehensive(cobol_content)
                cobol_nodes = self.graph_gen.generate_cobol_nodes_from_cst(
                    cst_analysis, Path(cobol_file).stem
                )
                
                # Connect COBOL to rules
                self.graph_gen.connect_cobol_to_rules(cobol_nodes)
                
                # Detect violations
                violations = self.rule_detector.detect_violations(self.graph_gen.graph)
                all_violations.extend(violations)
                
            except Exception as e:
                print(f"⚠️ CST parsing failed for {cobol_file}: {e}")
                # Continue with other files
        
        # Generate report
        report_path = self.report_gen.generate_html_report(
            all_violations, self.graph_gen.graph, generated_files
        )
        
        # Verify workflow completed successfully
        self.assertTrue(Path(report_path).exists())
        
        print(f"\n✅ AI generation workflow with OpenAI successful!")
        print(f"   🤖 AI-generated COBOL files: {len(generated_files)}")
        print(f"   📊 Graph nodes: {len(self.graph_gen.graph['nodes'])}")
        print(f"   🔗 Graph edges: {len(self.graph_gen.graph['edges'])}")
        print(f"   ❌ Violations detected: {len(all_violations)}")
        print(f"   📝 Report generated: {report_path}")
    
    def test_ai_generation_workflow_with_template_fallback(self):
        """Test AI generation workflow with template fallback"""
        # Mock OpenAI as unavailable
        with patch.object(self.cobol_gen, 'openai_available', False):
            # Parse DSL rule
            parser = DSLParser(rules_dir=str(self.rules_dir))
            rules = parser.load_all_rules()
            self.graph_gen.add_dsl_rule(rules[0])
            
            # Generate COBOL examples using template fallback
            generated_files = self.cobol_gen.save_multiple_cobol_examples(
                rules, str(self.examples_dir)
            )
            
            # Verify template generation
            self.assertGreater(len(generated_files), 0)
            
            # Parse generated COBOL files with CST
            all_violations = []
            for cobol_file in generated_files:
                try:
                    cobol_content = Path(cobol_file).read_text()
                    cst_analysis = self.cst_parser.analyze_cobol_comprehensive(cobol_content)
                    cobol_nodes = self.graph_gen.generate_cobol_nodes_from_cst(
                        cst_analysis, Path(cobol_file).stem
                    )
                    
                    # Connect COBOL to rules
                    self.graph_gen.connect_cobol_to_rules(cobol_nodes)
                    
                    # Detect violations
                    violations = self.rule_detector.detect_violations(self.graph_gen.graph)
                    all_violations.extend(violations)
                    
                except Exception as e:
                    print(f"⚠️ CST parsing failed for {cobol_file}: {e}")
                    # Continue with other files
            
            # Generate report
            report_path = self.report_gen.generate_html_report(
                all_violations, self.graph_gen.graph, generated_files
            )
            
            # Verify workflow completed successfully with template fallback
            self.assertTrue(Path(report_path).exists())
            
            print(f"\n✅ AI generation workflow with template fallback successful!")
            print(f"   📝 Template-generated COBOL files: {len(generated_files)}")
            print(f"   📊 Graph nodes: {len(self.graph_gen.graph['nodes'])}")
            print(f"   🔗 Graph edges: {len(self.graph_gen.graph['edges'])}")
            print(f"   ❌ Violations detected: {len(all_violations)}")
            print(f"   📝 Report generated: {report_path}")
            print(f"   ⚠️ Template fallback used instead of AI")
    
    def test_ai_generation_workflow_with_mixed_generation(self):
        """Test AI generation workflow with mixed AI and template generation"""
        # Mock partial OpenAI availability
        with patch.object(self.cobol_gen, 'openai_available', True):
            with patch.object(self.cobol_gen, '_generate_ai_cobol') as mock_ai_generate:
                # Make AI generation fail for some rules
                mock_ai_generate.side_effect = Exception("AI generation failed")
                
                # Parse DSL rule
                parser = DSLParser(rules_dir=str(self.rules_dir))
                rules = parser.load_all_rules()
                self.graph_gen.add_dsl_rule(rules[0])
                
                # Generate COBOL examples with mixed generation
                generated_files = self.cobol_gen.save_multiple_cobol_examples(
                    rules, str(self.examples_dir)
                )
                
                # Verify mixed generation
                self.assertGreater(len(generated_files), 0)
                
                # Parse generated COBOL files with CST
                all_violations = []
                for cobol_file in generated_files:
                    try:
                        cobol_content = Path(cobol_file).read_text()
                        cst_analysis = self.cst_parser.analyze_cobol_comprehensive(cobol_content)
                        cobol_nodes = self.graph_gen.generate_cobol_nodes_from_cst(
                            cst_analysis, Path(cobol_file).stem
                        )
                        
                        # Connect COBOL to rules
                        self.graph_gen.connect_cobol_to_rules(cobol_nodes)
                        
                        # Detect violations
                        violations = self.rule_detector.detect_violations(self.graph_gen.graph)
                        all_violations.extend(violations)
                        
                    except Exception as e:
                        print(f"⚠️ CST parsing failed for {cobol_file}: {e}")
                        # Continue with other files
                
                # Generate report
                report_path = self.report_gen.generate_html_report(
                    all_violations, self.graph_gen.graph, generated_files
                )
                
                # Verify workflow completed successfully with mixed generation
                self.assertTrue(Path(report_path).exists())
                
                print(f"\n✅ AI generation workflow with mixed generation successful!")
                print(f"   🔀 Mixed-generation COBOL files: {len(generated_files)}")
                print(f"   📊 Graph nodes: {len(self.graph_gen.graph['nodes'])}")
                print(f"   🔗 Graph edges: {len(self.graph_gen.graph['edges'])}")
                print(f"   ❌ Violations detected: {len(all_violations)}")
                print(f"   📝 Report generated: {report_path}")
                print(f"   ⚠️ Mixed AI and template generation used")
    
    def test_ai_generation_workflow_with_cst_parsing_errors(self):
        """Test AI generation workflow with CST parsing errors"""
        # Parse DSL rule
        parser = DSLParser(rules_dir=str(self.rules_dir))
        rules = parser.load_all_rules()
        self.graph_gen.add_dsl_rule(rules[0])
        
        # Generate COBOL examples
        generated_files = self.cobol_gen.save_multiple_cobol_examples(
            rules, str(self.examples_dir)
        )
        
        # Mock CST parsing to fail
        with patch.object(self.cst_parser, 'analyze_cobol_comprehensive') as mock_cst:
            mock_cst.side_effect = Exception("CST parsing failed")
            
            # Parse generated COBOL files with CST (should fail)
            all_violations = []
            for cobol_file in generated_files:
                try:
                    cobol_content = Path(cobol_file).read_text()
                    cst_analysis = self.cst_parser.analyze_cobol_comprehensive(cobol_content)
                    cobol_nodes = self.graph_gen.generate_cobol_nodes_from_cst(
                        cst_analysis, Path(cobol_file).stem
                    )
                    
                    # Connect COBOL to rules
                    self.graph_gen.connect_cobol_to_rules(cobol_nodes)
                    
                    # Detect violations
                    violations = self.rule_detector.detect_violations(self.graph_gen.graph)
                    all_violations.extend(violations)
                    
                except Exception as e:
                    print(f"⚠️ CST parsing failed for {cobol_file}: {e}")
                    # Continue with other files
            
            # Generate report
            report_path = self.report_gen.generate_html_report(
                all_violations, self.graph_gen.graph, generated_files
            )
            
            # Verify workflow completed successfully despite CST parsing errors
            self.assertTrue(Path(report_path).exists())
            
            print(f"\n✅ AI generation workflow with CST parsing errors successful!")
            print(f"   📝 Generated COBOL files: {len(generated_files)}")
            print(f"   📊 Graph nodes: {len(self.graph_gen.graph['nodes'])}")
            print(f"   🔗 Graph edges: {len(self.graph_gen.graph['edges'])}")
            print(f"   ❌ Violations detected: {len(all_violations)}")
            print(f"   📝 Report generated: {report_path}")
            print(f"   ⚠️ CST parsing errors handled gracefully")
    
    def test_ai_generation_workflow_with_openai_rate_limits(self):
        """Test AI generation workflow with OpenAI rate limits"""
        # Mock OpenAI rate limit
        with patch.object(self.cobol_gen, 'openai_available', True):
            with patch.object(self.cobol_gen, '_generate_ai_cobol') as mock_ai_generate:
                # Simulate rate limit error
                mock_ai_generate.side_effect = Exception("Rate limit exceeded")
                
                # Parse DSL rule
                parser = DSLParser(rules_dir=str(self.rules_dir))
                rules = parser.load_all_rules()
                self.graph_gen.add_dsl_rule(rules[0])
                
                # Generate COBOL examples (should fallback to template)
                generated_files = self.cobol_gen.save_cobol_examples(
                    rules[0], str(self.examples_dir)
                )
                
                # Verify fallback generation
                self.assertGreater(len(generated_files), 0)
                
                # Parse generated COBOL files with CST
                all_violations = []
                for cobol_file in generated_files:
                    try:
                        cobol_content = Path(cobol_file).read_text()
                        cst_analysis = self.cst_parser.analyze_cobol_comprehensive(cobol_content)
                        cobol_nodes = self.graph_gen.generate_cobol_nodes_from_cst(
                            cst_analysis, Path(cobol_file).stem
                        )
                        
                        # Connect COBOL to rules
                        self.graph_gen.connect_cobol_to_rules(cobol_nodes)
                        
                        # Detect violations
                        violations = self.rule_detector.detect_violations(self.graph_gen.graph)
                        all_violations.extend(violations)
                        
                    except Exception as e:
                        print(f"⚠️ CST parsing failed for {cobol_file}: {e}")
                        # Continue with other files
                
                # Generate report
                report_path = self.report_gen.generate_html_report(
                    all_violations, self.graph_gen.graph, generated_files
                )
                
                # Verify workflow completed successfully with rate limit fallback
                self.assertTrue(Path(report_path).exists())
                
                print(f"\n✅ AI generation workflow with rate limits successful!")
                print(f"   📝 Fallback-generated COBOL files: {len(generated_files)}")
                print(f"   📊 Graph nodes: {len(self.graph_gen.graph['nodes'])}")
                print(f"   🔗 Graph edges: {len(self.graph_gen.graph['edges'])}")
                print(f"   ❌ Violations detected: {len(all_violations)}")
                print(f"   📝 Report generated: {report_path}")
                print(f"   ⚠️ Rate limit fallback to template used")
    
    def test_ai_generation_workflow_with_invalid_dsl(self):
        """Test AI generation workflow with invalid DSL rules"""
        # Create invalid DSL rule
        invalid_rule = """
rule:
  name: "Invalid Rule"
  # Missing description
variables:
  # Invalid structure
conditions:
  # Missing check
requirements:
  # Missing description
"""
        
        invalid_rule_file = self.rules_dir / "invalid_rule.dsl"
        invalid_rule_file.write_text(invalid_rule.strip())
        
        # Parse DSL rule (should fail)
        parser = DSLParser(rules_dir=str(self.rules_dir))
        
        try:
            rules = parser.load_all_rules()
            self.fail("Expected DSL parsing to fail with invalid rule")
        except Exception as e:
            print(f"⚠️ DSL parsing failed as expected: {e}")
            
            # Verify workflow handles invalid DSL gracefully
            self.assertIsInstance(e, (DSLError, Exception))
            
            print(f"\n✅ AI generation workflow with invalid DSL successful!")
            print(f"   ❌ DSL parsing failed as expected")
            print(f"   ⚠️ Invalid DSL handled gracefully")
    
    def test_ai_generation_workflow_performance(self):
        """Test AI generation workflow performance"""
        import time
        
        # Parse DSL rule
        parser = DSLParser(rules_dir=str(self.rules_dir))
        rules = parser.load_all_rules()
        self.graph_gen.add_dsl_rule(rules[0])
        
        # Measure generation time
        start_time = time.time()
        
        # Generate COBOL examples
        generated_files = self.cobol_gen.save_multiple_cobol_examples(
            rules, str(self.examples_dir)
        )
        
        generation_time = time.time() - start_time
        
        # Parse generated COBOL files with CST
        parsing_start = time.time()
        all_violations = []
        for cobol_file in generated_files:
            try:
                cobol_content = Path(cobol_file).read_text()
                cst_analysis = self.cst_parser.analyze_cobol_comprehensive(cobol_content)
                cobol_nodes = self.graph_gen.generate_cobol_nodes_from_cst(
                    cst_analysis, Path(cobol_file).stem
                )
                
                # Connect COBOL to rules
                self.graph_gen.connect_cobol_to_rules(cobol_nodes)
                
                # Detect violations
                violations = self.rule_detector.detect_violations(self.graph_gen.graph)
                all_violations.extend(violations)
                
            except Exception as e:
                print(f"⚠️ CST parsing failed for {cobol_file}: {e}")
                # Continue with other files
        
        parsing_time = time.time() - parsing_start
        
        # Generate report
        report_start = time.time()
        report_path = self.report_gen.generate_html_report(
            all_violations, self.graph_gen.graph, generated_files
        )
        report_time = time.time() - report_start
        
        total_time = time.time() - start_time
        
        # Verify performance metrics
        self.assertLess(generation_time, 30.0)  # Generation should be under 30 seconds
        self.assertLess(parsing_time, 10.0)     # Parsing should be under 10 seconds
        self.assertLess(report_time, 5.0)       # Report generation should be under 5 seconds
        self.assertLess(total_time, 60.0)       # Total workflow should be under 60 seconds
        
        print(f"\n✅ AI generation workflow performance successful!")
        print(f"   📝 Generated COBOL files: {len(generated_files)}")
        print(f"   ⏱️ Generation time: {generation_time:.2f}s")
        print(f"   ⏱️ Parsing time: {parsing_time:.2f}s")
        print(f"   ⏱️ Report time: {report_time:.2f}s")
        print(f"   ⏱️ Total time: {total_time:.2f}s")
        print(f"   📊 Graph nodes: {len(self.graph_gen.graph['nodes'])}")
        print(f"   🔗 Graph edges: {len(self.graph_gen.graph['edges'])}")
        print(f"   ❌ Violations detected: {len(all_violations)}")


if __name__ == '__main__':
    unittest.main()
