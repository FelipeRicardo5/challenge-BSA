import asyncio
import json
import websockets

# conecta no servidor WebSocket, envia comandos e mostra as respostas

class ClienteWebSocket:
    def __init__(self, endereco="ws://localhost:8000/ws"):
        self.endereco = endereco
        self.websocket = None
        self.id_usuario = None

    async def conectar(self):
        try:
            self.websocket = await websockets.connect(self.endereco)
            print("Conectado ao servidor!")
            mensagem = await self.websocket.recv()
            dados = json.loads(mensagem)
            self.id_usuario = dados.get('client_id')
            print(f"Seu ID de usuário: {self.id_usuario}")
            return True
        except Exception as erro:
            print(f"Erro ao conectar: {erro}")
            return False

    async def desconectar(self):
        if self.websocket:
            await self.websocket.close()
            print("Desconectado do servidor.")

    async def enviar_mensagem(self, mensagem):
        if self.websocket:
            try:
                await self.websocket.send(json.dumps(mensagem))
                print(f"Mensagem enviada: {mensagem}")
            except Exception as erro:
                print(f"Erro ao enviar mensagem: {erro}")

    async def pedir_fibonacci(self, n):
        mensagem = {
            "type": "fibonacci",
            "input": n
        }
        await self.enviar_mensagem(mensagem)

    async def ouvir_mensagens(self):
        if not self.websocket:
            return
        try:
            async for mensagem in self.websocket:
                try:
                    dados = json.loads(mensagem)
                    if dados.get("type") == "datetime":
                        print(f"Data/Hora do servidor: {dados.get('datetime')}")
                    elif dados.get("type") == "fibonacci":
                        print(f"Fibonacci({dados.get('input')}) = {dados.get('result')}")
                    elif dados.get("type") == "welcome":
                        print(f"Boas-vindas: {dados.get('message')}")
                    elif dados.get("type") == "error":
                        print(f"Erro do servidor: {dados.get('message')}")
                    else:
                        print(f"Mensagem recebida: {dados}")
                except json.JSONDecodeError:
                    print(f"Mensagem inválida recebida: {mensagem}")
        except websockets.exceptions.ConnectionClosed:
            print("Conexão fechada pelo servidor.")
        except Exception as erro:
            print(f"Erro ao ouvir mensagens: {erro}")

async def main():
    cliente = ClienteWebSocket()

    conectado = await cliente.conectar()
    if not conectado:
        print("Não foi possível conectar. Verifique se o servidor está rodando.")
        return


    tarefa_ouvir = asyncio.create_task(cliente.ouvir_mensagens())

    try:
        print("Esperando 2 segundos...")
        await asyncio.sleep(2)

        print("Testando Fibonacci...")
        numeros = [5, 10, 15, 20]
        for n in numeros:
            await cliente.pedir_fibonacci(n)
            await asyncio.sleep(1)

        print("Aguardando mensagens do servidor por mais 15 segundos...")
        await asyncio.sleep(15)

    except KeyboardInterrupt:
        print("Programa interrompido pelo usuário.")
    finally:
        await cliente.desconectar()
        tarefa_ouvir.cancel()

if __name__ == "__main__":
    asyncio.run(main())