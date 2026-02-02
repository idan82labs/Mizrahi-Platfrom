---
description: Add a new validation check to an existing hook
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

Create a new validation check for: $ARGUMENTS

Expected format: `<hook_name> <check_name>` (e.g., "monthly_report price_validation")

## Process

1. **Parse Arguments**
   - Extract hook_name and check_name
   - Validate hook exists in packages/hooks/

2. **Read Existing Patterns**
   - Look at existing checks in the hook's checks/ directory
   - Use `completeness.py` as reference pattern

3. **Create Check File**
   Location: `packages/hooks/src/mizrahi_hooks/<hook_name>/checks/<check_name>.py`

4. **Template:**
   ```python
   """
   Check: <Check Name> (<Hebrew Name>)

   <Description of what this check validates>
   """

   import time
   import logging
   from typing import Any, Dict, List

   from mizrahi_shared.models import CheckResult

   logger = logging.getLogger(__name__)

   CHECK_ID = "<check_name>"
   CHECK_NAME_HE = "<Hebrew Name>"


   async def check_<check_name>(data: Dict[str, Any]) -> CheckResult:
       """
       <Description>

       Args:
           data: Dictionary containing:
               - <field>: <description>

       Returns:
           CheckResult with findings
       """
       start_time = time.time()
       findings: List[Dict[str, Any]] = []

       try:
           # TODO: Implement validation logic

           # Determine status
           if findings:
               status = "fail"
               message = f"נמצאו {len(findings)} בעיות"
           else:
               status = "pass"
               message = "הבדיקה עברה בהצלחה"

           return CheckResult(
               check_id=CHECK_ID,
               check_name=CHECK_ID,
               check_name_he=CHECK_NAME_HE,
               status=status,
               message=message,
               findings_count=len(findings),
               findings=findings,
               duration_ms=int((time.time() - start_time) * 1000),
           )

       except Exception as e:
           logger.exception(f"{CHECK_ID} check error: {e}")
           return CheckResult(
               check_id=CHECK_ID,
               check_name=CHECK_ID,
               check_name_he=CHECK_NAME_HE,
               status="fail",
               message=f"שגיאה בבדיקה: {str(e)}",
               duration_ms=int((time.time() - start_time) * 1000),
           )
   ```

5. **Update checks/__init__.py**
   Add export for new check function

6. **Update hook.py**
   - Import new check function
   - Add to `checks` property list
   - Add to `check_functions` in `run_checks()`

7. **Add Configuration** to `config/hooks.yaml`:
   ```yaml
   checks:
     - id: <check_name>
       name_he: <Hebrew Name>
       description: <Description>
       enabled: true
   ```

8. **Create Test File**
   At `apps/api/tests/hooks/test_<hook_name>/test_<check_name>.py`

9. **Verify** by running tests:
   ```bash
   cd apps/api && uv run pytest tests/hooks/test_<hook_name>/test_<check_name>.py -v
   ```
