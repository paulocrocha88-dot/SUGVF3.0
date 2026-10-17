import zmq
import zmq.asyncio
import json
import logging
from typing import Optional, Dict, Any

class NinjaBridge:
    def __init__(self, port: int = 5555):
        self.logger = logging.getLogger("NinjaBridge")
        self.port = port
        self.context = zmq.asyncio.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(f"tcp://localhost:{self.port}")
        self.logger.info(f"NinjaBridge initialized, connecting to tcp://localhost:{self.port} with REQ socket")

    async def send_order(self, action: str, quantity: int, ticker: Optional[str] = None, price: Optional[float] = None) -> Dict[str, Any]:
        """
        Sends an order (or any message with action/quantity) to the NT8 ZMQ server
        and awaits the response.
        """
        payload = {
            "action": action,
            "quantity": quantity
        }
        if ticker:
            payload["ticker"] = ticker
        if price is not None:
            payload["price"] = price

        message_str = json.dumps(payload)
        self.logger.debug(f"Sending message to NT8: {message_str}")

        try:
            await self.socket.send_string(message_str)
            response_str = await self.socket.recv_string()
            self.logger.debug(f"Received response from NT8: {response_str}")
            return json.loads(response_str)
        except Exception as e:
            self.logger.error(f"Error communicating with NT8 via ZMQ: {e}")
            return {"status": "error", "message": str(e)}

    def close(self):
        self.socket.close()
        self.context.term()
        self.logger.info("NinjaBridge connection closed")
