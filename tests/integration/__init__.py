"""
Integration Tests for Stacktalk Workflows

These tests verify component interactions and end-to-end workflows:
- Full Workflow: DSL → COBOL → CST → Graph → Violations → Report
- DSL-to-Graph: Rule parsing to graph node creation
- COBOL-to-CST: Code generation to parsing integration
- CST-to-Graph: Parsing results to graph integration
- Graph-to-Violations: Graph analysis to violation detection
- Violations-to-Report: Violation data to HTML report generation
- Neo4j Integration: Full workflow with graph database persistence
- Error Handling: Cross-component error handling and fallbacks
- AI Generation: AI-powered COBOL generation workflows
- Multiple Rules: Complex scenarios with multiple DSL rules
"""
