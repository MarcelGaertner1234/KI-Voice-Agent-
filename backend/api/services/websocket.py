"""WebSocket service."""

from typing import Dict, Set, List, Optional, Any
from fastapi import WebSocket
import json
import asyncio
from datetime import datetime

from api.utils.logger import setup_logger

logger = setup_logger(__name__)


class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        # Store active connections by call_id
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Store websocket to call_id mapping
        self.websocket_to_call: Dict[WebSocket, str] = {}
        # Store connection metadata
        self.connection_metadata: Dict[str, Dict] = {}
        # Dashboard connections
        self.dashboard_connections: Dict[str, WebSocket] = {}
        # Event subscriptions
        self.event_subscriptions: Dict[str, Set[str]] = {}
    
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
    
    async def connect(self, websocket: WebSocket, connection_id: str, call_id: str):
        """Connect WebSocket with connection ID."""
        if call_id not in self.active_connections:
            self.active_connections[call_id] = set()
        
        self.active_connections[call_id].add(websocket)
        self.websocket_to_call[websocket] = call_id
        self.connection_metadata[connection_id] = {
            "call_id": call_id,
            "websocket": websocket,
            "connected_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"WebSocket {connection_id} connected for call: {call_id}")
    
    def disconnect(self, connection_id: str):
        """Disconnect by connection ID."""
        if connection_id in self.connection_metadata:
            metadata = self.connection_metadata[connection_id]
            websocket = metadata["websocket"]
            call_id = metadata["call_id"]
            
            if call_id in self.active_connections:
                self.active_connections[call_id].discard(websocket)
                if not self.active_connections[call_id]:
                    del self.active_connections[call_id]
            
            if websocket in self.websocket_to_call:
                del self.websocket_to_call[websocket]
            
            del self.connection_metadata[connection_id]
            
            if connection_id in self.event_subscriptions:
                del self.event_subscriptions[connection_id]
            
            logger.info(f"WebSocket {connection_id} disconnected")
    
    async def connect_dashboard(self, websocket: WebSocket, connection_id: str, user: Optional[Any] = None):
        """Connect dashboard WebSocket."""
        self.dashboard_connections[connection_id] = websocket
        self.connection_metadata[connection_id] = {
            "type": "dashboard",
            "websocket": websocket,
            "user": user,
            "connected_at": datetime.utcnow().isoformat()
        }
        logger.info(f"Dashboard WebSocket {connection_id} connected")
    
    def disconnect_dashboard(self, connection_id: str):
        """Disconnect dashboard WebSocket."""
        if connection_id in self.dashboard_connections:
            del self.dashboard_connections[connection_id]
        if connection_id in self.connection_metadata:
            del self.connection_metadata[connection_id]
        if connection_id in self.event_subscriptions:
            del self.event_subscriptions[connection_id]
        logger.info(f"Dashboard WebSocket {connection_id} disconnected")
    
    async def subscribe_to_events(self, connection_id: str, events: List[str]):
        """Subscribe connection to specific events."""
        if connection_id not in self.event_subscriptions:
            self.event_subscriptions[connection_id] = set()
        self.event_subscriptions[connection_id].update(events)
        logger.info(f"Connection {connection_id} subscribed to events: {events}")
    
    async def broadcast_to_call(self, call_id: str, message: Dict):
        """Broadcast message to all connections for a call."""
        await self.send_json(call_id, message)
    
    async def broadcast_to_dashboards(self, message: Dict):
        """Broadcast message to all dashboard connections."""
        disconnected = []
        for connection_id, websocket in self.dashboard_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to dashboard {connection_id}: {e}")
                disconnected.append(connection_id)
        
        # Clean up disconnected dashboards
        for connection_id in disconnected:
            self.disconnect_dashboard(connection_id)
    
    async def send_to_connection(self, connection_id: str, message: Dict):
        """Send message to specific connection."""
        if connection_id in self.connection_metadata:
            metadata = self.connection_metadata[connection_id]
            websocket = metadata["websocket"]
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to connection {connection_id}: {e}")
                self.disconnect(connection_id)


# Global WebSocket manager instance
websocket_manager = ConnectionManager()


class WebSocketManager:
    """WebSocket manager for call handling."""
    
    def __init__(self):
        self.manager = websocket_manager
    
    async def connect(self, websocket: WebSocket, call_id: str):
        """Connect WebSocket to call."""
        await self.manager.connect(websocket, call_id)
    
    def disconnect(self, call_id: str):
        """Disconnect all WebSockets for a call."""
        if call_id in self.manager.active_connections:
            websockets = list(self.manager.active_connections[call_id])
            for ws in websockets:
                self.manager.disconnect(ws)
    
    async def send_bytes(self, call_id: str, data: bytes):
        """Send audio bytes to call."""
        await self.manager.send_bytes(call_id, data)
    
    async def send_json(self, call_id: str, data: dict):
        """Send JSON data to call."""
        await self.manager.send_json(call_id, data)
    
    async def broadcast_event(self, call_id: str, event_type: str, data: dict):
        """Broadcast event to call."""
        await self.manager.broadcast_event(call_id, event_type, data)