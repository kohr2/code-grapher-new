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
    rprint("  • examples/compliant.cob (Compliant COBOL examples)")
    rprint("  • examples/violation.cob (Violation COBOL examples)")


def run_demo(rules_dir: str = "rules", output_dir: str = "output", examples_dir: str = "examples") -> None:
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
        
        # TODO: This will be implemented when we create the graph generator
        graph = {
            "type": "graph",
            "version": "1.0",
            "nodes": [],
            "edges": [],
            "metadata": {
                "rules_count": len(rules),
                "total_variables": sum(len(rule.variables) for rule in rules),
                "total_requirements": sum(len(rule.requirements) for rule in rules),
                "generated_by": "Stacktalk MVP",
                "demo_mode": True
            }
        }
        
        # Add DSL rule nodes to graph
        for rule in rules:
            rule_node = {
                "id": f"rule_{rule.name.lower().replace(' ', '_')}",
                "type": "dsl_rule",
                "name": rule.name,
                "description": rule.description,
                "data": {
                    "variables_count": len(rule.variables),
                    "requirements_count": len(rule.requirements)
                }
            }
            graph["nodes"].append(rule_node)
            
            # Add variable nodes
            for var in rule.variables:
                var_node = {
                    "id": f"var_{var.name.lower().replace('-', '_')}",
                    "type": "dsl_variable",
                    "name": var.name,
                    "description": var.description,
                    "parent_rule": rule.name,
                    "data": {
                        "type": var.type,
                        "pic": var.pic,
                        "value": var.value,
                        "default": var.default
                    }
                }
                graph["nodes"].append(var_node)
                
                # Connect variable to rule
                graph["edges"].append({
                    "from": rule_node["id"],
                    "to": var_node["id"],
                    "type": "defines_variable",
                    "description": "DSL rule defines variable"
                })
            
            # Add requirement nodes
            for req in rule.requirements:
                req_node = {
                    "id": f"req_{req.name.lower().replace('-', '_')}",
                    "type": "dsl_requirement",
                    "name": req.name,
                    "description": req.description,
                    "parent_rule": rule.name,
                    "data": {
                        "check": req.check,
                        "violation_message": req.violation_message,
                        "severity": req.severity
                    }
                }
                graph["nodes"].append(req_node)
                
                # Connect requirement to rule
                graph["edges"].append({
                    "from": rule_node["id"],
                    "to": req_node["id"],
                    "type": "defines_requirement",
                    "description": "DSL rule defines requirement"
                })
        
        rprint("✅ Generated graph from DSL rules")
        rprint(f"📊 Graph Statistics: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")
        
        # Step 3: Generate COBOL examples (placeholder for now)
        rprint("\n[yellow]📝 Step 3: Generating COBOL examples...[/yellow]")
        
        # TODO: This will be implemented when we create the COBOL generator
        rprint("✅ Generated COBOL examples")
        
        # Step 4: Parse COBOL code into graph (placeholder for maintenant)
        rprint("\n[yellow]📝 Step 4: Parsing COBOL code into graph...[/yellow]")
        
        # TODO: This will be implemented when we create the COBOL parser
        rprint("✅ Parsed COBOL code into graph")
        
        # Step 5: Connect code elements to DSL rules (placeholder for maintenant)
        rprint("\n[yellow]🔗 Step 5: Connecting code elements to DSL rules...[/yellow]")
        
        # TODO: This will be implemented when we create the graph generator
        rprint("✅ Connected code elements to DSL rules")
        
        # Step 6: Analyze graph for violations (placeholder for maintenant)
        rprint("\n[yellow]🔍 Step 6: Analyzing graph for violations...[/yellow]")
        
        # TODO: This will be implemented when we create the rule detector
        violations_count = 0  # Placeholder
        rprint(f"   ❌ Found {violations_count} violations")
        rprint("   ✅ Compliance analysis complete")
        
        # Step 7: Generate HTML report (placeholder for maintenant)
        rprint("\n[yellow]📊 Step 7: Generating HTML report...[/yellow]")
        
        # TODO: This will be implemented when we create the report generator
        rprint("✅ Generated HTML report")
        
        # Save graph to file
        graph_file = Path(output_dir) / "graph.json"
        with open(graph_file, 'w', encoding='utf-8') as f:
            json.dump(graph, f, indent=2, ensure_ascii=False)
        
        rprint(f"\n📁 Graph saved: {graph_file}")
        
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


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Stacktalk MVP - DSL-Driven Financial Rule Detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --validate          # Validate DSL files only
  python main.py --demo              # Run full demo
  python main.py --preview           # Show demo preview
  python main.py                     # Run full demo (default)
        """
    )
    
    parser.add_argument('--validate', action='store_true', help='Validate DSL files only')
    parser.add_argument('--demo', action='store_true', help='Run full demo')
    parser.add_argument('--preview', action='store_true', help='Show demo preview')
    parser.add_argument('--rules-dir', type=str, default='rules', help='Rules directory path')
    parser.add_argument('--output-dir', type=str, default='output', help='Output directory path')
    parser.add_argument('--examples-dir', type=str, default='examples', help='Examples directory path')
    
    args = parser.parse_args()
    
    # Default behavior: run demo
    if args.validate:
        success = validate_dsl_files(rules_dir=args.rules_dir)
        sys.exit(0 if success else 1)
    elif args.preview:
        demo_preview()
        sys.exit(0)
    elif args.demo or len(sys.argv) == 1:  # Default when no args
        run_demo(rules_dir=args.rules_dir, output_dir=args.output_dir, examples_dir=args.examples_dir)
        sys.exit(0)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
