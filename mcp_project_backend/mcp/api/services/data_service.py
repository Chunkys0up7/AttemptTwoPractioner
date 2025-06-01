from fastapi import APIRouter, HTTPException

router = APIRouter()

def get_data(item_id: int):
    # Placeholder for data retrieval logic
    # Replace with real database access
    if item_id == 1:
        return {"item_id": 1, "value": "Sample Data"}
    raise HTTPException(status_code=404, detail="Item not found")

@router.get("/data/{item_id}")
def read_data(item_id: int):
    return get_data(item_id) 