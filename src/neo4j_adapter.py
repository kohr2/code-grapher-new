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
            user=os.getenv('NEO4J_USER', 'neo4j'),
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
        """Create a node in Neo4j"""
        node_type = node_data.get("type", "Unknown")
        node_id = node_data.get("id", "")
        
        # Build properties
        properties = {
            "id": node_id,
            "name": node_data.get("name", ""),
            "description": node_data.get("description", ""),
            "session": session_name
        }
        
        # Add additional data properties
        if "data" in node_data:
            for key, value in node_data["data"].items():
                properties[key] = value
        
        # Create node with appropriate labels
        labels = [node_type.replace("_", "")]  # Clean label names
        if "parent_rule" in node_data:
            labels.append("DSLComponent")
        
        query = f"""
            CREATE (n:{':'.join(labels)} $properties)
            WITH n
            MATCH (s:StacktalkSession {{name: $session_name}})
            CREATE (s)-[:CONTAINS]->(n)
        """
        
        session.run(query, properties=properties, session_name=session_name)
    
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
