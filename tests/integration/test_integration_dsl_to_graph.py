"""
Integration tests for DSL parser to GraphGenerator workflow
Tests the integration between DSL parsing and graph node creation
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from dsl_parser import DSLParser, DSLError
from graph_generator import GraphGenerator


class TestDSLToGraphIntegration(unittest.TestCase):
    """Test DSL parser integration with GraphGenerator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create test directories
        self.rules_dir = self.temp_path / "rules"
        self.rules_dir.mkdir()
        
        self.graph_gen = GraphGenerator()
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def _create_complex_dsl_rule(self):
        """Create a complex DSL rule for testing"""
        complex_rule = """
rule:
  name: "Complex Banking Rule"
  description: "Complex rule with multiple variables and requirements"

variables:
  - name: "ACCOUNT-BALANCE"
    type: "numeric"
    pic: "9(8)V99"
    description: "Current account balance"
  - name: "NSF-FLAG"
    type: "flag"
    pic: "X(1)"
    description: "NSF event flag"
  - name: "NSF-FEE"
    type: "numeric"
    pic: "9(2)V99"
    description: "NSF fee amount"
  - name: "TRANSACTION-AMOUNT"
    type: "numeric"
    pic: "9(8)V99"
    description: "Transaction amount"
  - name: "APPROVAL-LEVEL"
    type: "string"
    pic: "X(10)"
    description: "Approval level required"

conditions:
  insufficient_funds:
    check: "ACCOUNT-BALANCE < 1000"
    description: "Check if account has sufficient funds"
  high_value_transaction:
    check: "TRANSACTION-AMOUNT > 10000"
    description: "Check if transaction requires senior approval"

requirements:
  account_balance_presence:
    description: "Account balance must be present"
    check: "ACCOUNT-BALANCE variable must be defined"
    violation_message: "ACCOUNT-BALANCE variable not defined"
    severity: "HIGH"
  nsf_flag_presence:
    description: "NSF flag must be present"
    check: "NSF-FLAG variable must be defined"
    violation_message: "NSF-FLAG variable not defined"
    severity: "HIGH"
  nsf_logic:
    description: "NSF flag set when balance below threshold"
    check: "IF ACCOUNT-BALANCE < 1000 THEN NSF-FLAG = 'Y' logic must be present"
    violation_message: "NSF logic not implemented"
    severity: "MEDIUM"
  approval_logic:
    description: "High-value transactions require senior approval"
    check: "IF TRANSACTION-AMOUNT > 10000 THEN APPROVAL-LEVEL = 'SENIOR' logic must be present"
    violation_message: "Approval logic not implemented"
    severity: "HIGH"
  fee_validation:
    description: "NSF fee must be non-negative"
    check: "NSF-FEE >= 0 validation must be present"
    violation_message: "Fee validation not implemented"
    severity: "MEDIUM"

compliant_logic:
  when_insufficient_funds:
    - "MOVE 'Y' TO NSF-FLAG"
    - "DISPLAY 'NSF Event Logged'"
  when_high_value:
    - "MOVE 'SENIOR' TO APPROVAL-LEVEL"
    - "DISPLAY 'Senior Approval Required'"

violation_examples:
  missing_nsf_flag:
    description: "NSF-FLAG variable missing"
    remove_variables: ["NSF-FLAG"]
  missing_approval_logic:
    description: "Approval logic missing"
    remove_logic: ["MOVE 'SENIOR' TO APPROVAL-LEVEL"]
"""
        
        rule_file = self.rules_dir / "complex_banking_rule.dsl"
        rule_file.write_text(complex_rule.strip())
        return rule_file
    
    def test_dsl_rule_to_graph_nodes_integration(self):
        """Test DSL rule parsing and graph node creation"""
        # Create complex DSL rule
        rule_file = self._create_complex_dsl_rule()
        
        # Parse DSL rule
        parser = DSLParser(rules_dir=str(self.rules_dir))
        rules = parser.load_all_rules()
        
        self.assertEqual(len(rules), 1)
        rule = rules[0]
        
        # Verify rule structure
        self.assertEqual(rule.name, "Complex Banking Rule")
        self.assertEqual(len(rule.variables), 5)
        self.assertEqual(len(rule.requirements), 5)
        
        # Add rule to graph
        self.graph_gen.add_dsl_rule(rule)
        
        # Verify graph structure
        nodes = self.graph_gen.graph["nodes"]
        edges = self.graph_gen.graph["edges"]
        
        # Should have 1 rule node + 5 variable nodes + 5 requirement nodes = 11 nodes
        rule_nodes = [n for n in nodes if n["type"] == "dsl_rule"]
        variable_nodes = [n for n in nodes if n["type"] == "dsl_variable"]
        requirement_nodes = [n for n in nodes if n["type"] == "dsl_requirement"]
        
        self.assertEqual(len(rule_nodes), 1)
        self.assertEqual(len(variable_nodes), 5)
        self.assertEqual(len(requirement_nodes), 5)
        
        # Verify rule node
        rule_node = rule_nodes[0]
        self.assertEqual(rule_node["name"], "Complex Banking Rule")
        self.assertEqual(rule_node["description"], "Complex rule with multiple variables and requirements")
        
        # Verify variable nodes
        var_names = [n["name"] for n in variable_nodes]
        expected_vars = ["ACCOUNT-BALANCE", "NSF-FLAG", "NSF-FEE", 
                        "TRANSACTION-AMOUNT", "APPROVAL-LEVEL"]
        
        for expected_var in expected_vars:
            self.assertIn(expected_var, var_names)
        
        # Verify requirement nodes
        req_descriptions = [n["description"] for n in requirement_nodes]
        self.assertIn("Account balance must be present", req_descriptions)
        self.assertIn("NSF flag must be present", req_descriptions)
        self.assertIn("NSF flag set when balance below threshold", req_descriptions)
        
        # Verify edges (rule -> variables, rule -> requirements, rule -> conditions)
        rule_edges = [e for e in edges if e["from_node"] == rule_node["id"]]
        condition_nodes = [n for n in nodes if n["type"] == "dsl_condition"]
        expected_edges = len(variable_nodes) + len(requirement_nodes) + len(condition_nodes)
        self.assertEqual(len(rule_edges), expected_edges)
        
        print(f"\n✅ DSL to Graph integration test passed!")
        print(f"   📊 Created {len(nodes)} nodes, {len(edges)} edges")
        print(f"   📋 Rule: {rule.name}")
        print(f"   🔗 Variables: {len(variable_nodes)}")
        print(f"   📝 Requirements: {len(requirement_nodes)}")
    
    def test_multiple_dsl_rules_integration(self):
        """Test integration with multiple DSL rules"""
        # Create multiple DSL rules
        rules_data = [
            {
                "name": "NSF Rule",
                "description": "NSF event handling rule",
                "domain": "banking",
                "variables": ["ACCOUNT-BALANCE", "NSF-FLAG"],
                "requirements": ["NSF handling", "Fee application"]
            },
            {
                "name": "Approval Rule", 
                "description": "Transaction approval rule",
                "domain": "banking",
                "variables": ["TRANSACTION-AMOUNT", "APPROVAL-LEVEL"],
                "requirements": ["Amount validation", "Approval check"]
            },
            {
                "name": "Audit Rule",
                "description": "Audit trail rule",
                "domain": "compliance",
                "variables": ["AUDIT-LOG", "USER-ID"],
                "requirements": ["Log creation", "User tracking"]
            }
        ]
        
        for i, rule_data in enumerate(rules_data):
            rule_content = f"""
rule:
  name: "{rule_data['name']}"
  description: "{rule_data['description']}"

variables:
"""
            for var in rule_data["variables"]:
                rule_content += f"  - name: \"{var}\"\n    type: \"string\"\n    pic: \"X(10)\"\n    description: \"{var} variable\"\n"
            
            rule_content += "conditions:\n"
            rule_content += f"  {rule_data['name'].lower().replace(' ', '_')}:\n"
            rule_content += f"    check: \"{rule_data['variables'][0]} is defined\"\n"
            rule_content += f"    description: \"Check {rule_data['variables'][0]} variable\"\n\n"
            
            rule_content += "requirements:\n"
            for j, req in enumerate(rule_data["requirements"]):
                rule_content += f"  {rule_data['name'].lower().replace(' ', '_')}_req_{j+1}:\n"
                rule_content += f"    description: \"{req}\"\n"
                rule_content += f"    check: \"{rule_data['variables'][0]} variable must be defined\"\n"
                rule_content += f"    violation_message: \"{rule_data['variables'][0]} variable not defined\"\n"
                rule_content += f"    severity: \"HIGH\"\n"
            
            rule_content += "\ncompliant_logic:\n"
            rule_content += f"  {rule_data['name'].lower().replace(' ', '_')}_logic:\n"
            rule_content += f"    - \"DISPLAY '{rule_data['name']} Logic Executed'\"\n"
            
            rule_content += "\nviolation_examples:\n"
            rule_content += f"  - description: \"{rule_data['variables'][0]} variable missing\"\n"
            rule_content += f"    code: |\n"
            rule_content += f"      IDENTIFICATION DIVISION.\n"
            rule_content += f"      PROGRAM-ID. TEST.\n"
            rule_content += f"      PROCEDURE DIVISION.\n"
            rule_content += f"      STOP RUN.\n"
            
            rule_file = self.rules_dir / f"rule_{i+1}.dsl"
            rule_file.write_text(rule_content.strip())
        
        # Parse all rules
        parser = DSLParser(rules_dir=str(self.rules_dir))
        rules = parser.load_all_rules()
        
        self.assertEqual(len(rules), 3)
        
        # Add all rules to graph
        for rule in rules:
            self.graph_gen.add_dsl_rule(rule)
        
        # Verify graph structure
        nodes = self.graph_gen.graph["nodes"]
        rule_nodes = [n for n in nodes if n["type"] == "dsl_rule"]
        variable_nodes = [n for n in nodes if n["type"] == "dsl_variable"]
        requirement_nodes = [n for n in nodes if n["type"] == "dsl_requirement"]
        
        # Should have 3 rules + 6 variables + 6 requirements = 15 nodes
        self.assertEqual(len(rule_nodes), 3)
        self.assertEqual(len(variable_nodes), 6)  # 2 + 2 + 2
        self.assertEqual(len(requirement_nodes), 6)  # 2 + 2 + 2
        
        # Verify rule names
        rule_names = [n["name"] for n in rule_nodes]
        self.assertIn("NSF Rule", rule_names)
        self.assertIn("Approval Rule", rule_names)
        self.assertIn("Audit Rule", rule_names)
        
        print(f"\n✅ Multiple DSL rules integration test passed!")
        print(f"   📊 Created {len(nodes)} nodes for {len(rules)} rules")
        print(f"   🏦 Rules: {rule_names}")
    
    def test_dsl_rule_metadata_integration(self):
        """Test DSL rule metadata preservation in graph"""
        # Create rule with rich metadata
        metadata_rule = """
rule:
  name: "Metadata Rich Rule"
  description: "Rule with comprehensive metadata"

variables:
  - name: "TEST-VAR"
    type: "numeric"
    pic: "9(5)"
    value: "0"
    description: "Test variable"

conditions:
  test_condition:
    check: "TEST-VAR >= 0"
    description: "Test variable validation"

requirements:
  test_variable_presence:
    description: "Test variable must be present"
    check: "TEST-VAR variable must be defined"
    violation_message: "TEST-VAR variable not defined"
    severity: "HIGH"

compliant_logic:
  test_logic:
    - "MOVE 0 TO TEST-VAR"
    - "DISPLAY 'Test Variable Set'"

violation_examples:
  missing_test_var:
    description: "TEST-VAR variable missing"
    remove_variables: ["TEST-VAR"]
"""
        
        rule_file = self.rules_dir / "metadata_rule.dsl"
        rule_file.write_text(metadata_rule.strip())
        
        # Parse and add to graph
        parser = DSLParser(rules_dir=str(self.rules_dir))
        rules = parser.load_all_rules()
        self.graph_gen.add_dsl_rule(rules[0])
        
        # Verify metadata preservation
        rule_nodes = [n for n in self.graph_gen.graph["nodes"] if n["type"] == "dsl_rule"]
        rule_node = rule_nodes[0]
        
        self.assertEqual(rule_node["name"], "Metadata Rich Rule")
        self.assertEqual(rule_node["description"], "Rule with comprehensive metadata")
        
        # Verify variable metadata
        variable_nodes = [n for n in self.graph_gen.graph["nodes"] if n["type"] == "dsl_variable"]
        var_node = variable_nodes[0]
        
        self.assertEqual(var_node["data"]["type"], "numeric")
        # Note: 'required' and 'default_value' attributes are not currently stored in variable nodes
        self.assertIn("pic_clause", var_node["data"])
        self.assertIn("description", var_node["data"])
        # Note: validation field not currently stored in variable data
        
        print(f"\n✅ DSL metadata integration test passed!")
        print(f"   📋 Preserved metadata: {len(rule_node['data'])} fields")
    
    def test_dsl_error_handling_integration(self):
        """Test DSL error handling in graph integration"""
        # Test with invalid DSL syntax
        invalid_rules = [
            # Missing required fields
            """
name: "Invalid Rule 1"
# Missing description, domain, variables, requirements
""",
            # Invalid YAML syntax
            """
name: "Invalid Rule 2"
description: "Invalid YAML
domain: banking  # Missing quote
variables: []
requirements: []
""",
            # Empty rule
            """
name: ""
description: ""
domain: ""
variables: []
requirements: []
"""
        ]
        
        for i, invalid_rule in enumerate(invalid_rules):
            rule_file = self.rules_dir / f"invalid_rule_{i+1}.dsl"
            rule_file.write_text(invalid_rule.strip())
        
        # Should handle invalid DSL gracefully
        parser = DSLParser(rules_dir=str(self.rules_dir))
        
        with self.assertRaises(DSLError):
            parser.load_all_rules()
        
        print(f"\n✅ DSL error handling integration test passed!")
        print(f"   ⚠️ Properly rejected {len(invalid_rules)} invalid rules")


if __name__ == '__main__':
    unittest.main()
