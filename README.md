# 🔐 News Hack Bot

**Agregador de Notícias de Hacking e Cibersegurança para Telegram**

Bot Telegram automatizado que coleta e entrega notícias de hacking, cibersegurança e infosec de múltiplas fontes RSS, incluindo sites mainstream e blogs underground.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

---

## 📋 Índice

- [Características](#-características)
- [Fontes de Notícias](#-fontes-de-notícias)
- [Comandos do Bot](#-comandos-do-bot)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Uso](#-uso)
- [Systemd Service](#-systemd-service)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Melhorias Futuras](#-melhorias-futuras)

---

## ✨ Características

### 🎯 Funcionalidades Principais

- **Agregação Automática**: Coleta notícias de 60+ feeds RSS automaticamente
- **Categorização Inteligente**: Organiza notícias por categoria (News, Research, Exploits, Malware, etc.)
- **Priorização**: Sistema de prioridade (Alta, Média, Baixa) para feeds
- **Envio Automático**: Envia novas notícias automaticamente para o Telegram
- **Comandos Interativos**: Interface rica com múltiplos comandos
- **Busca**: Sistema de busca por palavras-chave
- **Estatísticas**: Acompanhamento de métricas e status dos feeds
- **Banco de Dados**: SQLite para armazenamento e controle de duplicatas
- **Systemd Integration**: Execução como serviço do sistema

### 🛡️ Categorias de Notícias

- **News**: Notícias gerais de cibersegurança
- **Research**: Pesquisas técnicas e acadêmicas
- **Exploits**: Vulnerabilidades e exploits
- **Malware**: Análise de malware
- **Threat Intel**: Inteligência de ameaças
- **Tools**: Ferramentas de hacking e pentest
- **Cloud**: Segurança em cloud
- **Crypto**: Criptografia

---

## 📡 Fontes de Notícias

### 🔥 Mainstream (Alta Prioridade)

- **The Hacker News** - Notícias diárias de cibersegurança
- **Krebs on Security** - Blog do jornalista Brian Krebs
- **Bleeping Computer** - Notícias de tecnologia e segurança
- **Dark Reading** - Análises profundas de segurança
- **Schneier on Security** - Blog do especialista Bruce Schneier
- **Troy Hunt** - Criador do Have I Been Pwned
- **Graham Cluley** - Notícias e análises de segurança

### 🔬 Threat Intelligence & Research

- **Google Project Zero** - Pesquisa de vulnerabilidades do Google
- **Cisco Talos** - Inteligência de ameaças da Cisco
- **Kaspersky Securelist** - Pesquisas da Kaspersky
- **Mandiant** - Threat intelligence e resposta a incidentes
- **CrowdStrike Blog** - Análises de ameaças avançadas
- **Palo Alto Unit 42** - Pesquisa de segurança
- **Checkpoint Research** - Descobertas de vulnerabilidades
- **ESET Research** - Análises de malware

### 💣 Vulnerabilities & Exploits

- **Exploit-DB** - Base de dados de exploits
- **Zero Day Initiative** - Programa de vulnerabilidades
- **Packet Storm Security** - Ferramentas e exploits
- **CISA Advisories** - Alertas governamentais (EUA)

### 🕵️ Underground & Independent

- **Darknet** - Ferramentas e tutoriais de hacking
- **Hacker Combat** - Tutoriais e notícias
- **Null Byte** - Tutoriais de hacking ético
- **Kitploit** - Ferramentas de pentest
- **PortSwigger Research** - Pesquisa em segurança web
- **Bishop Fox** - Blog de pentest
- **Offensive Security** - Criadores do Kali Linux
- **Rapid7** - Pesquisa e ferramentas

### 🔧 Technical Research

- **Trail of Bits** - Auditorias e pesquisa
- **NCC Group** - Pesquisa de segurança
- **Quarkslab** - Reverse engineering
- **Positive Security** - Pesquisa técnica
- **RCE Security** - Técnicas de exploração

### 🦠 Malware Analysis

- **Malwarebytes Labs** - Análise de malware
- **ANY.RUN** - Sandbox de malware
- **Avast Decoded** - Pesquisa de ameaças

### 👥 Community

- **r/netsec** - Subreddit de segurança de redes
- **r/blackhat** - Discussões de hacking
- **r/ReverseEngineering** - Engenharia reversa

### ☁️ Cloud Security

- **AWS Security Blog** - Segurança na AWS
- **Google Cloud Security** - Segurança no GCP
- **Microsoft Security** - Segurança na Azure

---

## 🤖 Comandos do Bot

### Comandos Básicos

```
/start - Mensagem de boas-vindas e ajuda
/help - Mostrar todos os comandos disponíveis
```

### Consulta de Notícias

```
/news - Ver últimas notícias não enviadas (até 10)
/recent - Notícias das últimas 24 horas (até 15)
/categories - Navegar notícias por categoria (menu interativo)
/search [termo] - Buscar notícias por palavra-chave
```

### Informações e Status

```
/stats - Estatísticas do bot (total de notícias, por categoria, etc.)
/feeds - Status dos feeds RSS (ativos, com erros)
```

### Administração

```
/update - Forçar atualização manual dos feeds RSS
```

---

## 🚀 Instalação

### Pré-requisitos

- Ubuntu/Debian Linux (ou similar)
- Python 3.8 ou superior
- pip3
- Git
- Acesso root (para systemd)

### Instalação Rápida

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/newshack.git
cd newshack

# 2. Execute o script de instalação
chmod +x install.sh
./install.sh

# 3. Configure as variáveis de ambiente
nano .env
# Adicione seu TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID

# 4. Teste o bot
./venv/bin/python3 main.py
```

### Instalação Manual

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/newshack.git
cd newshack

# 2. Crie ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instale dependências
pip install --upgrade pip
pip install -r requirements.txt

# 4. Crie diretórios necessários
mkdir -p data logs

# 5. Configure variáveis de ambiente
cp .env.example .env
nano .env
```

---

## ⚙️ Configuração

### 1. Criar Bot no Telegram

1. Abra o Telegram e procure por `@BotFather`
2. Envie `/newbot` e siga as instruções
3. Copie o **token** fornecido
4. (Opcional) Configure foto, descrição e comandos do bot

### 2. Obter Chat ID

**Método 1 - Para envio pessoal:**
```bash
# Envie uma mensagem para seu bot no Telegram
# Depois execute:
curl https://api.telegram.org/bot<SEU_TOKEN>/getUpdates
# Procure por "chat":{"id": XXXXXXX
```

**Método 2 - Para canal:**
1. Crie um canal no Telegram
2. Adicione o bot como administrador
3. O Chat ID será algo como `-100XXXXXXXXX`

### 3. Configurar .env

Edite o arquivo `.env`:

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=SEU_TOKEN_AQUI
TELEGRAM_CHAT_ID=seu_chat_id_aqui

# RSS Feed Check Interval (in minutes)
CHECK_INTERVAL=30

# Database Path
DATABASE_PATH=./data/news.db

# Logging Level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
```

### 4. Personalizar Feeds (Opcional)

Edite `config/rss_feeds.py` para adicionar/remover feeds RSS.

---

## 💻 Uso

### Executar Manualmente

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Executar bot
python3 main.py
```

### Executar em Background

```bash
# Com nohup
nohup ./venv/bin/python3 main.py > logs/output.log 2>&1 &

# Ou com screen
screen -S newshack
./venv/bin/python3 main.py
# Ctrl+A, D para detach
```

### Verificar Logs

```bash
# Log principal
tail -f logs/newshack.log

# Log do systemd
tail -f logs/systemd.log

# Erros do systemd
tail -f logs/systemd-error.log
```

---

## 🔧 Systemd Service

### Instalar Serviço

```bash
# 1. Editar o arquivo de serviço (já configurado pelo install.sh)
# Verifique se os caminhos estão corretos

# 2. Copiar para systemd
sudo cp newshack.service.tmp /etc/systemd/system/newshack.service

# 3. Recarregar systemd
sudo systemctl daemon-reload

# 4. Habilitar serviço (iniciar no boot)
sudo systemctl enable newshack

# 5. Iniciar serviço
sudo systemctl start newshack
```

### Gerenciar Serviço

```bash
# Status
sudo systemctl status newshack

# Parar
sudo systemctl stop newshack

# Reiniciar
sudo systemctl restart newshack

# Ver logs
sudo journalctl -u newshack -f

# Desabilitar
sudo systemctl disable newshack
```

---

## 📁 Estrutura do Projeto

```
newshack/
├── main.py                 # Ponto de entrada principal
├── requirements.txt        # Dependências Python
├── .env                    # Variáveis de ambiente (não versionado)
├── .env.example           # Exemplo de configuração
├── .gitignore             # Arquivos ignorados pelo Git
├── install.sh             # Script de instalação
├── newshack.service       # Template do serviço systemd
├── README.md              # Esta documentação
│
├── config/                # Configurações
│   ├── __init__.py
│   └── rss_feeds.py       # Lista de feeds RSS
│
├── src/                   # Código fonte
│   ├── __init__.py
│   ├── database.py        # Gerenciamento do banco de dados
│   ├── rss_parser.py      # Parser de feeds RSS
│   ├── telegram_bot.py    # Bot do Telegram
│   └── scheduler.py       # Agendador de tarefas
│
├── data/                  # Dados (não versionado)
│   └── news.db           # Banco de dados SQLite
│
└── logs/                  # Logs (não versionado)
    ├── newshack.log      # Log principal
    ├── systemd.log       # Log do systemd
    └── systemd-error.log # Erros do systemd
```

---

## 🎨 Melhorias Futuras

### 🔮 Funcionalidades Planejadas

- [ ] **Filtros Personalizados**: Permitir usuários criarem filtros de palavras-chave
- [ ] **Notificações por Prioridade**: Enviar notícias de alta prioridade com notificação sonora
- [ ] **Resumos com IA**: Usar LLM para gerar resumos das notícias
- [ ] **Análise de Sentimento**: Classificar notícias por severidade/impacto
- [ ] **Multi-idioma**: Suporte para notícias em português, inglês, espanhol
- [ ] **Web Dashboard**: Interface web para gerenciamento
- [ ] **Exportação**: Exportar notícias para PDF, CSV, JSON
- [ ] **Integração com Discord**: Suporte para Discord além do Telegram
- [ ] **Machine Learning**: Recomendações personalizadas baseadas em leitura
- [ ] **RSS Dinâmico**: Adicionar/remover feeds via comandos do bot
- [ ] **Webhooks**: Integração com outras ferramentas via webhooks
- [ ] **Backup Automático**: Backup do banco de dados na nuvem

### 🛠️ Melhorias Técnicas

- [ ] **Docker**: Containerização da aplicação
- [ ] **Testes**: Adicionar testes unitários e de integração
- [ ] **CI/CD**: Pipeline de integração contínua
- [ ] **Monitoring**: Integração com Prometheus/Grafana
- [ ] **Rate Limiting**: Melhor controle de rate limiting
- [ ] **Caching**: Sistema de cache para melhor performance
- [ ] **API REST**: API para integração com outras aplicações

### 💡 Comandos Adicionais Sugeridos

```
/subscribe [categoria] - Inscrever-se em categoria específica
/unsubscribe [categoria] - Cancelar inscrição
/filter add [palavra] - Adicionar filtro de palavra-chave
/filter remove [palavra] - Remover filtro
/summary - Resumo diário das notícias
/trending - Notícias mais populares
/export [formato] - Exportar notícias (pdf, csv, json)
/feed add [url] - Adicionar novo feed RSS
/feed remove [nome] - Remover feed RSS
/schedule [hora] - Agendar envio de resumo diário
```

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abrir um Pull Request

---

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

## 🙏 Agradecimentos

- Comunidade de cibersegurança por compartilhar conhecimento
- Todos os blogs e sites que mantêm feeds RSS ativos
- python-telegram-bot por excelente biblioteca
- feedparser por facilitar o parsing de RSS

---

## 📧 Contato

Para dúvidas, sugestões ou reportar problemas:

- Abra uma issue no GitHub
- Entre em contato via Telegram

---

## ⚠️ Disclaimer

Este bot é para fins educacionais e de pesquisa. Use de forma responsável e ética. O autor não se responsabiliza pelo uso indevido da ferramenta.

---

**Feito com ❤️ para a comunidade de cibersegurança**

🔐 **Stay Safe, Stay Informed!** 🔐
