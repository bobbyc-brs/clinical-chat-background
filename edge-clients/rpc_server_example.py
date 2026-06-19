from pyrpc.RPCServer import RPCServer
from pyrpc.RPCServerHandler import RPCServerHandler

class TranscriptHandler(RPCServerHandler):
    def handle_push_transcript(self, payload):
        segments = payload.get("segments", [])
        print(f"received {len(segments)} segment(s) from {payload.get('speaker_role')}")
        for seg in segments:
            print(seg.get("text"))
        return {"ok": True, "received": len(segments)}

if __name__ == "__main__":
    server = RPCServer(("0.0.0.0", 9090), TranscriptHandler)
    print("PyRPC server listening on 0.0.0.0:9090")
    server.serve_forever()
