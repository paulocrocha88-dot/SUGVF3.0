import zmq
import json
import logging

logger = logging.getLogger(__name__)

class NinjaBridge:
    def __init__(self, port=5555):
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(f"tcp://*:{self.port}")
        logger.info(f"NinjaBridge inicializado. PUB socket na porta {self.port}.")

    def enviar_ordem(self, ticker, direcao, preco):
        payload = {
            "ticker": ticker,
            "action": direcao,
            "price": preco
        }
        message = json.dumps(payload)
        self.socket.send_string(message)
        logger.info(f"Ordem enviada: {message}")
