import asyncio
import json
from datetime import datetime
from typing import Dict
import sqlite3

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

class GerenciadorWebSocket:
    def __init__(self):
        self.conexoes: Dict[str, WebSocket] = {}
        self.contador_usuarios = 0
        self._iniciar_banco()

    def _iniciar_banco(self):
        conn = sqlite3.connect("websocket_system.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios_conectados (
                user_id TEXT PRIMARY KEY,
                conectado_em TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _adicionar_usuario_banco(self, user_id):
        conn = sqlite3.connect("websocket_system.db")
        cursor = conn.cursor()
        cursor.execute("REPLACE INTO usuarios_conectados (user_id, conectado_em) VALUES (?, ?)",
                       (user_id, datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def _remover_usuario_banco(self, user_id):
        conn = sqlite3.connect("websocket_system.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios_conectados WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()

    async def adicionar_usuario(self, websocket: WebSocket) -> str:
        await websocket.accept()

        self.contador_usuarios += 1
        user_id = f"usuario_{self.contador_usuarios}"
        self.conexoes[user_id] = websocket
        self._adicionar_usuario_banco(user_id)
        return user_id

    def remover_usuario(self, user_id: str):
        if user_id in self.conexoes:
            del self.conexoes[user_id]
        self._remover_usuario_banco(user_id)

    async def enviar_para_usuario(self, mensagem: str, user_id: str):
        if user_id in self.conexoes:
            try:
                await self.conexoes[user_id].send_text(mensagem)
            except:
                self.remover_usuario(user_id)

    async def enviar_para_todos(self, mensagem: str):
        for user_id, conexao in list(self.conexoes.items()):
            try:
                await conexao.send_text(mensagem)
            except:
                self.remover_usuario(user_id)

hub = GerenciadorWebSocket()

def calcular_fibonacci(n: int) -> int:
    """Calcula o n-ésimo número de Fibonacci"""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

async def enviar_data_hora():
    while True:
        try:
            agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            mensagem = json.dumps({"type": "datetime", "datetime": agora})
            await hub.enviar_para_todos(mensagem)
            await asyncio.sleep(1)
        except:
            await asyncio.sleep(1)

app = FastAPI(title="WebSocket-BSA")

@app.on_event("startup")
async def ao_iniciar():
    asyncio.create_task(enviar_data_hora())

@app.get("/", response_class=HTMLResponse)
async def get():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>BSA-Tech</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .container { max-width: 600px; margin: 0 auto; }
                .status { padding: 10px; margin: 10px 0; border: 1px solid #ccc; }
                .connected { background-color: #d4edda; }
                .disconnected { background-color: #f8d7da; }
                .message { padding: 5px; margin: 5px 0; border-left: 3px solid #007bff; }
                .datetime { padding: 5px; margin: 5px 0; border-left: 3px solid #28a745; background-color: #f8f9fa; }
                input, button { padding: 8px; margin: 5px; }
                button { background-color: #007bff; color: white; border: none; cursor: pointer; }
                #messages { max-height: 300px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>WebSocket-BSA</h1>
                
                <div id="status" class="status disconnected">Desconectado</div>
                
                <div>
                    <button onclick="connect()">Conectar</button>
                    <button onclick="disconnect()">Desconectar</button>
                </div>
                
                <div>
                    <input type="number" id="fibonacciInput" placeholder="Digite um número para Fibonacci" min="0">
                    <button onclick="sendFibonacci()">Calcular</button>
                </div>
                
                <h3>Mensagens:</h3>
                <div id="messages"></div>
            </div>

            <script>
                let ws = null;
                let userId = null;

                function connect() {
                    ws = new WebSocket('ws://localhost:8000/ws');
                    
                    ws.onopen = function(event) {
                        document.getElementById('status').textContent = 'Conectado';
                        document.getElementById('status').className = 'status connected';
                        addMessage('Sistema', 'Conectado ao chat!');
                    };
                    
                    ws.onmessage = function(event) {
                        const data = JSON.parse(event.data);
                        if (data.type === 'datetime') {
                            addDateTimeMessage(data.datetime);
                        } else if (data.type === 'fibonacci') {
                            addMessage('Fibonacci', data.input + ' = ' + data.result);
                        } else if (data.type === 'welcome') {
                            addMessage('Servidor', data.message);
                        } else {
                            addMessage('Servidor', JSON.stringify(data));
                        }
                    };
                    
                    ws.onclose = function(event) {
                        document.getElementById('status').textContent = 'Desconectado';
                        document.getElementById('status').className = 'status disconnected';
                        addMessage('Sistema', 'Desconectado do chat');
                    };
                    
                    ws.onerror = function(error) {
                        addMessage('Erro', 'Problema na conexão');
                    };
                }
                
                function disconnect() {
                    if (ws) {
                        ws.close();
                        ws = null;
                    }
                }
                
                function sendFibonacci() {
                    if (ws && ws.readyState === WebSocket.OPEN) {
                        const input = document.getElementById('fibonacciInput').value;
                        if (input) {
                            const message = {
                                type: 'fibonacci',
                                input: parseInt(input)
                            };
                            ws.send(JSON.stringify(message));
                            addMessage('Você', 'Pedindo Fibonacci(' + input + ')');
                        }
                    } else {
                        addMessage('Erro', 'Conecte-se primeiro!');
                    }
                }
                
                function addMessage(sender, message) {
                    const messagesDiv = document.getElementById('messages');
                    const messageDiv = document.createElement('div');
                    messageDiv.className = 'message';
                    messageDiv.innerHTML = '<strong>' + sender + ':</strong> ' + message;
                    messagesDiv.appendChild(messageDiv);
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                }
                
                function addDateTimeMessage(datetime) {
                    const messagesDiv = document.getElementById('messages');
                    const messageDiv = document.createElement('div');
                    messageDiv.className = 'datetime';
                    messageDiv.innerHTML = '<strong>Data/Hora:</strong> ' + datetime;
                    messagesDiv.appendChild(messageDiv);
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                }
            </script>
        </body>
    </html>
    """

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    user_id = None
    try:
        user_id = await hub.adicionar_usuario(websocket)

        mensagem_boas_vindas = json.dumps({
            "type": "welcome",
            "message": f"Bem-vindo! Você é o {user_id}",
            "client_id": user_id,
        })
        await hub.enviar_para_usuario(mensagem_boas_vindas, user_id)

        while True:
            data = await websocket.receive_text()
            try:
                mensagem = json.loads(data)

                if mensagem.get("type") == "fibonacci":
                    n = mensagem.get("input", 0)
                    if n < 0:
                        erro = json.dumps({
                            "type": "error", 
                            "message": "Por favor, envie apenas números positivos!"
                        })
                        await hub.enviar_para_usuario(erro, user_id)
                    else:
                        resultado = calcular_fibonacci(n)
                        resposta = json.dumps({
                            "type": "fibonacci", 
                            "input": n, 
                            "result": resultado
                        })
                        await hub.enviar_para_usuario(resposta, user_id)

                else:
                    eco = json.dumps({"type": "echo", "message": mensagem})
                    await hub.enviar_para_usuario(eco, user_id)

            except:
                pass

    except WebSocketDisconnect:
        pass
    except:
        pass
    finally:
        # Quando o cliente desconecta
        if user_id:
            hub.remover_usuario(user_id)

@app.get("/health")
async def checar_status():

    return {
        "status": "tudo certo!",
        "usuarios_online": len(hub.conexoes),
        "timestamp": datetime.now().isoformat(),
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)