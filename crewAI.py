from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
import json
import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Carregar variáveis de ambiente do ficheiro .env
load_dotenv()

@tool("consultar_erp")
def consultar_ficha_cliente(telefone: str) -> str:
    """
    Usa esta ferramenta APENAS para procurar os dados de um cliente no ERP através do seu número de telefone. 
    Recebe um número de telefone como string (ex: '912345678').
    Retorna os dados do cliente: nome, status, consumo médio de garrafões, rota associada e saldo pendente.
    """
    
    # NOTA PARA SI: No futuro, aqui entrará o código real que faz a query 
    # à sua base de dados SQL ou a chamada à API do seu software.
    # Para o seu projeto/MVP, vamos usar um dicionário para simular a resposta do ERP

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
            "dias_atraso": 35, # Dívida velha, tem de bloquear!
            "dados_pagamento": "Entidade: 12345 | Ref: 987 654 321 | Valor: 18,50€"
        }
    }

    # Procura o cliente pelo telefone
    cliente = db_simulada_erp.get(telefone)

    # A ferramenta devolve sempre texto (String ou JSON) para o Agente conseguir ler
    if cliente:
        return json.dumps(cliente, ensure_ascii=False, indent=2)
    else:
        return "Atenção: Cliente não encontrado no ERP com este número de telefone. Pede ao cliente para confirmar o número ou o NIF."

@tool("verificar_rota")
def verificar_disponibilidade_rota(rota_habitual: str) -> str:
    """
    Usa esta ferramenta APENAS para verificar se uma rota específica 
    tem capacidade de carga para mais garrafões hoje, e se tem um 
    técnico de equipamentos POU disponível nessa zona.
    Recebe o nome da rota exato (ex: 'Rota_Sul_04').
    """
    
    # Simulação da base de dados de Logística/Rotas do seu ERP
    db_simulada_rotas = {
        "Rota_Sul_04": {
            "estado": "Em curso",
            "espaco_livre_garrafoes": 15,
            "tecnico_pou_disponivel": True,
            "notas": "O motorista/técnico Carlos está na zona e tem ferramentas para reparar fugas de água."
        },
        "Rota_Centro_02": {
            "estado": "Fechada",
            "espaco_livre_garrafoes": 0,
            "tecnico_pou_disponivel": False,
            "notas": "Carrinha cheia, impossível encaixar entregas ou reparações hoje."
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
    Usa esta ferramenta para consultar as próximas 3 datas ideais de entrega 
    onde a rota tem capacidade de carga para a quantidade pedida de garrafões.
    Recebe o nome da rota exato (ex: 'Rota_Sul_04') e a quantidade de garrafões (ex: 3).
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
        return "Erro: Rota não encontrada no calendário logístico."
        
    datas_disponiveis = []
    
    # 1. Buscar a data exata de hoje, zerando as horas para a matemática ser limpa
    hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    for dia in datas_rota:
        data_obj = datetime.strptime(dia["data"], "%Y-%m-%d")
        
        # 2. A VALIDAÇÃO DE OURO: Tem de ser maior ou igual a hoje E ter espaço!
        if data_obj >= hoje and dia["espaco_livre_garrafoes"] >= quantidade_pedida:
            data_pt = data_obj.strftime("%d-%m-%Y")
            
            datas_disponiveis.append(data_pt) 
            if len(datas_disponiveis) == 3:
                break
                
    if datas_disponiveis:
        return json.dumps(datas_disponiveis, ensure_ascii=False)
    else:
        return f"Sem disponibilidade de carga ({quantidade_pedida} garrafões) nas datas futuras para esta rota."
        

# 1. Criação do Agente de Atendimento
agente_atendimento = Agent(
    role='Gestor Sénior de Atendimento ao Cliente',
    goal='Identificar o cliente pelo número de telefone, analisar o seu histórico de consumo de água e perceber exatamente o que ele precisa na mensagem atual.',
    backstory=(
        "Trabalhas há 10 anos na equipa de suporte de uma empresa líder de "
        "distribuição de garrafões de água (18,9L) e fontes POU. "
        "És conhecido por ser extremamente educado, empático e eficiente. "
        "O teu superpoder é conhecer os clientes: tu nunca respondes a um "
        "pedido sem antes consultar a ficha do cliente no ERP para saber "
        "se ele tem dívidas, qual a sua rota habitual e o que consome."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[consultar_ficha_cliente],
)

agente_financeiro = Agent(
    role='Analista Financeiro e de Cobranças',
    goal='Verificar o saldo do cliente e bloquear encomendas se existirem dívidas antigas, fornecendo os dados de pagamento.',
    backstory=(
        "És o 'guarda-costas' financeiro da empresa. A tua regra é cega e absoluta: "
        "Se um cliente tem um saldo pendente e os 'dias_atraso' são maiores que 30, a encomenda é BLOQUEADA. "
        "Se o cliente não tem dívidas, ou o atraso é inferior a 30 dias, a encomenda é APROVADA."
    ),
    verbose=True,
    allow_delegation=False,
)

agente_logistica = Agent(
    role='Coordenador de Tráfego e Logística',
    goal='Verificar a disponibilidade das carrinhas e dos técnicos para satisfazer os pedidos dos clientes no próprio dia.',
    backstory=(
        "És o cérebro das operações de uma empresa de distribuição de águas. "
        "És extremamente pragmático e rigoroso. Avalias sempre a capacidade da frota "
        "antes de prometer uma entrega ou reparação de máquina POU. "
        "Baseias as tuas decisões APENAS nos dados que a ferramenta de rotas te dá."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[verificar_disponibilidade_rota, verificar_proximas_entregas],
)

agente_comunicacao = Agent(
    role='Especialista de Comunicação por WhatsApp',
    goal='Escrever a mensagem final perfeita para enviar ao cliente, baseando-se estritamente na decisão do departamento de logística.',
    backstory=(
        "És o 'rosto' da empresa de águas. O teu tom é sempre simpático, prestável e profissional. "
        "Escreves SEMPRE em Português de Portugal (PT-PT) europeu correto, nunca usando expressões como 'Opa' ou 'Desafortunadamente'. "
        "Sabes que as pessoas lêem as mensagens de WhatsApp à pressa, por isso usas parágrafos curtos "
        "e emojis contextuais (como 💧 ou 🚚) sem exagerar. Nunca usas jargão logístico."
    ),
    verbose=True,
    allow_delegation=False,
)

# Inicializar a API
app = Flask(__name__)

# O nosso caderno de memória RAM (guarda o histórico por número de telefone)
historico_conversas = {}

# Criar a Rota da API (O "ouvido" do seu script)
@app.route('/api/whatsapp', methods=['POST'])
def processar_mensagem():
    # 1. Receber os dados do n8n
    dados = request.json
    telefone_whatsapp = dados.get('telefone')
    mensagem_cliente = dados.get('mensagem')
    
    # 1.1 GERIR A MEMÓRIA 🧠
    if telefone_whatsapp not in historico_conversas:
        historico_conversas[telefone_whatsapp] = []
        
    # Vamos buscar as últimas 4 mensagens para não sobrecarregar a IA
    historico_recente = "\n".join(historico_conversas[telefone_whatsapp][-4:])
    if not historico_recente:
        historico_recente = "Primeiro contacto do cliente."

    print(f"\n[API] Nova mensagem de {telefone_whatsapp}: {mensagem_cliente}")
    print(f"[MEMÓRIA] Contexto recuperado: {len(historico_conversas[telefone_whatsapp])} mensagens anteriores.")

    # 2. Calcular o tempo real
    agora = datetime.now()
    data_hoje = agora.strftime("%Y-%m-%d")
    hora_atual = agora.strftime("%H:%M")
    data_limite_pagamento_MB = (agora + timedelta(days=7)).strftime("%d-%m-%Y")

    # 3. A Tarefa de Triagem (Agora com Memória!)
    tarefa_analise_inicial = Task(
        description=f"""
        Lê o histórico recente com este cliente:
        ---
        {historico_recente}
        ---
        Mensagem ATUAL do cliente: "{mensagem_cliente}"
        
        Usa a ferramenta 'consultar_erp' com o número {telefone_whatsapp}.
        Se a ferramenta disser "Cliente não encontrado...", escreve APENAS "DESCONHECIDO".
        Caso contrário, extrai os dados. Se a mensagem atual for uma reclamação, comentário ou ajuste (ex: "mas dia 25 é hoje"), anota isso no campo 'Pedido' para os outros agentes saberem o contexto!
        """,
        expected_output="Se não existir: 'DESCONHECIDO'. Se existir: Nome, Rota, Dias de Atraso, Dados de Pagamento e Pedido (com contexto).",
        agent=agente_atendimento
    )

    # Corre APENAS o Agente de Atendimento primeiro
    equipa_triagem = Crew(
        agents=[agente_atendimento],
        tasks=[tarefa_analise_inicial],
        process=Process.sequential
    )
    resultado_triagem = str(equipa_triagem.kickoff())
    print(f"\n[ROUTER] Resultado da Triagem: {resultado_triagem}\n")

    # 4. O DESVIO INTELIGENTE (IF / ELSE)
    if "DESCONHECIDO" in resultado_triagem.upper():
        print("🚨 Cliente não encontrado! A desviar direto para a Comunicação...")
        
        tarefa_cliente_desconhecido = Task(
            description="""
            O cliente enviou mensagem mas o número não está no ERP. 
            Escreve UMA única frase em Português pedindo o NIF ou Número de Cliente.
            A tua resposta deve conter EXCLUSIVAMENTE o texto final que o cliente vai ler no telemóvel. Sem introduções, sem notas, sem pensamentos.
            """,
            expected_output="Uma frase simples em Português como: 'Olá! 💧 Não encontro o seu registo. Indique o seu NIF ou Número de Cliente, por favor.' e absolutamente mais NADA.",
            agent=agente_comunicacao
        )
        
        equipa_cliente_desconhecido = Crew(agents=[agente_comunicacao], tasks=[tarefa_cliente_desconhecido])
        resultado_final = equipa_cliente_desconhecido.kickoff()

    else:
        print("✅ Cliente encontrado! A iniciar análise Financeira...")
        
        # 4.1 A Tarefa Financeira
        tarefa_analise_financeira = Task(
            description=f"Lê este relatório: {resultado_triagem}. Se 'Dias de Atraso' > 30, o status é BLOQUEADO. Se <= 30, é APROVADO. NÃO USES FERRAMENTAS.",
            expected_output="Status Financeiro: [APROVADO ou BLOQUEADO]\nNome: [Copia o Nome]\nRota: [Copia a Rota]\nDados de Pagamento: [Copia os Dados]\nPedido: [Copia o Pedido]",
            agent=agente_financeiro
        )

        equipa_financeira = Crew(agents=[agente_financeiro], tasks=[tarefa_analise_financeira])
        resultado_financeiro = str(equipa_financeira.kickoff())
        print(f"\n[ROUTER 2] Resultado Financeiro: {resultado_financeiro}\n")

        # 5. O SEGUNDO DESVIO INTELIGENTE (Aprovado vs Bloqueado)
        if "BLOQUEADO" in resultado_financeiro.upper():
            print("❌ Cliente BLOQUEADO! A saltar a Logística e ir direto para a Comunicação...")
            
            tarefa_redacao_bloqueado = Task(
                description=f"""
                Lê o relatório financeiro: {resultado_financeiro}.
                O histórico recente com o cliente é: {historico_recente}
                A mensagem atual do cliente é: "{mensagem_cliente}"
                
                Gera a resposta de WhatsApp.
                
                REGRAS ABSOLUTAS (A tua Voz de Marca):
                1. Começa SEMPRE com "Olá [Nome do Cliente]!"
                2. Termina SEMPRE com a assinatura exata: "Se necessitar de mais alguma coisa, estou à disposição. 💧🚚 Water you love!"
                3. LÓGICA DE CONVERSA:
                   - Se for o PRIMEIRO contacto sobre a dívida, informa do cancelamento e apresenta os Dados de Pagamento (Entidade, Ref, Valor) em lista clara.
                   - Se ele perguntar sobre prazos (ex: "até quando posso pagar?"), responde de forma natural e INFORMA QUE O PRAZO LIMITE É O DIA {data_limite_pagamento_MB}.
                   - Se ele apenas agradecer ou confirmar (ex: "obrigado", "ok"), responde apenas com simpatia (ex: "De nada! Fico a aguardar a regularização."). NÃO repitas a lista de pagamento nestes casos.
                4. PROIBIDO: NUNCA coloques aspas (") no início ou no fim da tua resposta.
                """,
                expected_output="Apenas o texto limpo do WhatsApp, sem aspas e com a assinatura.",
                agent=agente_comunicacao
            )
            
            equipa_comunicacao_bloqueado = Crew(agents=[agente_comunicacao], tasks=[tarefa_redacao_bloqueado])
            resultado_final = equipa_comunicacao_bloqueado.kickoff()

        else:
            print("🚚 Cliente APROVADO! A iniciar Logística e agendamento...")

            tarefa_despacho_logistico = Task(
                description=f"""
                Lê o seguinte relatório financeiro: {resultado_financeiro}
                Lê o histórico recente: {historico_recente}
                
                Usa a ferramenta 'verificar_proximas_entregas' para a rota indicada no relatório (Hoje é {data_hoje}). A quantidade pedida é o número que está no 'Pedido'.
                REGRA DE OURO: Se já sugeriste uma data no histórico e o cliente NÃO a rejeitou (apenas fez uma pergunta sobre o ano ou outro detalhe), MANTÉM essa data! Só avanças para a próxima data se o cliente disser explicitamente que não pode.
                """,
                expected_output="Data de Entrega: [Data da ferramenta]\nNome: [Copia o Nome]",
                agent=agente_logistica
            )

            tarefa_redacao_aprovado = Task(
                description=f"""
                Lê a Data de Entrega e o Nome escolhidos pela Logística.
                Mensagem atual do cliente: "{mensagem_cliente}"
                O histórico era: {historico_recente}
                
                Gera a mensagem de WhatsApp. O teu tom deve ser acolhedor, simpático e humano.
                
                REGRAS ABSOLUTAS (A tua Voz de Marca):
                1. Começa SEMPRE com "Olá [Nome do Cliente]!"
                2. Termina SEMPRE com a assinatura exata: "Se necessitar de mais alguma coisa, estou à disposição. 💧🚚 Water you love!"
                3. Responde ao contexto da mensagem do cliente de forma natural (se aplicável).
                4. Estamos no ano de 2026. NUNCA escrevas 2024.
                5. PROIBIDO: NUNCA coloques aspas (") no início ou no fim da tua resposta.
                
                Exemplo de estrutura:
                Olá [Nome]! Confirmamos a sua entrega para [Data]. O nosso técnico irá passar no seu local.
                Se necessitar de mais alguma coisa, estou à disposição. 💧🚚 Water you love!
                """,
                expected_output="APENAS o texto limpo do WhatsApp, sem aspas e com a assinatura da marca.",
                agent=agente_comunicacao
            )

            equipa_logistica_aprovado = Crew(
                agents=[agente_logistica, agente_comunicacao],
                tasks=[tarefa_despacho_logistico, tarefa_redacao_aprovado],
                process=Process.sequential 
            )
            resultado_final = str(equipa_logistica_aprovado.kickoff())

    # 6. GUARDAR A CONVERSA NA MEMÓRIA ANTES DE RESPONDER 🧠
    historico_conversas[telefone_whatsapp].append(f"Cliente: {mensagem_cliente}")
    historico_conversas[telefone_whatsapp].append(f"Assistente: {resultado_final}")

    # 7. Devolver a resposta final ao n8n
    return jsonify({
        "status": "sucesso",
        "resposta_whatsapp": str(resultado_final)
    })

# Arrancar o Servidor da API
if __name__ == '__main__':
    print("🚀 Servidor AI a correr na porta 5001... À espera do n8n!")
    app.run(host='0.0.0.0', port=5001)
