"""
WebSocket handler for real-time research updates.
"""
import logging
import json
from typing import Set, Dict, Optional
from collections import defaultdict
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        """Initialize the connection manager."""
        self.active_connections: Dict[str, Set[WebSocket]] = defaultdict(set)
    
    async def connect(self, websocket: WebSocket, job_id: str) -> None:
        """
        Accept a new WebSocket connection and associate it with a job_id.
        
        Args:
            websocket: WebSocket connection
            job_id: Research job ID to associate with this connection
        """
        await websocket.accept()
        self.active_connections[job_id].add(websocket)
        logger.info(f"WebSocket connected for job {job_id}. Total connections for job: {len(self.active_connections[job_id])}")
    
    def disconnect(self, websocket: WebSocket, job_id: str) -> None:
        """
        Remove a WebSocket connection from the specified job.
        
        Args:
            websocket: WebSocket connection to remove
            job_id: Research job ID associated with this connection
        """
        if job_id in self.active_connections:
            self.active_connections[job_id].discard(websocket)
            # Clean up empty sets
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]
        logger.info(f"WebSocket disconnected for job {job_id}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket) -> None:
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
    
    async def _broadcast_to_job(self, job_id: str, message: dict) -> None:
        """
        Internal method to broadcast a message to all connections for a specific job.
        
        Args:
            job_id: Research job ID to broadcast to
            message: Message dictionary to send
        """
        if job_id not in self.active_connections:
            logger.debug(f"No active connections for job {job_id}")
            return
        
        disconnected = set()
        connections = self.active_connections[job_id].copy()  # Copy to avoid modification during iteration
        
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket for job {job_id}: {e}")
                disconnected.add(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.active_connections[job_id].discard(connection)
        
        # Clean up empty sets
        if not self.active_connections[job_id]:
            del self.active_connections[job_id]
    
    async def broadcast_status(self, job_id: str, status: str, progress: Optional[float] = None) -> None:
        """
        Broadcast status update to all clients connected to a specific job.
        
        Args:
            job_id: Research job ID
            status: Job status (pending, running, completed, failed, cancelled)
            progress: Optional progress percentage (0-100)
        """
        message = {
            "type": "status",
            "job_id": job_id,
            "data": {
                "status": status,
                "progress": progress
            }
        }
        await self._broadcast_to_job(job_id, message)
    
    async def broadcast_iteration(self, job_id: str, iteration_data: dict) -> None:
        """
        Broadcast iteration update to all clients connected to a specific job.
        
        Args:
            job_id: Research job ID
            iteration_data: Dictionary containing iteration information
        """
        message = {
            "type": "iteration",
            "job_id": job_id,
            "data": iteration_data
        }
        await self._broadcast_to_job(job_id, message)
    
    async def broadcast_source(self, job_id: str, source_data: dict) -> None:
        """
        Broadcast source discovery update to all clients connected to a specific job.
        
        Args:
            job_id: Research job ID
            source_data: Dictionary containing source information
        """
        message = {
            "type": "source",
            "job_id": job_id,
            "data": source_data
        }
        await self._broadcast_to_job(job_id, message)
    
    async def broadcast_report(self, job_id: str, report: str) -> None:
        """
        Broadcast final report to all clients connected to a specific job.
        
        Args:
            job_id: Research job ID
            report: Final research report text
        """
        message = {
            "type": "report",
            "job_id": job_id,
            "data": {
                "report": report
            }
        }
        await self._broadcast_to_job(job_id, message)
    
    async def broadcast_error(self, job_id: str, error_message: str) -> None:
        """
        Broadcast error message to all clients connected to a specific job.
        
        Args:
            job_id: Research job ID
            error_message: Error message to send
        """
        message = {
            "type": "error",
            "job_id": job_id,
            "data": {
                "error": error_message
            }
        }
        await self._broadcast_to_job(job_id, message)
    
    async def broadcast(self, message: dict) -> None:
        """
        Broadcast a message to all connected WebSocket clients (legacy method).
        Note: Prefer using job-specific broadcast methods instead.
        
        Args:
            message: Message dictionary to send
        """
        job_id = message.get("job_id")
        if job_id:
            await self._broadcast_to_job(job_id, message)
        else:
            logger.warning("Broadcast message missing job_id, skipping")


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, job_id: str) -> None:
    """
    WebSocket endpoint for real-time research job updates.
    
    Args:
        websocket: WebSocket connection
        job_id: Research job ID to subscribe to
    """
    try:
        await manager.connect(websocket, job_id)
        logger.info(f"WebSocket connection established for job {job_id}")
    except Exception as e:
        logger.error(f"Error accepting WebSocket connection for job {job_id}: {e}", exc_info=True)
        return
    
    try:
        # Send initial connection confirmation
        try:
            await manager.send_personal_message({
                "type": "connected",
                "job_id": job_id,
                "data": {"message": "WebSocket connected successfully"}
            }, websocket)
            logger.info(f"Sent initial connection message for job {job_id}")
        except Exception as e:
            logger.error(f"Error sending initial connection message for job {job_id}: {e}", exc_info=True)
            # Don't return, continue to the message loop
        
        # Keep connection alive and listen for messages
        while True:
            try:
                # Wait for message from client (this will block until a message is received)
                data = await websocket.receive_text()
                logger.debug(f"Received raw message for job {job_id}: {data[:100]}...")
                
                try:
                    message = json.loads(data)
                    logger.info(f"Received WebSocket message for job {job_id}: {message}")
                    
                    # Handle client messages (ping, pause, cancel, etc.)
                    msg_type = message.get("type", "")
                    if msg_type == "ping":
                        # Respond to ping with pong
                        try:
                            await manager.send_personal_message({
                                "type": "pong",
                                "job_id": job_id,
                                "data": {"message": "pong"}
                            }, websocket)
                            logger.debug(f"Sent pong response for job {job_id}")
                        except Exception as e:
                            logger.error(f"Error sending pong for job {job_id}: {e}", exc_info=True)
                    else:
                        # Echo other messages back or handle them
                        logger.debug(f"Unhandled message type: {msg_type} for job {job_id}")
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received from client for job {job_id}: {e}. Data: {data[:100]}")
                    try:
                        await manager.send_personal_message({
                            "type": "error",
                            "job_id": job_id,
                            "data": {"error": "Invalid JSON format"}
                        }, websocket)
                    except Exception as send_error:
                        logger.error(f"Error sending error message for job {job_id}: {send_error}", exc_info=True)
                    
            except WebSocketDisconnect:
                # This is expected when client disconnects
                logger.info(f"WebSocket disconnected normally for job {job_id}")
                break
            except Exception as e:
                logger.error(f"Error processing WebSocket message for job {job_id}: {e}", exc_info=True)
                # Continue the loop to keep connection alive unless it's a disconnect
                # Check if websocket is still connected
                try:
                    # Try to send an error message to see if connection is still alive
                    await manager.send_personal_message({
                        "type": "error",
                        "job_id": job_id,
                        "data": {"error": "Internal error processing message"}
                    }, websocket)
                except Exception:
                    # Connection is likely dead, break out of loop
                    logger.warning(f"Connection appears to be dead for job {job_id}, breaking loop")
                    break
                continue
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for job {job_id}")
    except Exception as e:
        logger.error(f"Unexpected error in WebSocket endpoint for job {job_id}: {e}", exc_info=True)
    finally:
        # Always clean up the connection
        try:
            manager.disconnect(websocket, job_id)
        except Exception as e:
            logger.error(f"Error during WebSocket disconnect cleanup for job {job_id}: {e}", exc_info=True)

