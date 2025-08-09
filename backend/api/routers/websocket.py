"""
WebSocket router for real-time communication
Handles media streams, live transcriptions, and call events
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.responses import HTMLResponse
import json
import asyncio
from typing import Optional, Dict
from datetime import datetime
import uuid

from api.dependencies.auth import get_current_user_ws
from api.services.voice.media_stream import media_stream_handler
from api.services.websocket import websocket_manager
from api.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(
    prefix="/websocket",
    tags=["websocket"]
)


@router.websocket("/media-stream")
async def media_stream_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for Twilio Media Streams
    Handles real-time audio streaming from phone calls
    """
    await websocket.accept()
    
    try:
        # Delegate to media stream handler
        await media_stream_handler.handle_websocket(websocket, "/media-stream")
        
    except WebSocketDisconnect:
        logger.info("Media stream WebSocket disconnected")
    except Exception as e:
        logger.error(f"Media stream error: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass


@router.websocket("/call/{call_id}")
async def call_websocket(
    websocket: WebSocket,
    call_id: str,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time call updates
    Provides live transcriptions and call events to dashboard
    """
    # Authenticate WebSocket connection
    user = None
    if token:
        try:
            user = await get_current_user_ws(token)
        except:
            await websocket.close(code=1008, reason="Invalid authentication")
            return
    
    await websocket.accept()
    connection_id = str(uuid.uuid4())
    
    try:
        # Add to connection manager
        await websocket_manager.connect(websocket, connection_id, call_id)
        
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "connection_id": connection_id,
            "call_id": call_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep connection alive and handle messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_json()
                message_type = data.get("type")
                
                if message_type == "ping":
                    # Respond to ping
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
                elif message_type == "subscribe":
                    # Subscribe to specific events
                    events = data.get("events", [])
                    await websocket_manager.subscribe_to_events(
                        connection_id, events
                    )
                    
                elif message_type == "command":
                    # Handle call commands (mute, hold, transfer, etc.)
                    await handle_call_command(
                        call_id, data.get("command"), data.get("params")
                    )
                    
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON"
                })
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                
    except Exception as e:
        logger.error(f"WebSocket error for call {call_id}: {e}")
    finally:
        # Disconnect and cleanup
        websocket_manager.disconnect(connection_id)
        logger.info(f"WebSocket disconnected: {connection_id}")


@router.websocket("/dashboard")
async def dashboard_websocket(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for dashboard real-time updates
    Provides system-wide events and statistics
    """
    # Authenticate
    user = None
    if token:
        try:
            user = await get_current_user_ws(token)
        except:
            await websocket.close(code=1008, reason="Invalid authentication")
            return
    
    await websocket.accept()
    connection_id = str(uuid.uuid4())
    
    try:
        # Add to connection manager for dashboard
        await websocket_manager.connect_dashboard(websocket, connection_id, user)
        
        # Send initial dashboard state
        await send_dashboard_state(websocket)
        
        # Keep connection alive
        while True:
            try:
                data = await websocket.receive_json()
                message_type = data.get("type")
                
                if message_type == "ping":
                    await websocket.send_json({"type": "pong"})
                    
                elif message_type == "get_stats":
                    await send_dashboard_stats(websocket)
                    
                elif message_type == "get_active_calls":
                    await send_active_calls(websocket)
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Dashboard WebSocket error: {e}")
                
    finally:
        websocket_manager.disconnect_dashboard(connection_id)


async def handle_call_command(call_id: str, command: str, params: Dict):
    """
    Handle call control commands
    
    Args:
        call_id: Call identifier
        command: Command type (mute, hold, transfer, end)
        params: Command parameters
    """
    from api.services.telephony import twilio_service
    
    try:
        if command == "mute":
            # Mute/unmute call
            muted = params.get("muted", True)
            # Implementation would interact with Twilio API
            logger.info(f"Call {call_id} mute: {muted}")
            
        elif command == "hold":
            # Put call on hold
            on_hold = params.get("on_hold", True)
            logger.info(f"Call {call_id} hold: {on_hold}")
            
        elif command == "transfer":
            # Transfer call
            target = params.get("target")
            logger.info(f"Call {call_id} transfer to: {target}")
            
        elif command == "end":
            # End call
            success = twilio_service.end_call(call_id, "User requested")
            logger.info(f"Call {call_id} ended: {success}")
            
            # Notify all connected clients
            await websocket_manager.broadcast_to_call(call_id, {
                "type": "call_ended",
                "call_id": call_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Error handling command {command} for call {call_id}: {e}")


async def send_dashboard_state(websocket: WebSocket):
    """Send initial dashboard state to client"""
    from api.services.voice.media_stream import media_stream_handler
    
    try:
        active_streams = media_stream_handler.get_active_streams()
        
        await websocket.send_json({
            "type": "dashboard_state",
            "data": {
                "active_calls": len(active_streams),
                "streams": active_streams,
                "timestamp": datetime.utcnow().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Error sending dashboard state: {e}")


async def send_dashboard_stats(websocket: WebSocket):
    """Send dashboard statistics"""
    # This would fetch real statistics from database
    stats = {
        "total_calls_today": 42,
        "average_call_duration": 180,
        "active_agents": 5,
        "queue_size": 3
    }
    
    await websocket.send_json({
        "type": "stats",
        "data": stats,
        "timestamp": datetime.utcnow().isoformat()
    })


async def send_active_calls(websocket: WebSocket):
    """Send list of active calls"""
    from api.services.voice.media_stream import media_stream_handler
    
    active_streams = media_stream_handler.get_active_streams()
    
    calls = []
    for stream_sid, stream_info in active_streams.items():
        calls.append({
            "stream_sid": stream_sid,
            "call_sid": stream_info["call_sid"],
            "status": "active" if stream_info["is_active"] else "ended",
            "metadata": stream_info["metadata"]
        })
    
    await websocket.send_json({
        "type": "active_calls",
        "data": calls,
        "timestamp": datetime.utcnow().isoformat()
    })


# WebSocket Test Page (for development)
@router.get("/test")
async def websocket_test_page():
    """Test page for WebSocket connections"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket Test</title>
    </head>
    <body>
        <h1>VocalIQ WebSocket Test</h1>
        
        <div>
            <h2>Dashboard WebSocket</h2>
            <button onclick="connectDashboard()">Connect</button>
            <button onclick="disconnectDashboard()">Disconnect</button>
            <button onclick="getStats()">Get Stats</button>
            <div id="dashboard-status">Disconnected</div>
            <div id="dashboard-messages"></div>
        </div>
        
        <script>
            let dashboardWs = null;
            
            function connectDashboard() {
                dashboardWs = new WebSocket("ws://localhost:8000/api/v1/websocket/dashboard");
                
                dashboardWs.onopen = () => {
                    document.getElementById("dashboard-status").textContent = "Connected";
                    console.log("Dashboard connected");
                };
                
                dashboardWs.onmessage = (event) => {
                    const msg = JSON.parse(event.data);
                    const messagesDiv = document.getElementById("dashboard-messages");
                    messagesDiv.innerHTML = "<pre>" + JSON.stringify(msg, null, 2) + "</pre>" + messagesDiv.innerHTML;
                };
                
                dashboardWs.onclose = () => {
                    document.getElementById("dashboard-status").textContent = "Disconnected";
                    console.log("Dashboard disconnected");
                };
                
                dashboardWs.onerror = (error) => {
                    console.error("WebSocket error:", error);
                };
            }
            
            function disconnectDashboard() {
                if (dashboardWs) {
                    dashboardWs.close();
                    dashboardWs = null;
                }
            }
            
            function getStats() {
                if (dashboardWs && dashboardWs.readyState === WebSocket.OPEN) {
                    dashboardWs.send(JSON.stringify({
                        type: "get_stats"
                    }));
                }
            }
            
            // Ping every 30 seconds to keep connection alive
            setInterval(() => {
                if (dashboardWs && dashboardWs.readyState === WebSocket.OPEN) {
                    dashboardWs.send(JSON.stringify({type: "ping"}));
                }
            }, 30000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)