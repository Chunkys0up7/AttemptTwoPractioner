from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List
import black

router = APIRouter()

@router.post("/format/code")
def format_code(payload: Dict[str, Any] = Body(...)):
    """
    Auto-format Python code using Black.
    """
    code = payload.get("code", "")
    mode = black.Mode()
    try:
        formatted_code = black.format_str(code, mode=mode)
        return {"formatted_code": formatted_code, "errors": []}
    except Exception as e:
        return {"formatted_code": code, "errors": [str(e)]}

@router.post("/format/batch")
def format_batch(payload: Dict[str, Any] = Body(...)):
    """
    Batch format multiple code snippets.
    """
    codes: List[str] = payload.get("codes", [])
    mode = black.Mode()
    results = []
    for code in codes:
        try:
            formatted = black.format_str(code, mode=mode)
            results.append({"formatted_code": formatted, "errors": []})
        except Exception as e:
            results.append({"formatted_code": code, "errors": [str(e)]})
    return {"results": results}

@router.post("/format/configure")
def configure_formatting(payload: Dict[str, Any] = Body(...)):
    """
    Dummy endpoint for custom rule support (not implemented).
    """
    # In a real implementation, store and apply user/project-specific formatting rules
    return {"success": True, "note": "Custom rule support not implemented yet."} 