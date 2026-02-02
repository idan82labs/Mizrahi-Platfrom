"""
Managers API endpoints.
"""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/managers")
async def list_managers():
    """List all fund managers."""
    try:
        from mizrahi_shared.config import get_managers

        managers_config = get_managers()
        managers = [
            {
                "key": m.key,
                "id": m.id,
                "name_he": m.name_he,
                "name_en": m.name_en,
                "enabled": m.enabled,
            }
            for m in managers_config.values()
        ]

        return {"managers": managers}
    except Exception as e:
        return {"managers": [], "error": str(e)}


@router.get("/managers/{manager_key}")
async def get_manager(manager_key: str):
    """Get manager by key."""
    try:
        from mizrahi_shared.config import get_managers

        managers = get_managers()
        manager = managers.get(manager_key)

        if not manager:
            raise HTTPException(
                status_code=404,
                detail=f"Manager '{manager_key}' not found",
            )

        return {
            "manager": {
                "key": manager.key,
                "id": manager.id,
                "name_he": manager.name_he,
                "name_en": manager.name_en,
                "enabled": manager.enabled,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
