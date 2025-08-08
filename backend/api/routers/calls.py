"""Call management endpoints."""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlmodel import Session

from api.dependencies import get_current_active_user, get_organization_id
from api.utils.database import get_db
from api.models.user import User
from api.models.call import Call
from api.schemas.request.call import CallCreate
from api.schemas.response.call import CallResponse
from api.services.call import CallService
from api.services.websocket import WebSocketManager

router = APIRouter()
websocket_manager = WebSocketManager()


@router.post("/", response_model=CallResponse, status_code=status.HTTP_201_CREATED)
async def create_call(
    call_data: CallCreate,
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_db)
) -> Any:
    """Initiate a new call."""
    call_service = CallService(db)
    call = await call_service.create_call(call_data, organization_id)
    return call


@router.get("/", response_model=List[CallResponse])
async def list_calls(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    agent_id: str = None,
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_db)
) -> Any:
    """List all calls for the organization."""
    call_service = CallService(db)
    calls = await call_service.list_calls(
        organization_id=organization_id,
        status=status,
        agent_id=agent_id,
        skip=skip,
        limit=limit
    )
    return calls


@router.get("/{call_id}", response_model=CallResponse)
async def get_call(
    call_id: str,
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_db)
) -> Any:
    """Get specific call details."""
    call_service = CallService(db)
    call = await call_service.get_call(call_id, organization_id)
    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )
    return call


@router.post("/{call_id}/end", response_model=CallResponse)
async def end_call(
    call_id: str,
    organization_id: str = Depends(get_organization_id),
    db: Session = Depends(get_db)
) -> Any:
    """End an active call."""
    call_service = CallService(db)
    call = await call_service.end_call(call_id, organization_id)
    if not call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )
    return call


@router.websocket("/{call_id}/stream")
async def call_stream(
    websocket: WebSocket,
    call_id: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time audio streaming."""
    await websocket_manager.connect(websocket, call_id)
    
    try:
        while True:
            # Receive audio data from client
            data = await websocket.receive_bytes()
            
            # Process audio (STT, AI response, TTS)
            # TODO: Implement audio processing pipeline
            
            # Send response back
            await websocket_manager.send_bytes(call_id, data)
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(call_id)


@router.post("/webhook/twilio")
async def twilio_webhook(
    # TODO: Implement Twilio webhook handling
    db: Session = Depends(get_db)
) -> Any:
    """Handle Twilio webhook events."""
    return {"status": "ok"}