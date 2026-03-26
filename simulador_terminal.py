from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
import json
import os
from datetime import datetime, timedelta

# Configuração do LLM
os.environ["OPENAI_API_BASE"] = "http://localhost:11434/v1"
os.environ["OPENAI_API_KEY"] = "ollama"
os.environ["OPENAI_MODEL_NAME"] = "qwen2.5:14b"

@tool("consultar_erp")
def consultar_ficha_cliente(telefone: str) -> str:
    """
    Usa esta ferramenta APENAS para procurar os dados de um cliente no ERP através do seu número de telefone. 
    """
    db_simulada_erp = {
        "912345678": {
            "nome": "Clínica Dentária Sorriso",
            "status": "Ativo",
            "sector": "Comercial",
            "consumo_medio_garrafoes": 8,
            "rota_habitual": "Rota_Sul_04",
            "saldo_pendente_eur": 0.00,
            "dias_atraso": 0,
            "dados_pagamento": "N/A"
        },
        "961112233": {
            "nome": "João Silva (Particular)",
            "status": "Em Risco",
            "sector": "Residencial",
            "consumo_medio_garrafoes": 3,
            "rota_habitual": "Rota_Centro_02",
            "saldo_pendente_eur": 18.50,
            "dias_atraso": 35, 
            "dados_pagamento": "Entidade: 12345 | Ref: 987 654 321 | Valor: 18,50€"
        }
    }
    cliente = db_simulada_erp.get(telefone)
    if cliente:
        return json.dumps(cliente, ensure_ascii=False, indent=2)
    else:
        return "Atenção: Cliente não encontrado no ERP com este número de telefone."

@tool("verificar_rota")
def verificar_disponibilidade_rota(rota_habitual: str) -> str:
    """
    Usa esta ferramenta APENAS para verificar se uma rota tem capacidade hoje.
    """
    db_simulada_rotas = {
        "Rota_Sul_04": {
            "estado": "Em curso",
            "espaco_livre_garrafoes": 15,
            "tecnico_pou_disponivel": True,
            "notas": "O técnico Carlos está na zona."
        },
        "Rota_Centro_02": {
            "estado": "Fechada",
            "espaco_livre_garrafoes": 0,
            "tecnico_pou_disponivel": False,
            "notas": "Carrinha cheia."
        }
    }
    rota = db_simulada_rotas.get(rota_habitual)
    if rota:
        return json.dumps(rota, ensure_ascii=False, indent=2)
    else:
        return "Erro: Rota não encontrada no sistema de logística."

@tool("verificar_proximas_entregas")
def verificar_proximas_entregas(rota_habitual: str, quantidade_pedida: int) -> str:
    """
    Consulta as próximas 3 datas ideais de entrega.
    """
    db_simulada_calendario = {
        "Rota_Sul_04": [
            {"data": "2026-03-25", "espaco_livre_garrafoes": 2},
            {"data": "2026-03-26", "espaco_livre_garrafoes": 20},
            {"data": "2026-03-29", "espaco_livre_garrafoes": 15},
            {"data": "2026-04-02", "espaco_livre_garrafoes": 10},
            {"data": "2026-04-05", "espaco_livre_garrafoes": 30}
        ],
        "Rota_Centro_02": [
            {"data": "2026-03-25", "espaco_livre_garrafoes": 0},
            {"data": "2026-03-27", "espaco_livre_garrafoes": 5},
            {"data": "2026-03-30", "espaco_livre_garrafoes": 12},
            {"data": "2026-04-01", "espaco_livre_garrafoes": 18}
        ]
    }
    
    datas_rota = db_simulada_calendario.get(rota_habitual)
    if not datas_rota:
        return "Erro: Rota não encontrada."
        
    datas_disponiveis = []
    hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    for dia in datas_rota:
        data_obj = datetime.strptime(dia["data"], "%Y-%m-%d")
        if data_obj >= hoje and dia["espaco_livre_garrafoes"] >= quantidade_pedida:
            data_pt = data_obj.strftime("%d-%m-%Y")
            datas_disponiveis.append(data_pt) 
            if len(datas_disponiveis) == 3:
                break
                
    if datas_disponiveis:
        return json.dumps(datas_disponiveis, ensure_ascii=False)
    else:
        return f"Sem disponibilidade de carga nas datas futuras."

# Agentes
agente_atendimento = Agent(
    role='Gestor Sénior de Atendimento ao Cliente',
    goal='Identificar o cliente pelo número de telefone, analisar o seu histórico de consumo de água e perceber exatamente o que ele precisa na mensagem atual.',
    backstory="És educado, empático e eficiente. Consultas sempre a ficha do cliente no ERP.",
    verbose=True, allow_delegation=False, tools=[consultar_ficha_cliente]
)

agente_financeiro = Agent(
    role='Analista Financeiro e de Cobranças',
    goal='Verificar o saldo do cliente e bloquear encomendas se existirem dívidas antigas.',
    backstory="Se dias_atraso > 30, BLOQUEADA. Se <= 30, APROVADA.",
    verbose=True, allow_delegation=False
)

agente_logistica = Agent(
    role='Coordenador de Tráfego e Logística',
    goal='Verificar a disponibilidade das carrinhas.',
    backstory="Baseias as tuas decisões APENAS nos dados que a ferramenta de rotas te dá.",
    verbose=True, allow_delegation=False, tools=[verificar_disponibilidade_rota, verificar_proximas_entregas]
)

agente_comunicacao = Agent(
    role='Especialista de Comunicação por WhatsApp',
    goal='Escrever a mensagem final perfeita para enviar ao cliente.',
    backstory="O teu tom é sempre simpático e profissional (PT-PT). Nunca usas jargão.",
    verbose=True, allow_delegation=False
)

# O nosso caderno de memória RAM
historico_conversas = {}

def iniciar_simulador():
    print("="*60)
    print("🚀 SIMULADOR DE TERMINAL - AGENTE DE ÁGUAS FRESCA 💧")
    print("="*60)
    
    telefone_whatsapp = input("📱 Introduza o número de telefone a simular (ex: 912345678 ou 961112233): ").strip()
    print(f"\n✅ Sessão iniciada para o número {telefone_whatsapp}. Digite 'sair' para terminar.\n")

    while True:
        mensagem_cliente = input(f"👤 Cliente ({telefone_whatsapp}): ")
        
        if mensagem_cliente.lower() in ['sair', 'exit', 'quit']:
            print("👋 Simulador encerrado. Bom trabalho!")
            break
            
        # 1.1 GERIR A MEMÓRIA
        if telefone_whatsapp not in historico_conversas:
            historico_conversas[telefone_whatsapp] = []
            
        historico_recente = "\n".join(historico_conversas[telefone_whatsapp][-4:])
        if not historico_recente:
            historico_recente = "Primeiro contacto do cliente."

        # 2. Tempo real
        agora = datetime.now()
        data_hoje = agora.strftime("%Y-%m-%d")
        data_limite_pagamento_MB = (agora + timedelta(days=7)).strftime("%d-%m-%Y")

        # 3. Triagem
        tarefa_analise_inicial = Task(
            description=f"""
            Lê o histórico recente com este cliente:
            ---
            {historico_recente}
            ---
            Mensagem ATUAL do cliente: "{mensagem_cliente}"
            
            Usa a ferramenta 'consultar_erp' com o número {telefone_whatsapp}.
            Se a ferramenta disser "Cliente não encontrado...", escreve APENAS "DESCONHECIDO".
            Caso contrário, extrai os dados. Se a mensagem atual for uma reclamação/ajuste, anota isso no campo 'Pedido'.
            """,
            expected_output="Se não existir: 'DESCONHECIDO'. Se existir: Nome, Rota, Dias de Atraso, Dados de Pagamento e Pedido.",
            agent=agente_atendimento
        )

        equipa_triagem = Crew(agents=[agente_atendimento], tasks=[tarefa_analise_inicial], process=Process.sequential)
        resultado_triagem = str(equipa_triagem.kickoff())

        # 4. IF / ELSE Principal
        if "DESCONHECIDO" in resultado_triagem.upper():
            tarefa_cliente_desconhecido = Task(
                description="O cliente não está no ERP. Escreve UMA única frase em Português pedindo o NIF ou Número de Cliente. Sem aspas.",
                expected_output="Uma frase simples pedindo o NIF.",
                agent=agente_comunicacao
            )
            resultado_final = str(Crew(agents=[agente_comunicacao], tasks=[tarefa_cliente_desconhecido]).kickoff())

        else:
            tarefa_analise_financeira = Task(
                description=f"Lê este relatório: {resultado_triagem}. Se 'Dias de Atraso' > 30, status BLOQUEADO. Se <= 30, APROVADO.",
                expected_output="Status Financeiro: [APROVADO ou BLOQUEADO]\nNome: [Copia]\nRota: [Copia]\nDados de Pagamento: [Copia]\nPedido: [Copia]",
                agent=agente_financeiro
            )
            resultado_financeiro = str(Crew(agents=[agente_financeiro], tasks=[tarefa_analise_financeira]).kickoff())

            if "BLOQUEADO" in resultado_financeiro.upper():
                tarefa_redacao_bloqueado = Task(
                    description=f"""
                    Lê o relatório financeiro: {resultado_financeiro}. Histórico: {historico_recente}. Mensagem atual: "{mensagem_cliente}"
                    REGRAS ABSOLUTAS:
                    1. Começa com "Olá [Nome]!"
                    2. Termina com: "Se necessitar de mais alguma coisa, estou à disposição. 💧🚚 Water you love!"
                    3. LÓGICA: Se 1º contacto, informa bloqueio e lista os Dados de Pagamento. Se perguntar prazos, avisa que o limite é {data_limite_pagamento_MB}. Se só agradecer, responde com simpatia (sem repetir pagamentos).
                    4. NUNCA uses aspas.
                    """,
                    expected_output="Mensagem de WhatsApp limpa.",
                    agent=agente_comunicacao
                )
                resultado_final = str(Crew(agents=[agente_comunicacao], tasks=[tarefa_redacao_bloqueado]).kickoff())

            else:
                tarefa_despacho_logistico = Task(
                    description=f"Relatório: {resultado_financeiro}. Histórico: {historico_recente}. Usa a ferramenta de entregas (Hoje é {data_hoje}). Mantém a data sugerida no histórico a não ser que o cliente rejeite.",
                    expected_output="Data de Entrega: [Data]\nNome: [Nome]",
                    agent=agente_logistica
                )
                tarefa_redacao_aprovado = Task(
                    description=f"""
                    Data de Entrega escolhida. Mensagem atual: "{mensagem_cliente}". Histórico: {historico_recente}.
                    REGRAS ABSOLUTAS:
                    1. Começa com "Olá [Nome]!"
                    2. Termina com: "Se necessitar de mais alguma coisa, estou à disposição. 💧🚚 Water you love!"
                    3. Ano 2026.
                    4. NUNCA uses aspas.
                    """,
                    expected_output="Mensagem de WhatsApp limpa.",
                    agent=agente_comunicacao
                )
                resultado_final = str(Crew(agents=[agente_logistica, agente_comunicacao], tasks=[tarefa_despacho_logistico, tarefa_redacao_aprovado], process=Process.sequential).kickoff())

        # 6. Guardar na Memória e Imprimir no ecrã
        historico_conversas[telefone_whatsapp].append(f"Cliente: {mensagem_cliente}")
        historico_conversas[telefone_whatsapp].append(f"Assistente: {resultado_final}")

        print(f"\n🤖 Assistente: {resultado_final}")
        print("-" * 60 + "\n")

if __name__ == '__main__':
    iniciar_simulador()