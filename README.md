# 💧 Agente inteligente de criação de encomendas para empresas de água 💧

Este projeto é um MVP de um assistente de WhatsApp alimentado por IA, desenvolvido com **CrewAI** e **Python**. 

O objectivo deste projeto é criar um assistente virtual, via whatsapp, que possa criar encomendas automaticamente no ERP, com base nas mensagens recebidas dos clientes. O sistema vai validar se o cliente existe (ou se o encontra), se tem dividas, e quando poderá fazer a entrega da encomenda. Deve ser um assistente cordial, educado e eficiente.

## 🎬 Vídeo de Apresentação

Veja o vídeo abaixo para entender o propósito do projeto, conhecer a arquitetura por trás dos Agentes de IA e ver uma demonstração passo a passo de como configurar e testar o sistema.

<video src="./presentation_1080p.mp4" controls="controls" style="max-width: 100%;">
  O seu navegador não suporta a visualização de vídeo. Pode <a href="./presentation_1080p.mp4">descarregar o vídeo aqui</a>.
</video>

*(Nota: O ficheiro `presentation_1080p.mp4` encontra-se na raiz deste repositório).*

---

## 🏗️ Arquitetura
- **n8n:** Gestão de Webhooks e integração com WhatsApp/Telegram.
- **Ollama (Qwen 2.5 14B):** Processamento de Linguagem Natural a correr localmente para garantir 100% de privacidade dos dados.
- **CrewAI:** Orquestração de 4 Agentes Especializados (Atendimento, Financeiro, Logística e Comunicação).
- **Python (Flask):** Criação da API REST e gestão do Roteamento Condicional (Multi-Tier Logic) para proteção de regras de negócio estritas.

## ✨ Funcionalidades
- Triagem em tempo real com base no número de telefone.
- Consulta de ERP simulado (Tools).
- Bloqueio automático de encomendas para clientes com dívidas > 30 dias.
- Memória de sessão para contexto de conversação natural.

## 🔐 Configuração de Segurança (.env)
Para que o código da API (`crewAI.py`) funcione corretamente na sua máquina, precisa de configurar as variáveis de ambiente que ligam o CrewAI ao modelo local do Ollama.

1. Na raiz do projeto, crie um ficheiro chamado `.env`.
2. Abra o ficheiro e adicione as seguintes credenciais:

```env
OPENAI_API_BASE="http://localhost:11434/v1"
OPENAI_API_KEY="ollama"
OPENAI_MODEL_NAME="qwen2.5:14b"
```

## 🚀 Como Testar Localmente (Modo Simulador CLI)
Para facilitar a avaliação da lógica dos Agentes de Inteligência Artificial sem necessidade de configurar webhooks ou o n8n, criei um **Simulador de Terminal CLI** *Plug and Play*.

### Pré-requisitos:
1. Ter o Ollama instalado e a correr o modelo local (`qwen2.5:14b`).
2. Ter o Python 3 instalado na sua máquina.

### Instalação:
Antes de correr o código pela primeira vez, instale as dependências necessárias através do terminal:
```bash
pip install -r requirements.txt
```

### Passo a Passo para Testar:
1. Abra o terminal na pasta do projeto.
2. Execute o simulador:
   ```bash
   python3 simulador_terminal.py
   ```
3. O terminal irá pedir para inserir um número de telefone simulado. Pode usar:
   - `912345678` (Clínica Sorriso - Cliente sem dívidas, testa o fluxo de Logística e agendamento).
   - `961112233` (João Silva - Cliente com dívida, testa o bloqueio Financeiro e cálculos de datas-limite).
   - Qualquer outro número (Testa o fluxo de Desconhecidos/Triagem).
4. Converse naturalmente com a IA e observe o raciocínio dos agentes impresso em tempo real no ecrã! Digite `sair` para terminar a sessão.

---

## 🌐 Como Testar em Modo Produção (n8n + Telegram + Flask)

Se desejar testar a arquitetura completa com a integração visual, o projeto inclui dois workflows pré-configurados do n8n.

### Passo 1: Levantar o Servidor de Inteligência Artificial (Flask)
No terminal, certifique-se de que tem o `.env` configurado e inicie a API:
```bash
python3 crewAI.py
```
*(A API ficará à escuta na porta 5001).*

### Passo 2: Importar e Testar os Workflows no n8n
Na sua instância local do n8n, crie um workflow vazio, clique em **Import from File** e escolha uma das seguintes opções incluídas neste repositório:

#### Opção A: Chat Nativo do n8n (`Water_Agent_Chat_Simulation.json`)
Ideal para testar rapidamente sem configurar aplicações externas.
- **Cenário Simulado:** Está pré-configurado com o número `961112233` (João Silva - Cliente com Dívida). 
- **Como testar:** Clique em "Test Workflow" e use a janela de chat do n8n para falar com o bot e testar o bloqueio financeiro.

#### Opção B: Integração com Telegram (`Water_Agent_Telegram.json`)
Ideal para ver a IA a funcionar numa aplicação de mensagens real. Como o Telegram exige um URL público para enviar dados, é necessário expor o n8n à internet.
- **Cenário Simulado:** Está pré-configurado com o número `912345678` (Clínica Dentária - Cliente Aprovado).
- **Como testar:** 1. Num novo terminal, inicie o ngrok para expor a porta do n8n (por norma a 5678):
     ```bash
     ngrok http 5678
     ```
  2. Aceda ao n8n através do **link HTTPS** gerado pelo ngrok (isto garante que o nó do Telegram regista o Webhook com o URL público correto).
  3. Adicione as suas credenciais de Bot do Telegram no nó "Telegram Trigger" e no nó final "Send a text message".
  4. Ative o workflow ou clique em "Test Workflow".
  5. Vá ao seu telemóvel, abra o seu bot no Telegram e envie: *"Preciso de 3 garrafões"*.

*(Nota: Pode alterar os números de telefone simulados a qualquer momento no nó "Edit Fields" de qualquer um dos workflows para explorar as diferentes rotas de decisão dos Agentes).*