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
        
        # Initialize Neo4j adapter
        from neo4j_adapter import Neo4jAdapter
        self.neo4j_adapter = Neo4jAdapter()
        self.neo4j_available = self.neo4j_adapter.is_available()
        self._rule_index = {}  # Maps rule names to node IDs
    
    def create_basic_cobol_elements(self, program_name: str, cobol_content: str) -> List[Dict[str, Any]]:
        """
        Create basic atomic COBOL elements from content when CST parsing is not available
        
        Args:
            program_name: Name of the COBOL program
            cobol_content: Raw COBOL file content
            
        Returns:
            List of basic COBOL element nodes
        """
        nodes = []
        
        # Create program node
        program_node = {
            "id": f"prog_{program_name.lower().replace('-', '_')}",
            "type": "cobol_program",
            "name": program_name,
            "description": f"COBOL program: {program_name}",
            "source_file": program_name + ".cob",
            "data": {
                "program_name": program_name,
                "parsing_method": "basic",
                "file_size": len(cobol_content),
                "line_count": len(cobol_content.split('\n'))
            }
        }
        nodes.append(program_node)
        
        # Extract basic elements from COBOL content
        lines = cobol_content.split('\n')
        
        # Extract divisions
        divisions = []
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if line_clean.endswith('DIVISION.'):
                division_name = line_clean.replace('DIVISION.', '').strip()
                if division_name:
                    division_node = {
                        "id": f"div_{division_name.lower().replace(' ', '_')}_{program_name.lower()}",
                        "type": "cobol_division",
                        "name": division_name,
                        "description": f"COBOL division: {division_name}",
                        "source_file": program_name + ".cob",
                        "data": {
                            "division_name": division_name,
                            "line_number": i + 1,
                            "parsing_method": "basic"
                        }
                    }
                    nodes.append(division_node)
                    divisions.append(division_name)
        
        # Extract sections
        sections = []
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if line_clean.endswith('SECTION.'):
                section_name = line_clean.replace('SECTION.', '').strip()
                if section_name:
                    section_node = {
                        "id": f"sec_{section_name.lower().replace(' ', '_')}_{program_name.lower()}",
                        "type": "cobol_section",
                        "name": section_name,
                        "description": f"COBOL section: {section_name}",
                        "source_file": program_name + ".cob",
                        "data": {
                            "section_name": section_name,
                            "line_number": i + 1,
                            "parsing_method": "basic"
                        }
                    }
                    nodes.append(section_node)
                    sections.append(section_name)
        
        # Extract procedures/paragraphs
        procedures = []
        for i, line in enumerate(lines):
            line_clean = line.strip()
            # Look for procedure/paragraph names (typically start with numbers or are standalone)
            if (line_clean and not line_clean.startswith('*') and 
                not line_clean.endswith('.') and 
                not line_clean.endswith('DIVISION') and
                not line_clean.endswith('SECTION') and
                len(line_clean.split()) == 1 and
                line_clean.isupper()):
                proc_name = line_clean
                if proc_name not in procedures:
                    proc_node = {
                        "id": f"proc_{proc_name.lower().replace('-', '_')}_{program_name.lower()}",
                        "type": "cobol_procedure",
                        "name": proc_name,
                        "description": f"COBOL procedure: {proc_name}",
                        "source_file": program_name + ".cob",
                        "data": {
                            "procedure_name": proc_name,
                            "line_number": i + 1,
                            "parsing_method": "basic"
                        }
                    }
                    nodes.append(proc_node)
                    procedures.append(proc_name)
        
        # Extract variables (basic pattern matching)
        variables = []
        for i, line in enumerate(lines):
            line_clean = line.strip()
            # Look for variable definitions (01, 02, etc.)
            if (line_clean and 
                len(line_clean.split()) >= 2 and
                line_clean.split()[0].isdigit() and
                int(line_clean.split()[0]) <= 49):  # COBOL level numbers
                var_name = line_clean.split()[1]
                if var_name not in variables:
                    var_node = {
                        "id": f"var_{var_name.lower().replace('-', '_')}_{program_name.lower()}",
                        "type": "cobol_variable",
                        "name": var_name,
                        "description": f"COBOL variable: {var_name}",
                        "source_file": program_name + ".cob",
                        "data": {
                            "variable_name": var_name,
                            "level_number": int(line_clean.split()[0]),
                            "line_number": i + 1,
                            "parsing_method": "basic"
                        }
                    }
                    nodes.append(var_node)
                    variables.append(var_name)
        
        return nodes
    
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
        
        # Add atomic variable nodes as cobol_variable nodes from statement blocks
        for atomic_var in cst_analysis.get('atomic_variables', []):
            atomic_var_node = {
                "id": f"var_{atomic_var['name'].lower().replace('-', '_')}_{program_name.lower()}",
                "type": "cobol_variable",
                "name": atomic_var['name'],
                "description": f"COBOL variable: {atomic_var['name']}",
                "source_file": program_name + ".cob",
                "data": {
                    "variable_name": atomic_var['name'],
                    "references_count": len(atomic_var['references']),
                    "parent_procedure": atomic_var['parent_procedure'],
                    "parent_procedure_type": atomic_var['parent_procedure_type'],
                    "references": atomic_var['references'],
                    "parsing_method": "cst_atomic"
                }
            }
            nodes.append(atomic_var_node)
        
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
                    "blocks_count": len(proc.get('statement_blocks', [])),
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
                        "variables_used": stmt.get('variables', []),
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
                
                # Create edge from division to section
                div_sec_edge = {
                    "from": div_node["id"],
                    "to": sec_node["id"],
                    "type": "HAS_SECTION",
                    "description": f"Division {div['name']} contains section {sec['name']}"
                }
                self.graph["edges"].append(div_sec_edge)
        
        # Create edges from program to divisions
        program_id = f"program_{program_name.lower().replace('-', '_')}"
        for div in cst_analysis.get('divisions', []):
            div_id = f"div_{div['name'].lower().replace('-', '_')}_{program_name.lower()}"
            prog_div_edge = {
                "from": program_id,
                "to": div_id,
                "type": "HAS_DIVISION",
                "description": f"Program {program_name} contains division {div['name']}"
            }
            self.graph["edges"].append(prog_div_edge)
        
        # Add statement block nodes from CST analysis
        for block in cst_analysis.get('statement_blocks', []):
            block_node = {
                "id": f"block_{block['name'].lower().replace('-', '_')}_{program_name.lower()}",
                "type": "cobol_statement_block",
                "name": f"{block.get('parent_procedure', 'Unknown')}-{block.get('name', 'Block')}",
                "description": f"COBOL statement block: {block.get('type', 'SEQUENTIAL')}",
                "source_file": program_name + ".cob",
                "data": {
                    "block_type": block.get('type', 'SEQUENTIAL'),
                    "block_name": block.get('name', 'Block'),
                    "statements_count": len(block.get('statements', [])),
                    "start_line": block.get('start_line', 0),
                    "end_line": block.get('end_line', 0),
                    "variables_used": block.get('variables_used', []),
                    "parent_procedure": block.get('parent_procedure', 'Unknown'),
                    "parsing_method": "cst"
                }
            }
            nodes.append(block_node)
        
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
        
        # Connect atomic variables to statement blocks
        self._connect_atomic_variables_to_blocks()
        
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
    
    def _connect_atomic_variables_to_blocks(self) -> None:
        """Connect atomic variables to their statement blocks"""
        # Find all cobol_variable nodes that have atomic parsing data (references)
        atomic_vars = [node for node in self.graph["nodes"] 
                      if node["type"] == "cobol_variable" and 
                      node["data"].get("parsing_method") == "cst_atomic"]
        
        # Find all statement block nodes
        statement_blocks = [node for node in self.graph["nodes"] if node["type"] == "cobol_statement_block"]
        
        for atomic_var in atomic_vars:
            var_name = atomic_var["name"]
            var_references = atomic_var["data"].get("references", [])
            
            for ref in var_references:
                block_name = ref["statement_block_name"]
                
                # Find matching statement block
                for block in statement_blocks:
                    if block["data"].get("block_name") == block_name:
                        edge = {
                            "from": atomic_var["id"],
                            "to": block["id"],
                            "type": "USED_IN_BLOCK",
                            "description": f"Variable {var_name} used in {block_name} ({ref['statement_type']})"
                        }
                        self.graph["edges"].append(edge)
                        break
    
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
                    "from": violation_id,
                    "to": rule_id,
                    "type": "VIOLATES_RULE",
                    "description": f"Violation violates rule: {violation.dsl_rule}"
                }
                self.graph["edges"].append(violation_edge)
            
            # Create edge from violation to the most atomic COBOL element
            cobol_element_id = None
            
            if violation.code_element:
                # Priority order: statement > variable > section > procedure > statement_block > program
                priority_types = [
                    "cobol_statement",
                    "cobol_variable", 
                    "cobol_section",
                    "cobol_procedure",
                    "cobol_statement_block",
                    "cobol_program"
                ]
                
                # Find the most atomic COBOL element that matches
                for node_type in priority_types:
                    for node in self.graph["nodes"]:
                        if (node["type"] == node_type and 
                            node["name"] == violation.code_element):
                            cobol_element_id = node["id"]
                            break
                    if cobol_element_id:
                        break
            
            # If no specific element found, find the most atomic element available
            if not cobol_element_id:
                priority_types = [
                    "cobol_statement",
                    "cobol_variable", 
                    "cobol_section",
                    "cobol_procedure",
                    "cobol_statement_block",
                    "cobol_program"
                ]
                
                for node_type in priority_types:
                    for node in self.graph["nodes"]:
                        if node["type"] == node_type:
                            cobol_element_id = node["id"]
                            break
                    if cobol_element_id:
                        break
            
            if cobol_element_id:
                # Find the target node for description
                target_node = next(node for node in self.graph["nodes"] if node["id"] == cobol_element_id)
                element_edge = {
                    "from": violation_id,
                    "to": cobol_element_id,
                    "type": "VIOLATES_ELEMENT",
                    "description": f"Violation affects {target_node['type']}: {target_node['name']}"
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
