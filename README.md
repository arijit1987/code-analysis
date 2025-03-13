
## Overview

`code_monitor.py` is a Python script designed to monitor changes in PHP and Python code files within a directory and perform code analysis. It leverages the `watchdog` library to observe file system events and triggers actions upon file modifications.

Key features include:

* **Real-time File Monitoring:**  Watches for changes in `.php` and `.py` files (configurable).
* **Dependency Tracking (PHP):**  Builds a dependency map for PHP files by parsing `include`, `require`, `include_once`, and `require_once` statements.
* **Change Analysis:**
    * For Python files, it parses the code using `ast` to verify syntax and prints a success message upon parsing.
    * For PHP files, it detects changes by comparing the current content with the previous content using `difflib` and highlights added and removed lines.
* **Change Propagation (PHP):**  Identifies files that depend on a modified PHP file (based on the dependency map) and triggers analysis on these dependent files.
* **Code Modification (Search and Replace):** Provides a `CodeModifier` class to search for patterns and modify files across the codebase using regular expressions.

## Requirements

* Python 3.x
* Libraries listed in `requirements.txt`:
    * `watchdog`
    * `pathlib`

You can install the dependencies using pip:

```bash
pip install -r requirements.txt
```

## Usage

1. **Clone the repository or save `code_monitor.py` and `requirements.txt` in a directory.**
2. **Install the required libraries:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the script from the directory you want to monitor:**
   ```bash
   python code_monitor.py
   ```
   This will start the file system observer and begin monitoring for changes in `.php` and `.py` files within the current directory and its subdirectories.

4. **Modify a `.php` or `.py` file within the monitored directory.** The script will detect the change and perform the following actions:
    * Print a message indicating the file has been modified.
    * Analyze the changes:
        * For `.py` files, it will attempt to parse the Python code and print a success message if parsing is successful.
        * For `.php` files, it will compare the new content with the previously stored content (if available) and print the lines that have been added or removed.
    * If a `.php` file is modified, it will:
        * Propagate changes by identifying files that include/require the modified file.
        * Analyze these dependent files as well.

5. **To stop the monitor, press `Ctrl+C`.**

### Configuration

* **File Patterns:** By default, the script monitors `*.php` and `*.py` files. You can customize the file patterns by modifying the `patterns` attribute in the `CodeChangeHandler` class within `code_monitor.py`:

   ```python
   class CodeChangeHandler(FileSystemEventHandler):
       def __init__(self, patterns=None):
           self.patterns = patterns or ['*.php', '*.py'] # Modify this line
           # ... rest of the code
   ```
   For example, to monitor only `.py` files and `.js` files, you would change it to `patterns=['*.py', '*.js']`.

### Code Modification using `CodeModifier`

The `CodeModifier` class can be used independently to perform search and replace operations across your codebase.  While not directly triggered by file changes in the current monitoring setup, it's available within the script and can be extended or used in other scripts.

**Example Usage (within Python code or interactive shell):**

```python
from code_monitor import CodeModifier

modifier = CodeModifier(base_path='.') # '.' represents the current directory

# Search for a pattern (e.g., 'old_function_name' in PHP or Python files)
matches = modifier.search_pattern(r'old_function_name')
print("Files containing the pattern:", matches)

# Modify files to replace 'old_function_name' with 'new_function_name'
modified_files = modifier.modify_files(r'old_function_name', 'new_function_name')
print("Modified files:", modified_files)
```

**Important Notes:**

* **PHP Dependency Tracking:** The PHP dependency tracking relies on simple regular expressions to find `include`/`require` statements. It might not cover all complex scenarios or dynamic includes.
* **PHP Change Propagation:**  Change propagation currently only triggers analysis of dependent files.  It does not automatically apply changes to dependent files. The `CodeModifier` class provides tools for code modification, but further logic would be needed to automatically propagate specific changes based on the analysis.
* **Error Handling:** The script includes basic error handling (e.g., `try-except` blocks) to catch exceptions during file reading and parsing, but more robust error handling and logging could be added for production use.
* **Performance:** For very large codebases, the initial dependency map building and continuous file monitoring might have performance implications. Consider optimizing the dependency building or file watching if needed for large projects.

This script provides a foundation for code analysis and change management. It can be further extended to implement more sophisticated analysis, automated code modifications, and integration with other development tools.
```
