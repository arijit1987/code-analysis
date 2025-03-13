import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import ast
import re

class CodeChangeHandler(FileSystemEventHandler):
    def __init__(self, patterns=None):
        self.patterns = patterns or ['*.php', '*.py']
        self.dependency_map = {}
        self.build_dependency_map()
    
    def build_dependency_map(self):
        """Build a map of file dependencies by analyzing PHP includes and requires"""
        base_path = os.getcwd()
        for php_file in Path(base_path).rglob('*.php'):
            try:
                with open(php_file, 'r') as file:
                    content = file.read()
                    # Find all include/require statements
                    includes = re.findall(r'(include|require|include_once|require_once)\s*[\('"](.*?)['"\)]', content)
                    self.dependency_map[str(php_file)] = [
                        str(Path(php_file.parent / inc[1]).resolve())
                        for inc in includes
                    ]
            except Exception as e:
                print(f'Error analyzing dependencies in {php_file}: {str(e)}')
        
    def on_modified(self, event):
        if event.is_directory:
            return
        if any(Path(event.src_path).match(pattern) for pattern in self.patterns):
            print(f'File {event.src_path} has been modified')
            self.analyze_changes(event.src_path)
            if event.src_path.endswith('.php'):
                self.propagate_changes(event.src_path)
    
    def analyze_changes(self, file_path):
        """Analyze changes in the modified file"""
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                if file_path.endswith('.py'):
                    # Parse Python code into AST
                    tree = ast.parse(content)
                    print(f'Successfully parsed Python file {file_path}')
                else:
                    # For PHP files, we'll analyze the content directly
                    print(f'Analyzing PHP file {file_path}')
                    self.analyze_php_changes(content, file_path)
        except Exception as e:
            print(f'Error analyzing {file_path}: {str(e)}')
    
    def analyze_php_changes(self, content, file_path):
        """Analyze changes in PHP files and identify patterns"""
        # Store the original content for comparison
        if not hasattr(self, 'file_contents'):
            self.file_contents = {}
        
        if file_path in self.file_contents:
            old_content = self.file_contents[file_path]
            # Identify changed patterns using difflib
            import difflib
            diff = difflib.unified_diff(old_content.splitlines(), content.splitlines(), lineterm='')
            changes = list(diff)
            if changes:
                print(f'Detected changes in {file_path}:')
                for change in changes:
                    if change.startswith('+') and not change.startswith('+++'):
                        print(f'Added: {change[1:]}')
                    elif change.startswith('-') and not change.startswith('---'):
                        print(f'Removed: {change[1:]}')
        
        # Update stored content
        self.file_contents[file_path] = content
    
    def propagate_changes(self, source_file):
        """Propagate changes to dependent files"""
        # Find files that depend on the modified file
        dependent_files = []
        for file, deps in self.dependency_map.items():
            if str(Path(source_file).resolve()) in deps:
                dependent_files.append(file)
        
        if dependent_files:
            print(f'Found {len(dependent_files)} dependent files to update')
            code_modifier = CodeModifier(os.getcwd())
            # Analyze and apply similar changes to dependent files
            for dep_file in dependent_files:
                print(f'Analyzing dependent file: {dep_file}')
                self.analyze_changes(dep_file)

class CodeModifier:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
    
    def search_pattern(self, pattern):
        """Search for a pattern in all PHP and Python files"""
        matches = []
        for ext in ['*.php', '*.py']:
            for code_file in self.base_path.rglob(ext):
                try:
                    with open(code_file, 'r') as file:
                        content = file.read()
                        if re.search(pattern, content):
                            matches.append(code_file)
                except Exception as e:
                    print(f'Error searching {code_file}: {str(e)}')
        return matches
    
    def modify_files(self, pattern, replacement):
        """Modify files containing the pattern"""
        modified_files = []
        for code_file in self.search_pattern(pattern):
            try:
                with open(code_file, 'r') as file:
                    content = file.read()
                
                new_content = re.sub(pattern, replacement, content)
                
                if new_content != content:
                    with open(code_file, 'w') as file:
                        file.write(new_content)
                    modified_files.append(code_file)
                    print(f'Modified {code_file}')
            except Exception as e:
                print(f'Error modifying {code_file}: {str(e)}')
        return modified_files

def main():
    path = os.getcwd()
    event_handler = CodeChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    
    code_modifier = CodeModifier(path)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print('\nStopping code monitor...')
    
    observer.join()

if __name__ == '__main__':
    main()