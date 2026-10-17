import zmq
import json
import time

def enviar_ordem_sugf():
    print("Iniciando o cliente ZMQ do SUGF v3.0...")

    context = zmq.Context()
    socket = context.socket(zmq.REQ)

    print("Conectando ao NinjaTrader em tcp://localhost:5555...")
    socket.connect("tcp://localhost:5555")

    ordem_compra = {
        "action": "BUY",
        "quantity": 2,
        "instrument": "NQ"
    }

    print(f"Enviando ordem: {ordem_compra}")
    socket.send_string(json.dumps(ordem_compra))

    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)

    if poller.poll(3000):
        resposta = socket.recv_string()
        print(f"✅ Resposta recebida do NinjaTrader: {resposta}")
    else:
        print("❌ Timeout: O NinjaTrader não respondeu. A Estratégia C# está ativada no gráfico?")

if __name__ == "__main__":
    enviar_ordem_sugf()
