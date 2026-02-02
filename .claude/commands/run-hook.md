---
description: Execute a hook locally for testing
allowed-tools: Bash, Read, Write
---

Run hook locally for testing: $ARGUMENTS

Expected format: `<hook_id> [--manager <name>] [--dry-run]`

## Process

1. **Parse Arguments**
   - hook_id: required (monthly_report, special_transactions)
   - --manager: optional manager name (default: test data)
   - --dry-run: optional, skip email sending

2. **Validate Hook Exists**
   ```bash
   cd apps/api && uv run python -c "from mizrahi_hooks.registry import get_hook; print(get_hook('<hook_id>'))"
   ```

3. **Prepare Test Input**
   ```python
   input_data = {
       "manager_name": "<manager_name or test>",
       "manager_id": "<manager_id>",
       "email": "test@test.com",
       # Additional hook-specific fields
   }
   ```

4. **Execute Hook**
   ```bash
   cd apps/api && uv run python -c "
   import asyncio
   from mizrahi_hooks.registry import get_hook
   from mizrahi_shared.config import get_hook_config

   async def main():
       config = get_hook_config('<hook_id>')
       hook_class = get_hook('<hook_id>')
       hook = hook_class(config)

       input_data = {
           'manager_name': '<manager>',
           'email': 'test@test.com',
       }

       result = await hook.execute(input_data)
       print(f'Status: {result.status}')
       print(f'Message: {result.message}')
       print(f'Checks: {len(result.checks)}')
       for check in result.checks:
           print(f'  - {check.check_name_he}: {check.status}')

   asyncio.run(main())
   "
   ```

5. **Review Output**
   - Check status (success/partial/failed)
   - Review individual check results
   - Check output file if generated
   - Review logs

## Available Hooks

| Hook ID | Status | Description |
|---------|--------|-------------|
| `monthly_report` | Active | Monthly fund holdings validation |
| `special_transactions` | Development | Special transactions validation |

## Available Managers

| Hebrew Name | Key |
|-------------|-----|
| מגדל | migdal |
| איילון | ayalon |
| קסם | kesem |
| סיגמא | sigma |
| פורסט | forest |
| הראל | harel |
| אנליסט | analyst |
| מיטב | meitav |
| איביאי | ibi |
| אלטשולר-שחם | altshuler |

## Example Usage

```
/run-hook monthly_report --manager מגדל --dry-run
/run-hook special_transactions --manager סיגמא
```

## Troubleshooting

- **Import Error**: Check package is installed (`uv sync`)
- **Config Error**: Verify hooks.yaml has the hook configured
- **API Error**: Check APIFY_API_TOKEN is set (or use mock data)
