---
description: Scaffold a new validation hook with directory structure and base files
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

Create a new validation hook for: $ARGUMENTS

## Process

1. **Validate Hook Name**
   - Convert to snake_case for directory/file names
   - Convert to PascalCase for class name
   - Ensure unique (not existing in packages/hooks/)

2. **Create Directory Structure**
   ```
   packages/hooks/src/mizrahi_hooks/<hook_name>/
   ├── __init__.py
   ├── hook.py
   └── checks/
       └── __init__.py
   ```

3. **Create hook.py** with:
   - Class extending BaseHook
   - @register_hook decorator
   - Abstract method implementations
   - Docstrings with purpose

4. **Create __init__.py files** with proper exports

5. **Add to hooks.yaml** configuration:
   ```yaml
   <hook_name>:
     name: <Hook Name>
     name_he: <Hebrew Name>
     description: <Description>
     status: development
     schedule:
       enabled: false
     parameters: {}
     checks: []
     email:
       enabled: false
   ```

6. **Create initial test file** at `apps/api/tests/hooks/test_<hook_name>.py`

## Template for hook.py

```python
"""
<Hook Name> Validation Hook implementation.

<Description of what this hook validates>
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from mizrahi_hooks.base import BaseHook
from mizrahi_hooks.registry import register_hook
from mizrahi_shared.models import CheckResult, HookConfig


@register_hook("<hook_name>")
class <HookName>Hook(BaseHook):
    """
    Hook: <Hook Name>

    <Description>
    """

    @property
    def hook_id(self) -> str:
        return "<hook_name>"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def checks(self) -> List[str]:
        return []  # Add check IDs here

    async def validate_input(
        self, input_data: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """Validate required input fields."""
        # TODO: Implement validation
        return True, None

    async def fetch_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch required data from external sources."""
        # TODO: Implement data fetching
        return {}

    async def run_checks(self, data: Dict[str, Any]) -> List[CheckResult]:
        """Execute all validation checks."""
        # TODO: Implement checks
        return []

    async def generate_report(
        self,
        input_data: Dict[str, Any],
        results: List[CheckResult],
    ) -> Path:
        """Generate Excel report with findings."""
        # TODO: Implement report generation
        pass
```

7. **Verify** by running import test:
   ```bash
   cd apps/api && uv run python -c "from mizrahi_hooks.<hook_name> import <HookName>Hook"
   ```
