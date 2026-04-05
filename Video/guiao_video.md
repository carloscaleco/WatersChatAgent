# 🎬 Guião de Vídeo: Agente Inteligente para Empresas de Água

## ⏱️ Segmento 1: Introdução e O Problema (0:00 - 1:15)

**[VISUAL: Diapositivo de título vibrante com o logótipo do projeto. Título: "Revolucione as Encomendas de Água com IA"]**
**(Tone: Entusiástico e questionador)**

**Orador:**
Já alguma vez parou para pensar em quantas horas as empresas de distribuição de água perdem a processar encomendas manualmente através do WhatsApp? [PAUSE] E se pudéssemos automatizar tudo isso, mantendo um atendimento ao cliente impecável?

**[SHOW SCREEN: Animação de um telemóvel a receber mensagens no WhatsApp e a processar encomendas automaticamente]**

**Orador:**
Olá! Hoje vou mostrar-vos um assistente virtual incrível, alimentado por Inteligência Artificial, desenhado especificamente para criar encomendas automaticamente no vosso ERP. 

**[VISUAL: Aparecem bullet points dinâmicos: "Valida Cliente", "Verifica Dívidas", "Agenda Entregas"]**

**Orador:**
Sempre que um cliente envia uma mensagem, este sistema entra em ação. Ele valida se o cliente existe, verifica imediatamente se há dívidas pendentes e cruza dados para saber quando a entrega pode ser feita. Tudo isto com um tom cordial, educado e altamente eficiente. 

**[VISUAL: Ecrã divide-se. De um lado "Problema (Manual)", do outro "Solução (Agente IA)"]**
**(Tone: Direto e orientador)**

**Orador:**
Pense no seu processo atual por um segundo. [PAUSE] Está pronto para o otimizar? Vamos mergulhar na arquitetura e descobrir como a magia acontece.

---

## ⏱️ Segmento 2: A Arquitetura e os "Cérebros" da Operação (1:15 - 2:45)

**[SHOW SCREEN: Diagrama de arquitetura simplificado e moderno (n8n, Ollama, CrewAI, Flask)]**
**(Tone: Profissional, simplificando conceitos técnicos)**

**Orador:**
Então, como é que isto funciona nos bastidores? Construímos uma arquitetura robusta e, acima de tudo, segura. 

Para começar, usamos o **Ollama** a correr o modelo *Qwen 2.5*. Porquê localmente? Porque garante 100% de privacidade dos dados dos vossos clientes. Nenhuma informação sensível vai para a cloud pública. [PAUSE] 

No coração do sistema, temos o **CrewAI**. Em vez de usar apenas um bot genérico, criámos uma equipa de *quatro* agentes especializados: um para o Atendimento, um Financeiro, um de Logística e um de Comunicação. 

**[HIGHLIGHT AREA: Focar na parte do n8n e Flask no diagrama]**

**Orador:**
Para colar tudo isto, usamos **Python com Flask** para gerir as nossas regras de negócio estritas — como o bloqueio automático de encomendas para clientes com faturas em atraso há mais de 30 dias. E finalmente, o **n8n** trata da ligação direta ao WhatsApp ou Telegram.

**[VISUAL: Texto no ecrã - "Resumo: Privacidade Local + 4 Agentes + Regras Estritas"]**

**Orador:**
Até agora vimos o que o sistema faz e a tecnologia que o suporta. Já a seguir, vou mostrar como podem testar isto na vossa própria máquina! Preparados?

---

## ⏱️ Segmento 3: Configuração e o Simulador CLI (2:45 - 4:15)

**[SHOW SCREEN: Ficheiro `.env` borrado que se torna nítido]**
**(Tone: Prático e focado na ação)**

**Orador:**
Para pôr a mão na massa, o primeiro passo é a segurança. 

**[HIGHLIGHT CODE: Destacar a estrutura do `.env` sem ler o código]**

**Orador:**
Na raiz do vosso projeto, vão criar um ficheiro ponto env (`.env`). Lá dentro, só precisam de colocar três linhas de configuração. Em vez de apontarmos para serviços externos pagos, estas linhas dizem ao CrewAI para usar o nosso modelo local, gratuito e seguro. 

**[VISUAL: Ícone de "Pausa" a piscar no ecrã]**
**(Tone: Encorajador)**

**Orador:**
Este é um ótimo momento para pausar o vídeo. Vão lá, criem o ficheiro `.env` e instalem as dependências no terminal. Eu espero. [PAUSE]

**[SHOW SCREEN: Terminal a correr o `simulador_terminal.py`]**

**Orador:**
Tudo pronto? Fantástico. Criei um Simulador de Terminal *Plug and Play* para testarmos a IA sem termos de configurar integrações complexas. Basta executar o script do simulador. 

Quando ele pedir um número de telefone, tentem o `961112233`. Este é o nosso cliente de teste, o João Silva. [PAUSE] Ele tem uma dívida pendente. Experimentem conversar com a IA e vejam, em tempo real no ecrã, como o Agente Financeiro atua e bloqueia a encomenda. É fascinante ver a IA a "pensar"!

---

## ⏱️ Segmento 4: Entrada em Produção com Telegram e n8n (4:15 - 5:45)

**[VISUAL: Ecrã completo do workflow do n8n com nós conectados]**
**(Tone: Entusiástico, a construir para o clímax)**

**Orador:**
Testar no terminal é ótimo, mas ver isto a funcionar numa aplicação de mensagens real? Isso é outro nível. 

Para testar o modo de produção, incluí dois workflows pré-configurados para o **n8n**. Primeiro, iniciamos o nosso servidor Python. Depois, importamos o workflow.

**[HIGHLIGHT AREA: Mostrar as duas opções: "Chat Nativo n8n" e "Telegram"]**

**Orador:**
Têm duas opções: a Opção A permite testar diretamente no chat de teste do n8n. Mas se quiserem a experiência completa, escolham a Opção B, a integração com o Telegram! 

**[SHOW SCREEN: Telemóvel com o Telegram aberto a enviar "Preciso de 3 garrafões"]**

**Orador:**
Para o Telegram, só precisam de usar o *ngrok* para criar um link público, colocar as vossas credenciais e pronto. Podem pegar no telemóvel, enviar "Preciso de 3 garrafões" e ver toda a orquestração acontecer em segundos.

**[VISUAL: Ecrã de fecho com os próximos passos em lista]**
**(Tone: Confiante e acolhedor)**

**Orador:**
E aí o têm! Um sistema inteligente, rápido e seguro para gerir encomendas. 

Lembrem-se, podem alterar os números de telefone de teste a qualquer momento no n8n para explorar como os Agentes reagem a diferentes cenários. 

Experimentem o simulador hoje mesmo e explorem o código. Se tiverem dúvidas, deixem um comentário ou abram uma issue no repositório. Obrigado por assistirem e boas automações!