"""
Type Hints Auto-Fixer for DEDAN 2.0
Automatically adds type hints to all Python files for mypy strict mode compatibility
"""

import ast
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional, Union, Any, Tuple, Callable
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TypeHintsFixer:
    """Automatically adds type hints to Python files"""
    
    def __init__(self, root_directory: str = "/home/kali/mini_business/backend"):
        self.root_directory = Path(root_directory)
        self.common_imports = {
            'Dict': 'typing.Dict',
            'List': 'typing.List',
            'Set': 'typing.Set',
            'Optional': 'typing.Optional',
            'Union': 'typing.Union',
            'Any': 'typing.Any',
            'Tuple': 'typing.Tuple',
            'Callable': 'typing.Callable',
            'AsyncGenerator': 'typing.AsyncGenerator',
            'Generator': 'typing.Generator',
            'Iterator': 'typing.Iterator',
            'Pattern': 'typing.Pattern',
            'Match': 'typing.Match',
            'Type': 'typing.Type',
            'TypeVar': 'typing.TypeVar',
            'Generic': 'typing.Generic',
            'Protocol': 'typing.Protocol',
            'Literal': 'typing.Literal',
            'Final': 'typing.Final',
            'ClassVar': 'typing.ClassVar',
            'cast': 'typing.cast',
            'overload': 'typing.overload',
            'asyncio': 'asyncio',
            'datetime': 'datetime',
            'Decimal': 'decimal.Decimal',
            'UUID': 'uuid.UUID',
            'Path': 'pathlib.Path',
            'Request': 'fastapi.Request',
            'Response': 'fastapi.Response',
            'HTTPException': 'fastapi.HTTPException',
            'Depends': 'fastapi.Depends',
            'BackgroundTasks': 'fastapi.BackgroundTasks',
            'File': 'fastapi.File',
            'Form': 'fastapi.Form',
            'Query': 'fastapi.Query',
            'Path as FastAPIPath': 'fastapi.Path',
            'Body': 'fastapi.Body',
            'Header': 'fastapi.Header',
            'Cookie': 'fastapi.Cookie',
            'UploadFile': 'fastapi.UploadFile',
            'WebSocket': 'fastapi.WebSocket',
            'WebSocketDisconnect': 'fastapi.WebSocketDisconnect'
        }
        
        self.type_mapping = {
            'str': 'str',
            'int': 'int',
            'float': 'float',
            'bool': 'bool',
            'None': 'None',
            'bytes': 'bytes',
            'list': 'List',
            'dict': 'Dict',
            'tuple': 'Tuple',
            'set': 'Set',
            'frozenset': 'Set'
        }
    
    def fix_all_files(self) -> None:
        """Fix type hints in all Python files"""
        python_files = list(self.root_directory.rglob("*.py"))
        
        logger.info(f"Found {len(python_files)} Python files to process")
        
        fixed_files = 0
        total_files = len(python_files)
        
        for file_path in python_files:
            try:
                if self.fix_file_type_hints(file_path):
                    fixed_files += 1
                    logger.info(f"Fixed type hints in: {file_path}")
            except Exception as e:
                logger.error(f"Error fixing {file_path}: {e}")
        
        logger.info(f"Fixed type hints in {fixed_files}/{total_files} files")
    
    def fix_file_type_hints(self, file_path: Path) -> bool:
        """Fix type hints in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Check if file already has type hints
            if self.has_type_hints(tree):
                logger.debug(f"File {file_path} already has type hints")
                return False
            
            # Add type hints
            fixed_content = self.add_type_hints_to_file(content, tree)
            
            # Only write if content changed
            if fixed_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return False
    
    def has_type_hints(self, tree: ast.AST) -> bool:
        """Check if file already has type hints"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.returns:
                    return True
                if any(arg.annotation for arg in node.args.args):
                    return True
            elif isinstance(node, ast.AnnAssign):
                if node.annotation:
                    return True
            elif isinstance(node, ast.Assign):
                if hasattr(node, 'type_comment') and node.type_comment:
                    return True
        
        return False
    
    def add_type_hints_to_file(self, content: str, tree: ast.AST) -> str:
        """Add type hints to file content"""
        lines = content.split('\n')
        new_lines = []
        imports_added = set()
        
        # Add necessary imports at the top
        import_lines = self.generate_import_lines(tree)
        new_lines.extend(import_lines)
        imports_added.update(line.split()[1] for line in import_lines if line.startswith('from'))
        
        # Process each line
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped_line = line.strip()
            
            # Skip comments and docstrings
            if stripped_line.startswith('#') or '"""' in line or "'''" in line:
                new_lines.append(line)
                i += 1
                continue
            
            # Add type hints to function definitions
            if self.is_function_definition(stripped_line):
                fixed_line = self.add_function_type_hints(line, i, lines, imports_added)
                new_lines.append(fixed_line)
            # Add type hints to variable assignments
            elif self.is_variable_assignment(stripped_line):
                fixed_line = self.add_variable_type_hints(line, i, lines, imports_added)
                new_lines.append(fixed_line)
            else:
                new_lines.append(line)
            
            i += 1
        
        # Add missing imports if needed
        final_content = '\n'.join(new_lines)
        final_content = self.add_missing_imports(final_content, imports_added)
        
        return final_content
    
    def generate_import_lines(self, tree: ast.AST) -> List[str]:
        """Generate necessary import lines"""
        imports = set()
        
        # Analyze AST to determine needed types
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Check return types
                if node.returns:
                    imports.update(self.get_type_imports(node.returns))
                
                # Check parameter types
                for arg in node.args.args:
                    if arg.annotation:
                        imports.update(self.get_type_imports(arg.annotation))
            
            elif isinstance(node, ast.AnnAssign):
                if node.annotation:
                    imports.update(self.get_type_imports(node.annotation))
        
        # Generate import lines
        import_lines = []
        if imports:
            import_lines.append("from typing import (")
            import_lines.extend([f"    {imp}" for imp in sorted(imports)])
            import_lines.append(")")
            import_lines.append("")
        
        return import_lines
    
    def get_type_imports(self, annotation: ast.AST) -> Set[str]:
        """Get import names from type annotation"""
        imports = set()
        
        if isinstance(annotation, ast.Name):
            name = annotation.id
            if name in self.common_imports:
                imports.add(name)
        elif isinstance(annotation, ast.Attribute):
            imports.update(self.get_attribute_imports(annotation))
        elif isinstance(annotation, ast.Subscript):
            imports.update(self.get_subscript_imports(annotation))
        elif isinstance(annotation, ast.Constant):
            if isinstance(annotation.value, str):
                imports.add('str')
            elif isinstance(annotation.value, int):
                imports.add('int')
            elif isinstance(annotation.value, float):
                imports.add('float')
            elif isinstance(annotation.value, bool):
                imports.add('bool')
        
        return imports
    
    def get_attribute_imports(self, node: ast.Attribute) -> Set[str]:
        """Get imports from attribute access"""
        imports = set()
        
        if isinstance(node.value, ast.Name):
            base_name = node.value.id
            attr_name = node.attr
            
            # Handle typing module imports
            if base_name in ['List', 'Dict', 'Set', 'Tuple', 'Optional', 'Union']:
                imports.add(base_name)
        
        return imports
    
    def get_subscript_imports(self, node: ast.Subscript) -> Set[str]:
        """Get imports from subscript (generic types)"""
        imports = set()
        
        if isinstance(node.value, ast.Name):
            base_name = node.value.id
            if base_name in ['List', 'Dict', 'Set', 'Tuple', 'Optional', 'Union']:
                imports.add(base_name)
        
        # Check slice types
        if node.slice:
            imports.update(self.get_type_imports(node.slice))
        
        return imports
    
    def is_function_definition(self, line: str) -> bool:
        """Check if line is a function definition"""
        stripped = line.strip()
        return (
            stripped.startswith('def ') or 
            stripped.startswith('async def ') or
            stripped.startswith('async def ')
        )
    
    def is_variable_assignment(self, line: str) -> bool:
        """Check if line is a variable assignment"""
        stripped = line.strip()
        return (
            '=' in stripped and 
            not stripped.startswith('#') and
            not stripped.startswith('def ') and
            not stripped.startswith('async def ') and
            not stripped.startswith('class ') and
            not stripped.startswith('import ') and
            not stripped.startswith('from ')
        )
    
    def add_function_type_hints(
        self, 
        line: str, 
        line_index: int, 
        all_lines: List[str],
        imports_added: Set[str]
    ) -> str:
        """Add type hints to function definition"""
        # Parse function signature
        if 'def ' in line:
            func_match = re.match(r'(async\s+)?def\s+(\w+)\s*\((.*)\)(?:\s*->\s*(.*))?:', line)
        else:
            return line
        
        if not func_match:
            return line
        
        async_part = func_match.group(1) or ''
        func_name = func_match.group(2)
        params_part = func_match.group(3)
        return_type_part = func_match.group(4)
        
        # Parse parameters
        params = self.parse_parameters(params_part)
        
        # Add type hints to parameters
        typed_params = []
        for param in params:
            typed_param = self.add_parameter_type_hint(param, imports_added)
            typed_params.append(typed_param)
        
        # Determine return type
        if not return_type_part:
            return_type_part = self.infer_return_type(func_name, line_index, all_lines, imports_added)
        
        # Reconstruct function signature
        params_str = ', '.join(typed_params)
        if return_type_part:
            return f"{async_part}def {func_name}({params_str}) -> {return_type_part}:"
        else:
            return f"{async_part}def {func_name}({params_str}):"
    
    def parse_parameters(self, params_str: str) -> List[str]:
        """Parse function parameters"""
        params = []
        current_param = ""
        paren_count = 0
        
        for char in params_str:
            if char == ',' and paren_count == 0:
                params.append(current_param.strip())
                current_param = ""
            else:
                if char in '([{':
                    paren_count += 1
                elif char in ')]}':
                    paren_count -= 1
                current_param += char
        
        if current_param.strip():
            params.append(current_param.strip())
        
        return params
    
    def add_parameter_type_hint(
        self, 
        param: str, 
        imports_added: Set[str]
    ) -> str:
        """Add type hint to parameter"""
        param = param.strip()
        
        # Skip if already has type hint
        if ':' in param and not param.startswith('*'):
            return param
        
        # Handle self parameter
        if param == 'self':
            return param
        
        # Handle *args and **kwargs
        if param.startswith('*'):
            if param.startswith('**'):
                return f"**{param[2:]}: Dict[str, Any]"
            else:
                return f"*{param[1:]}: Tuple[Any, ...]"
        
        # Infer type from parameter name
        type_hint = self.infer_parameter_type(param)
        if type_hint:
            imports_added.add(type_hint.split('[')[0])
            return f"{param}: {type_hint}"
        
        return param
    
    def infer_parameter_type(self, param: str) -> Optional[str]:
        """Infer parameter type from name and context"""
        param_lower = param.lower()
        
        # Common parameter name patterns
        if any(keyword in param_lower for keyword in ['id', 'user_id', 'item_id']):
            return 'str'
        elif any(keyword in param_lower for keyword in ['count', 'limit', 'offset', 'size', 'length']):
            return 'int'
        elif any(keyword in param_lower for keyword in ['price', 'amount', 'value', 'quantity']):
            return 'Decimal'
        elif any(keyword in param_lower for keyword in ['active', 'enabled', 'is_', 'has_']):
            return 'bool'
        elif any(keyword in param_lower for keyword in ['data', 'content', 'text', 'name']):
            return 'str'
        elif any(keyword in param_lower for keyword in ['list', 'items', 'array']):
            return 'List[Any]'
        elif any(keyword in param_lower for keyword in ['dict', 'mapping', 'config']):
            return 'Dict[str, Any]'
        elif any(keyword in param_lower for keyword in ['time', 'date', 'created', 'updated']):
            return 'datetime'
        elif any(keyword in param_lower for keyword in ['request', 'req']):
            return 'Request'
        elif any(keyword in param_lower for keyword in ['response', 'res']):
            return 'Response'
        elif any(keyword in param_lower for keyword in ['db', 'conn', 'connection']):
            return 'asyncpg.Connection'
        elif any(keyword in param_lower for keyword in ['session']):
            return 'Dict[str, Any]'
        
        return None
    
    def infer_return_type(
        self, 
        func_name: str, 
        line_index: int, 
        all_lines: List[str],
        imports_added: Set[str]
    ) -> Optional[str]:
        """Infer return type from function name and context"""
        func_name_lower = func_name.lower()
        
        # Common function name patterns
        if func_name_lower.startswith('get_') or func_name_lower.startswith('find_'):
            return 'Optional[Any]'
        elif func_name_lower.startswith('is_') or func_name_lower.startswith('has_'):
            return 'bool'
        elif func_name_lower.startswith('create_') or func_name_lower.startswith('add_'):
            return 'Any'
        elif func_name_lower.startswith('update_') or func_name_lower.startswith('modify_'):
            return 'bool'
        elif func_name_lower.startswith('delete_') or func_name_lower.startswith('remove_'):
            return 'bool'
        elif func_name_lower.startswith('list_') or func_name_lower.endswith('_list'):
            return 'List[Any]'
        elif func_name_lower.startswith('count_'):
            return 'int'
        elif func_name_lower.startswith('calculate_'):
            return 'Decimal'
        elif func_name_lower.endswith('_async'):
            return 'Coroutine[Any, Any, Any]'
        
        # Look at return statements in function
        return_types = self.analyze_return_statements(line_index, all_lines)
        if return_types:
            return self.combine_return_types(return_types, imports_added)
        
        return None
    
    def analyze_return_statements(
        self, 
        start_line: int, 
        all_lines: List[str]
    ) -> List[str]:
        """Analyze return statements to infer return types"""
        return_types = []
        i = start_line + 1
        
        # Look for return statements in the function
        while i < len(all_lines):
            line = all_lines[i].strip()
            
            # Stop at next function or class
            if line.startswith('def ') or line.startswith('async def ') or line.startswith('class '):
                break
            
            if line.startswith('return '):
                return_value = line[7:].strip()
                if return_value:
                    inferred_type = self.infer_value_type(return_value)
                    if inferred_type:
                        return_types.append(inferred_type)
            
            i += 1
        
        return return_types
    
    def infer_value_type(self, value: str) -> Optional[str]:
        """Infer type from return value"""
        value_lower = value.lower()
        
        # Literal values
        if value_lower in ['true', 'false']:
            return 'bool'
        elif value_lower.startswith('"') or value_lower.startswith("'"):
            return 'str'
        elif value_lower.isdigit():
            return 'int'
        elif '.' in value_lower and value_lower.replace('.', '').isdigit():
            return 'float'
        
        # Common patterns
        if '[]' in value_lower:
            return 'List[Any]'
        elif '{}' in value_lower:
            return 'Dict[str, Any]'
        elif 'none' in value_lower:
            return 'None'
        
        return None
    
    def combine_return_types(
        self, 
        return_types: List[str], 
        imports_added: Set[str]
    ) -> str:
        """Combine multiple return types"""
        unique_types = list(set(return_types))
        
        if len(unique_types) == 1:
            return unique_types[0]
        elif len(unique_types) == 2 and 'None' in unique_types:
            other_type = [t for t in unique_types if t != 'None'][0]
            imports_added.add('Optional')
            return f'Optional[{other_type}]'
        elif len(unique_types) > 1:
            imports_added.add('Union')
            return f'Union[{", ".join(unique_types)}]'
        
        return 'Any'
    
    def add_variable_type_hints(
        self, 
        line: str, 
        line_index: int, 
        all_lines: List[str],
        imports_added: Set[str]
    ) -> str:
        """Add type hints to variable assignment"""
        # Skip if already has type hint
        if ':' in line and not line.lstrip().startswith('#'):
            return line
        
        # Parse assignment
        parts = line.split('=', 1)
        if len(parts) != 2:
            return line
        
        var_name = parts[0].strip()
        var_value = parts[1].strip()
        
        # Skip complex assignments
        if '(' in var_name or '[' in var_name:
            return line
        
        # Infer type
        type_hint = self.infer_variable_type(var_name, var_value, imports_added)
        
        if type_hint:
            return f"{var_name}: {type_hint} = {var_value}"
        
        return line
    
    def infer_variable_type(
        self, 
        var_name: str, 
        var_value: str, 
        imports_added: Set[str]
    ) -> Optional[str]:
        """Infer variable type from name and value"""
        var_name_lower = var_name.lower()
        var_value_lower = var_value.lower()
        
        # From variable name
        if any(keyword in var_name_lower for keyword in ['id', 'uuid']):
            return 'str'
        elif any(keyword in var_name_lower for keyword in ['count', 'length', 'size']):
            return 'int'
        elif any(keyword in var_name_lower for keyword in ['price', 'amount', 'value']):
            return 'Decimal'
        elif any(keyword in var_name_lower for keyword in ['active', 'enabled', 'is_', 'has_']):
            return 'bool'
        elif any(keyword in var_name_lower for keyword in ['time', 'date', 'created', 'updated']):
            return 'datetime'
        
        # From value
        if var_value_lower.startswith('"') or var_value_lower.startswith("'"):
            return 'str'
        elif var_value_lower.isdigit():
            return 'int'
        elif '.' in var_value_lower and var_value_lower.replace('.', '').isdigit():
            return 'float'
        elif var_value_lower in ['true', 'false']:
            return 'bool'
        elif '[]' in var_value_lower:
            return 'List[Any]'
        elif '{}' in var_value_lower:
            return 'Dict[str, Any]'
        elif 'none' in var_value_lower:
            return 'None'
        elif 'datetime' in var_value_lower:
            return 'datetime'
        elif 'uuid' in var_value_lower:
            return 'UUID'
        elif 'path' in var_value_lower:
            imports_added.add('Path')
            return 'Path'
        
        return None
    
    def add_missing_imports(self, content: str, imports_added: Set[str]) -> str:
        """Add missing imports to content"""
        lines = content.split('\n')
        
        # Find existing imports
        existing_imports = set()
        for line in lines:
            if line.strip().startswith('from typing import'):
                imports = line.replace('from typing import', '').strip()
                if imports.startswith('(') and imports.endswith(')'):
                    imports = imports[1:-1]
                for imp in imports.split(','):
                    existing_imports.add(imp.strip())
        
        # Add missing imports
        missing_imports = imports_added - existing_imports
        if missing_imports:
            # Find where to insert imports (after existing typing imports or at top)
            insert_index = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('from typing import'):
                    insert_index = i + 1
                elif line.strip() and not line.strip().startswith('#') and not line.strip().startswith('import'):
                    insert_index = i
                    break
            
            # Create import line
            import_line = "from typing import (" + ", ".join(sorted(missing_imports)) + ")"
            
            # Insert import
            lines.insert(insert_index, import_line)
        
        return '\n'.join(lines)

def main():
    """Main execution function"""
    fixer = TypeHintsFixer()
    fixer.fix_all_files()
    
    logger.info("Type hints fixing completed!")

if __name__ == "__main__":
    main()
