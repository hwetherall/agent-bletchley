"""
Test script for WebSocket connection to the research job endpoint.
"""
import asyncio
import websockets
import json


async def test_websocket():
    """Test WebSocket connection to research job endpoint."""
    uri = "ws://localhost:8000/ws/research/test-job-123"
    
    # First, check if server is running by testing HTTP endpoint
    import httpx
    try:
        with httpx.Client(timeout=2.0) as client:
            resp = client.get("http://localhost:8000/health")
            if resp.status_code == 200:
                print("✓ Server is running")
            else:
                print(f"⚠ Server responded with status {resp.status_code}")
    except httpx.ConnectError:
        print(f"✗ Cannot reach server at http://localhost:8000")
        print(f"\n💡 Make sure the server is running:")
        print(f"   cd backend")
        print(f"   .\\venv\\Scripts\\Activate.ps1")
        print(f"   uvicorn app.main:app --reload")
        return
    except Exception as e:
        print(f"✗ Error checking server: {e}")
        print(f"\n💡 Make sure the server is running:")
        print(f"   cd backend")
        print(f"   .\\venv\\Scripts\\Activate.ps1")
        print(f"   uvicorn app.main:app --reload")
        return
    
    try:
        print(f"\nConnecting to {uri}...")
        async with websockets.connect(uri, ping_interval=20, ping_timeout=10) as websocket:
            print("✓ Connected! Waiting for initial message from server...")
            
            # Create a task to receive messages
            async def receive_messages():
                try:
                    while True:
                        # Use a timeout to detect if connection is still alive
                        try:
                            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                            data = json.loads(message)
                            print(f"\n[Received] Type: {data.get('type', 'unknown')}")
                            print(f"         Data: {json.dumps(data.get('data', {}), indent=2)}")
                        except asyncio.TimeoutError:
                            print("(Still waiting for messages...)")
                            continue
                except websockets.exceptions.ConnectionClosed as e:
                    print(f"\n✗ Connection closed by server (code: {e.code}, reason: {e.reason})")
                    return
                except Exception as e:
                    print(f"\n✗ Error receiving messages: {e}")
                    import traceback
                    traceback.print_exc()
                    return
            
            # Create a task to send ping messages periodically
            async def send_ping():
                await asyncio.sleep(1)  # Wait a bit before first ping
                ping_count = 0
                while True:
                    try:
                        ping_count += 1
                        await websocket.send(json.dumps({
                            "type": "ping", 
                            "message": f"Ping #{ping_count} from test client"
                        }))
                        print(f"\n✓ Sent ping #{ping_count}")
                        await asyncio.sleep(3)  # Send ping every 3 seconds
                    except websockets.exceptions.ConnectionClosed:
                        return
                    except Exception as e:
                        print(f"\n✗ Error sending ping: {e}")
                        return
            
            # Run both tasks concurrently
            try:
                await asyncio.gather(
                    receive_messages(),
                    send_ping()
                )
            except KeyboardInterrupt:
                print("\n\n✓ Test interrupted by user (Ctrl+C)")
                print("✓ WebSocket connection test completed successfully!")
                
    except websockets.exceptions.InvalidURI:
        print(f"✗ Invalid URI: {uri}")
    except websockets.exceptions.InvalidStatus as e:
        print(f"✗ Connection failed with status {e.status_code}: {e.status_line}")
    except ConnectionRefusedError:
        print("✗ Connection refused. Is the server running on port 8000?")
    except websockets.exceptions.ConnectionClosed as e:
        print(f"✗ Connection closed (code: {e.code}, reason: {e.reason})")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_websocket())

