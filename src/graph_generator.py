#!/usr/bin/env python3
"""
Fixed Graph Generator Module for Stacktalk
Handles graph operations, COBOL parsing, and violation detection
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

# Setup logging
logger = logging.getLogger(__name__)

from dsl_parser import DSLRule, DSLVariable, DSLRequirement
from neo4j_adapter import Neo4jAdapter


@dataclass
class GraphNode:
    """Represents a node in the graph"""
    id: str
    type: str
    name: str
    description: str = ""
    parent_rule: Optional[str] = None
    data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}


@dataclass
class GraphEdge:
    """Represents an edge in the graph"""
    from_node: str
    to_node: str
    type: str
    description: str = ""


@dataclass
class Violation:
    """Represents a policy violation"""
    rule_name: str
    element_name: str
    violation_message: str
    severity: str
    element_type: str


class GraphGenerator:
    """
    Advanced graph generator for DSL rules and COBOL code analysis
    Implements comprehensive code-to-rule mapping and violation detection
    """
    
    def __init__(self):
        """Initialize the graph generator"""
        self.graph = {
            "type": "graph",
            "version": "1.1",
            "nodes": [],
            "edges": [],
            "metadata": {
                "generated_by": "Stacktalk Graph Generator",
                "rules_count": 0,
                "cobol_programs_count": 0,
                "total_violations": 0
            }
        }
        self._node_counter = 0
        self._rule_index = {}  # Maps rule names to node IDs
        
        # Initialize Neo4j adapter
        self.neo4j_adapter = Neo4jAdapter()
        self.neo4j_available = self.neo4j_adapter.is_available()
    
    def add_dsl_rule(self, rule: DSLRule) -> None:
        """
        Add DSL rule to the graph
        
        Args:
            rule: DSL rule to add
        """
        rule_node = {
            "id": f"rule_{rule.name.lower().replace(' ', '_')}",
            "type": "dsl_rule",
            "name": rule.name,
            "description": rule.description,
            "data": {
                "source": rule.source,
                "source_path": rule.source_path,
                "variables_count": len(rule.variables),
                "requirements_count": len(rule.requirements)
            }
        }
        self.graph["nodes"].append(rule_node)
        self._rule_index[rule.name] = rule_node["id"]
        
        # Add variable nodes
        for var in rule.variables:
            var_node = {
                "id": f"dsl_var_{var.name.lower().replace(' ', '_')}_{rule.name.lower()}",
                "type": "dsl_variable",
                "name": var.name,
                "description": f"DSL variable: {var.name}",
                "data": {
                    "rule_name": rule.name,
                    "data_type": var.type,
                    "description": var.description
                }
            }
            self.graph["nodes"].append(var_node)
            
            # Add edge from rule to variable
            edge = {
                "from": rule_node["id"],
                "to": var_node["id"],
                "type": "HAS_VARIABLE",
                "description": f"Rule {rule.name} has variable {var.name}"
            }
            self.graph["edges"].append(edge)

        # Add requirement nodes
        for req in rule.requirements:
            req_node = {
                "id": f"dsl_req_{req.name.lower().replace(' ', '_')}_{rule.name.lower()}",
                "type": "dsl_requirement",
                "name": req.name,
                "description": f"DSL requirement: {req.name}",
                "data": {
                    "rule_name": rule.name,
                    "check": req.check,
                    "description": req.description
                }
            }
            self.graph["nodes"].append(req_node)
            
            # Add edge from rule to requirement
            edge = {
                "from": rule_node["id"],
                "to": req_node["id"],
                "type": "HAS_REQUIREMENT",
                "description": f"Rule {rule.name} has requirement {req.name}"
            }
            self.graph["edges"].append(edge)
        
        self.graph["metadata"]["rules_count"] += 1
    
    def generate_cobol_nodes_from_cst(self, cst_analysis: Dict[str, Any], program_name: str) -> List[Dict[str, Any]]:
        """
        Generate graph nodes from CST analysis results
        
        Args:
            cst_analysis: Comprehensive COBOL analysis from CST parser
            program_name: Name of the COBOL program
            
        Returns:
            List of generated COBOL nodes
        """
        nodes = []
        
        # Create program node
        program_node = {
            "id": f"program_{program_name.lower().replace('-', '_')}",
            "type": "cobol_program",
            "name": program_name,
            "description": f"COBOL program: {program_name}",
            "source_file": program_name + ".cob",
            "data": {
                "program_info": cst_analysis.get('program_info', {}),
                "parsing_method": "cst"
            }
        }
        nodes.append(program_node)
        
        # Add variable nodes from CST analysis
        for var in cst_analysis.get('variables', []):
            var_node = {
                "id": f"var_{var.name.lower().replace('-', '_')}_{program_name.lower()}",
                "type": "cobol_variable",
                "name": var.name,
                "description": f"COBOL variable: {var.name}",
                "source_file": program_name + ".cob",
                "data": {
                    "level": var.level,
                    "value": var.value,
                    "parent": var.parent,
                    "children": var.children or [],
                    "parsing_method": "cst"
                }
            }
            nodes.append(var_node)
        
        # Add procedure nodes from CST analysis
        for proc in cst_analysis.get('procedures', []):
            proc_node = {
                "id": f"proc_{proc['name'].lower().replace('-', '_')}_{program_name.lower()}",
                "type": "cobol_procedure",
                "name": proc['name'],
                "description": f"COBOL procedure: {proc['name']}",
                "source_file": program_name + ".cob",
                "data": {
                    "type": proc.get('type', 'procedure'),
                    "statements_count": len(proc.get('statements', [])),
                    "parsing_method": "cst"
                }
            }
            nodes.append(proc_node)
            
            # Add individual statement nodes
            for i, stmt in enumerate(proc.get('statements', [])):
                stmt_node = {
                    "id": f"stmt_{proc['name'].lower().replace('-', '_')}_{i}_{program_name.lower()}",
                    "type": "cobol_statement",
                    "name": f"{proc['name']}-{stmt.get('type', 'UNKNOWN')}-{i}",
                    "description": f"COBOL statement: {stmt.get('type', 'UNKNOWN')}",
                    "source_file": program_name + ".cob",
                    "data": {
                        "statement_type": stmt.get('type', 'UNKNOWN'),
                        "content": stmt.get('content', ''),
                        "parent_procedure": proc['name'],
                        "statement_index": i,
                        "parsing_method": "cst"
                    }
                }
                nodes.append(stmt_node)
        
        # Add division nodes from CST analysis
        for div in cst_analysis.get('divisions', []):
            div_node = {
                "id": f"div_{div['name'].lower().replace('-', '_')}_{program_name.lower()}",
                "type": "cobol_division",
                "name": div['name'],
                "description": f"COBOL division: {div['name']}",
                "source_file": program_name + ".cob",
                "data": {
                    "type": "division",
                    "line_number": div.get('line_number'),
                    "sections_count": len(div.get('sections', [])),
                    "parsing_method": "cst"
                }
            }
            nodes.append(div_node)
            
            # Add section nodes within divisions
            for sec in div.get('sections', []):
                sec_node = {
                    "id": f"sec_{sec['name'].lower().replace('-', '_')}_{program_name.lower()}",
                    "type": "cobol_section",
                    "name": sec['name'],
                    "description": f"COBOL section: {sec['name']}",
                    "source_file": program_name + ".cob",
                    "data": {
                        "type": "section",
                        "parent_division": div['name'],
                        "line_number": sec.get('line_number'),
                        "parsing_method": "cst"
                    }
                }
                nodes.append(sec_node)
        
        return nodes
    
    def connect_cobol_to_rules(self, cobol_nodes: List[Dict[str, Any]]) -> None:
        """
        Connect COBOL nodes to applicable DSL rules
        
        Args:
            cobol_nodes: List of COBOL nodes to connect
        """
        for node in cobol_nodes:
            self.graph["nodes"].append(node)
            
            # Connect variables to DSL rules
            if node["type"] == "cobol_variable":
                self._connect_variable_to_rules(node)
            
            # Connect procedures to DSL rules
            elif node["type"] == "cobol_procedure":
                self._connect_procedure_to_rules(node)
        
        self.graph["metadata"]["cobol_programs_count"] += 1
    
    def _connect_variable_to_rules(self, var_node: Dict[str, Any]) -> None:
        """Connect COBOL variable to applicable DSL rules"""
        var_name = var_node["name"]
        
        # Find matching DSL variables
        for dsl_node in self.graph["nodes"]:
            if dsl_node["type"] == "dsl_variable":
                dsl_var_name = dsl_node["name"]
                if self._variables_match(var_name, dsl_var_name):
                    edge = {
                        "from": var_node["id"],
                        "to": dsl_node["id"],
                        "type": "MATCHES_DSL_VARIABLE",
                        "description": f"COBOL variable {var_name} matches DSL variable {dsl_var_name}"
                    }
                    self.graph["edges"].append(edge)
    
    def _connect_procedure_to_rules(self, proc_node: Dict[str, Any]) -> None:
        """Connect COBOL procedure to applicable DSL rules"""
        proc_name = proc_node["name"]
        
        # Find matching DSL requirements
        for dsl_node in self.graph["nodes"]:
            if dsl_node["type"] == "dsl_requirement":
                req_name = dsl_node["name"]
                if self._procedure_matches_requirement(proc_name, req_name):
                    edge = {
                        "from": proc_node["id"],
                        "to": dsl_node["id"],
                        "type": "IMPLEMENTS_REQUIREMENT",
                        "description": f"COBOL procedure {proc_name} implements requirement {req_name}"
                    }
                    self.graph["edges"].append(edge)
    
    def _variables_match(self, cobol_var: str, dsl_var: str) -> bool:
        """Check if COBOL variable matches DSL variable"""
        cobol_norm = cobol_var.upper().replace('-', '-')
        dsl_norm = dsl_var.upper().replace('-', '-')
        return cobol_norm == dsl_norm or cobol_norm in dsl_norm or dsl_norm in cobol_norm
    
    def _procedure_matches_requirement(self, proc_name: str, req_name: str) -> bool:
        """Check if COBOL procedure matches DSL requirement"""
        proc_norm = proc_name.upper().replace('-', '-')
        req_norm = req_name.upper().replace('-', '-')
        return proc_norm == req_norm or proc_norm in req_norm or req_norm in proc_norm
    
    def add_violation_nodes(self, violations: List[Any]) -> None:
        """
        Add violation nodes to the graph
        
        Args:
            violations: List of Violation objects from RuleDetector
        """
        for i, violation in enumerate(violations):
            violation_id = f"violation_{i+1}_{violation.type}_{violation.requirement}"
            
            # Create violation node
            violation_node = {
                "id": violation_id,
                "type": "violation",
                "name": f"Violation: {violation.requirement}",
                "description": violation.message,
                "data": {
                    "violation_type": violation.type,
                    "severity": violation.severity,
                    "requirement": violation.requirement,
                    "code_element": violation.code_element,
                    "source_file": violation.source_file,
                    "line_number": violation.line_number,
                    "dsl_rule": violation.dsl_rule,
                    "context": violation.context or {}
                }
            }
            
            self.graph["nodes"].append(violation_node)
            
            # Create edge from violation to the DSL rule that was violated
            if violation.dsl_rule:
                rule_id = f"rule_{violation.dsl_rule.lower().replace(' ', '_')}"
                violation_edge = {
                    "from_node": violation_id,
                    "to_node": rule_id,
                    "type": "VIOLATES_RULE",
                    "description": f"Violation violates rule: {violation.dsl_rule}"
                }
                self.graph["edges"].append(violation_edge)
            
            # Create edge from violation to the COBOL element that caused it
            if violation.code_element:
                # Find the COBOL element node
                cobol_element_id = None
                for node in self.graph["nodes"]:
                    if (node["type"] in ["cobol_variable", "cobol_procedure"] and 
                        node["name"] == violation.code_element):
                        cobol_element_id = node["id"]
                        break
                
                if cobol_element_id:
                    element_edge = {
                        "from_node": violation_id,
                        "to_node": cobol_element_id,
                        "type": "VIOLATES_ELEMENT",
                        "description": f"Violation affects element: {violation.code_element}"
                    }
                    self.graph["edges"].append(element_edge)
        
        # Update metadata
        self.graph["metadata"]["total_violations"] = len(violations)
        self.graph["metadata"]["violations_count"] = len(violations)

    def detect_violations(self) -> List[Violation]:
        """
        Detect policy violations in the graph
        
        Returns:
            List of detected violations
        """
        violations = []
        
        # Check for missing DSL variable implementations
        for dsl_var in self.graph["nodes"]:
            if dsl_var["type"] == "dsl_variable":
                var_name = dsl_var["name"]
                rule_name = dsl_var["data"].get("rule_name", "")
                
                # Check if any COBOL variable matches
                has_match = False
                for cobol_var in self.graph["nodes"]:
                    if cobol_var["type"] == "cobol_variable":
                        if self._variables_match(cobol_var["name"], var_name):
                            has_match = True
                            break
                
                if not has_match:
                    violation = Violation(
                        rule_name=rule_name,
                        element_name=var_name,
                        violation_message=f"DSL variable {var_name} not implemented in COBOL code",
                        severity="HIGH",
                        element_type="variable"
                        )
                    violations.append(violation)
        
        # Check for missing DSL requirement implementations
        for dsl_req in self.graph["nodes"]:
            if dsl_req["type"] == "dsl_requirement":
                req_name = dsl_req["name"]
                rule_name = dsl_req["data"].get("rule_name", "")
                
                # Check if any COBOL procedure matches
                has_match = False
                for cobol_proc in self.graph["nodes"]:
                    if cobol_proc["type"] == "cobol_procedure":
                        if self._procedure_matches_requirement(cobol_proc["name"], req_name):
                            has_match = True
                            break
                
                if not has_match:
                    violation = Violation(
                        rule_name=rule_name,
                        element_name=req_name,
                        violation_message=f"DSL requirement {req_name} not implemented in COBOL code",
                        severity="HIGH",
                        element_type="requirement"
                    )
                    violations.append(violation)
        
        self.graph["metadata"]["total_violations"] = len(violations)
        return violations
    
    def save_graph(self, filepath: str) -> bool:
        """
        Save graph to JSON file
        
        Args:
            filepath: Path to save graph
            
        Returns:
            True if save successful, False otherwise
        """
        try:
            output_path = Path(filepath)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.graph, f, indent=2, ensure_ascii=False)
            
            # Also save to Neo4j if available
            if self.neo4j_available:
                self.save_to_neo4j(session_name=f"session_{output_path.stem}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to save graph: {e}")
            return False
    
    def save_to_neo4j(self, session_name: str = "latest") -> bool:
        """
        Save graph to Neo4j database if available
        
        Args:
            session_name: Name for the session
            
        Returns:
            True if save successful, False otherwise
        """
        if not self.neo4j_available:
            logger.warning("Neo4j not available, skipping database save")
            return False
        
        try:
            # Clear existing session data
            self.neo4j_adapter.clear_session(session_name)
            
            # Save entire graph to Neo4j
            success = self.neo4j_adapter.save_graph(self.graph, session_name)
            
            logger.info(f"Graph saved to Neo4j session: {session_name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to save to Neo4j: {e}")
            return False
