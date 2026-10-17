// Adicione os blocos Using no topo do ficheiro C#
using NetMQ;
using NetMQ.Sockets;
using System.Threading.Tasks;
using Newtonsoft.Json; // Precisa desta DLL no NT8 para ler o JSON
using System.Collections.Generic;

// Dentro da sua classe de Estratégia (ex: public class ZMQServerStrategy : Strategy)

private ResponseSocket serverSocket;
private Task serverTask;
private bool isRunning;

protected override void OnStateChange()
{
    if (State == State.SetDefaults)
    {
        Description = @"Ponte ZMQ para receber ordens do Python SUGF v3.0";
        Name = "ZMQ_Bridge_Server";
        Calculate = Calculate.OnEachTick;
    }
    else if (State == State.DataLoaded)
    {
        // Inicia o Servidor ZMQ numa thread separada para não bloquear a UI do NT8
        isRunning = true;
        serverTask = Task.Run(() => StartZMQServer());
        Print("Servidor ZMQ Iniciado na porta 5555.");
    }
    else if (State == State.Terminated)
    {
        // Limpeza rigorosa quando o script é desligado
        isRunning = false;
        if (serverSocket != null)
        {
            serverSocket.Dispose();
        }
        NetMQConfig.Cleanup();
        Print("Servidor ZMQ Desligado.");
    }
}

private void StartZMQServer()
{
    using (serverSocket = new ResponseSocket("@tcp://localhost:5555"))
    {
        while (isRunning)
        {
            string message = string.Empty;
            // Tenta receber a mensagem sem bloquear eternamente
            if (serverSocket.TryReceiveFrameString(System.TimeSpan.FromMilliseconds(100), out message))
            {
                // Processa o JSON recebido do Python
                dynamic payload = JsonConvert.DeserializeObject(message);
                string action = payload.action;

                string responseJson = "{\"status\":\"error\", \"message\":\"Unknown action\"}";

                if (action == "GET_TICK")
                {
                    // Envia o preço de fecho atual
                    responseJson = JsonConvert.SerializeObject(new
                    {
                        status = "success",
                        instrument = Instrument.FullName,
                        price = Close[0]
                    });
                }
                else if (action == "BUY" || action == "SELL")
                {
                    int qty = payload.quantity;
                    // O NT8 exige que a execução da ordem ocorra na thread principal (Dispatcher)
                    Dispatcher.InvokeAsync(() =>
                    {
                        if (action == "BUY")
                            EnterLong(qty, "ZMQ_Buy");
                        else
                            EnterShort(qty, "ZMQ_Sell");
                    });

                    responseJson = JsonConvert.SerializeObject(new
                    {
                        status = "success",
                        message = $"Ordem {action} de {qty} contratos enviada."
                    });
                }

                // Devolve a resposta ao Python
                serverSocket.SendFrame(responseJson);
            }
        }
    }
}
