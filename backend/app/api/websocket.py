"""
WebSocket handler for real-time research updates.
"""
import logging
import json
from typing import Set
from fastapi import WebSocket, WebSocketDisconnect
from app.orchestrator.research_engine import ResearchEngine

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        """Initialize the connection manager."""
        self.active_connections: Set[WebSocket] = set()
        self.research_engine = ResearchEngine()
    
    async def connect(self, websocket: WebSocket) -> None:
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket) -> None:
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
    
    async def broadcast(self, message: dict) -> None:
        """Broadcast a message to all connected WebSocket clients."""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {e}")
                disconnected.add(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.active_connections.discard(connection)


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, job_id: str) -> None:
    """
    WebSocket endpoint for real-time research job updates.
    
    Args:
        websocket: WebSocket connection
        job_id: Research job ID to subscribe to
    """
    await manager.connect(websocket)
    
    try:
        # TODO: Subscribe to job updates
        # TODO: Send initial job state
        # TODO: Listen for updates and forward to client
        
        while True:
            # Keep connection alive and listen for messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # TODO: Handle client messages (pause, cancel, etc.)
            logger.info(f"Received WebSocket message for job {job_id}: {message}")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"WebSocket disconnected for job {job_id}")

