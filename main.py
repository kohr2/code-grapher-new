#!/usr/bin/env python3
"""
Stacktalk MVP - Main Orchestration Script
DSL-Driven Financial Rule Detection for COBOL Systems
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
# Rich imports commented out for simplicity
# from rich import print as rprint
# from rich.panel import Panel
# from rich.table import Table
# from rich.console import Console

def rprint(text):
    """Simple print function without rich formatting"""
    print(text)

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from dsl_parser import DSLParser, DSLError


def validate_dsl_files(rules_dir: str = "rules") -> bool:
    """
    Validate all DSL files in the rules directory
    
    Args:
        rules_dir: Path to rules directory
        
    Returns:
        bool: True if validation passes, False otherwise
    """
    try:
        parser = DSLParser(rules_dir=rules_dir)
        rules = parser.load_all_rules()
        
        if not rules:
            rprint("[red]❌ No DSL rules found[/red]")
            return False
        
        rprint("[green]✅ DSL validation passed! Stacktalk is ready to use.[/green]")
        
        # Display loaded rules
        rprint("\n📋 DSL Rules Summary:")
        rprint("==========================================")
        for rule in rules:
            description = rule.description[:50] + "..." if len(rule.description) > 50 else rule.description
            rprint(f"Rule: {rule.name} | Variables: {len(rule.variables)} | Requirements: {len(rule.requirements)}")
            rprint(f"Description: {description}")
            rprint("------------------------------------------")
        
        return True
        
    except DSLError as e:
        rprint(f"[red]❌ DSL validation failed: {str(e)}[/red]")
        return False
    except Exception as e:
        rprint(f"[red]❌ Unexpected error during DSL validation: {str(e)}[/red]")
        return False


def demo_preview() -> None:
    """
    Show preview of what the demo will do
    """
    rprint("\n[bold blue]🏦 Stacktalk MVP Preview[/bold blue]")
    rprint("[bold blue]" + "="*50 + "[/bold blue]")
    
    rprint("[yellow]📋 DSL Rules Found:[/yellow]")
    rprint("  • NSF Banking Rule (NSF events must be logged and fee applied)")
    rprint("  • Dual Approval Rule (Payments >$10K require two approvers)")
    
    rprint("\n[yellow]🔄 Demo Workflow:[/yellow]")
    rprint("  1. Parse DSL rules from rules/*.dsl files")
    rprint("  2. Generate graph from DSL rules")
    rprint("  3. Create compliant COBOL examples")
    rprint("  4. Create violation COBOL examples") 
    rprint("  5. Parse COBOL code into graph")
    rprint("  6. Connect code elements to DSL rules")
    rprint("  7. Analyze graph for policy violations")
    rprint("  8. Generate HTML report")
    
    rprint("\n[yellow]📊 Expected Graph Structure:[/yellow]")
    rprint("  • DSL Rule nodes → Variable nodes → Requirement nodes")
    rprint("  • COBOL Program nodes → Variable nodes → Procedure nodes")
    rprint("  • Code variables connected to DSL rule variables")
    rprint("  • Violations linked to specific code elements and rules")
    
    rprint("\n[yellow]📁 Output Files:[/yellow]")
    rprint("  • output/graph.json (Complete graph representation)")
    rprint("  • output/report.html (Audit-ready violation report)")
    rprint("  • programs/test/rules/nsf_rule.dsl (Test DSL rule)")
    rprint("  • programs/test/compliant.cob (Compliant COBOL examples)")
    rprint("  • programs/test/violation.cob (Violation COBOL examples)")


def run_demo(rules_dir: str = "programs/test/rules", output_dir: str = "output", examples_dir: str = "programs/test") -> None:
    """
    Run the complete Stacktalk MVP demo
    
    Args:
        rules_dir: Path to DSL rules directory
        output_dir: Path to output directory
        examples_dir: Path to examples directory
    """
    rprint("\n[bold blue]🏦 Stacktalk MVP: DSL-Driven Financial Rule Detection[/bold blue]")
    rprint("[bold blue]" + "="*60 + "[/bold blue]")
    
    # Create directories
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    Path(examples_dir).mkdir(parents=True, exist_ok=True)
    
    try:
        # Step 1: Parse DSL rules
        rprint("\n[yellow]📋 Step 1: Parsing DSL rules...[/yellow]")
        parser = DSLParser(rules_dir=rules_dir)
        rules = parser.load_all_rules()
        
        if not rules:
            raise DSLError("No DSL rules found")
        
        # Display loaded rules
        for rule in rules:
            rprint(f"✅ Loaded rule: {rule.name} ({len(rule.variables)} variables, {len(rule.requirements)} requirements)")
        
        # Step 2: Generate graph from DSL rules
        rprint("\n[yellow]🔄 Step 2: Generating graph from DSL rules...[/yellow]")
        
        # Import and initialize GraphGenerator
        from graph_generator import GraphGenerator
        graph_gen = GraphGenerator()
        
        # Check Neo4j status
        if graph_gen.neo4j_available:
            rprint("✅ Neo4j graph database: Available")
        else:
            rprint("⚠️ Neo4j graph database: Unavailable (using JSON fallback)")
        
        # Add DSL rules to graph
        for rule in rules:
            graph_gen.add_dsl_rule(rule)
        
        graph = graph_gen.graph
        
        rprint("✅ Generated graph from DSL rules")
        rprint(f"📊 Graph Statistics: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")
        
        # Step 3: Generate COBOL examples
        rprint("\n[yellow]📝 Step 3: Generating COBOL examples...[/yellow]")
        
        # Import and initialize COBOL Generator
        from cobol_generator import COBOLGenerator
        cobol_gen = COBOLGenerator()
        
        # Check AI availability
        if cobol_gen.ai_available:
            rprint("🧠 AI COBOL Generation: Enabled (OpenAI GPT-4)")
        else:
            rprint("🧠 AI COBOL Generation: Disabled (using template mode)")
        
        # Generate COBOL examples for each rule
        generated_files = []
        for rule in rules:
            try:
                compliant_file, violation_file = cobol_gen.save_cobol_examples(rule, examples_dir)
                generated_files.extend([compliant_file, violation_file])
                rprint(f"✅ Generated examples for rule: {rule.name}")
            except Exception as e:
                rprint(f"⚠️ Failed to generate examples for {rule.name}: {e}")
        
        rprint(f"✅ Generated {len(generated_files)} COBOL examples")
        
        # Step 4: Parse COBOL code with Tree-sitter CST
        rprint("\n[yellow]📝 Step 4: Parsing COBOL code with Tree-sitter CST...[/yellow]")
        
        # Import and initialize CST Parser
        from cobol_cst_parser import COBOLCSTParser
        cst_parser = COBOLCSTParser()
        
        if cst_parser.tree_sitter_available:
            rprint("🌳 Tree-sitter CST Parser: Enabled (Comprehensive COBOL parsing)")
        else:
            rprint("🌳 Tree-sitter CST Parser: Disabled (fallback mode)")
        
        # Parse all generated COBOL files
        cobol_analyses = {}
        for cobol_file in generated_files:
            try:
                analysis = cst_parser.analyze_cobol_comprehensive(cobol_file.read_text())
                program_name = cobol_file.stem.upper()
                cobol_analyses[program_name] = analysis
                rprint(f"✅ Parsed {cobol_file.name} with CST analysis")
            except Exception as e:
                rprint(f"⚠️ Failed to parse {cobol_file.name}: {e}")
        
        # Generate CST-based nodes for the graph
        for program_name, analysis in cobol_analyses.items():
            try:
                nodes = graph_gen.generate_cobol_nodes_from_cst(analysis, program_name)
                graph_gen.connect_cobol_to_rules(nodes)
                rprint(f"✅ Connected {program_name} to DSL rules")
            except Exception as e:
                rprint(f"⚠️ Failed to connect {program_name}: {e}")
        
        rprint("✅ Parsed COBOL code with Tree-sitter CST into graph")
        
        # Step 5: Connect code elements to DSL rules (already done above)
        rprint("\n[yellow]🔗 Step 5: Connecting code elements to DSL rules...[/yellow]")
        rprint("✅ Connected code elements to DSL rules")
        
        # Step 6: Analyze graph for violations
        rprint("\n[yellow]🔍 Step 6: Analyzing graph for violations...[/yellow]")
        
        # Import and initialize Rule Detector
        from rule_detector import RuleDetector
        detector = RuleDetector()
        
        violations = detector.detect_violations(graph_gen.graph)
        violations_count = len(violations)
        
        # Add violations as nodes to the graph
        if violations:
            graph_gen.add_violation_nodes(violations)
            rprint(f"✅ Added {len(violations)} violation nodes to graph")
        
        # Group violations by file
        violations_by_file = {}
        for violation in violations:
            source_file = violation.source_file
            if source_file not in violations_by_file:
                violations_by_file[source_file] = []
            violations_by_file[source_file].append(violation)
        
        # Display violations
        for source_file, file_violations in violations_by_file.items():
            if file_violations:
                rprint(f"   ❌ Found {len(file_violations)} violations in {source_file}")
            else:
                rprint(f"   ✅ No violations in {source_file}")
        
        rprint(f"   ✅ Compliance analysis complete")
        
        # Step 7: Generate HTML report
        rprint("\n[yellow]📊 Step 7: Generating HTML report...[/yellow]")
        
        # Import and initialize Report Generator
        from report_generator import ReportGenerator
        report_gen = ReportGenerator()
        
        try:
            cobol_files = [f.name for f in generated_files]
            report_path = report_gen.generate_text_report(violations, graph_gen.graph, cobol_files)
            rprint(f"✅ Generated text report: {report_path}")
        except Exception as e:
            rprint(f"⚠️ Failed to generate report: {e}")
            rprint("✅ Generated text report")
        
        # Save graph to file and Neo4j
        graph_file = Path(output_dir) / "graph.json"
        graph_gen.save_graph(str(graph_file))
        
        rprint(f"\n📁 Graph saved: {graph_file}")
        
        # Show Neo4j export status
        session_name = f"demo_{Path(output_dir).name}"
        neo4j_saved = graph_gen.save_to_neo4j(session_name)
        if neo4j_saved:
            rprint(f"✅ Neo4j session saved: {session_name}")
        else:
            rprint("⚠️ Neo4j export skipped (neo4j unavailable)")
        
        # Display final summary
        rprint("\n[yellow]🎯 Demo Complete![/yellow]")
        rprint(f"📊 Graph Statistics: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")
        rprint(f"🏦 Rules Processed: {len(rules)} DSL rules")
        rprint(f"📁 Output Directory: {output_dir}/")
        rprint(f"📁 Examples Directory: {examples_dir}/")
        
    except DSLError as e:
        rprint(f"[red]❌ DSL error: {str(e)}[/red]")
        sys.exit(1)
    except Exception as e:
        rprint(f"[red]❌ Unexpected error: {str(e)}[/red]")
        sys.exit(1)


def analyze_cobol_file(cobol_file: str, rules_dir: str = "rules", output_dir: str = "output") -> None:
    """
    Analyze a single COBOL file for policy violations
    
    Args:
        cobol_file: Path to COBOL file to analyze
        rules_dir: Path to DSL rules directory
        output_dir: Path to output directory
    """
    rprint(f"\n[bold blue]🔍 Analyzing COBOL File: {cobol_file}[/bold blue]")
    rprint("[bold blue]" + "="*60 + "[/bold blue]")
    
    # Validate COBOL file exists
    cobol_path = Path(cobol_file)
    if not cobol_path.exists():
        rprint(f"[red]❌ COBOL file not found: {cobol_file}[/red]")
        sys.exit(1)
    
    if not cobol_path.suffix.lower() in ['.cbl', '.cob', '.cobol']:
        rprint(f"[yellow]⚠️ Warning: File doesn't have COBOL extension (.cbl, .cob, .cobol)[/yellow]")
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    try:
        # Step 1: Parse DSL rules for this specific program
        rprint("\n[yellow]📋 Step 1: Loading DSL rules...[/yellow]")
        parser = DSLParser(rules_dir=rules_dir)
        rules = parser.load_rules_for_program(cobol_file)
        
        if not rules:
            rprint("[red]❌ No DSL rules found[/red]")
            sys.exit(1)
        
        rprint(f"✅ Loaded {len(rules)} DSL rules")
        for rule in rules:
            rprint(f"   • {rule.name} ({rule.source} from {rule.source_path})")
        
        # Step 2: Initialize graph generator
        rprint("\n[yellow]🔄 Step 2: Initializing graph generator...[/yellow]")
        from graph_generator import GraphGenerator
        graph_gen = GraphGenerator()
        
        # Check Neo4j status
        if graph_gen.neo4j_available:
            rprint("✅ Neo4j graph database: Available")
        else:
            rprint("⚠️ Neo4j graph database: Unavailable (using JSON fallback)")
        
        # Add DSL rules to graph
        for rule in rules:
            graph_gen.add_dsl_rule(rule)
        
        rprint(f"✅ Graph initialized with {len(graph_gen.graph['nodes'])} nodes")
        
        # Step 3: Parse COBOL file with CST parser
        rprint(f"\n[yellow]🌳 Step 3: Parsing COBOL file with Tree-sitter CST...[/yellow]")
        from cobol_cst_parser import COBOLCSTParser
        cst_parser = COBOLCSTParser()
        
        try:
            # Parse the COBOL file
            cst_analysis = cst_parser.analyze_cobol_comprehensive(str(cobol_path))
            rprint("✅ COBOL file parsed successfully with CST parser")
            
            # Extract program name from file or analysis
            program_name = cst_analysis.get('program_info', {}).get('program_name', cobol_path.stem.upper())
            
            # Generate graph nodes from CST analysis
            cobol_nodes = graph_gen.generate_cobol_nodes_from_cst(cst_analysis, program_name)
            rprint(f"✅ Generated {len(cobol_nodes)} COBOL nodes from CST analysis")
            
            # Add COBOL nodes to the graph
            graph_gen.graph["nodes"].extend(cobol_nodes)
            
        except Exception as cst_error:
            rprint(f"[yellow]⚠️ CST parsing failed: {cst_error}[/yellow]")
            rprint("   Falling back to basic file analysis...")
            
            # Fallback: read file content and do basic analysis
            with open(cobol_path, 'r', encoding='utf-8', errors='ignore') as f:
                cobol_content = f.read()
            
            # Create basic atomic elements for the COBOL file
            program_name = cobol_path.stem.upper()
            basic_nodes = graph_gen.create_basic_cobol_elements(program_name, cobol_content)
            graph_gen.graph["nodes"].extend(basic_nodes)
            rprint(f"✅ Created {len(basic_nodes)} basic COBOL elements: {program_name}")
        
        # Step 4: Connect COBOL elements to DSL rules
        rprint("\n[yellow]🔗 Step 4: Connecting COBOL elements to DSL rules...[/yellow]")
        # Get all COBOL nodes from the graph
        cobol_nodes = [node for node in graph_gen.graph["nodes"] if node["type"] in ["cobol_program", "cobol_variable", "cobol_procedure", "cobol_division", "cobol_section"]]
        graph_gen.connect_cobol_to_rules(cobol_nodes)
        rprint(f"✅ Connected {len(cobol_nodes)} COBOL elements to DSL rules")
        
        # Step 5: Detect violations
        rprint("\n[yellow]🔍 Step 5: Detecting policy violations...[/yellow]")
        from rule_detector import RuleDetector
        detector = RuleDetector()
        violations = detector.detect_violations(graph_gen.graph)
        
        # Add violations as nodes to the graph
        if violations:
            graph_gen.add_violation_nodes(violations)
            rprint(f"✅ Added {len(violations)} violation nodes to graph")
        
        if violations:
            rprint(f"❌ Found {len(violations)} policy violations:")
            violations_by_severity = {}
            for violation in violations:
                severity = violation.severity
                if severity not in violations_by_severity:
                    violations_by_severity[severity] = []
                violations_by_severity[severity].append(violation)
            
            for severity, v_list in violations_by_severity.items():
                rprint(f"   {severity.upper()}: {len(v_list)} violations")
                for violation in v_list[:3]:  # Show first 3
                    rprint(f"     • {violation.message}")
                if len(v_list) > 3:
                    rprint(f"     ... and {len(v_list) - 3} more")
        else:
            rprint("✅ No policy violations detected")
        
        # Step 6: Generate text report
        rprint("\n[yellow]📊 Step 6: Generating text report...[/yellow]")
        from report_generator import ReportGenerator
        report_gen = ReportGenerator()
        
        try:
            report_path = report_gen.generate_text_report(violations, graph_gen.graph, [cobol_path.name])
            rprint(f"✅ Generated text report: {report_path}")
        except Exception as e:
            rprint(f"⚠️ Failed to generate report: {e}")
        
        # Step 7: Save analysis results
        rprint("\n[yellow]💾 Step 7: Saving analysis results...[/yellow]")
        
        # Save to JSON for reference
        graph_file = Path(output_dir) / f"{cobol_path.stem}_analysis.json"
        graph_gen.save_graph(str(graph_file))
        rprint(f"✅ Analysis results saved to JSON: {graph_file}")
        
        # Display final summary
        rprint("\n[yellow]🎯 Analysis Complete![/yellow]")
        rprint(f"📊 Graph Statistics: {len(graph_gen.graph['nodes'])} nodes, {len(graph_gen.graph['edges'])} edges")
        rprint(f"📁 COBOL File: {cobol_file}")
        rprint(f"📁 Output Directory: {output_dir}/")
        rprint(f"🏦 DSL Rules: {len(rules)} rules applied")
        
        if violations:
            rprint(f"❌ Violations Found: {len(violations)} policy violations detected")
        else:
            rprint("✅ Compliance Status: No violations detected")
        
    except Exception as e:
        rprint(f"[red]❌ Analysis failed: {str(e)}[/red]")
        sys.exit(1)


def analyze_cobol_file_with_rules(cobol_file: str, rules: List[Any], output_dir: str = "output") -> None:
    """
    Analyze a COBOL file using pre-loaded DSL rules
    
    Args:
        cobol_file: Path to COBOL file to analyze
        rules: List of pre-loaded DSL rules
        output_dir: Path to output directory
    """
    # Validate COBOL file exists
    cobol_path = Path(cobol_file)
    if not cobol_path.exists():
        rprint(f"[red]❌ COBOL file not found: {cobol_file}[/red]")
        return
    
    try:
        # Step 1: Initialize graph generator
        rprint("🔄 Initializing graph generator...")
        from graph_generator import GraphGenerator
        graph_gen = GraphGenerator()
        
        # Add DSL rules to graph
        for rule in rules:
            graph_gen.add_dsl_rule(rule)
        
        rprint(f"✅ Graph initialized with {len(graph_gen.graph['nodes'])} nodes")
        
        # Step 2: Parse COBOL file with CST parser
        rprint("🌳 Parsing COBOL file with Tree-sitter CST...")
        from cobol_cst_parser import COBOLCSTParser
        cst_parser = COBOLCSTParser()
        
        try:
            # Parse the COBOL file
            cst_analysis = cst_parser.analyze_cobol_comprehensive(str(cobol_path))
            rprint("✅ COBOL file parsed successfully with CST parser")
            
            # Extract program name from file or analysis
            program_name = cst_analysis.get('program_info', {}).get('program_name', cobol_path.stem.upper())
            
            # Generate graph nodes from CST analysis
            cobol_nodes = graph_gen.generate_cobol_nodes_from_cst(cst_analysis, program_name)
            rprint(f"✅ Generated {len(cobol_nodes)} COBOL nodes from CST analysis")
            
            # Add COBOL nodes to the graph
            graph_gen.graph["nodes"].extend(cobol_nodes)
            
        except Exception as cst_error:
            rprint(f"[yellow]⚠️ CST parsing failed: {cst_error}[/yellow]")
            rprint("   Falling back to basic file analysis...")
            
            # Fallback: read file content and do basic analysis
            with open(cobol_path, 'r', encoding='utf-8', errors='ignore') as f:
                cobol_content = f.read()
            
            # Create basic nodes for the COBOL file
            program_name = cobol_path.stem.upper()
            graph_gen.graph["nodes"].append({
                "id": f"program_{program_name}",
                "type": "cobol_program",
                "name": program_name,
                "description": f"COBOL Program: {program_name}",
                "data": {
                    "source_file": str(cobol_path),
                    "file_size": len(cobol_content),
                    "line_count": len(cobol_content.split('\n'))
                }
            })
            rprint(f"✅ Created basic program node: {program_name}")
        
        # Step 3: Connect COBOL elements to DSL rules
        rprint("🔗 Connecting COBOL elements to DSL rules...")
        # Get all COBOL nodes from the graph
        cobol_nodes = [node for node in graph_gen.graph["nodes"] if node["type"] in ["cobol_program", "cobol_variable", "cobol_procedure", "cobol_division", "cobol_section"]]
        graph_gen.connect_cobol_to_rules(cobol_nodes)
        rprint(f"✅ Connected {len(cobol_nodes)} COBOL elements to DSL rules")
        
        # Step 4: Detect violations
        rprint("🔍 Detecting policy violations...")
        from rule_detector import RuleDetector
        detector = RuleDetector()
        violations = detector.detect_violations(graph_gen.graph)
        
        # Add violations as nodes to the graph
        if violations:
            graph_gen.add_violation_nodes(violations)
            rprint(f"✅ Added {len(violations)} violation nodes to graph")
        
        if violations:
            rprint(f"❌ Found {len(violations)} policy violations")
        else:
            rprint("✅ No policy violations detected")
        
        # Step 5: Generate text report
        rprint("📊 Generating text report...")
        from report_generator import ReportGenerator
        report_gen = ReportGenerator()
        
        try:
            report_path = report_gen.generate_text_report(violations, graph_gen.graph, [cobol_path.name])
            rprint(f"✅ Generated text report: {report_path}")
        except Exception as e:
            rprint(f"⚠️ Failed to generate report: {e}")
        
        # Step 6: Save analysis results
        rprint("💾 Saving analysis results...")
        graph_file = Path(output_dir) / f"{cobol_path.stem}_analysis.json"
        graph_gen.save_graph(str(graph_file))
        rprint(f"✅ Analysis results saved: {graph_file}")
        
    except Exception as e:
        rprint(f"[red]❌ Analysis failed: {str(e)}[/red]")


def analyze_cobol_directory(cobol_dir: str, rules_dir: str = "rules", output_dir: str = "output") -> None:
    """
    Analyze all COBOL files in a directory
    
    Args:
        cobol_dir: Path to directory containing COBOL files
        rules_dir: Path to DSL rules directory
        output_dir: Path to output directory
    """
    rprint(f"\n[bold blue]📁 Analyzing COBOL Directory: {cobol_dir}[/bold blue]")
    rprint("[bold blue]" + "="*60 + "[/bold blue]")
    
    # Find all COBOL files
    cobol_path = Path(cobol_dir)
    if not cobol_path.exists():
        rprint(f"[red]❌ Directory not found: {cobol_dir}[/red]")
        sys.exit(1)
    
    cobol_extensions = ['.cbl', '.cob', '.cobol']
    cobol_files = []
    
    for ext in cobol_extensions:
        cobol_files.extend(cobol_path.glob(f"*{ext}"))
        cobol_files.extend(cobol_path.glob(f"*{ext.upper()}"))
    
    if not cobol_files:
        rprint(f"[red]❌ No COBOL files found in {cobol_dir}[/red]")
        rprint("   Looking for files with extensions: .cbl, .cob, .cobol")
        sys.exit(1)
    
    rprint(f"📋 Found {len(cobol_files)} COBOL files:")
    for cobol_file in cobol_files:
        rprint(f"   • {cobol_file.name}")
    
    # Create batch output directory
    batch_output = Path(output_dir) / f"batch_{cobol_path.name}"
    batch_output.mkdir(parents=True, exist_ok=True)
    
    # Load DSL rules for this directory
    rprint("\n[yellow]📋 Loading DSL rules for directory...[/yellow]")
    parser = DSLParser(rules_dir=rules_dir)
    rules = parser.load_rules_for_program(cobol_dir)
    
    if not rules:
        rprint("[red]❌ No DSL rules found[/red]")
        sys.exit(1)
    
    rprint(f"✅ Loaded {len(rules)} DSL rules")
    for rule in rules:
        rprint(f"   • {rule.name} ({rule.source} from {rule.source_path})")
    
    all_violations = []
    successful_analyses = 0
    
    # Analyze each file
    for i, cobol_file in enumerate(cobol_files, 1):
        rprint(f"\n[yellow]📄 Analyzing file {i}/{len(cobol_files)}: {cobol_file.name}[/yellow]")
        
        try:
            # Create individual output directory for this file
            file_output = batch_output / cobol_file.stem
            file_output.mkdir(parents=True, exist_ok=True)
            
            # Analyze the file with the already loaded rules
            analyze_cobol_file_with_rules(str(cobol_file), rules, str(file_output))
            successful_analyses += 1
            
            # Collect violations for summary
            # Note: This is a simplified approach - in a full implementation,
            # we'd collect violations from each analysis
            
        except Exception as e:
            rprint(f"[red]❌ Failed to analyze {cobol_file.name}: {e}[/red]")
            continue
    
    # Display batch summary
    rprint(f"\n[yellow]🎯 Batch Analysis Complete![/yellow]")
    rprint(f"📊 Files Processed: {successful_analyses}/{len(cobol_files)}")
    rprint(f"📁 Output Directory: {batch_output}/")
    
    if successful_analyses == 0:
        rprint("[red]❌ No files were successfully analyzed[/red]")
        sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Stacktalk MVP - DSL-Driven Financial Rule Detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --validate                    # Validate DSL files only
  python main.py --demo                        # Run full demo
  python main.py --preview                     # Show demo preview
  python main.py --analyze-file program.cbl    # Analyze single COBOL file
  python main.py --analyze-dir /path/to/cobol  # Analyze all COBOL files in directory
  python main.py                               # Run full demo (default)
        """
    )
    
    parser.add_argument('--validate', action='store_true', help='Validate DSL files only')
    parser.add_argument('--demo', action='store_true', help='Run full demo')
    parser.add_argument('--preview', action='store_true', help='Show demo preview')
    parser.add_argument('--analyze-file', type=str, metavar='COBOL_FILE', help='Analyze single COBOL file')
    parser.add_argument('--analyze-dir', type=str, metavar='COBOL_DIR', help='Analyze all COBOL files in directory')
    parser.add_argument('--rules-dir', type=str, default='programs/test/rules', help='Rules directory path')
    parser.add_argument('--output-dir', type=str, default='output', help='Output directory path')
    parser.add_argument('--examples-dir', type=str, default='programs/test', help='Examples directory path')
    
    args = parser.parse_args()
    
    # Default behavior: run demo
    if args.validate:
        success = validate_dsl_files(rules_dir=args.rules_dir)
        sys.exit(0 if success else 1)
    elif args.preview:
        demo_preview()
        sys.exit(0)
    elif args.analyze_file:
        analyze_cobol_file(args.analyze_file, rules_dir=args.rules_dir, output_dir=args.output_dir)
        sys.exit(0)
    elif args.analyze_dir:
        analyze_cobol_directory(args.analyze_dir, rules_dir=args.rules_dir, output_dir=args.output_dir)
        sys.exit(0)
    elif args.demo or len(sys.argv) == 1:  # Default when no args
        run_demo(rules_dir=args.rules_dir, output_dir=args.output_dir, examples_dir=args.examples_dir)
        sys.exit(0)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
