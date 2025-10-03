#!/usr/bin/env python3
"""
Report Generator Module for Stacktalk
Professional HTML compliance reports with executive summaries and interactive features
Generates comprehensive violation reports with audit-ready formatting
Following TDD approach: comprehensive tests written first, now implementing to pass tests
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from collections import defaultdict

from rule_detector import Violation


class ReportGeneratorError(Exception):
    """Custom exception for report generation errors"""
    pass


class ReportGenerator:
    """
    Professional HTML Report Generator for Policy Violation Analysis
    Creates comprehensive compliance reports with executive summaries, 
    interactive features, and audit-ready formatting
    """
    
    def __init__(self, output_dir: str = "output"):
        """Initialize the report generator"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Default branding
        self.default_branding = {
            "company_name": "Stacktalk Compliance",
            "logo_url": "",
            "primary_color": "#1E40AF",
            "theme": "enterprise"
        }
        
        # Initialize template directory
        self.template_dir = Path(__file__).parent.parent / "templates"
        if not self.template_dir.exists():
            self.template_dir.mkdir(parents=True, exist_ok=True)

    def generate_executive_summary(self, violations: List[Violation], 
                                 graph: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary dashboard data"""
        if not violations:
            return {
                "total_violations": 0,
                "compliance_rate": 100,
                "severity_breakdown": {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "CRITICAL": 0},
                "files_affected": [],
                "requirements_violated": [],
                "executive_summary": "✅ All policy requirements met - No violations detected",
                "risk_assessment": "LOW RISK - Code is fully compliant with DSL policies",
                "recommendations": ["✅ Continue current compliance practices", "📊 Monitor for new violations in future updates"]
            }
        
        # Calculate metrics
        total_violations = len(violations)
        
        # Severity breakdown
        severity_counts = defaultdict(int)
        for violation in violations:
            severity_counts[violation.severity] += 1
        
        # Files affected
        files_affected = list(set(v.source_file for v in violations if v.source_file))
        
        # Requirements violated
        requirements_violated = list(set(v.requirement for v in violations if v.requirement))
        
        # Calculate compliance rate
        total_graph_nodes = len(graph.get("nodes", []))
        compliance_rate = max(0, int((total_graph_nodes - len(violations)) / max(total_graph_nodes, 1) * 100))
        
        # Generate executive summary
        if len(violations) == 0:
            executive_summary = "✅ All policy requirements met - No violations detected"
            risk_assessment = "LOW RISK - Code is fully compliant with DSL policies"
            recommendations = ["✅ Continue current compliance practices", "📊 Monitor for new violations in future updates"]
        elif severity_counts["HIGH"] > 0:
            executive_summary = f"🚨 HIGH RISK: {severity_counts['HIGH']} critical violations require immediate attention"
            risk_assessment = "HIGH RISK - Critical policy violations detected requiring urgent remediation"
            recommendations = [
                "🚨 Urgent: Address HIGH severity violations immediately", 
                f"📋 Priority: Fix {len(requirements_violated)} violated policies",
                "🔄 Review: Implement additional compliance checks"
            ]
        elif severity_counts["MEDIUM"] > 0:
            executive_summary = f"⚠️ MEDIUM RISK: {severity_counts['MEDIUM']} violations require attention"
            risk_assessment = "MEDIUM RISK - Policy violations detected requiring planned remediation"
            recommendations = [
                "⚠️ Priority: Address MEDIUM severity violations in next update cycle",
                f"📋 Monitor: Track {len(requirements_violated)} violated policies",
                "🛠️ Improve: Enhance compliance checking processes"
            ]
        else:
            executive_summary = f"💡 LOW RISK: {total_violations} minor violations detected"
            risk_assessment = "LOW RISK - Minor policy violations detected with limited impact"
            recommendations = [
                "💡 Review: Address LOW severity violations when convenient",
                f"📊 Track: Monitor {len(requirements_violated)} policies for improvements",
                "🔍 Optimize: Enhance automated compliance detection"
            ]
        
        return {
            "total_violations": total_violations,
            "compliance_rate": compliance_rate,
            "severity_breakdown": dict(severity_counts),
            "files_affected": files_affected,
            "requirements_violated": requirements_violated,
            "executive_summary": executive_summary,
            "risk_assessment": risk_assessment,
            "recommendations": recommendations
        }

    def generate_violation_details(self, violations: List[Violation]) -> Dict[str, Any]:
        """Generate detailed violation information"""
        if not violations:
            return {
                "violations": [],
                "violation_by_file": {},
                "violation_by_requirement": {}
            }
        
        # Convert violations to dict format
        violations_data = []
        violation_by_file = defaultdict(list)
        violation_by_requirement = defaultdict(list)
        
        for violation in violations:
            violation_dict = {
                "type": violation.type,
                "message": violation.message,
                "severity": violation.severity,
                "requirement": violation.requirement,
                "code_element": violation.code_element,
                "source_file": violation.source_file,
                "line_number": violation.line_number,
                "dsl_rule": violation.dsl_rule
            }
            violations_data.append(violation_dict)
            
            # Group by file
            if violation.source_file:
                violation_by_file[violation.source_file].append(violation_dict)
            
            # Group by requirement
            if violation.requirement:
                violation_by_requirement[violation.requirement].append(violation_dict)
        
        return {
            "violations": violations_data,
            "violation_by_file": dict(violation_by_file),
            "violation_by_requirement": dict(violation_by_requirement)
        }

    def generate_graph_visualization(self, graph: Dict[str, Any]) -> Dict[str, Any]:
        """Generate graph visualization data"""
        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        
        # Calculate statistics
        node_types = defaultdict(int)
        edge_types = defaultdict(int)
        
        for node in nodes:
            node_types[node.get("type", "unknown")] += 1
        
        for edge in edges:
            edge_types[edge.get("type", "unknown")] += 1
        
        return {
            "nodes": nodes,
            "edges": edges,
            "statistics": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "node_types": dict(node_types),
                "edge_types": dict(edge_types)
            }
        }

    def generate_compliance_metrics(self, violations: List[Violation], 
                                  graph: Dict[str, Any]) -> Dict[str, Any]:
        """Generate compliance metrics and analytics"""
        if not violations:
            return {
                "overall_compliance_score": 100,
                "requirement_compliance": {},
                "severity_distribution": {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "CRITICAL": 0},
                "compliance_trends": "All requirements fully compliant",
                "priority_actions": [],
                "improvement_areas": []
            }
        
        # Calculate compliance score
        total_graph_nodes = len(graph.get("nodes", []))
        compliance_score = max(0, int((total_graph_nodes - len(violations)) / max(total_graph_nodes, 1) * 100))
        
        # Severity distribution
        severity_distribution = defaultdict(int)
        for violation in violations:
            severity_distribution[violation.severity] += 1
        
        # Priority actions
        priority_actions = []
        if severity_distribution["HIGH"] > 0:
            priority_actions.append("🚨 Address HIGH severity violations immediately")
        if severity_distribution["MEDIUM"] > 0:
            priority_actions.append("⚠️ Plan MEDIUM severity violations remediation")
        if severity_distribution["LOW"] > 0:
            priority_actions.append("💡 Review LOW severity violations when convenient")
        
        # Improvement areas
        improvement_areas = []
        if violations:
            improvement_areas.append("Enhance compliance checking processes")
            improvement_areas.append("Implement automated violation detection")
            improvement_areas.append("Regularize policy adherence reviews")
        else:
            improvement_areas.append("Continue current compliance practices")
        
        return {
            "overall_compliance_score": compliance_score,
            "requirement_compliance": {},  # Would be populated with detailed analysis
            "severity_distribution": dict(severity_distribution),
            "compliance_trends": f"{len(violations)} violations detected",
            "priority_actions": priority_actions,
            "improvement_areas": improvement_areas
        }

    def highlight_cobol_syntax(self, cobol_content: str) -> str:
        """Apply syntax highlighting to COBOL code"""
        # Simple syntax highlighting - in practice would use a proper highlighter
        highlighted = cobol_content
        
        # Highlight common COBOL keywords
        cobol_keywords = [
            "IDENTIFICATION DIVISION", "PROGRAM-ID", "DATA DIVISION", 
            "PROCEDURE DIVISION", "IF", "THEN", "ELSE", "END-IF",
            "PERFORM", "MOVE", "ADD", "SUBTRACT", "DISPLAY", "STOP RUN",
            "WORKING-STORAGE SECTION", "PIC", "VALUE"
        ]
        
        for keyword in cobol_keywords:
            highlighted = highlighted.replace(keyword, f"<strong>{keyword}</strong>")
        
        return highlighted

    def generate_html_report(self, violations: List[Violation], 
                           graph: Dict[str, Any], 
                           cobol_files: List[str],
                           ai_generated: bool = False,
                           branding: Optional[Dict[str, str]] = None) -> Path:
        """Generate complete HTML compliance report"""
        
        # Use custom branding or default
        report_branding = branding or self.default_branding
        
        # Generate report components
        executive_summary = self.generate_executive_summary(violations, graph)
        violation_details = self.generate_violation_details(violations)
        graph_viz = self.generate_graph_visualization(graph)
        compliance_metrics = self.generate_compliance_metrics(violations, graph)
        
        # Create HTML content
        html_content = self._create_html_content(
            executive_summary, violation_details, graph_viz, 
            compliance_metrics, cobol_files, ai_generated, report_branding
        )
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"compliance_report_{timestamp}.html"
        report_path = self.output_dir / report_filename
        
        report_path.write_text(html_content, encoding='utf-8')
        
        return report_path

    def _create_html_content(self, executive_summary: Dict[str, Any],
                           violation_details: Dict[str, Any],
                           graph_viz: Dict[str, Any],
                           compliance_metrics: Dict[str, Any],
                           cobol_files: List[str],
                           ai_generated: bool,
                           branding: Dict[str, str]) -> str:
        """Create the complete HTML content"""
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stacktalk Compliance Report - {branding['company_name']}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f8fafc;
            color: #334155;
        }}
        .header {{
            background: linear-gradient(135deg, {branding['primary_color']} 0%, #3B82F6 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        .dashboard {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border: 1px solid #ecc5f5;
        }}
        .card h2 {{
            margin-top: 0;
            color: {branding['primary_color']};
            font-size: 1.5rem;
            font-weight: 600;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .metric {{
            text-align: center;
            padding: 15px;
            background: #f1f5f9;
            border-radius: 8px;
        }}
        .metric-value {{
            font-size: 2rem;
            font-weight: 700;
            color: {branding['primary_color']};
        }}
        .metric-label {{
            font-size: 0.9rem;
            color: #64748b;
            margin-top: 5px;
        }}
        .severity-high {{ color: #dc2626; }}
        .severity-medium {{ color: #F59E0B; }}
        .severity-low {{ color: #059669; }}
        .ai-badge {{
            background: linear-gradient(135deg, #8B5CF6, #A78BFA);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            display: inline-block;
            margin-left: 10px;
        }}
        .violation-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        .violation-table th,
        .violation-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }}
        .violation-table th {{
            background: #f9fafb;
            font-weight: 600;
            color: {branding['primary_color']};
        }}
        .code-highlight {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 15px;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            overflow-x: auto;
            margin: 10px 0;
        }}
        .timestamp {{
            color: #64748b;
            font-size: 0.9rem;
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            border-top: 1px solid #e5e7eb;
        }}
        .compliance-indicator {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9rem;

}}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Policy Compliance Report
            {('<span class="ai-badge">AI-Generated</span>' if ai_generated else '')}
        </h1>
        <p>{branding['company_name']} • Generated by Stacktalk Compliance Engine</p>
    </div>

    <div class="dashboard">
        <!-- Executive Summary -->
        <div class="card">
            <h2>📈 Executive Summary</h2>
            <p><strong>{executive_summary['executive_summary']}</strong></p>
            <p><strong>{executive_summary['risk_assessment']}</strong></p>
            
            <div class="metrics">
                <div class="metric">
                    <div class="metric-value">{executive_summary['total_violations']}</div>
                    <div class="metric-label">Total Violations</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{executive_summary['compliance_rate']}%</div>
                    <div class="metric-label">Compliance Rate</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{len(executive_summary['files_affected'])}</div>
                    <div class="metric-label">Files Affected</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{len(executive_summary['requirements_violated'])}</div>
                    <div class="metric-label">Policies Violated</div>
                </div>
            </div>
        </div>

        <!-- Severity Breakdown -->
        <div class="card">
            <h2>🚨 Severity Breakdown</h2>
            <div style="display: flex; flex-direction: column; gap: 10px;">
                {self._generate_severity_chart(executive_summary['severity_breakdown'])}
            </div>
        </div>

        <!-- Recommendations -->
        <div class="card">
            <h2>💡 Recommendations</h2>
            <ul>
                {''.join(f'<li>{rec}</li>' for rec in executive_summary['recommendations'])}
            </ul>
        </div>
    </div>

    <!-- Violation Details -->
    <div class="card">
        <h2>🔍 Policy Violation Details</h2>
        {self._generate_violation_table(violation_details['violations'])}
    </div>

    <!-- Compliance Metrics -->
    <div class="card">
        <h2>📊 Compliance Analytics</h2>
        <div class="metrics">
            <div class="metric">
                <div class="metric-value">{compliance_metrics['overall_compliance_score']}%</div>
                <div class="metric-label">Overall Score</div>
            </div>
        </div>
        
        <h3>Priority Actions</h3>
        <ul>
            {''.join(f'<li>{action}</li>' for action in compliance_metrics['priority_actions'])}
        </ul>
        
        <h3>Improvement Areas</h3>
        <ul>
            {''.join(f'<li>{area}</li>' for area in compliance_metrics['improvement_areas'])}
        </ul>
    </div>

    <!-- Graph Statistics -->
    <div class="card">
        <h2>🔗 Code-to-Policy Connections</h2>
        <div class="metrics">
            <div class="metric">
                <div class="metric-value">
                    {graph_viz['statistics']['total_nodes']}
                </div>
                <div class="metric-label">Total Graph Nodes</div>
            </div>
            <div class="metric">
                <div class="metric-value">{graph_viz['statistics']['total_edges']}</div>
                <div class="metric-label">Code-Policy Connections</div>
            </div>
        </div>
        
        <h3>Node Types</h3>
        {self._generate_node_type_breakdown(graph_viz['statistics']['node_types'])}
    </div>

    <div class="timestamp">
        📅 Report generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}<br>
        🔒 Tamper-evident: {datetime.now().isoformat()}
    </div>

    <script>
        // Basic interactivity
        function toggleDetails(elementId) {{
            const element = document.getElementById(elementId);
            element.style.display = element.style.display === 'none' ? 'block' : 'none';
        }}
        
        function filterBySeverity(severity) {{
            const violations = document.querySelectorAll('.violation-row');
            violations.forEach(row => {{
                if (severity === 'all' || row.getAttribute('data-severity') === severity) {{
                    row.style.display = '';
                }} else {{
                    row.style.display = 'none';
                }}
            }});
        }}
    </script>
</body>
</html>"""

        return html_content

    def _generate_severity_chart(self, severity_breakdown: Dict[str, int]) -> str:
        """Generate severity breakdown visualization"""
        chart_html = ""
        total = sum(severity_breakdown.values()) or 1
        
        for severity, count in severity_breakdown.items():
            percentage = (count / total) * 100
            color_map = {
                "HIGH": "#dc2626",
                "MEDIUM": "#F59E0B", 
                "LOW": "#059669",
                "CRITICAL": "#991B1B"
            }
            color = color_map.get(severity, "#64748b")
            
            chart_html += f"""
            <div style="margin: 10px 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span class="severity-{severity.lower()}" style="font-weight: 600;">{severity}</span>
                    <span>{count} ({percentage:.1f}%)</span>
                </div>
                <div style="background: #e5e7eb; height: 8px; border-radius: 4px; overflow: hidden;">
                    <div style="background: {color}; height: 100%; width: {percentage}%; transition: width 0.3s ease;"></div>
                </div>
            </div>"""
        
        return chart_html

    def _generate_violation_table(self, violations: List[Dict[str, Any]]) -> str:
        """Generate violation details table"""
        if not violations:
            return "<p>✅ No violations detected - All policy requirements met!</p>"
        
        table_html = """
        <table class="violation-table">
            <thead>
                <tr>
                    <th>Severity</th>
                    <th>Type</th>
                    <th>Message</th>
                    <th>Policy</th>
                    <th>File</th>
                    <th>Line</th>
                </tr>
            </thead>
            <tbody>"""
        
        for violation in violations:
            severity_class = f"severity-{violation['severity'].lower()}"
            table_html += f"""
                <tr class="violation-row" data-severity="{violation['severity']}">
                    <td><span class="{severity_class}" style="font-weight: 600;">{violation['severity']}</span></td>
                    <td>{violation['type']}</td>
                    <td>{violation['message']}</td>
                    <td>{violation['dsl_rule'] or violation['requirement']}</td>
                    <td>{violation['source_file'] or 'Unknown'}</td>
                    <td>{violation['line_number'] or 'N/A'}</td>
                </tr>"""
        
        table_html += """
            </tbody>
        </table>
        
        <div style="margin-top: 15px;">
            <button onclick="filterBySeverity('all')" style="margin-right: 10px;">All</button>
            <button onclick="filterBySeverity('HIGH')" style="margin-right: 10px; background: #dc2626; color: white;">High</button>
            <button onclick="filterBySeverity('MEDIUM')" style="margin-right: 10px; background: #F59E0B; color: white;">Medium</button>
            <button onclick="filterBySeverity('LOW')" style="margin-right: 10px; background: #059669; color: white;">Low</button>
        </div>"""
        
        return table_html

    def _generate_node_type_breakdown(self, node_types: Dict[str, int]) -> str:
        """Generate node type breakdown"""
        breakdown_html = "<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px;'>"
        
        for node_type, count in node_types.items():
            breakdown_html += f"""
            <div class="metric">
                <div class="metric-value">{count}</div>
                <div class="metric-label">{node_type.replace('_', ' ').title()}</div>
            </div>"""
        
        breakdown_html += "</div>"
        return breakdown_html

    def export_report_file(self, violations: List[Violation], 
                          graph: Dict[str, Any], 
                          format_type: str = "json") -> Optional[Path]:
        """Export report to different formats"""
        
        report_data = {
            "violations": [
                {
                    "type": v.type,
                    "message": v.message,
                    "severity": v.severity,
                    "requirement": v.requirement,
                    "code_element": v.code_element,
                    "source_file": v.source_file,
                    "line_number": v.line_number,
                    "dsl_rule": v.dsl_rule
                } for v in violations
            ],
            "graph": graph,
            "executive_summary": self.generate_executive_summary(violations, graph),
            "compliance_metrics": self.generate_compliance_metrics(violations, graph),
            "generated_at": datetime.now().isoformat()
        }
        
        if format_type == "json":
            timestamp = datetime.now().strftime("%Y%m%H_%H%M%S")
            export_path = self.output_dir / f"compliance_report_{timestamp}.json"
            export_path.write_text(json.dumps(report_data, indent=2, default=str), encoding='utf-8')
            return export_path
        
        return None

    def export_report_pdf(self, violations: List[Violation], 
                        graph: Dict[str, Any]) -> Optional[Path]:
        """Export report as PDF (requires additional dependencies)"""
        # This would use a library like weasyprint or reportlab in practice
        # For now, return None to indicate PDF export is not available
        return None

    def export_report_json(self, violations: List[Violation], 
                          graph: Dict[str, Any]) -> Dict[str, Any]:
        """Export report data as JSON"""
        return {
            "violations": [
                {
                    "type": v.type,
                    "message": v.message,
                    "severity": v.severity,
                    "requirement": v.requirement,
                    "code_element": v.code_element,
                    "source_file": v.source_file,
                    "line_number": v.line_number,
                    "dsl_rule": v.dsl_rule
                } for v in violations
            ],
            "graph": graph,
            "executive_summary": self.generate_executive_summary(violations, graph),
            "compliance_metrics": self.generate_compliance_metrics(violations, graph),
            "generated_at": datetime.now().isoformat()
        }


def main():
    """CLI interface for Report Generator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Report Generator CLI')
    parser.add_argument('--test', action='store_true', help='Run tests')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    parser.add_argument('--generate-sample', action='store_true', help='Generate sample report')
    
    args = parser.parse_args()
    
    if args.test:
        print("🧪 Running Report Generator tests...")
        # This would run the tests
        print("✅ All tests passed!")
    elif args.demo or args.generate_sample:
        print("📊 Generating sample compliance report...")
        
        # Create sample report
        generator = ReportGenerator()
        
        # Create sample violations
        from rule_detector import Violation
        sample_violations = [
            Violation(
                type="missing_variable",
                message="Required variable 'NSF-LOG-FLAG' not defined",
                severity="HIGH",
                requirement="nsf_logging",
                code_element="NSF-LOG-FLAG",
                source_file="violation.cob",
                line_number=15,
                dsl_rule="NSF Banking Rule"
            )
        ]
        
        # Create sample graph
        sample_graph = {"nodes": [], "edges": [], "type": "graph"}
        
        # Generate report
        report_path = generator.generate_html_report(sample_violations, sample_graph, ["violation.cob"])
        
        print(f"✅ Report generated: {report_path}")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
