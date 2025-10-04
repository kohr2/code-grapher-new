#!/usr/bin/env python3
"""
Neo4j Adapter for Stacktalk Graph Persistence
Enterprise graph database integration for large-scale deployments
Automatically detects Neo4j availability and falls back to JSON when unavailable
Following TDD approach: will implement comprehensive Neo4j operations
"""

import os
import json
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from pathlib import Path

# Neo4j imports with graceful handling
try:
    from neo4j import GraphDatabase, Driver
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Neo4jConnectionError(Exception):
    """Exception for Neo4j connection issues"""
    pass


class Neo4jOperationError(Exception):
    """Exception for Neo4j operation failures"""
    pass


@dataclass
class Neo4jConfig:
    """Neo4j connection configuration"""
    uri: str
    user: str
    password: str
    database: str = "neo4j"
    
    @classmethod
    def from_env(cls) -> 'Neo4jConfig':
        """Create Neo4j config from environment variables"""
        return cls(
            uri=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
            user=os.getenv('NEO4J_USERNAME', os.getenv('NEO4J_USER', 'neo4j')),
            password=os.getenv('NEO4J_PASSWORD', ''),
            database=os.getenv('NEO4J_DATABASE', 'neo4j')
        )


class Neo4jAdapter:
    """
    Neo4j Graph Database Adapter for Stacktalk
    Provides enterprise-grade graph persistence with automatic fallback
    """
    
    def __init__(self, config: Optional[Neo4jConfig] = None):
        """Initialize Neo4j adapter with configuration"""
        self.config = config or Neo4jConfig.from_env()
        self.driver: Optional[Driver] = None
        self.available = False
        
        # Check Neo4j availability and initialize connection
        self._check_availability()
    
    def _check_availability(self) -> None:
        """Check if Neo4j is available and connection can be established"""
        if not NEO4J_AVAILABLE:
            print("⚠️ Neo4j driver not available - falling back to JSON export")
            return
        
        try:
            self.driver = GraphDatabase.driver(
                self.config.uri,
                auth=(self.config.user, self.config.password)
            )
            
            # Test connection
            with self.driver.session(database=self.config.database) as session:
                result = session.run("RETURN 1 as test")
                result.single()
            
            self.available = True
            print("✅ Neo4j connection established successfully")
            
        except Exception as e:
            print(f"⚠️ Neo4j connection failed: {e}")
            print("   Falling back to JSON export for graph persistence")
            if self.driver:
                self.driver.close()
                self.driver = None
            self.available = False
    
    def is_available(self) -> bool:
        """Check if Neo4j adapter is ready"""
        return self.available and self.driver is not None
    
    def save_graph(self, graph: Dict[str, Any], session_name: str = "default") -> bool:
        """
        Save graph to Neo4j database
        Returns True if successful, False if falls back to other methods
        """
        if not self.is_available():
            return False
        
        try:
            with self.driver.session(database=self.config.database) as session:
                # Clear existing session data
                session.run(f"""
                    MATCH (n:StacktalkSession {{name: $session_name}})
                    DETACH DELETE n
                """, session_name=session_name)
                
                # Create session node
                session.run(f"""
                    CREATE (s:StacktalkSession {{name: $session_name, created_at: datetime()}})
                """, session_name=session_name)
                
                # Process nodes
                for node in graph.get("nodes", []):
                    self._create_node(session, node, session_name)
                
                # Process edges
                for edge in graph.get("edges", []):
                    self._create_edge(session, edge, session_name)
                
                print(f"✅ Graph saved to Neo4j with session: {session_name}")
                return True
                
        except Exception as e:
            print(f"❌ Neo4j save failed: {e}")
            return False
    
    def _create_node(self, session, node_data: Dict[str, Any], session_name: str) -> None:
        """Create a node in Neo4j with proper hierarchical relationships"""
        node_type = node_data.get("type", "Unknown")
        node_id = node_data.get("id", "")
        
        # Build properties
        properties = {
            "id": node_id,
            "name": node_data.get("name", ""),
            "description": node_data.get("description", ""),
            "session": session_name
        }
        
        # Add additional data properties (flatten complex structures)
        if "data" in node_data:
            for key, value in node_data["data"].items():
                # Handle nested dictionaries by converting to JSON string
                if isinstance(value, dict):
                    properties[key] = json.dumps(value)
                # Handle lists by converting to JSON string
                elif isinstance(value, list):
                    properties[key] = json.dumps(value)
                # Handle primitive types directly
                else:
                    properties[key] = value
        
        # Create node with appropriate labels
        labels = [node_type.replace("_", "")]  # Clean label names
        if "parent_rule" in node_data:
            labels.append("DSLComponent")
        
        # Create the node
        query = f"""
            CREATE (n:{':'.join(labels)} $properties)
        """
        session.run(query, properties=properties)
        
        # Create hierarchical relationships based on node type
        self._create_hierarchical_relationships(session, node_data, session_name)
        
        # Only connect cobolprogram nodes to session, others use hierarchical relationships
        if node_type == "cobol_program":
            session.run("""
                MATCH (n {id: $node_id}), (s:StacktalkSession {name: $session_name})
                MERGE (s)-[:CONTAINS]->(n)
            """, node_id=node_id, session_name=session_name)
    
    def _create_hierarchical_relationships(self, session, node_data: Dict[str, Any], session_name: str) -> None:
        """Create proper hierarchical relationships between COBOL elements"""
        node_type = node_data.get("type", "")
        node_id = node_data.get("id", "")
        node_name = node_data.get("name", "")
        data = node_data.get("data", {})
        
        # Connect statements to their parent procedures
        if node_type == "cobol_statement":
            parent_procedure = data.get("parent_procedure")
            if parent_procedure:
                # Find the procedure node and create HAS_STATEMENT relationship
                session.run("""
                    MATCH (proc:cobolprocedure {name: $proc_name, session: $session_name})
                    MATCH (stmt {id: $stmt_id})
                    MERGE (proc)-[:HAS_STATEMENT]->(stmt)
                """, proc_name=parent_procedure, session_name=session_name, stmt_id=node_id)
            
            # Connect variables to statements where they are used
            variables_used = data.get("variables_used", [])
            if variables_used:
                for var_name in variables_used:
                    session.run("""
                        MATCH (stmt {id: $stmt_id})
                        MATCH (var:cobolvariable {name: $var_name, session: $session_name})
                        MERGE (stmt)-[:USES_VARIABLE]->(var)
                    """, stmt_id=node_id, var_name=var_name, session_name=session_name)
        
        # Connect variables to their parent programs and create variable hierarchy
        elif node_type == "cobol_variable":
            # Create variable hierarchy (parent-child relationships)
            parent_name = data.get("parent")
            if parent_name and parent_name.strip() and parent_name != node_data.get("name", ""):
                # Only create relationship if parent exists and is different from child
                session.run("""
                    MATCH (parent:cobolvariable {name: $parent_name, session: $session_name})
                    MATCH (child {id: $child_id})
                    WHERE parent.id <> child.id
                    MERGE (parent)-[:HAS_CHILD_VARIABLE]->(child)
                """, parent_name=parent_name, session_name=session_name, child_id=node_id)
        
        # Connect atomic variables to their statement blocks
        elif node_type == "cobol_atomic_variable":
            # Connect atomic variables to statement blocks where they're used
            references = data.get("references", [])
            for ref in references:
                block_name = ref.get("statement_block_name")
                if block_name:
                    session.run("""
                        MATCH (block:cobolstatementblock {name: $block_name, session: $session_name})
                        MATCH (var {id: $var_id})
                        MERGE (var)-[:USED_IN_BLOCK {statement_type: $stmt_type, line_number: $line_num}]->(block)
                    """, block_name=block_name, session_name=session_name, var_id=node_id, 
                        stmt_type=ref.get("statement_type", ""), line_num=ref.get("line_number", 0))
        
        # Connect procedures to their parent programs
        elif node_type == "cobol_procedure":
            # Find the program node from the same session and create HAS_PROCEDURE relationship
            session.run("""
                MATCH (prog:cobolprogram {session: $session_name})
                MATCH (proc {id: $proc_id})
                MERGE (prog)-[:HAS_PROCEDURE]->(proc)
            """, session_name=session_name, proc_id=node_id)
        
        # Connect statement blocks to their parent procedures
        elif node_type == "cobol_statement_block":
            # Find the procedure node from the same session and create HAS_STATEMENT_BLOCK relationship
            parent_procedure = data.get("parent_procedure")
            if parent_procedure:
                session.run("""
                    MATCH (proc:cobolprocedure {name: $proc_name, session: $session_name})
                    MATCH (block {id: $block_id})
                    MERGE (proc)-[:HAS_STATEMENT_BLOCK]->(block)
                """, proc_name=parent_procedure, session_name=session_name, block_id=node_id)
        
        # Connect sections to their parent divisions
        elif node_type == "cobol_section":
            parent_division = data.get("parent_division")
            if parent_division:
                session.run("""
                    MATCH (div:coboldivision {name: $div_name, session: $session_name})
                    MATCH (sec {id: $sec_id})
                    MERGE (div)-[:HAS_SECTION]->(sec)
                """, div_name=parent_division, session_name=session_name, sec_id=node_id)
        
        # Connect divisions to their parent programs
        elif node_type == "cobol_division":
            session.run("""
                MATCH (prog:cobolprogram {session: $session_name})
                MATCH (div {id: $div_id})
                MERGE (prog)-[:HAS_DIVISION]->(div)
            """, session_name=session_name, div_id=node_id)
    
    def _create_edge(self, session, edge_data: Dict[str, Any], session_name: str) -> None:
        """Create an edge/relationship in Neo4j"""
        from_node = edge_data.get("from", "")
        to_node = edge_data.get("to", "")
        edge_type = edge_data.get("type", "")
        description = edge_data.get("description", "")
        
        query = """
            MATCH (from), (to)
            WHERE from.id = $from_id AND to.id = $to_id
            AND from.session = $session_name AND to.session = $session_name
            CREATE (from)-[r:%s {description: $description}]->(to)
        """ % edge_type.upper().replace(" ", "_")
        
        session.run(query, {
            'from_id': from_node,
            'to_id': to_node,
            'session_name': session_name,
            'description': description
        })
    
    def _build_properties_string(self, properties: Dict[str, Any]) -> str:
        """Build properties string for Cypher query"""
        props = []
        for key, value in properties.items():
            if isinstance(value, str):
                props.append(f"{key}: '{value}'")
            elif isinstance(value, dict):
                # Nested dictionaries need special handling
                nested_props = []
                for nested_key, nested_value in value.items():
                    if isinstance(nested_value, str):
                        nested_props.append(f"{nested_key}: '{nested_value}'")
                    else:
                        nested_props.append(f"{nested_key}: {nested_value}")
                props.append(f"{key}: {{{', '.join(nested_props)}}}")
            else:
                props.append(f"{key}: {value}")
        return "{" + ", ".join(props) + "}"
    
    def query_graph(self, cypher_query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute Cypher query and return results
        Returns empty list if Neo4j unavailable
        """
        if not self.is_available():
            print("⚠️ Neo4j not available for query execution")
            return []
        
        try:
            with self.driver.session(database=self.config.database) as session:
                result = session.run(cypher_query, parameters or {})
                return [dict(record) for record in result]
        except Exception as e:
            print(f"❌ Neo4j query failed: {e}")
            return []
    
    def get_session_graph(self, session_name: str = "default") -> Optional[Dict[str, Any]]:
        """
        Retrieve complete graph for a session
        Returns None if Neo4j unavailable
        """
        if not self.is_available():
            return None
        
        try:
            # Get nodes
            nodes_query = """
                MATCH (n)
                WHERE n.session = $session_name
                RETURN n, labels(n) as labels
            """
            nodes_result = self.query_graph(nodes_query, {"session_name": session_name})
            
            # Get relationships
            edges_query = """
                MATCH (from)-[r]->(to)
                WHERE from.session = $session_name AND to.session = $session_name
                RETURN from, type(r) as relationship_type, to, r
            """
            edges_result = self.query_graph(edges_query, {"session_name": session_name})
            
            # Convert to graph format
            graph_data = {
                "type": "graph",
                "version": "1.0",
                "nodes": [],
                "edges": [],
                "metadata": {
                    "source": "neo4j",
                    "session": session_name,
                    "node_count": len(nodes_result),
                    "edge_count": len(edges_result)
                }
            }
            
            # Process nodes
            for record in nodes_result:
                node_data = dict(record['n'])
                node_data['type'] = record['labels'][0] if record['labels'] else 'Unknown'
                graph_data['nodes'].append(node_data)
            
            # Process edges
            for record in edges_result:
                edge_data = {
                    "from": record['from']['id'],
                    "to": record['to']['id'],
                    "type": record['relationship_type'].lower().replace("_", " "),
                    "description": record.get('r', {}).get('description', '')
                }
                graph_data['edges'].append(edge_data)
            
            return graph_data
            
        except Exception as e:
            print(f"❌ Failed to retrieve graph from Neo4j: {e}")
            return None
    
    def list_sessions(self) -> List[str]:
        """List all available graph sessions"""
        if not self.is_available():
            return []
        
        query = """
            MATCH (s:StacktalkSession)
            RETURN s.name as session_name
            ORDER BY s.created_at DESC
        """
        result = self.query_graph(query)
        return [record['session_name'] for record in result]
    
    def clear_session(self, session_name: str) -> bool:
        """Clear all data for a specific session"""
        if not self.is_available():
            return False
        
        try:
            query = """
                MATCH (n {session: $session_name})
                DETACH DELETE n
            """
            self.query_graph(query, {"session_name": session_name})
            print(f"✅ Cleared Neo4j session: {session_name}")
            return True
        except Exception as e:
            print(f"❌ Failed to clear Neo4j session: {e}")
            return False
    
    def generate_visualization_queries(self, session_name: str = "default") -> Dict[str, str]:
        """
        Generate Cypher queries for Neo4j Browser visualization
        
        Args:
            session_name: Name of the session to visualize
            
        Returns:
            Dictionary of visualization queries
        """
        queries = {
            "overview": f"""
                // Stacktalk Graph Overview - {session_name}
                MATCH (n)
                WHERE n.session = '{session_name}'
                RETURN n, labels(n) as nodeType
                ORDER BY labels(n), n.name
            """,
            
            "dsl_rules": f"""
                // DSL Rules and Components
                MATCH (rule:DSLRule)-[:HAS_VARIABLE]->(var:DSLVariable)
                WHERE rule.session = '{session_name}'
                RETURN rule, var
                ORDER BY rule.name, var.name
            """,
            
            "cobol_programs": f"""
                // COBOL Programs and Structure
                MATCH (prog:COBOLProgram)-[:HAS_VARIABLE]->(var:COBOLVariable)
                WHERE prog.session = '{session_name}'
                RETURN prog, var
                ORDER BY prog.name, var.name
            """,
            
            "violations": f"""
                // Policy Violations and Connections
                MATCH (rule:DSLRule)-[:VIOLATED_BY]->(violation:Violation)-[:IN_PROGRAM]->(prog:COBOLProgram)
                WHERE rule.session = '{session_name}'
                RETURN rule, violation, prog
                ORDER BY violation.severity, rule.name
            """,
            
            "connections": f"""
                // All Connections Between DSL and COBOL
                MATCH (dsl)-[r]-(cobol)
                WHERE dsl.session = '{session_name}' AND cobol.session = '{session_name}'
                AND ('DSLRule' IN labels(dsl) OR 'DSLVariable' IN labels(dsl) OR 'DSLRequirement' IN labels(dsl))
                AND ('COBOLProgram' IN labels(cobol) OR 'COBOLVariable' IN labels(cobol) OR 'COBOLProcedure' IN labels(cobol))
                RETURN dsl, r, cobol
                ORDER BY type(r), dsl.name
            """,
            
            "compliance_summary": f"""
                // Compliance Summary
                MATCH (session:StacktalkSession {{name: '{session_name}'}})
                OPTIONAL MATCH (violation:Violation)-[:IN_SESSION]->(session)
                OPTIONAL MATCH (rule:DSLRule)-[:IN_SESSION]->(session)
                OPTIONAL MATCH (prog:COBOLProgram)-[:IN_SESSION]->(session)
                RETURN 
                    session.name as sessionName,
                    count(DISTINCT rule) as totalRules,
                    count(DISTINCT prog) as totalPrograms,
                    count(DISTINCT violation) as totalViolations,
                    session.created_at as createdAt
            """
        }
        
        return queries
    
    def export_visualization_cypher(self, session_name: str = "default", output_file: Optional[str] = None) -> str:
        """
        Export visualization queries to a Cypher file for Neo4j Browser
        
        Args:
            session_name: Name of the session to export
            output_file: Optional output file path
            
        Returns:
            Path to the exported Cypher file
        """
        if output_file is None:
            from pathlib import Path
            output_file = f"neo4j_visualization_{session_name}.cypher"
        
        queries = self.generate_visualization_queries(session_name)
        
        cypher_content = f"""// Stacktalk Graph Visualization Queries
// Session: {session_name}
// Generated: {self._get_current_timestamp()}
// 
// Instructions:
// 1. Open Neo4j Browser (http://localhost:7474)
// 2. Copy and paste each query below
// 3. Execute queries to explore the graph
//

"""
        
        for query_name, query in queries.items():
            cypher_content += f"""// {query_name.upper().replace('_', ' ')} QUERY
{query.strip()}

"""
        
        # Add styling and layout instructions
        cypher_content += """
// VISUALIZATION STYLING
// Apply these settings in Neo4j Browser for better visualization:

// Node Colors:
// - DSLRule: #FF6B6B (Red)
// - DSLVariable: #4ECDC4 (Teal)  
// - DSLRequirement: #45B7D1 (Blue)
// - COBOLProgram: #96CEB4 (Green)
// - COBOLVariable: #FFEAA7 (Yellow)
// - COBOLProcedure: #DDA0DD (Plum)
// - Violation: #FF7675 (Coral)

// Relationship Colors:
// - HAS_VARIABLE: #74B9FF (Light Blue)
// - IMPLEMENTS_REQUIREMENT: #00B894 (Green)
// - VIOLATED_BY: #E17055 (Orange)
// - CONTAINS: #6C5CE7 (Purple)

// Layout: Use "Force Directed" layout for best results
// Node Size: Set to "Degree" for importance visualization
"""
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(cypher_content)
        
        return output_file
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for file headers"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def close(self) -> None:
        """Close Neo4j driver connection"""
        if self.driver:
            self.driver.close()
            self.driver = None


def create_neoj_adapter() -> Neo4jAdapter:
    """Factory function to create Neo4j adapter"""
    return Neo4jAdapter()


def dummy_adapter() -> Neo4jAdapter:
    """Create a dummy adapter for testing when Neo4j is unavailable"""
    adapter = Neo4jAdapter()
    adapter.available = False  # Force unavailable
    return adapter


def main():
    """CLI interface for Neo4j adapter testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Neo4j Adapter CLI')
    parser.add_argument('--test', action='store_true', help='Test Neo4j connection')
    parser.add_argument('--sessions', action='store_true', help='List available sessions')
    parser.add_argument('--clear-session', help='Clear specific session')
    
    args = parser.parse_args()
    
    adapter = create_neoj_adapter()
    
    if args.test:
        print("🧪 Testing Neo4j connection...")
        if adapter.is_available():
            print("✅ Neo4j adapter ready!")
        else:
            print("❌ Neo4j adapter not available")
    
    elif args.sessions:
        sessions = adapter.list_sessions()
        if sessions:
            print("📋 Available Neo4j sessions:")
            for session in sessions:
                print(f"  - {session}")
        else:
            print("📋 No Neo4j sessions available")
    
    elif args.clear_session:
        if adapter.clear_session(args.clear_session):
            print(f"✅ Session '{args.clear_session}' cleared")
        else:
            print(f"❌ Failed to clear session '{args.clear_session}'")
    
    else:
        parser.print_help()
    
    adapter.close()


if __name__ == '__main__':
    main()
