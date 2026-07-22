from fastapi import APIRouter, Depends

from app.deps import get_current_user
from app.models import User
from app.schemas import GraphResponse
from app.services.neo4j_service import fetch_graph

router = APIRouter(prefix="/api", tags=["graph"])


@router.get("/graph", response_model=GraphResponse)
def get_graph(current_user: User = Depends(get_current_user), limit: int = 300):
    data = fetch_graph(limit=limit)
    return GraphResponse(**data)
