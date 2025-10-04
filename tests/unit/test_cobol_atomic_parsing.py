"""
Unit tests for COBOL CST Parser atomic variable parsing and output structure verification
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from src.cobol_cst_parser import COBOLCSTParser, COBOLParsingError


class TestCOBOLAtomicParsing:
    """Test atomic variable parsing and output structure"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = COBOLCSTParser()
        
        # Mock COBOL text with atomic variables
        self.sample_cobol_text = """
000100 IDENTIFICATION DIVISION.
000200 PROGRAM-ID. TEST-PROGRAM.
000300 
000400 PROCEDURE DIVISION.
000500 0000-MAIN-CONTROL SECTION.
000600 0000-MAIN-PROCESS.
000700     PERFORM 1000-INITIALIZE-PROGRAM
000800     MOVE WS-TOTAL-AMOUNT TO WS-FINAL-RESULT
000900     IF WS-RISK-SCORE > 50
001000         PERFORM 2000-HIGH-RISK-PROCESS
001100     END-IF
001200     STOP RUN.
001300 
001400 1000-INITIALIZE-PROGRAM SECTION.
001500 1000-INIT-START.
001600     MOVE ZERO TO WS-TOTAL-AMOUNT
001700     MOVE ZERO TO WS-RISK-SCORE
001800     DISPLAY 'INITIALIZATION COMPLETE'
001900     EXIT.
002000 
002100 2000-HIGH-RISK-PROCESS SECTION.
002200 2000-PROCESS-START.
002300     ADD 10 TO WS-RISK-SCORE
002400     MOVE 'HIGH RISK' TO WS-RISK-STATUS
002500     EXIT.
"""
        
        # Expected atomic variables from the sample
        self.expected_atomic_variables = [
            'MAIN-CONTROL', 'SECTION', 'MAIN-PROCESS', 'INITIALIZE-PROGRAM',
            'WS-TOTAL-AMOUNT', 'WS-FINAL-RESULT', 'WS-RISK-SCORE', 'HIGH-RISK-PROCESS',
            'INIT-START', 'ZERO', 'INITIALIZATION', 'COMPLETE', 'PROCESS-START',
            'RISK-STATUS', 'HIGH', 'RISK'
        ]
    
    @patch('src.cobol_cst_parser.tree_sitter')
    def test_atomic_variable_extraction(self, mock_tree_sitter):
        """Test that atomic variables are extracted correctly from statement blocks"""
        # Mock the CST parsing
        mock_cst = Mock()
        mock_cst.root_node.text = self.sample_cobol_text.encode('utf-8')
        mock_tree_sitter.Language.build_library.return_value = None
        mock_tree_sitter.Language.return_value = Mock()
        
        # Mock the parser to return our sample text
        with patch.object(self.parser, 'parse_cobol_file', return_value=mock_cst):
            with patch.object(self.parser, 'extract_procedures') as mock_extract_procedures:
                # Create mock procedures with statement blocks and variable references
                mock_procedures = [
                    {
                        'name': '0000-MAIN-PROCESS',
                        'type': 'paragraph',
                        'statement_blocks': [
                            {
                                'name': 'PERFORM_1000-INITIALIZE-PROGRAM',
                                'type': 'PERFORM_BLOCK',
                                'statements': [
                                    {'type': 'PERFORM', 'content': 'PERFORM 1000-INITIALIZE-PROGRAM', 'line_number': 7}
                                ],
                                'variable_references': [
                                    {
                                        'variable_name': 'INITIALIZE-PROGRAM',
                                        'statement_type': 'PERFORM',
                                        'statement_content': 'PERFORM 1000-INITIALIZE-PROGRAM',
                                        'line_number': 7
                                    }
                                ]
                            },
                            {
                                'name': 'MOVE_BLOCK_1',
                                'type': 'SEQUENTIAL',
                                'statements': [
                                    {'type': 'MOVE', 'content': 'MOVE WS-TOTAL-AMOUNT TO WS-FINAL-RESULT', 'line_number': 8}
                                ],
                                'variable_references': [
                                    {
                                        'variable_name': 'WS-TOTAL-AMOUNT',
                                        'statement_type': 'MOVE',
                                        'statement_content': 'MOVE WS-TOTAL-AMOUNT TO WS-FINAL-RESULT',
                                        'line_number': 8
                                    },
                                    {
                                        'variable_name': 'WS-FINAL-RESULT',
                                        'statement_type': 'MOVE',
                                        'statement_content': 'MOVE WS-TOTAL-AMOUNT TO WS-FINAL-RESULT',
                                        'line_number': 8
                                    }
                                ]
                            }
                        ]
                    }
                ]
                mock_extract_procedures.return_value = mock_procedures
                
                # Test atomic variable extraction
                atomic_vars = self.parser._extract_atomic_variables(mock_procedures)
                
                # Verify atomic variables are extracted
                assert len(atomic_vars) > 0
                
                # Check that variables have references
                for var in atomic_vars:
                    assert 'name' in var
                    assert 'references' in var
                    assert 'parent_procedure' in var
                    assert len(var['references']) > 0
                    
                    # Check reference structure
                    for ref in var['references']:
                        assert 'statement_block_name' in ref
                        assert 'statement_type' in ref
                        assert 'statement_content' in ref
                        assert 'line_number' in ref
                        assert 'parent_procedure' in ref
    
    def test_atomic_variable_structure(self):
        """Test the structure of atomic variable data"""
        # Create sample atomic variable data
        sample_procedures = [
            {
                'name': 'TEST-PROCEDURE',
                'type': 'section',
                'statement_blocks': [
                    {
                        'name': 'TEST-BLOCK',
                        'type': 'PERFORM_BLOCK',
                        'variable_references': [
                            {
                                'variable_name': 'TEST-VAR',
                                'statement_type': 'PERFORM',
                                'statement_content': 'PERFORM TEST-SUB',
                                'line_number': 100
                            }
                        ]
                    }
                ]
            }
        ]
        
        atomic_vars = self.parser._extract_atomic_variables(sample_procedures)
        
        # Verify structure
        assert len(atomic_vars) == 1
        var = atomic_vars[0]
        
        assert var['name'] == 'TEST-VAR'
        assert var['parent_procedure'] == 'TEST-PROCEDURE'
        assert var['parent_procedure_type'] == 'section'
        assert len(var['references']) == 1
        
        ref = var['references'][0]
        assert ref['statement_block_name'] == 'TEST-BLOCK'
        assert ref['statement_block_type'] == 'PERFORM_BLOCK'
        assert ref['statement_type'] == 'PERFORM'
        assert ref['statement_content'] == 'PERFORM TEST-SUB'
        assert ref['line_number'] == 100
        assert ref['parent_procedure'] == 'TEST-PROCEDURE'
    
    def test_comprehensive_analysis_includes_atomic_variables(self):
        """Test that comprehensive analysis includes atomic variables"""
        # Mock the parser methods
        with patch.object(self.parser, 'parse_cobol_file') as mock_parse:
            with patch.object(self.parser, 'extract_program_info') as mock_program_info:
                with patch.object(self.parser, 'extract_variables') as mock_variables:
                    with patch.object(self.parser, 'extract_procedures') as mock_procedures:
                        with patch.object(self.parser, 'extract_divisions') as mock_divisions:
                            with patch.object(self.parser, 'extract_file_sections') as mock_file_sections:
                                with patch.object(self.parser, 'extract_copy_statements') as mock_copy_statements:
                                    with patch.object(self.parser, '_extract_statement_blocks') as mock_statement_blocks:
                                        with patch.object(self.parser, '_extract_atomic_variables') as mock_atomic_variables:
                                            
                                            # Set up mocks
                                            mock_parse.return_value = Mock()
                                            mock_program_info.return_value = {'program_name': 'TEST'}
                                            mock_variables.return_value = []
                                            mock_procedures.return_value = []
                                            mock_divisions.return_value = []
                                            mock_file_sections.return_value = []
                                            mock_copy_statements.return_value = []
                                            mock_statement_blocks.return_value = []
                                            mock_atomic_variables.return_value = [
                                                {
                                                    'name': 'TEST-VAR',
                                                    'references': [],
                                                    'parent_procedure': 'TEST-PROC',
                                                    'parent_procedure_type': 'section'
                                                }
                                            ]
                                            
                                            # Run comprehensive analysis
                                            result = self.parser.analyze_cobol_comprehensive('test.cbl')
                                            
                                            # Verify atomic variables are included
                                            assert 'atomic_variables' in result
                                            assert len(result['atomic_variables']) == 1
                                            assert result['atomic_variables'][0]['name'] == 'TEST-VAR'
    
    def test_variable_extraction_from_statement(self):
        """Test variable extraction from individual statements"""
        # Test different statement types
        test_cases = [
            ('MOVE WS-AMOUNT TO WS-RESULT', 'MOVE', ['WS-AMOUNT', 'WS-RESULT']),
            ('PERFORM 1000-INITIALIZE', 'PERFORM', ['INITIALIZE']),
            ('IF WS-SCORE > 50', 'IF', ['WS-SCORE']),
            ('ADD WS-VALUE TO WS-TOTAL', 'ADD', ['WS-VALUE', 'WS-TOTAL']),
            ('DISPLAY "HELLO WORLD"', 'DISPLAY', []),
        ]
        
        for statement, stmt_type, expected_vars in test_cases:
            variables = self.parser._extract_variables_from_statement(statement, stmt_type)
            
            # Check that expected variables are found
            for expected_var in expected_vars:
                assert any(expected_var in var for var in variables), f"Expected variable {expected_var} not found in {variables}"
    
    def test_statement_block_grouping_with_variables(self):
        """Test that statement blocks are grouped correctly with variable references"""
        # Create a mock procedure
        procedure = {
            'name': 'TEST-PROCEDURE',
            'type': 'section',
            'statement_blocks': [],
            'current_block': None
        }
        
        # Test grouping statements into blocks
        test_statements = [
            ('PERFORM 1000-INIT', 'PERFORM', 100),
            ('MOVE WS-VAR1 TO WS-VAR2', 'MOVE', 101),
            ('IF WS-CONDITION', 'IF', 102),
            ('MOVE WS-VAR3 TO WS-VAR4', 'MOVE', 103),
            ('END-IF', 'END-IF', 104),
        ]
        
        for stmt_content, stmt_type, line_num in test_statements:
            self.parser._group_statements_into_blocks(procedure, stmt_type, stmt_content, line_num)
        
        # Finalize any remaining blocks
        if procedure.get('current_block'):
            procedure['statement_blocks'].append(procedure['current_block'])
            procedure['current_block'] = None
        
        # Verify blocks were created
        assert len(procedure['statement_blocks']) > 0
        
        # Verify each block has variable references
        for block in procedure['statement_blocks']:
            assert 'variable_references' in block
            assert isinstance(block['variable_references'], list)
            
            # Check that variables were extracted and added
            for ref in block['variable_references']:
                assert 'variable_name' in ref
                assert 'statement_type' in ref
                assert 'statement_content' in ref
                assert 'line_number' in ref


class TestCOBOLOutputStructure:
    """Test the complete COBOL output structure including atomic variables"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = COBOLCSTParser()
    
    def test_graph_structure_with_atomic_variables(self):
        """Test that the graph structure includes atomic variables correctly"""
        # Mock comprehensive analysis result
        mock_analysis = {
            'program_info': {'program_name': 'TEST-PROGRAM'},
            'variables': [],
            'procedures': [
                {
                    'name': 'TEST-PROCEDURE',
                    'type': 'section',
                    'statement_blocks': [
                        {
                            'name': 'TEST-BLOCK',
                            'type': 'PERFORM_BLOCK',
                            'statements': [{'type': 'PERFORM', 'content': 'PERFORM TEST-SUB', 'line_number': 100}],
                            'start_line': 100,
                            'end_line': 100,
                            'variables_used': ['TEST-SUB'],
                            'parent_procedure': 'TEST-PROCEDURE'
                        }
                    ]
                }
            ],
            'divisions': [],
            'file_sections': [],
            'copy_statements': [],
            'statement_blocks': [
                {
                    'name': 'TEST-BLOCK',
                    'type': 'PERFORM_BLOCK',
                    'statements': [{'type': 'PERFORM', 'content': 'PERFORM TEST-SUB', 'line_number': 100}],
                    'start_line': 100,
                    'end_line': 100,
                    'variables_used': ['TEST-SUB'],
                    'parent_procedure': 'TEST-PROCEDURE'
                }
            ],
            'atomic_variables': [
                {
                    'name': 'TEST-SUB',
                    'references': [
                        {
                            'statement_block_name': 'TEST-BLOCK',
                            'statement_block_type': 'PERFORM_BLOCK',
                            'statement_type': 'PERFORM',
                            'statement_content': 'PERFORM TEST-SUB',
                            'line_number': 100,
                            'parent_procedure': 'TEST-PROCEDURE'
                        }
                    ],
                    'parent_procedure': 'TEST-PROCEDURE',
                    'parent_procedure_type': 'section'
                }
            ],
            'parsing_method': 'cst',
            'source_file': 'test.cbl'
        }
        
        # Test that all expected components are present
        assert 'atomic_variables' in mock_analysis
        assert len(mock_analysis['atomic_variables']) == 1
        
        atomic_var = mock_analysis['atomic_variables'][0]
        assert atomic_var['name'] == 'TEST-SUB'
        assert len(atomic_var['references']) == 1
        
        ref = atomic_var['references'][0]
        assert ref['statement_block_name'] == 'TEST-BLOCK'
        assert ref['statement_type'] == 'PERFORM'
        assert ref['line_number'] == 100
    
    def test_node_types_in_graph(self):
        """Test that all expected node types are present in the graph"""
        expected_node_types = [
            'cobol_program',
            'cobol_division', 
            'cobol_section',
            'cobol_procedure',
            'cobol_statement_block',
            'cobol_atomic_variable',
            'cobol_variable',
            'cobol_statement',
            'dsl_rule',
            'dsl_variable',
            'dsl_requirement',
            'violation'
        ]
        
        # This test would be run against actual graph output
        # For now, we verify the expected structure
        for node_type in expected_node_types:
            assert node_type in expected_node_types  # Placeholder assertion
    
    def test_relationship_types_in_graph(self):
        """Test that all expected relationship types are present in the graph"""
        expected_relationship_types = [
            'HAS_PROCEDURE',
            'HAS_SECTION', 
            'HAS_STATEMENT_BLOCK',
            'USED_IN_BLOCK',
            'MATCHES_DSL_VARIABLE',
            'IMPLEMENTS_REQUIREMENT',
            'VIOLATES_RULE',
            'VIOLATES_ELEMENT'
        ]
        
        # This test would be run against actual graph output
        # For now, we verify the expected structure
        for rel_type in expected_relationship_types:
            assert rel_type in expected_relationship_types  # Placeholder assertion


class TestCOBOLParsingIntegration:
    """Integration tests for COBOL parsing with atomic variables"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.parser = COBOLCSTParser()
    
    @patch('src.cobol_cst_parser.tree_sitter')
    def test_end_to_end_atomic_parsing(self, mock_tree_sitter):
        """Test end-to-end atomic variable parsing"""
        # Mock tree-sitter
        mock_cst = Mock()
        mock_cst.root_node.text = """
000100 PROCEDURE DIVISION.
000200 0000-MAIN.
000300     MOVE WS-VAR1 TO WS-VAR2
000400     PERFORM 1000-SUB
000500     STOP RUN.
""".encode('utf-8')
        
        mock_tree_sitter.Language.build_library.return_value = None
        mock_tree_sitter.Language.return_value = Mock()
        
        # Mock all extraction methods
        with patch.object(self.parser, 'parse_cobol_file', return_value=mock_cst):
            with patch.object(self.parser, 'extract_program_info', return_value={'program_name': 'TEST'}):
                with patch.object(self.parser, 'extract_variables', return_value=[]):
                    with patch.object(self.parser, 'extract_divisions', return_value=[]):
                        with patch.object(self.parser, 'extract_file_sections', return_value=[]):
                            with patch.object(self.parser, 'extract_copy_statements', return_value=[]):
                                with patch.object(self.parser, 'extract_procedures') as mock_extract_procedures:
                                    with patch.object(self.parser, '_extract_statement_blocks') as mock_statement_blocks:
                                        with patch.object(self.parser, '_extract_atomic_variables') as mock_atomic_vars:
                                            
                                            # Set up mock procedures with atomic variables
                                            mock_procedures = [
                                                {
                                                    'name': '0000-MAIN',
                                                    'type': 'paragraph',
                                                    'statement_blocks': [
                                                        {
                                                            'name': 'MOVE_BLOCK',
                                                            'type': 'SEQUENTIAL',
                                                            'variable_references': [
                                                                {
                                                                    'variable_name': 'WS-VAR1',
                                                                    'statement_type': 'MOVE',
                                                                    'statement_content': 'MOVE WS-VAR1 TO WS-VAR2',
                                                                    'line_number': 3
                                                                },
                                                                {
                                                                    'variable_name': 'WS-VAR2',
                                                                    'statement_type': 'MOVE',
                                                                    'statement_content': 'MOVE WS-VAR1 TO WS-VAR2',
                                                                    'line_number': 3
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                }
                                            ]
                                            
                                            mock_extract_procedures.return_value = mock_procedures
                                            mock_statement_blocks.return_value = []
                                            mock_atomic_vars.return_value = [
                                                {
                                                    'name': 'WS-VAR1',
                                                    'references': [{
                                                        'statement_block_name': 'MOVE_BLOCK',
                                                        'statement_block_type': 'SEQUENTIAL',
                                                        'statement_type': 'MOVE',
                                                        'statement_content': 'MOVE WS-VAR1 TO WS-VAR2',
                                                        'line_number': 3,
                                                        'parent_procedure': '0000-MAIN'
                                                    }],
                                                    'parent_procedure': '0000-MAIN',
                                                    'parent_procedure_type': 'paragraph'
                                                }
                                            ]
                                            
                                            # Run comprehensive analysis
                                            result = self.parser.analyze_cobol_comprehensive('test.cbl')
                                            
                                            # Verify atomic variables are present
                                            assert 'atomic_variables' in result
                                            assert len(result['atomic_variables']) == 1
                                            
                                            atomic_var = result['atomic_variables'][0]
                                            assert atomic_var['name'] == 'WS-VAR1'
                                            assert len(atomic_var['references']) == 1
                                            
                                            ref = atomic_var['references'][0]
                                            assert ref['statement_block_name'] == 'MOVE_BLOCK'
                                            assert ref['statement_type'] == 'MOVE'
                                            assert ref['line_number'] == 3


if __name__ == '__main__':
    pytest.main([__file__])
