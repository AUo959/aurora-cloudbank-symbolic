import os

from fastapi.testclient import TestClient

os.environ["AIF_TOKEN"] = "test-token"

from services.aif_hub import app  # noqa: E402


def test_websocket_broadcast():
    client = TestClient(app)
    with client.websocket_connect("/ws", headers={"Authorization": "Bearer test-token"}) as ws1:
        with client.websocket_connect("/ws", headers={"Authorization": "Bearer test-token"}) as ws2:
            ws1.send_text("anchor")
            data = ws2.receive_text()
            assert data == "anchor"
