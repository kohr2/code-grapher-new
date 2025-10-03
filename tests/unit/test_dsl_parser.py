#!/usr/bin/env python3
"""
Test module for DSL Parser
Following TDD approach: tests first, then implementation validation
"""

import unittest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from dsl_parser import (
    DSLParser, DSLRule, DSLVariable, DSLRequirement, DSLCondition,
    DSLError, DSLLocationError, DSLValidationError
)


class TestDSLParser(unittest.TestCase):
    """Test cases for the DSL Parser module"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create sample DSL content
        self.sample_dsl_content = {
            'rule': {
                'name': 'Test Banking Rule',
                'description': 'Test rule for banking compliance'
            },
            'variables': [
                {
                    'name': 'ACCOUNT-BALANCE',
                    'type': 'numeric',
                    'pic': '9(8)V99',
                    'description': 'Current account balance'
                },
                {
                    'name': 'TRANSACTION-AMOUNT',
                    'type': 'numeric',
                    'pic': '9(6)V99',
                    'description': 'Transaction amount',
                    'value': '1000.00'
                }
            ],
            'conditions': {
                'sufficient_funds': {
                    'check': 'ACCOUNT-BALANCE >= TRANSACTION-AMOUNT',
                    'description': 'Check if account has sufficient funds'
                }
            },
            'requirements': {
                'transaction_logging': {
                    'description': 'All transactions must be logged',
                    'check': 'TRANSACTION-LOG-PRESENT must be true',
                    'violation_message': 'Transaction not logged',
                    'severity': 'HIGH'
                },
                'balance_validation': {
                    'description': 'Account balance must be validated',
                    'check': 'Account balance checked before transaction',
                    'violation_message': 'Balance not validated',
                    'severity': 'MEDIUM'
                }
            },
            'compliant_logic': {
                'when_sufficient_funds': [
                    'PERFORM VALIDATE-TRANSACTION',
                    'ADD TRANSACTION-AMOUNT TO ACCOUNT-BALANCE',
                    'PERFORM LOG-TRANSACTION'
                ]
            },
            'violation_examples': {
                'missing_logging': {
                    'description': 'Transaction logging missing',
                    'remove_logic': ['PERFORM LOG-TRANSACTION']
                }
            }
        }
        
        # Create sample DSL files
        self.create_sample_files()

    def create_sample_files(self):
        """Create sample DSL files for testing"""
        # Valid DSL file
        valid_dsl_file = self.temp_path / "valid_rule.dsl"
        with open(valid_dsl_file, 'w') as f:
            yaml.dump(self.sample_dsl_content, f)
        
        # Invalid DSL file (missing required sections)
        invalid_dsl_content = {
            'rule': {'name': 'Invalid Rule'},
            'variables': []
        }
        invalid_dsl_file = self.temp_path / "invalid_rule.dsl"
        with open(invalid_dsl_file, 'w') as f:
            yaml.dump(invalid_dsl_content, f)
        
        # Malformed YAML file
        malformed_dsl_file = self.temp_path / "malformed_rule.dsl"
        with open(malformed_dsl_file, 'w') as f:
            f.write("rule:\n  name: Invalid YAML\n  incomplete: \"")  # Missing closing quote

    def test_dsl_parser_initialization(self):
        """Test DSLParser can be initialized with custom rules directory"""
        parser = DSLParser(rules_dir=str(self.temp_path))
        self.assertIsNotNone(parser)
        self.assertEqual(parser.rules_dir, self.temp_path)
        self.assertEqual(len(parser.loaded_rules), 0)

    def test_dsl_parser_default_initialization(self):
        """Test DSLParser initialization with default rules directory"""
        # This test assumes rules directory doesn't exist yet
        parser = DSLParser()
        self.assertIsNotNone(parser)
        # Should create the rules directory
        self.assertTrue(Path("rules").exists())
        
        # Clean up
        import shutil
        shutil.rmtree("rules", ignore_errors=True)

    def test_load_rule_file_success(self):
        """Test successful loading of a valid DSL file"""
        parser = DSLParser(rules_dir=str(self.temp_path))
        
        rule = parser.load_rule_file("valid_rule.dsl")
        
        self.assertIsInstance(rule, DSLRule)
        self.assertEqual(rule.name, "Test Banking Rule")
        self.assertEqual(rule.description, "Test rule for banking compliance")
        self.assertEqual(len(rule.variables), 2)
        self.assertEqual(len(rule.conditions), 1)
        self.assertEqual(len(rule.requirements), 2)

    def test_load_rule_file_not_found(self):
        """Test loading non-existent DSL file raises DSLLocationError"""
        parser = DSLParser(rules_dir=str(self.temp_path))
        
        with self.assertRaises(DSLLocationError) as context:
            parser.load_rule_file("nonexistent.dsl")
        
        self.assertIn("DSL file not found", str(context.exception))

    def test_load_rule_file_invalid_extension(self):
        """Test loading file with wrong extension raises error"""
        parser = DSLParser(rules_dir=str(self.temp_path))
        
        # Create a .txt file
        txt_file = self.temp_path / "test.txt"
        with open(txt_file, 'w') as f:
            f.write("content")
        
        with self.assertRaises(DSLError) as context:
            parser.load_rule_file("test.txt")
        
        self.assertIn("Invalid DSL filename", str(context.exception))

    def test_load_rule_file_yaml_parsing_error(self):
        """Test loading malformed YAML raises DSLValidationError"""
        parser = DSLParser(rules_dir=str(self.temp_path))
        
        with self.assertRaises(DSLValidationError) as context:
            parser.load_rule_file("malformed_rule.dsl")
        
        self.assertIn("YAML parsing error", str(context.exception))

    def test_load_rule_file_missing_sections(self):
        """Test loading DSL file with missing required sections"""
        parser = DSLParser(rules_dir=str(self.temp_path))
        
        with self.assertRaises(DSLValidationError) as context:
            parser.load_rule_file("invalid_rule.dsl")
        
        self.assertIn("Missing required DSL sections", str(context.exception))

    def test_load_rule_file_invalid_rule_section(self):
        """Test DSL file with invalid rule section"""
        parser = DSLParser(rules_dir=str(self.temp_path))
        
        # Create DSL file with invalid rule section
        invalid_rule_dsl = self.temp_path / "invalid_rule_section.dsl"
        invalid_content = {'invalid': 'content'}  # Missing 'rule' key
        with open(invalid_rule_dsl, 'w') as f:
            yaml.dump(invalid_content, f)
        
        with self.assertRaises(DSLValidationError) as context:
            parser.load_rule_file("invalid_rule_section.dsl")
        
        self.assertIn("Missing required DSL sections", str(context.exception))

    def test_parse_variable_success(self):
        """Test successful parsing of variable from DSL data"""
        parser = DSLParser()
        
        var_data = {
            'name': 'TEST-VARIABLE',
            'type': 'flag',
            'pic': 'X(1)',
            'description': 'Test flag variable',
            'default': 'N'
        }
        
        variable = parser._parse_variable(var_data, 'test.dsl')
        
        self.assertIsInstance(variable, DSLVariable)
        self.assertEqual(variable.name, 'TEST-VARIABLE')
        self.assertEqual(variable.type, 'flag')
        self.assertEqual(variable.pic, 'X(1)')
        self.assertEqual(variable.description, 'Test flag variable')
        self.assertEqual(variable.default, 'N')

    def test_parse_variable_missing_fields(self):
        """Test parsing variable with missing required fields"""
        parser = DSLParser()
        
        var_data = {'name': 'INCOMPLETE'}  # Missing 'type' and 'pic'
        
        with self.assertRaises(DSLValidationError) as context:
            parser._parse_variable(var_data, 'test.dsl')
        
        self.assertIn("Missing variable fields", str(context.exception))

    def test_parse_condition_success(self):
        """Test successful parsing of condition from DSL data"""
        parser = DSLParser()
        
        cond_data = {
            'check': 'ACCOUNT-BALANCE > 0',
            'description': 'Check positive balance'
        }
        
        condition = parser._parse_condition('balance_check', cond_data, 'test.dsl')
        
        self.assertIsInstance(condition, DSLCondition)
        self.assertEqual(condition.name, 'balance_check')
        self.assertEqual(condition.check, 'ACCOUNT-BALANCE > 0')
        self.assertEqual(condition.description, 'Check positive balance')

    def test_parse_condition_missing_check(self):
        """Test parsing condition with missing check field"""
        parser = DSLParser()
        
        cond_data = {'description': 'Incomplete condition'}
        
        with self.assertRaises(DSLValidationError) as context:
            parser._parse_condition('incomplete', cond_data, 'test.dsl')
        
        self.assertIn("Missing condition check", str(context.exception))

    def test_parse_requirement_success(self):
        """Test successful parsing of requirement from DSL data"""
        parser = DSLParser()
        
        req_data = {
            'description': 'Test requirement',
            'check': 'Variable must exist',
            'violation_message': 'Variable missing',
            'severity': 'HIGH'
        }
        
        requirement = parser._parse_requirement('test_req', req_data, 'test.dsl')
        
        self.assertIsInstance(requirement, DSLRequirement)
        self.assertEqual(requirement.name, 'test_req')
        self.assertEqual(requirement.description, 'Test requirement')
        self.assertEqual(requirement.check, 'Variable must exist')
        self.assertEqual(requirement.violation_message, 'Variable missing')
        self.assertEqual(requirement.severity, 'HIGH')

    def test_parse_requirement_with_default_severity(self):
        """Test parsing requirement with default severity"""
        parser = DSLParser()
        
        req_data = {
            'description': 'Test requirement',
            'check': 'Variable must exist',
            'violation_message': 'Variable missing'
            # No severity specified
        }
        
        requirement = parser._parse_requirement('test_req', req_data, 'test.dsl')
        
        self.assertEqual(requirement.severity, 'MEDIUM')  # Default severity

    def test_parse_requirement_missing_fields(self):
        """Test parsing requirement with missing required fields"""
        parser = DSLParser()
        
        req_data = {
            'description': 'Incomplete requirement'
            # Missing check and violation_message
        }
        
        with self.assertRaises(DSLValidationError) as context:
            parser._parse_requirement('incomplete', req_data, 'test.dsl')
        
        self.assertIn("Missing requirement fields", str(context.exception))

    def test_validate_rule_success(self):
        """Test successful rule validation"""
        parser = DSLParser()
        
        rule = DSLRule(
            name="Test Rule",
            description="Test rule",
            variables=[
                DSLVariable("VAR1", "numeric", "9(5)", "First variable"),
                DSLVariable("VAR2", "numeric", "9(5)", "Second variable")
            ],
            conditions=[],
            requirements=[
                DSLRequirement("req1", "Requirement 1", "VAR1 exists", "Missing", "HIGH")
            ],
            compliant_logic={"when_valid": ["MOVE 'Y' TO VAR1"]},
            violation_examples={"missing": {"remove_variables": ["VAR1"]}}
        )
        
        # Should not raise exception
        parser._validate_rule(rule, 'test.dsl')

    def test_validate_rule_no_variables(self):
        """Test rule validation with no variables"""
        parser = DSLParser()
        
        rule = DSLRule(
            name="Empty Rule",
            description="Rule with no variables",
            variables=[],
            conditions=[],
            requirements=[],
            compliant_logic={},
            violation_examples={}
        )
        
        with self.assertRaises(DSLValidationError) as context:
            parser._validate_rule(rule, 'test.dsl')
        
        self.assertIn("No variables defined", str(context.exception))

    def test_validate_rule_no_requirements(self):
        """Test rule validation with no requirements"""
        parser = DSLParser()
        
        rule = DSLRule(
            name="No Requirements Rule",
            description="Rule with no requirements",
            variables=[DSLVariable("VAR1", "numeric", "9(5)", "Variable")],
            conditions=[],
            requirements=[],
            compliant_logic={},
            violation_examples={}
        )
        
        with self.assertRaises(DSLValidationError) as context:
            parser._validate_rule(rule, 'test.dsl')
        
        self.assertIn("No requirements defined", str(context.exception))

    def test_validate_rule_duplicate_variable_names(self):
        """Test rule validation with duplicate variable names"""
        parser = DSLParser()
        
        rule = DSLRule(
            name="Duplicate Variables Rule",
            description="Rule with duplicate variables",
            variables=[
                DSLVariable("DUPLICATE", "numeric", "9(5)", "First occurrence"),
                DSLVariable("DUPLICATE", "numeric", "9(5)", "Second occurrence")
            ],
            conditions=[],
            requirements=[
                DSLRequirement("req1", "Requirement 1", "DUPLICATE exists", "Missing", "HIGH")
            ],
            compliant_logic={"when_valid": ["MOVE 'Y' TO DUPLICATE"]},
            violation_examples={"missing": {"remove_variables": ["DUPLICATE"]}}
        )
        
        with self.assertRaises(DSLValidationError) as context:
            parser._validate_rule(rule, 'test.dsl')
        
        self.assertIn("Duplicate variable names", str(context.exception))

    def test_get_all_rules_empty_directory(self):
        """Test get_all_rules with empty rules directory"""
        empty_dir = self.temp_path / "empty"
        empty_dir.mkdir()
        
        parser = DSLParser(rules_dir=str(empty_dir))
        rules = parser.get_all_rules()
        
        self.assertEqual(len(rules), 0)

    def test_get_all_rules_with_files(self):
        """Test get_all_rules finds DSL files"""
        parser = DSLParser(rules_dir=str(self.temp_path))
        rules = parser.get_all_rules()
        
        # Should find valid_rule.dsl
        self.assertIn('valid_rule', rules)
        self.assertIn('invalid_rule', rules)
        self.assertIn('malformed_rule', rules)

    def test_load_all_rules_success(self):
        """Test successful loading of all valid DSL files"""
        parser = DSLParser(rules_dir=str(self.temp_path))
        
        rules = parser.load_all_rules()
        
        self.assertEqual(len(rules), 1)  # Only valid_rule should load successfully
        self.assertEqual(rules[0].name, "Test Banking Rule")

    def test_load_all_rules_empty_directory(self):
        """Test load_all_rules with empty rules directory"""
        empty_dir = self.temp_path / "empty"
        empty_dir.mkdir()
        
        parser = DSLParser(rules_dir=str(empty_dir))
        
        with self.assertRaises(DSLLocationError) as context:
            parser.load_all_rules()
        
        self.assertIn("No DSL files found", str(context.exception))

    def test_load_all_rules_with_errors(self):
        """Test load_all_rules with some invalid files gracefully handles errors"""
        parser = DSLParser(rules_dir=str(self.temp_path))
        
        # Should succeed even with invalid files, loading only valid ones
        rules = parser.load_all_rules()
        
        # Should load the valid rule and skip invalid ones
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0].name, "Test Banking Rule")

    def test_load_lesson_file_success(self):
        """Test successful loading of lesson file"""
        parser = DSLParser(rules_dir=str(self.temp_path))
        
        rule = parser.load_lesson_file(str(self.temp_path / "valid_rule.dsl"))
        
        self.assertIsInstance(rule, DSLRule)
        self.assertEqual(rule.name, "Test Banking Rule")

    def test_load_lesson_file_not_found(self):
        """Test loading non-existent lesson file"""
        parser = DSLParser()
        
        with self.assertRaises(DSLValidationError) as context:
            parser.load_lesson_file("nonexistent.dsl")
        
        self.assertIn("DSL file not found", str(context.exception))

    def test_load_lesson_file_wrong_extension(self):
        """Test loading lesson file with wrong extension"""
        parser = DSLParser()
        
        txt_file = self.temp_path / "test.txt"
        with open(txt_file, 'w') as f:
            f.write("content")
        
        with self.assertRaises(DSLError) as context:
            parser.load_lesson_file(str(txt_file))
        
        self.assertIn("Invalid DSL filename", str(context.exception))

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
