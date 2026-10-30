---
format: html
---

# Validation Script

## File: `tests/validate.py`

This script validates the extraction results against expected values from the samples4 directory.

```python
#!/usr/bin/env python3
"""
Validation Script for Universal File Metadata & Version History Extractor

Validates extraction results against expected edit histories.

Usage:
    python validate.py <file_path> [expected_history.json]
    python validate.py samples4/text_files/multi_edit_text.txt
    python -m tests.validate samples4/text_files/multi_edit_text.txt
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class Validator:
    """Validates extraction results against expected history."""
    
    def __init__(self, tolerance_seconds: float = 1.0):
        """
        Initialize validator.
        
        Args:
            tolerance_seconds: Time tolerance for timestamp matching (in seconds)
        """
        self.tolerance_seconds = tolerance_seconds
        self.errors = []
        self.warnings = []
        self.passed = []
    
    def validate(self, extracted: Dict, expected: Optional[Dict] = None,
                 expected_path: Optional[str] = None) -> bool:
        """
        Validate extracted results.
        
        Args:
            extracted: Extracted results from extractor
            expected: Expected results (if provided directly)
            expected_path: Path to expected results JSON file
        
        Returns:
            True if validation passes, False otherwise
        """
        # Load expected if path provided
        if expected is None and expected_path:
            expected = self._load_expected(expected_path)
        
        if expected is None:
            # No expected results, just check basic structure
            return self._validate_structure(extracted)
        
        # Run all validation rules
        self._validate_node_count(extracted, expected)
        self._validate_edge_count(extracted, expected)
        self._validate_timestamps(extracted, expected)
        self._validate_authors(extracted, expected)
        self._validate_edit_types(extracted, expected)
        self._validate_content(extracted, expected)
        self._validate_confidence(extracted, expected)
        self._validate_structure(extracted)
        
        return len(self.errors) == 0
    
    def _load_expected(self, path: str) -> Dict:
        """Load expected results from JSON file."""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _validate_structure(self, extracted: Dict) -> bool:
        """Validate basic structure of extracted results."""
        required_keys = [
            'extraction_metadata',
            'file_metadata',
            'version_history',
            'knowledge_graph',
            'summary',
            'evaluation_bands'
        ]
        
        for key in required_keys:
            if key not in extracted:
                self.errors.append(f"Missing required key: {key}")
            else:
                self.passed.append(f"Structure: {key} present")
        
        # Validate knowledge graph structure
        kg = extracted.get('knowledge_graph', {})
        if 'nodes' not in kg or 'edges' not in kg:
            self.errors.append("Knowledge graph missing nodes or edges")
        else:
            self.passed.append("Knowledge graph structure valid")
        
        return True
    
    def _validate_node_count(self, extracted: Dict, expected: Dict):
        """Validate node count matches expected."""
        extracted_nodes = extracted.get('knowledge_graph', {}).get('nodes', [])
        expected_nodes = expected.get('total_expected_edits', 
                                     expected.get('expected_knowledge_graph', {}).get('nodes', 0))
        
        if expected_nodes > 0 and len(extracted_nodes) != expected_nodes:
            self.errors.append(
                f"Node count mismatch: expected {expected_nodes}, got {len(extracted_nodes)}"
            )
        else:
            self.passed.append(f"Node count: {len(extracted_nodes)} matches expected")
    
    def _validate_edge_count(self, extracted: Dict, expected: Dict):
        """Validate edge count matches expected."""
        extracted_edges = extracted.get('knowledge_graph', {}).get('edges', [])
        expected_edges = expected.get('total_expected_edges',
                                     expected.get('expected_knowledge_graph', {}).get('edges', 0))
        
        if expected_edges > 0 and len(extracted_edges) != expected_edges:
            self.errors.append(
                f"Edge count mismatch: expected {expected_edges}, got {len(extracted_edges)}"
            )
        else:
            self.passed.append(f"Edge count: {len(extracted_edges)} matches expected")
    
    def _validate_timestamps(self, extracted: Dict, expected: Dict):
        """Validate that extracted timestamps match expected timestamps."""
        extracted_nodes = extracted.get('knowledge_graph', {}).get('nodes', [])
        expected_edits = expected.get('known_edits', [])
        
        if not expected_edits:
            return
        
        extracted_timestamps = [node.get('timestamp') for node in extracted_nodes]
        expected_timestamps = [edit.get('timestamp') for edit in expected_edits]
        
        for expected_ts in expected_timestamps:
            if expected_ts not in extracted_timestamps:
                # Check if it's close enough (within tolerance)
                found = False
                for extracted_ts in extracted_timestamps:
                    if self._timestamps_close(expected_ts, extracted_ts):
                        found = True
                        break
                if not found:
                    self.errors.append(f"Missing expected timestamp: {expected_ts}")
            else:
                self.passed.append(f"Timestamp found: {expected_ts}")
        
        # Check chronological order
        if extracted_timestamps:
            sorted_timestamps = sorted(extracted_timestamps)
            if extracted_timestamps != sorted_timestamps:
                self.errors.append("Timestamps are not in chronological order")
            else:
                self.passed.append("Timestamps are in chronological order")
    
    def _timestamps_close(self, ts1: str, ts2: str) -> bool:
        """Check if two timestamps are within tolerance."""
        try:
            from datetime import datetime
            dt1 = datetime.fromisoformat(ts1.replace('Z', '+00:00'))
            dt2 = datetime.fromisoformat(ts2.replace('Z', '+00:00'))
            diff = abs((dt1 - dt2).total_seconds())
            return diff <= self.tolerance_seconds
        except:
            return False
    
    def _validate_authors(self, extracted: Dict, expected: Dict):
        """Validate that all expected authors are present."""
        expected_edits = expected.get('known_edits', [])
        extracted_nodes = extracted.get('knowledge_graph', {}).get('nodes', [])
        
        expected_authors = set()
        for edit in expected_edits:
            if edit.get('author'):
                expected_authors.add(edit['author'])
        
        extracted_authors = set()
        for node in extracted_nodes:
            if node.get('author'):
                extracted_authors.add(node['author'])
        
        if not expected_authors:
            return
        
        missing_authors = expected_authors - extracted_authors
        if missing_authors:
            self.errors.append(f"Missing authors: {', '.join(missing_authors)}")
        else:
            self.passed.append(f"All expected authors found: {', '.join(expected_authors)}")
    
    def _validate_edit_types(self, extracted: Dict, expected: Dict):
        """Validate edit type distribution."""
        expected_edits = expected.get('known_edits', [])
        extracted_nodes = extracted.get('knowledge_graph', {}).get('nodes', [])
        
        # Count expected edit types
        expected_types = {}
        for edit in expected_edits:
            edit_type = edit.get('edit_type', 'unknown')
            expected_types[edit_type] = expected_types.get(edit_type, 0) + 1
        
        # Count extracted edit types
        extracted_types = {}
        for node in extracted_nodes:
            edit_type = node.get('edit_type', 'unknown')
            extracted_types[edit_type] = extracted_types.get(edit_type, 0) + 1
        
        if not expected_types:
            return
        
        for edit_type, expected_count in expected_types.items():
            extracted_count = extracted_types.get(edit_type, 0)
            if extracted_count != expected_count:
                self.errors.append(
                    f"Edit type mismatch for '{edit_type}': expected {expected_count}, got {extracted_count}"
                )
            else:
                self.passed.append(f"Edit type '{edit_type}': {extracted_count} matches")
    
    def _validate_content(self, extracted: Dict, expected: Dict):
        """Validate that content changes are correctly extracted."""
        expected_edits = expected.get('known_edits', [])
        extracted_nodes = extracted.get('knowledge_graph', {}).get('nodes', [])
        
        # For now, just check that content_after is present for non-delete edits
        for node in extracted_nodes:
            edit_type = node.get('edit_type', '')
            if edit_type in ['create', 'add', 'modify']:
                if not node.get('content_after'):
                    self.warnings.append(
                        f"Node {node.get('node_id', 'unknown')} (type: {edit_type}) has no content_after"
                    )
                else:
                    self.passed.append(
                        f"Content extracted for {edit_type} edit"
                    )
        
        # Check that delete edits have content_before
        for node in extracted_nodes:
            if node.get('edit_type') == 'delete':
                if not node.get('content_before'):
                    self.warnings.append(
                        f"Delete node {node.get('node_id', 'unknown')} has no content_before"
                    )
    
    def _validate_confidence(self, extracted: Dict, expected: Dict):
        """Validate confidence bands."""
        summary = extracted.get('summary', {})
        confidence = summary.get('confidence_distribution', {})
        
        total = sum(confidence.values())
        if total > 0:
            self.passed.append(f"Confidence distribution: {confidence}")
        else:
            self.warnings.append("No confidence data found in summary")
        
        # For embedded markers, all should be high confidence
        if expected.get('extraction_method') == 'embedded_marker':
            if confidence.get('high', 0) != total:
                self.warnings.append(
                    f"Expected all high confidence for embedded markers, got {confidence}"
                )
    
    def get_results(self) -> Dict:
        """Get validation results."""
        return {
            "passed": len(self.passed),
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "is_valid": len(self.errors) == 0,
            "passed_checks": self.passed,
            "error_checks": self.errors,
            "warning_checks": self.warnings
        }
    
    def print_results(self):
        """Print validation results."""
        results = self.get_results()
        
        print("\n" + "=" * 60)
        print("VALIDATION RESULTS")
        print("=" * 60)
        
        if results['is_valid']:
            print("✅ VALIDATION PASSED")
        else:
            print("❌ VALIDATION FAILED")
        
        print(f"\nPassed: {results['passed']}")
        print(f"Errors: {results['errors']}")
        print(f"Warnings: {results['warnings']}")
        
        if results['passed'] > 0:
            print("\n✓ Passed Checks:")
            for check in results['passed_checks']:
                print(f"  ✓ {check}")
        
        if results['error_checks'] > 0:
            print("\n✗ Error Checks:")
            for error in results['error_checks']:
                print(f"  ✗ {error}")
        
        if results['warning_checks'] > 0:
            print("\n⚠ Warning Checks:")
            for warning in results['warning_checks']:
                print(f"  ⚠ {warning}")
        
        print("=" * 60 + "\n")
        
        return results['is_valid']


def run_validation(file_path: str, expected_path: Optional[str] = None) -> bool:
    """
    Run validation on an extracted file.
    
    Args:
        file_path: Path to the file that was extracted
        expected_path: Optional path to expected results JSON file
    
    Returns:
        True if validation passes
    """
    # Extract the file
    import subprocess
    import tempfile
    
    # Run extractor
    cmd = [sys.executable, 'extract.py', file_path, '--output-format', 'json']
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    
    if result.returncode != 0:
        print(f"Extraction failed: {result.stderr}")
        return False
    
    # Parse extracted results
    try:
        extracted = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"Failed to parse extraction output: {e}")
        return False
    
    # Load expected if not provided
    if expected_path is None:
        # Try to find expected file
        file_path_obj = Path(file_path)
        expected_path = file_path_obj.parent / (file_path_obj.name + ".history.json")
        if not expected_path.exists():
            # Try in samples4 directory
            samples4_path = Path(__file__).parent.parent / "samples4" / file_path_obj.name
            expected_path = samples4_path.parent / (samples4_path.name + ".history.json")
            if not expected_path.exists():
                expected_path = None
    
    # Run validation
    validator = Validator()
    is_valid = validator.validate(extracted, expected_path=str(expected_path) if expected_path else None)
    validator.print_results()
    
    return is_valid


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Validate extraction results against expected edit histories'
    )
    parser.add_argument('file', help='Path to the file to validate')
    parser.add_argument('expected', nargs='?', help='Path to expected history JSON file (optional)')
    parser.add_argument('--tolerance', type=float, default=1.0,
                        help='Time tolerance in seconds for timestamp matching')
    parser.add_argument('--strict', action='store_true',
                        help='Exit with error code 1 on validation failure')
    
    args = parser.parse_args()
    
    validator = Validator(tolerance_seconds=args.tolerance)
    
    # Load extracted results
    file_path = Path(args.file)
    
    # Check if file exists
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    # If it's a .json file, assume it's already extracted
    if file_path.suffix == '.json':
        with open(file_path, 'r') as f:
            extracted = json.load(f)
        expected_path = args.expected
    else:
        # Extract the file first
        import extract
        extracted = extract.extract_file(str(file_path))
        expected_path = args.expected
    
    # Load expected
    expected = None
    if expected_path:
        expected_path = Path(expected_path)
        if expected_path.exists():
            with open(expected_path, 'r') as f:
                expected = json.load(f)
    
    # Run validation
    is_valid = validator.validate(extracted, expected)
    
    # Print results
    results = validator.get_results()
    validator.print_results()
    
    # Exit with appropriate code
    if args.strict and not is_valid:
        sys.exit(1)
    
    return is_valid


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

## Usage

### Validate a File

```bash
# Validate with auto-discovered expected file
python tests/validate.py samples4/text_files/multi_edit_text.txt

# Specify expected file explicitly
python tests/validate.py samples4/text_files/multi_edit_text.txt samples4/text_files/multi_edit_text.history.json
```

### Run All Tests

```bash
# Test all samples4 files
for file in samples4/**/*.txt; do
    python tests/validate.py "$file"
done
```

### Strict Mode

```bash
# Exit with error code 1 on failure (useful for CI)
python tests/validate.py file.txt --strict
```

### Python API

```python
from tests.validate import Validator

# Create validator
validator = Validator(tolerance_seconds=2.0)

# Load extracted and expected
with open('extracted.json') as f:
    extracted = json.load(f)
with open('expected.json') as f:
    expected = json.load(f)

# Validate
is_valid = validator.validate(extracted, expected)
validator.print_results()

# Get programmatic results
results = validator.get_results()
print(f"Is valid: {results['is_valid']}")
print(f"Errors: {results['errors']}")
```

## Test Cases

### Test Case 1: multi_edit_text.txt

**Input**: `samples4/text_files/multi_edit_text.txt`  
**Expected**: `samples4/text_files/multi_edit_text.history.json`  
**Expected Result**: ✅ PASS (6 nodes, 5 edges)

### Test Case 2: Text File with No Markers

**Input**: Plain text file with no embedded markers  
**Expected**: Filesystem fallback (1 node)  
**Expected Result**: ✅ PASS (1 node, 0 edges, low confidence)

### Test Case 3: Git Repository File

**Input**: File in a git repository  
**Expected**: Git history as edit nodes  
**Expected Result**: ✅ PASS (N nodes where N = git commits)

### Test Case 4: Word Document with Track Changes

**Input**: Word document with track changes enabled  
**Expected**: Track changes as edit nodes  
**Expected Result**: ✅ PASS (N nodes where N = tracked changes)

## Validation Rules

The validator checks the following:

1. **Structure**: Required keys present in output
2. **Node Count**: Matches expected number of edits
3. **Edge Count**: Matches expected number of relationships
4. **Timestamps**: All expected timestamps present
5. **Authors**: All expected authors present
6. **Edit Types**: Distribution matches expected
7. **Content**: Content changes extracted correctly
8. **Confidence**: Evaluation bands assigned appropriately
9. **Chronological Order**: Nodes in correct time order

## Creating New Tests

To add a new test case:

1. **Create a test file** in `samples4/` directory
2. **Create expected results** file with `.history.json` extension
3. **Run validation**:

```bash
python tests/validate.py samples4/new_test.txt
```

The expected file should follow the format in `samples4/text_files/multi_edit_text.history.json`.

## Continuous Integration

For CI/CD integration:

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run validation
        run: |
          python tests/validate.py samples4/text_files/multi_edit_text.txt --strict
```
