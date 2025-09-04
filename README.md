# Desafio Websocket

desenvolvido com FastAPI e WebSocket.

##  Detalhes Importantes:

 - Tive problemas com o primeiro repositório, mas no fim do readme, tem um print do histórico de commits. 
 - O áudio "Completo Linha a Linha" vai explicar o código mais detalhadamente. Introduzindo do por quê usei as ferramentas que usei.
 - O áudio "Reduzido Cortado" vai explicar apenas o código principal de maneira mais breve.

##  O que ele faz?

- **Websocket** - conecta várias pessoas ao mesmo tempo
- **Datetime** - envia o horário atual a cada segundo
- **Calculadora Fibonacci** 
- **Interface** 
- **Cliente Python**

##  Tecnologias

- **Backend**: FastAPI (Python)
- **WebSocket**: Conexões em tempo real
- **Banco**: SQLite
- **Docker**: Componentização
- **Interface**

##  Estrutura

```
WebSocket-BSA/
├── app/                   # Código principal
│   ├── main.py           # Servidor do chat
│   ├── client.py         # Cliente Python
│   └── __init__.py       # Configuração do pacote
├── explainChallenge/      # Áudios Explicando o Código
├── requirements.txt       # Dependências
├── Dockerfile            # Container Docker
├── docker-compose.yml    # Orquestração
└── README.md             # Este arquivo
```

##  Como usar

### Opção 1: Rodar localmente (recomendado pra testar)

1. **Instalar dependências**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Rodar o servidor**:
   ```bash
   python app/main.py
   ```

3. **Abrir no navegador**:
   - Vai para http://localhost:8000
   - Clica em "Conectar"

### Opção 2: Docker

```bash
# Construir e rodar com compose
docker compose up -d --build

```

##  Testando

### Cliente Python
```bash
python app/client.py
```

##  Endpoints

- `GET /` - Interface do chat
- `GET /health` - Status do sistema
- `WS /ws` - Conexão WebSocket

##  Como funciona o chat

### Mensagens que você envia:
```json
{
  "type": "fibonacci",
  "input": 10
}
```

### Mensagens que você recebe:
```json
// Boas-vindas
{
  "type": "welcome",
  "message": "Você é o usuário user_1",
  "client_id": "user_1"
}

// Tempo (a cada segundo)
{
  "type": "time",
  "time": "14:30:25"
}

// Resposta Fibonacci
{
  "type": "fibonacci",
  "input": 10,
  "result": 55
}
```

##  Banco de dados

Usa SQLite com uma tabela simples:
- `connected_users` - Rastreia quem está online

##  Monitoramento

- Logs de conexões e desconexões
- Status de saúde do sistema
- Número de usuários ativos

##  Docker

- **Dockerfile**: Python 3.11-slim
- **Docker Compose**: Serviços organizados
- **Porta**: 8000

##  Tratamento de erros

- Reconexão automática
- Validação de entrada
- Logs detalhados
- Limpeza de conexões mortas

##  Performance

- Operações assíncronas
- Broadcast eficiente
- Limpeza automática

##  Configuração

- **Porta**: 8000
- **Banco**: SQLite local
- **Logs**: Em tempo real

##  Licença

Projeto desenvolvido como desafio técnico.

##  Desenvolvedor

**F. Ricardo** - Desenvolveu este chat com FastAPI e WebSocket, seguindo boas práticas de programação assíncrona. O projeto é funcional, bem estruturado e fácil de entender e modificar. 