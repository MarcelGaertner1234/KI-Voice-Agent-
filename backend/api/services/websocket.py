"""WebSocket service."""

from typing import Dict, Set
from fastapi import WebSocket
import json

from api.utils.logger import setup_logger

logger = setup_logger(__name__)


class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        # Store active connections by call_id
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Store websocket to call_id mapping
        self.websocket_to_call: Dict[WebSocket, str] = {}
    
    async def connect(self, websocket: WebSocket, call_id: str):
        """Accept and store WebSocket connection."""
        await websocket.accept()
        
        # Add to connections
        if call_id not in self.active_connections:
            self.active_connections[call_id] = set()
        
        self.active_connections[call_id].add(websocket)
        self.websocket_to_call[websocket] = call_id
        
        logger.info(f"WebSocket connected for call: {call_id}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        call_id = self.websocket_to_call.get(websocket)
        
        if call_id:
            if call_id in self.active_connections:
                self.active_connections[call_id].discard(websocket)
                if not self.active_connections[call_id]:
                    del self.active_connections[call_id]
            
            del self.websocket_to_call[websocket]
            
            logger.info(f"WebSocket disconnected for call: {call_id}")
    
    async def send_json(self, call_id: str, data: dict):
        """Send JSON data to all connections for a call."""
        if call_id in self.active_connections:
            message = json.dumps(data)
            disconnected = set()
            
            for websocket in self.active_connections[call_id]:
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    logger.error(f"Error sending to websocket: {e}")
                    disconnected.add(websocket)
            
            # Clean up disconnected websockets
            for websocket in disconnected:
                self.disconnect(websocket)
    
    async def send_bytes(self, call_id: str, data: bytes):
        """Send binary data to all connections for a call."""
        if call_id in self.active_connections:
            disconnected = set()
            
            for websocket in self.active_connections[call_id]:
                try:
                    await websocket.send_bytes(data)
                except Exception as e:
                    logger.error(f"Error sending to websocket: {e}")
                    disconnected.add(websocket)
            
            # Clean up disconnected websockets
            for websocket in disconnected:
                self.disconnect(websocket)
    
    async def broadcast_event(self, call_id: str, event_type: str, data: dict):
        """Broadcast event to all connections for a call."""
        await self.send_json(call_id, {
            "type": event_type,
            "data": data
        })


# Global WebSocket manager instance
websocket_manager = ConnectionManager()