#!/usr/bin/env python3
"""
DSL Parser Module for Stacktalk
Parses YAML DSL rule files and validates their structure
"""

import yaml
import os
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DSLVariable:
    """Represents a variable in a DSL rule"""
    name: str
    type: str
    pic: str
    description: str
    value: Optional[str] = None
    default: Optional[str] = None


@dataclass
class DSLCondition:
    """Represents a condition in a DSL rule"""
    name: str
    check: str
    description: str


@dataclass
class DSLRequirement:
    """Represents a requirement in a DSL rule"""
    name: str
    description: str
    check: str
    violation_message: str
    severity: str


@dataclass
class DSLRule:
    """Represents a complete DSL rule"""
    name: str
    description: str
    variables: List[DSLVariable]
    conditions: List[DSLCondition]
    requirements: List[DSLRequirement]
    compliant_logic: Dict[str, List[str]]
    violation_examples: Dict[str, Dict[str, Any]]
    source: str = "global"  # "global", "program-specific", "local"
    source_path: str = ""   # Full path to the DSL file


class DSLError(Exception):
    """Custom exception for DSL parsing errors"""
    pass


class DSLLocationError(DSLError):
    """Exception for DSL file location errors"""
    pass


class DSLValidationError(DSLError):
    """Exception for DSL validation errors"""
    pass


class DSLParser:
    """Parser for YAML DSL rule files with multi-source support"""
    
    def __init__(self, rules_dir: str = "rules", program_dir: Optional[str] = None):
        self.rules_dir = Path(rules_dir)
        self.rules_dir.mkdir(parents=True, exist_ok=True)
        self.program_dir = Path(program_dir) if program_dir else None
        self.loaded_rules: Dict[str, DSLRule] = {}
    
    def load_rule_file(self, filename: str) -> DSLRule:
        """
        Load and parse a single DSL rule file
        
        Args:
            filename: Name of the DSL file (e.g., 'nsf_rule.dsl')
            
        Returns:
            DSLRule: Parsed rule object
            
        Raises:
            DSLLocationError: If file doesn't exist
            DSLValidationError: If file content is invalid
        """
        file_path = self.rules_dir / filename
        
        if not file_path.exists():
            raise DSLLocationError(f"DSL file not found → {file_path}")
        
        if not filename.endswith('.dsl'):
            raise DSLError(f"Invalid DSL filename → {filename}, must be *.dsl")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                root = yaml.load(f, Loader=yaml.Loader)
        except Exception as e:
            raise DSLValidationError(f"YAML parsing error → {file_path}: {str(e)}")
        
        # Validate required sections exist
        required_sections = ['rule', 'variables', 'conditions', 'requirements', 
                           'compliant_logic', 'violation_examples']
        missing = [req for req in required_sections if req not in root]
        if missing:
            raise DSLValidationError(f"Missing required DSL sections → {filename}: {missing}")
        
        # Extract rule metadata
        rule_info = root['rule']
        if not isinstance(rule_info, dict) or 'name' not in rule_info:
            raise DSLValidationError(f"Invalid rule section → {filename}: must contain 'name'")
        
        # Parse variables
        variables = []
        for var_data in root['variables']:
            if not isinstance(var_data, dict):
                raise DSLValidationError(f"Invalid variable data → {filename}: {var_data}")
            variables.append(self._parse_variable(var_data, filename))
        
        # Parse conditions
        conditions = []
        for name, cond_data in root['conditions'].items():
            if not isinstance(cond_data, dict):
                raise DSLValidationError(f"Invalid condition data → {filename}: {name}")
            conditions.append(self._parse_condition(name, cond_data, filename))
        
        # Parse requirements
        requirements = []
        for name, req_data in root['requirements'].items():
            if not isinstance(req_data, dict):
                raise DSLValidationError(f"Invalid requirement data → {filename}: {name}")
            requirements.append(self._parse_requirement(name, req_data, filename))
        
        # Build rule object
        rule = DSLRule(
            name=rule_info['name'],
            description=rule_info.get('description', ''),
            variables=variables,
            conditions=conditions,
            requirements=requirements,
            compliant_logic=root['compliant_logic'],
            violation_examples=root['violation_examples']
        )
        
        # Validate rule completeness
        self._validate_rule(rule, filename)
        
        return rule
    
    def _parse_variable(self, var_data: Dict, filename: str) -> DSLVariable:
        """Parse a variable from DSL data"""
        required_fields = ['name', 'type', 'pic']
        missing = [field for field in required_fields if field not in var_data]
        if missing:
            raise DSLValidationError(f"Missing variable fields → {filename}: {missing}")
        
        return DSLVariable(
            name=var_data['name'],
            type=var_data['type'],
            pic=var_data['pic'],
            description=var_data.get('description', ''),
            value=var_data.get('value'),
            default=var_data.get('default')
        )
    
    def _parse_condition(self, name: str, cond_data: Dict, filename: str) -> DSLCondition:
        """Parse a condition from DSL data"""
        if 'check' not in cond_data:
            raise DSLValidationError(f"Missing condition check → {filename}: {name}")
        
        return DSLCondition(
            name=name,
            check=cond_data['check'],
            description=cond_data.get('description', '')
        )
    
    def _parse_requirement(self, name: str, req_data: Dict, filename: str) -> DSLRequirement:
        """Parse a requirement from DSL data"""
        required_fields = ['description', 'check', 'violation_message']
        missing = [field for field in required_fields if field not in req_data]
        if missing:
            raise DSLValidationError(f"Missing requirement fields → {filename}: {name}: {missing}")
        
        return DSLRequirement(
            name=name,
            description=req_data['description'],
            check=req_data['check'],
            violation_message=req_data['violation_message'],
            severity=req_data.get('severity', 'MEDIUM')
        )
    
    def _validate_rule(self, rule: DSLRule, filename: str) -> None:
        """Validate a parsed rule for completeness"""
        if not rule.variables:
            raise DSLValidationError(f"No variables defined → {filename}")
        
        if not rule.requirements:
            raise DSLValidationError(f"No requirements defined → {filename}")
        
        if not rule.compliant_logic:
            raise DSLValidationError(f"No compliant logic defined → {filename}")
        
        if not rule.violation_examples:
            raise DSLValidationError(f"No violation examples defined → {filename}")
        
        # Validate variable names are unique
        var_names = [var.name for var in rule.variables]
        if len(var_names) != len(set(var_names)):
            raise DSLValidationError(f"Duplicate variable names → {filename}: {var_names}")
        
        # Validate requirements reference existing variables (optional check)
        for req in rule.requirements:
            # Only check if the requirement explicitly references a variable name
            var_refs = [var.name for var in rule.variables if var.name in req.check]
            if var_refs:
                unknown_refs = [ref for ref in var_refs if not any(var.name == ref for var in rule.variables)]
                if unknown_refs:
                    raise DSLValidationError(f"Requirement '{req.name}' references unknown variables → {filename}: {unknown_refs}")
    
    def get_all_rules(self) -> List[str]:
        """
        Returns a list of all DSL rule files that can be parsed
        
        Returns:
            List[str]: List of DSL filenames
        """
        if not self.rules_dir.exists():
            return []
        
        return [f.stem for f in self.rules_dir.glob('*.dsl')]
    
    def load_all_rules(self) -> List[DSLRule]:
        """
        Load and parse all DSL files in the rules directory
        
        Returns:
            List[DSLRule]: List of parsed rule objects
            
        Raises:
            DSLValidationError: If any DSL file is invalid
        """
        if not self.rules_dir.exists():
            raise DSLLocationError(f"Rules directory not found → {self.rules_dir}")
        
        dsl_files = [str(f) for f in self.rules_dir.glob('*.dsl')]
        if not dsl_files:
            raise DSLLocationError(f"No DSL files found in → {self.rules_dir}")
        
        rules = []
        errors = []
        
        for filename in dsl_files:
            try:
                # Extract just the filename from the full path
                filename_only = Path(filename).name
                rule = self.load_rule_file(filename_only)
                rules.append(rule)
                self.loaded_rules[rule.name] = rule
            except Exception as e:
                errors.append(f"Failed to load rule file → {filename}: {str(e)}")
        
        # Only raise error if no valid rules were loaded
        if not rules:
            error_msg = "\n".join(errors) if errors else "No valid DSL files found"
            raise DSLValidationError(error_msg)
        
        return rules
    
    def load_rules_for_program(self, program_path: str) -> List[DSLRule]:
        """
        Load DSL rules for a specific program with precedence:
        1. Global rules (rules/*.dsl)
        2. Program-specific rules (programs/domain/rules/*.dsl)  
        3. Local rules (programs/domain/*.dsl)
        
        Args:
            program_path: Path to the program directory or COBOL file
            
        Returns:
            List[DSLRule]: List of parsed rule objects in precedence order
            
        Raises:
            DSLLocationError: If no rules found
            DSLValidationError: If any DSL file is invalid
        """
        program_path = Path(program_path)
        
        # Determine program directory
        if program_path.is_file():
            program_dir = program_path.parent
        else:
            program_dir = program_path
        
        all_rules = []
        rule_sources = []
        
        # 1. Load global rules (lowest precedence)
        try:
            global_rules = self.load_all_rules()
            for rule in global_rules:
                rule.source = "global"
                rule.source_path = str(self.rules_dir / f"{rule.name.lower().replace(' ', '_')}.dsl")
            all_rules.extend(global_rules)
            rule_sources.extend([(rule.name, "global") for rule in global_rules])
        except DSLLocationError:
            pass  # No global rules found, continue
        
        # 2. Load program-specific rules (medium precedence)
        program_rules_dir = program_dir / "rules"
        if program_rules_dir.exists():
            try:
                program_rules = self._load_rules_from_directory(program_rules_dir, "program-specific")
                all_rules.extend(program_rules)
                rule_sources.extend([(rule.name, "program-specific") for rule in program_rules])
            except DSLLocationError:
                pass  # No program-specific rules found, continue
        
        # 3. Load local rules (highest precedence)
        try:
            local_rules = self._load_rules_from_directory(program_dir, "local")
            all_rules.extend(local_rules)
            rule_sources.extend([(rule.name, "local") for rule in local_rules])
        except DSLLocationError:
            pass  # No local rules found, continue
        
        if not all_rules:
            raise DSLLocationError(f"No DSL rules found for program → {program_path}")
        
        # Apply precedence: local > program-specific > global
        final_rules = self._apply_rule_precedence(all_rules)
        
        return final_rules
    
    def _load_rules_from_directory(self, directory: Path, source_type: str) -> List[DSLRule]:
        """
        Load all DSL rules from a specific directory
        
        Args:
            directory: Directory to search for .dsl files
            source_type: Type of rules ("global", "program-specific", "local")
            
        Returns:
            List[DSLRule]: List of parsed rule objects
            
        Raises:
            DSLLocationError: If no DSL files found
            DSLValidationError: If any DSL file is invalid
        """
        if not directory.exists():
            raise DSLLocationError(f"Directory not found → {directory}")
        
        dsl_files = list(directory.glob('*.dsl'))
        if not dsl_files:
            raise DSLLocationError(f"No DSL files found in → {directory}")
        
        rules = []
        errors = []
        
        for dsl_file in dsl_files:
            try:
                rule = self._load_rule_from_path(dsl_file, source_type)
                rules.append(rule)
            except Exception as e:
                errors.append(f"Failed to load rule file → {dsl_file}: {str(e)}")
        
        if not rules and errors:
            error_msg = "\n".join(errors)
            raise DSLValidationError(error_msg)
        
        return rules
    
    def _load_rule_from_path(self, file_path: Path, source_type: str) -> DSLRule:
        """
        Load and parse a DSL rule from a specific file path
        
        Args:
            file_path: Full path to the DSL file
            source_type: Type of rule ("global", "program-specific", "local")
            
        Returns:
            DSLRule: Parsed rule object
            
        Raises:
            DSLValidationError: If file content is invalid
        """
        if not file_path.exists():
            raise DSLValidationError(f"DSL file not found → {file_path}")
        
        if not file_path.suffix == '.dsl':
            raise DSLError(f"Invalid DSL filename → {file_path}, must be *.dsl")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                root = yaml.load(f, Loader=yaml.Loader)
        except Exception as e:
            raise DSLValidationError(f"YAML parsing error → {file_path}: {str(e)}")
        
        # Validate required sections exist
        required_sections = ['rule', 'variables', 'conditions', 'requirements', 
                           'compliant_logic', 'violation_examples']
        missing = [req for req in required_sections if req not in root]
        if missing:
            raise DSLValidationError(f"Missing required DSL sections → {file_path}: {missing}")
        
        # Parse variables
        variables = []
        for var_data in root['variables']:
            if not isinstance(var_data, dict):
                raise DSLValidationError(f"Invalid variable data → {file_path}: {var_data}")
            variables.append(self._parse_variable(var_data, str(file_path)))
        
        # Parse conditions
        conditions = []
        for name, cond_data in root['conditions'].items():
            if not isinstance(cond_data, dict):
                raise DSLValidationError(f"Invalid condition data → {file_path}: {name}")
            conditions.append(self._parse_condition(name, cond_data, str(file_path)))
        
        # Parse requirements
        requirements = []
        for name, req_data in root['requirements'].items():
            if not isinstance(req_data, dict):
                raise DSLValidationError(f"Invalid requirement data → {file_path}: {name}")
            requirements.append(self._parse_requirement(name, req_data, str(file_path)))
        
        # Build rule object
        rule_info = root['rule']
        rule = DSLRule(
            name=rule_info['name'],
            description=rule_info.get('description', ''),
            variables=variables,
            conditions=conditions,
            requirements=requirements,
            compliant_logic=root['compliant_logic'],
            violation_examples=root['violation_examples'],
            source=source_type,
            source_path=str(file_path)
        )
        
        # Validate rule completeness
        self._validate_rule(rule, str(file_path))
        
        return rule
    
    def _apply_rule_precedence(self, all_rules: List[DSLRule]) -> List[DSLRule]:
        """
        Apply rule precedence: local > program-specific > global
        
        Args:
            all_rules: List of all loaded rules
            
        Returns:
            List[DSLRule]: Final rules with precedence applied
        """
        # Group rules by name
        rule_groups = {}
        for rule in all_rules:
            if rule.name not in rule_groups:
                rule_groups[rule.name] = []
            rule_groups[rule.name].append(rule)
        
        final_rules = []
        
        # For each rule name, select the highest precedence version
        for rule_name, rules in rule_groups.items():
            # Sort by precedence: local > program-specific > global
            precedence_order = {"local": 3, "program-specific": 2, "global": 1}
            selected_rule = max(rules, key=lambda r: precedence_order.get(r.source, 0))
            final_rules.append(selected_rule)
        
        return final_rules
    
    def load_lesson_file(self, filepath: str) -> DSLRule:
        """
        Load and parse a lesson file whose path is specified
        
        Args:
            filepath: The full path to the DSL file
            
        Returns:
            DSLRule: Parsed rule object
            
        Raises:
            DSLValidationError: If file content is invalid
        """
        file_path = Path(filepath)
        
        if not file_path.exists():
            raise DSLValidationError(f"DSL file not found → {filepath}")
        
        if not file_path.suffix == '.dsl':
            raise DSLError(f"Invalid DSL filename → {filepath}, must be *.dsl")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                root = yaml.load(f, Loader=yaml.Loader)
        except Exception as e:
            raise DSLValidationError(f"YAML parsing error → {filepath}: {str(e)}")
        
        # Validate required sections exist
        required_sections = ['rule', 'variables', 'conditions', 'requirements', 
                           'compliant_logic']
        
        missing = [req for req in required_sections if req not in root]
        if missing:
            raise DSLValidationError(f"Missing required DSL sections → {filepath}: {missing}")
        
        name = root['rule']['name']
        if 'violation_examples' not in root:
            # Add empty violation_examples if not present
            root['violation_examples'] = dict()
        
        # Parse variables
        variables = []
        for var in root['variables']:
            variables.append(self._parse_variable(var, filepath))
        
        # Parse conditions
        conditions = []
        for name, cond in root['conditions'].items():
            conditions.append(self._parse_condition(name, cond, filepath))
        
        # Parse requirements
        requirements = []
        for name, req in root['requirements'].items():
            requirements.append(self._parse_requirement(name, req, filepath))
        
        # Build rule object
        rule = DSLRule(
            name=root['rule']['name'],
            description=root['rule'].get('description', ''),
            variables=variables,
            conditions=conditions,
            requirements=requirements,
            compliant_logic=root['compliant_logic'],
            violation_examples=root['violation_examples']
        )
        
        # Validate rule completeness
        self._validate_rule(rule, filepath)
        
        return rule


def main():
    """CLI interface for DSL parser"""
    import argparse
    
    parser = argparse.ArgumentParser(description='DSL Parser CLI')
    parser.add_argument('--validate-all', action='store_true', help='Validate all DSL files')
    parser.add_argument('--validate-file', type=str, help='Validate a specific DSL file')
    parser.add_argument('--rules-dir', type=str, default='rules', help='Rules directory path')
    
    args = parser.parse_args()
    
    dsl_parser = DSLParser(rules_dir=args.rules_dir)
    
    try:
        if args.validate_all:
            print("🔍 Validating all DSL files →")
            
            try:
                rules = dsl_parser.load_all_rules()
                violations_count = sum(len(rule.requirements) for rule in rules)
                print(f"✅ DSL validation passed! Loaded {len(rules)} rules.")
                
                for rule in rules:
                    print(f"📋 Loaded rule: {rule.name} ({len(rule.variables)} variables, {len(rule.requirements)} violations)")
                
                print(f"📊 Total violations defined: {violations_count}")
                
            except DSLError as e:
                print(f"❌ DSL validation failed: {str(e)}")
                exit(1)
                
        elif args.validate_file:
            print(f"🔍 Validating DSL file: {args.validate_file}")
            
            try:
                rule = dsl_parser.load_lesson_file(args.validate_file)
                print(f"✅ DSL validation passed! Loaded rule: {rule.name}")
                print(f"📋 Variables: {len(rule.variables)}")
                print(f"📋 Conditions: {len(rule.conditions)}")
                print(f"📋 Requirements: {len(rule.requirements)}")
                
                for var in rule.variables:
                    print(f"   Variable: {var.name} (type={var.type}, pic={var.pic})")
                
                for req in rule.requirements:
                    print(f"   Requirement: {req.name} (severity={req.severity})")
                
                print(f"📋 Complaint logic scenarios: {len(rule.compliant_logic)}")
                
            except DSLError as e:
                print(f"❌ DSL validation failed: {str(e)}")
                exit(1)
                
        else:
            print("Usage: python dsl_parser.py --validate-all | --validate-file <path>")
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        exit(1)


if __name__ == '__main__':
    main()
