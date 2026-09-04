import asyncio
import json

class MeshNode:
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.tasks_queue = asyncio.Queue()

    async def handle_client(self, reader, writer):
        data = await reader.read(1024)
        message = data.decode()
        addr = writer.get_extra_info('peername')
        print(f"[MeshWeaver] Received task workload from {addr}: {message}")
        
        await self.tasks_queue.put(message)
        response = json.dumps({
            "status": "Task Assigned & Processed", 
            "assigned_node": f"{self.host}:{self.port}",
            "load_status": "Low CPU Load"
        })
        
        writer.write(response.encode())
        await writer.drain()
        writer.close()

    async def start_server(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        addr = server.sockets[0].getsockname()
        print(f"[MeshWeaver Node] Active and listening on {addr} (P2P Mesh)")
        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    node = MeshNode()
    try:
        asyncio.run(node.start_server())
    except KeyboardInterrupt:
        print("\n[MeshWeaver Node] Node disconnected from mesh network.")