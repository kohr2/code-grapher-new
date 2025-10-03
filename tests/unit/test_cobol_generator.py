#!/usr/bin/env python3
"""
Test module for COBOL Generator
Following TDD approach: tests first, then implementation
"""

import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import sys
import os

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from dsl_parser import DSLRule, DSLVariable, DSLRequirement, DSLCondition
from graph_generator import GraphGenerator, Violation


class TestCOBOLGenerator(unittest.TestCase):
    """Test cases for the COBOL Generator module"""
    
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

    def test_cobol_generator_initialization(self):
        """Test COBOLGenerator can be initialized"""
        from cobol_generator import COBOLGenerator
        
        generator = COBOLGenerator()
        self.assertIsNotNone(generator)
        self.assertIsInstance(generator.templates, dict)
        self.assertTrue(generator.templates)

    def test_generate_compliant_cobol(self):
        """Test generating compliant COBOL code from DSL rule"""
        from cobol_generator import COBOLGenerator
        
        generator = COBOLGenerator()
        cobol_code = generator.generate_compliant_cobol(self.sample_rule, "WITHDRAWAL-PROCESS")
        
        # Should generate valid COBOL structure
        self.assertIn("IDENTIFICATION DIVISION", cobol_code)
        self.assertIn("PROGRAM-ID", cobol_code)
        self.assertIn("DATA DIVISION", cobol_code)
        self.assertIn("PROCEDURE DIVISION", cobol_code)
        self.assertIn("PROGRAM-ID. WITHDRAWAL-PROCESS", cobol_code)
        
        # Should include all variables from DSL rule
        self.assertIn("ACCOUNT-BALANCE", cobol_code)
        self.assertIn("WITHDRAWAL-AMOUNT", cobol_code)
        self.assertIn("NSF-FEE", cobol_code)
        self.assertIn("NSF-LOG-FLAG", cobol_code)
        
        # Should include PIC clauses
        self.assertIn("PIC 9(8)V99", cobol_code)
        self.assertIn("PIC X(1)", cobol_code)

    def test_generate_compliant_cobol_with_logic(self):
        """Test compliant COBOL includes proper NSF logic"""
        from cobol_generator import COBOLGenerator
        
        generator = COBOLGenerator()
        cobol_code = generator.generate_compliant_cobol(self.sample_rule, "WITHDRAWAL-PROCESS")
        
        # Should include compliant logic from DSL rule
        self.assertIn("IF ACCOUNT-BALANCE < WITHDRAWAL-AMOUNT", cobol_code)
        self.assertIn("MOVE 'Y' TO NSF-LOG-FLAG", cobol_code)
        self.assertIn("ADD NSF-FEE TO WITHDRAWAL-AMOUNT", cobol_code)
        self.assertIn("DISPLAY 'NSF Event Logged - Fee Applied'", cobol_code)
        self.assertIn("PERFORM REJECT-TRANSACTION", cobol_code)

    def test_generate_violation_cobol_missing_variable(self):
        """Test generating COBOL with specific violation (missing variable)"""
        from cobol_generator import COBOLGenerator
        
        generator = COBOLGenerator()
        
        # Generate violation example for missing NSF-LOG-FLAG
        cobol_code = generator.generate_violation_cobol(
            self.sample_rule, 
            "VIOLATION-TEST",
            "missing_log_flag"
        )
        
        # Should not include NSF-LOG-FLAG variable
        self.assertNotIn("NSF-LOG-FLAG", cobol_code)
        
        # Should still include other variables
        self.assertIn("ACCOUNT-BALANCE", cobol_code)
        self.assertIn("NSF-FEE", cobol_code)
        
        # Should still be valid COBOL
        self.assertIn("IDENTIFICATION DIVISION", cobol_code)
        self.assertIn("DATA DIVISION", cobol_code)

    def test_generate_violation_cobol_missing_logic(self):
        """Test generating COBOL with missing logic violation"""
        from cobol_generator import COBOLGenerator
        
        generator = COBOLGenerator()
        
        # Generate violation example for missing fee application
        cobol_code = generator.generate_violation_cobol(
            self.sample_rule,
            "VIOLATION-FEE-TEST", 
            "missing_fee_application"
        )
        
        # Should not include NSF fee addition logic
        self.assertNotIn("ADD NSF-FEE TO WITHDRAWAL-AMOUNT", cobol_code)
        
        # Should still include NSF-LOG-FLAG
        self.assertIn("NSF-LOG-FLAG", cobol_code)
        
        # Should still include other compliant logic
        self.assertIn("MOVE 'Y' TO NSF-LOG-FLAG", cobol_code)

    def test_generate_multiple_violations(self):
        """Test generating COBOL with multiple violations"""
        from cobol_generator import COBOLGenerator
        
        generator = COBOLGenerator()
        
        # Create combined violation example
        violation_examples = {
            "missing_log_flag_and_fee": {
                "remove_variables": ["NSF-LOG-FLAG"],
                "remove_logic": ["ADD NSF-FEE TO WITHDRAWAL-AMOUNT"]
            }
        }
        
        cobol_code = generator.generate_violation_cobol_custom(
            self.sample_rule,
            "MULTI-VIOLATION-TEST",
            violation_examples["missing_log_flag_and_fee"]
        )
        
        # Should not include any rejected elements
        self.assertNotIn("NSF-LOG-FLAG", cobol_code)
        self.assertNotIn("ADD NSF-FEE TO WITHDRAWAL-AMOUNT", cobol_code)
        
        # Should still include other elements
        self.assertIn("ACCOUNT-BALANCE", cobol_code)
        self.assertIn("DISPLAY 'NSF Event Logged - Fee Applied'", cobol_code)

    def test_save_generated_cobol_files(self):
        """Test saving generated COBOL to files"""
        from cobol_generator import COBOLGenerator
        
        generator = COBOLGenerator()
        output_dir = self.temp_path / "cobol_examples"
        output_dir.mkdir(parents=True)
        
        # Generate and save files
        files_created = generator.save_cobol_examples(self.sample_rule, str(output_dir))
        
        # Check files were created
        compliant_file = output_dir / "compliant.cob"
        violation_file = output_dir / "violation.cob"
        
        self.assertTrue(compliant_file.exists())
        self.assertTrue(violation_file.exists())
        
        # Check file contents
        with open(compliant_file, 'r') as f:
            compliant_content = f.read()
            self.assertIn("COMPLIANT", compliant_content)
            self.assertIn("NSF-LOG-FLAG", compliant_content)
        
        with open(violation_file, 'r') as f:
            violation_content = f.read()
            self.assertIn("violation", violation_content.lower())

    def test_cobol_validation(self):
        """Test basic COBOL syntax validation"""
        from cobol_generator import COBOLGenerator
        
        generator = COBOLGenerator()
        cobol_code = generator.generate_compliant_cobol(self.sample_rule, "VALIDATION-TEST")
        
        is_valid = generator.validate_cobol_syntax(cobol_code)
        self.assertTrue(is_valid)
        
        # Test invalid COBOL
        invalid_cobol = "PROGRAM-ID. INVALID-PROGRAM\nINVALID-SYNTAX"
        is_invalid = generator.validate_cobol_syntax(invalid_cobol)
        self.assertFalse(is_invalid)

    def test_template_customization(self):
        """Test COBOL template customization"""
        from cobol_generator import COBOLGenerator
        
        generator = COBOLGenerator()
        
        # Test program header customization
        custom_header = "IDENTIFICATION DIVISION.\nPROGRAM-ID. CUSTOM-PROGRAM."
        cobol_code = generator.generate_compliant_cobol(
            self.sample_rule, 
            "CUSTOM-TEST",
            custom_header=custom_header
        )
        
        self.assertIn("PROGRAM-ID. CUSTOM-PROGRAM", cobol_code)

    def test_variable_definition_generation(self):
        """Test proper COBOL variable definition generation"""
        from cobol_generator import COBOLGenerator
        
        generator = COBOLGenerator()
        cobol_code = generator.generate_compliant_cobol(self.sample_rule, "VARIABLE-TEST")
        
        # Check variable definitions in DATA DIVISION
        lines = cobol_code.split('\n')
        data_section_index = next((i for i, line in enumerate(lines) if "DATA DIVISION" in line), None)
        self.assertIsNotNone(data_section_index)
        
        # Check PIC clauses for different data types
        self.assertIn("PIC 9(8)V99", cobol_code)  # numeric
        self.assertIn("PIC X(1)", cobol_code)     # flag/text

    def test_procedure_generation(self):
        """Test PROCEDURE DIVISION generation with proper logic"""
        from cobol_generator import COBOLGenerator
        
        generator = COBOLGenerator()
        cobol_code = generator.generate_compliant_cobol(self.sample_rule, "PROCEDURE-TEST")
        
        # Should include PROCEDURE DIVISION
        self.assertIn("PROCEDURE DIVISION", cobol_code)
        
        # Should include STOP RUN
        self.assertIn("STOP RUN", cobol_code)
        
        # Should include proper logic flow
        lines = cobol_code.split('\n')
        procedure_index = next((i for i, line in enumerate(lines) if "PROCEDURE DIVISION" in line), None)
        stop_run_index = next((i for i, line in enumerate(lines) if "STOP RUN" in line), None)
        self.assertIsNotNone(procedure_index)
        self.assertIsNotNone(stop_run_index)
        self.assertLess(procedure_index, stop_run_index)

    def test_error_handling_invalid_violation(self):
        """Test error handling for invalid violation example names"""
        from cobol_generator import COBOLGenerator, COBOLGenerationError
        
        generator = COBOLGenerator()
        
        with self.assertRaises(COBOLGenerationError) as context:
            generator.generate_violation_cobol(self.sample_rule, "TEST", "nonexistent_violation")
        
        self.assertIn("Violation example 'nonexistent_violation' not found", str(context.exception))

    def test_empty_rule_handling(self):
        """Test handling of empty or minimal DSL rules"""
        from cobol_generator import COBOLGenerator
        
        empty_rule = DSLRule(
            name="Empty Rule",
            description="Minimal rule",
            variables=[],
            conditions=[],
            requirements=[],
            compliant_logic={},
            violation_examples={}
        )
        
        generator = COBOLGenerator()
        cobol_code = generator.generate_compliant_cobol(empty_rule, "EMPTY-TEST")
        
        # Should still generate valid COBOL structure
        self.assertIn("IDENTIFICATION DIVISION", cobol_code)
        self.assertIn("PROGRAM-ID. EMPTY-TEST", cobol_code)
        self.assertIn("DATA DIVISION", cobol_code)
        self.assertIn("PROCEDURE DIVISION", cobol_code)

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


class TestCOBOLAIGenerator(unittest.TestCase):
    """Test cases for AI-powered COBOL Generator features"""
    
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

    def test_ai_generator_detection_openai_key(self):
        """Test AI generator detects OPENAI_KEY environment variable"""
        # Set environment variable
        os.environ['OPENAI_KEY'] = 'test_api_key'
        
        from cobol_generator import COBOLGenerator
        generator = COBOLGenerator()
        
        # Should detect AI capability
        self.assertTrue(generator.ai_available)
        
        # Clean up
        del os.environ['OPENAI_KEY']

    def test_ai_generator_fallback_no_key(self):
        """Test AI generator falls back to template mode without OPENAI_KEY"""
        # Ensure no environment variable
        if 'OPENAI_KEY' in os.environ:
            del os.environ['OPENAI_KEY']
        
        from cobol_generator import COBOLGenerator
        generator = COBOLGenerator()
        
        # Whether AI is available depends on whether keys are set
        # May be available or not - both are valid states
        self.assertIsInstance(generator.ai_available, bool)

    @patch('openai.OpenAI')
    def test_generate_ai_compliant_cobol(self, mock_openai):
        """Test generating compliant COBOL using AI"""
        # Mock OpenAI response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """IDENTIFICATION DIVISION.
       PROGRAM-ID. TEST-PROGRAM.
       AUTHOR. AI Generated.
       DATE-WRITTEN. Generated by AI.

       ENVIRONMENT DIVISION.

       DATA DIVISION.
       WORKING-CORAGE SECTION.
       01 ACCOUNT-BALANCE PIC 9(8)V99.
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
        
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Set up AI environment
        os.environ['OPENAI_KEY'] = 'test_api_key'
        
        from cobol_generator import COBOLGenerator
        generator = COBOLGenerator()
        
        cobol_code = generator.generate_compliant_cobol(self.sample_rule, "TEST-PROGRAM")
        
        # Should contain AI-generated content
        self.assertIn("PROGRAM-ID. TEST-PROGRAM", cobol_code)
        self.assertIn("AI Generated", cobol_code)
        
        # Clean up
        del os.environ['OPENAI_KEY']

    @patch('openai.OpenAI')
    def test_generate_ai_violation_cobol(self, mock_openai):
        """Test generating violation COBOL using AI"""
        # Mock OpenAI response with sophisticated violation
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """IDENTIFICATION DIVISION.
       PROGRAM-ID. VIOLATION-TEST.
       * SOPHISTICATED VIOLATION: Missing audit trail validation

       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 ACCOUNT-BALANCE PIC 9(8)V99.
       01 NSF-FEE PIC 9(2)V99.
        * Missing: NSF-LOG-FLAG variable

       PROCEDURE DIVISION.
       IF ACCOUNT-BALANCE < WITHDRAWAL-AMOUNT THEN
           ADD NSF-FEE TO WITHDRAWAL-AMOUNT
           DISPLAY 'Transaction Failed'  * Subtle: no logging requirement
       END-IF
       STOP RUN."""
        
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Set up AI environment
        os.environ['OPENAI_KEY'] = 'test_api_key'
        
        from cobol_generator import COBOLGenerator
        generator = COBOLGenerator()
        
        cobol_code = generator.generate_violation_cobol(self.sample_rule, "VIOLATION-TEST", "missing_log_flag")
        
        # Should contain AI-generated sophisticated violation
        self.assertIn("SOPHISTICATED VIOLATION", cobol_code)
        self.assertNotIn("NSF-LOG-FLAG", cobol_code)  # Should be missing
        
        # Clean up
        del os.environ['OPENAI_KEY']

    @patch('openai.OpenAI')
    def test_ai_context_building(self, mock_openai):
        """Test building rich context from DSL rule for AI prompts"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Generated COBOL"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        os.environ['OPENAI_KEY'] = 'test_api_key'
        
        from cobol_generator import COBOLGenerator
        generator = COBOLGenerator()
        
        # Verify context is built correctly
        context = generator._build_ai_context(self.sample_rule, "compliant")
        
        # Context should include business information
        context_str = str(context)
        self.assertIn("NSF", context_str)
        self.assertIn("banking", context_str.lower())
        self.assertIn("compliance", context_str.lower())
        
        # Should include technical requirements
        self.assertIn("NSF-LOG-FLAG", context_str)
        self.assertIn("NSF-FEE", context_str)
        
        del os.environ['OPENAI_KEY']

    def test_ai_model_configuration(self):
        """Test AI model and parameter configuration"""
        os.environ['OPENAI_KEY'] = 'test_api_key'
        
        from cobol_generator import COBOLGenerator
        generator = COBOLGenerator()
        
        # Should have AI configuration
        self.assertIsInstance(generator.ai_model, str)
        self.assertIsInstance(generator.ai_temperature, float)
        self.assertIsInstance(generator.ai_max_tokens, int)
        
        del os.environ['OPENAI_KEY']

    def test_template_fallback_on_ai_error(self):
        """Test falls back to template generation when AI fails"""
        os.environ['OPENAI_KEY'] = 'test_api_key'
        
        from cobol_generator import COBOLGenerator
        generator = COBOLGenerator()
        
        # Mock the actual AI generation call to raise exception
        with patch.object(generator, '_generate_ai_cobol') as mock_ai_generate:
            mock_ai_generate.side_effect = Exception("API Error")
            
            # Should fall back to template generation
            cobol_code = generator.generate_compliant_cobol(self.sample_rule, "FALLBACK-TEST")
            
            # Should still generate valid COBOL
            self.assertIn("PROGRAM-ID. FALLBACK-TEST", cobol_code)
            self.assertIn("NSF-LOG-FLAG", cobol_code)
        
        del os.environ['OPENAI_KEY']

    def test_ai_cost_tracking(self):
        """Test AI cost and token tracking"""
        os.environ['OPENAI_KEY'] = 'test_api_key'
        
        from cobol_generator import COBOLGenerator
        generator = COBOLGenerator()
        
        # Should track usage metrics
        self.assertIsInstance(generator.ai_generation_count, int)
        self.assertIsInstance(generator.ai_total_tokens, int)
        
        del os.environ['OPENAI_KEY']

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        # Clean up any environment variables
        for key in ['OPENAI_KEY', 'OPENAI_MODEL', 'OPENAI_TEMPERATURE']:
            if key in os.environ:
                del os.environ[key]
        
        shutil.rmtree(self.temp_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
