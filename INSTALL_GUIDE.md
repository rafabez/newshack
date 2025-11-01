# 📖 Guia de Instalação Completo - News Hack Bot

Este guia detalha passo a passo como instalar e configurar o News Hack Bot no seu servidor VPS Ubuntu.

---

## 📋 Pré-requisitos

### Sistema Operacional
- Ubuntu 20.04 LTS ou superior (recomendado)
- Debian 10+ também funciona
- Acesso SSH ao servidor
- Usuário com privilégios sudo

### Software Necessário
- Python 3.8+
- pip3
- git
- Conexão com internet

---

## 🚀 Instalação Passo a Passo

### Passo 1: Conectar ao Servidor VPS

```bash
ssh seu_usuario@seu_servidor_ip
```

### Passo 2: Atualizar o Sistema

```bash
sudo apt update
sudo apt upgrade -y
```

### Passo 3: Instalar Dependências do Sistema

```bash
# Instalar Python 3 e ferramentas
sudo apt install -y python3 python3-pip python3-venv git

# Verificar instalação
python3 --version
pip3 --version
git --version
```

### Passo 4: Clonar o Repositório

```bash
# Navegar para o diretório home
cd ~

# Clonar o repositório
git clone https://github.com/seu-usuario/newshack.git

# Entrar no diretório
cd newshack
```

### Passo 5: Executar Script de Instalação

```bash
# Tornar o script executável
chmod +x install.sh

# Executar instalação
./install.sh
```

O script irá:
- ✅ Verificar versão do Python
- ✅ Criar ambiente virtual Python
- ✅ Instalar todas as dependências
- ✅ Criar diretórios necessários (data, logs)
- ✅ Copiar arquivo de configuração de exemplo

### Passo 6: Configurar o Bot do Telegram

#### 6.1 Criar o Bot

1. Abra o Telegram no seu celular ou desktop
2. Procure por `@BotFather`
3. Envie o comando: `/newbot`
4. Escolha um nome para o bot: `News Hack`
5. Escolha um username: `newshack_bot` (ou outro disponível)
6. **Copie o TOKEN** que o BotFather forneceu

Exemplo de token:
```
8523870647:AAGMnxPGWnjPPlbMFZfGq9Tf-DY6DTXNQP8
```

#### 6.2 Obter o Chat ID

**Opção A - Para receber mensagens pessoalmente:**

```bash
# 1. Envie uma mensagem para o seu bot no Telegram (qualquer mensagem)

# 2. Execute este comando (substitua SEU_TOKEN):
curl https://api.telegram.org/botSEU_TOKEN/getUpdates

# 3. Procure por "chat":{"id":123456789
# Este número é seu CHAT_ID
```

**Opção B - Para enviar para um canal:**

1. Crie um canal no Telegram
2. Adicione o bot como administrador do canal
3. Envie uma mensagem no canal
4. Use o mesmo comando curl acima
5. O Chat ID do canal será algo como: `-1001234567890`

**Opção C - Usar bot auxiliar:**

1. Procure por `@userinfobot` no Telegram
2. Envie `/start`
3. O bot mostrará seu Chat ID

### Passo 7: Configurar Variáveis de Ambiente

```bash
# Editar arquivo .env
nano .env
```

Configure as seguintes variáveis:

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=8523870647:AAGMnxPGWnjPPlbMFZfGq9Tf-DY6DTXNQP8
TELEGRAM_CHAT_ID=seu_chat_id_aqui

# RSS Feed Check Interval (in minutes)
CHECK_INTERVAL=30

# Database Path
DATABASE_PATH=./data/news.db

# Logging Level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
```

**Salvar e sair:**
- Pressione `Ctrl + X`
- Pressione `Y` para confirmar
- Pressione `Enter`

### Passo 8: Testar o Bot

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Executar bot em modo teste
python3 main.py
```

**O que deve acontecer:**
- ✅ Bot inicia sem erros
- ✅ Conecta ao Telegram
- ✅ Carrega feeds RSS iniciais
- ✅ Envia primeiras notícias para o Telegram

**Testar comandos no Telegram:**
1. Abra o Telegram
2. Procure seu bot
3. Envie `/start`
4. Teste outros comandos: `/news`, `/stats`, `/recent`

**Para parar o bot:**
- Pressione `Ctrl + C`

### Passo 9: Configurar como Serviço Systemd

#### 9.1 Preparar arquivo de serviço

```bash
# O install.sh já criou o arquivo newshack.service.tmp
# Verificar se está correto:
cat newshack.service.tmp
```

#### 9.2 Instalar o serviço

```bash
# Copiar para systemd
sudo cp newshack.service.tmp /etc/systemd/system/newshack.service

# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar para iniciar no boot
sudo systemctl enable newshack

# Iniciar o serviço
sudo systemctl start newshack
```

#### 9.3 Verificar status

```bash
# Ver status do serviço
sudo systemctl status newshack

# Deve mostrar: Active: active (running)
```

#### 9.4 Ver logs em tempo real

```bash
# Logs do aplicativo
tail -f ~/newshack/logs/newshack.log

# Logs do systemd
sudo journalctl -u newshack -f
```

---

## 🔧 Comandos Úteis

### Gerenciar o Serviço

```bash
# Iniciar
sudo systemctl start newshack

# Parar
sudo systemctl stop newshack

# Reiniciar
sudo systemctl restart newshack

# Status
sudo systemctl status newshack

# Ver logs
sudo journalctl -u newshack -n 100

# Ver logs em tempo real
sudo journalctl -u newshack -f
```

### Atualizar o Bot

```bash
# Parar o serviço
sudo systemctl stop newshack

# Atualizar código
cd ~/newshack
git pull

# Atualizar dependências (se necessário)
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Reiniciar serviço
sudo systemctl start newshack
```

### Backup do Banco de Dados

```bash
# Criar backup
cp ~/newshack/data/news.db ~/newshack/data/news.db.backup-$(date +%Y%m%d)

# Ou com compressão
tar -czf ~/newshack-backup-$(date +%Y%m%d).tar.gz ~/newshack/data/
```

### Limpar Logs Antigos

```bash
# Limpar logs com mais de 7 dias
find ~/newshack/logs/ -name "*.log" -mtime +7 -delete

# Ou truncar log atual
> ~/newshack/logs/newshack.log
```

---

## 🐛 Solução de Problemas

### Problema: Bot não inicia

**Verificar logs:**
```bash
tail -n 50 ~/newshack/logs/newshack.log
sudo journalctl -u newshack -n 50
```

**Causas comuns:**
1. Token do Telegram inválido
2. Chat ID incorreto
3. Dependências não instaladas
4. Permissões incorretas

**Solução:**
```bash
# Verificar .env
cat ~/newshack/.env

# Reinstalar dependências
cd ~/newshack
source venv/bin/activate
pip install -r requirements.txt --force-reinstall

# Verificar permissões
chmod +x ~/newshack/main.py
```

### Problema: Feeds RSS não atualizam

**Verificar status dos feeds:**
```bash
# No Telegram, envie:
/feeds
```

**Verificar conectividade:**
```bash
# Testar conexão com um feed
curl -I https://feeds.feedburner.com/TheHackersNews
```

**Forçar atualização:**
```bash
# No Telegram, envie:
/update
```

### Problema: Banco de dados corrompido

**Backup e recriar:**
```bash
# Parar serviço
sudo systemctl stop newshack

# Backup do banco atual
mv ~/newshack/data/news.db ~/newshack/data/news.db.old

# Reiniciar (criará novo banco)
sudo systemctl start newshack
```

### Problema: Serviço não inicia no boot

**Verificar se está habilitado:**
```bash
sudo systemctl is-enabled newshack
```

**Habilitar:**
```bash
sudo systemctl enable newshack
```

### Problema: Muitas notícias duplicadas

**Limpar banco e reiniciar:**
```bash
sudo systemctl stop newshack
rm ~/newshack/data/news.db
sudo systemctl start newshack
```

### Problema: Bot lento ou travando

**Verificar recursos:**
```bash
# CPU e memória
top -p $(pgrep -f "python3.*main.py")

# Espaço em disco
df -h
du -sh ~/newshack/data/
```

**Otimizar:**
```bash
# Limpar banco de dados antigo
sqlite3 ~/newshack/data/news.db "DELETE FROM news_entries WHERE fetched_at < datetime('now', '-30 days');"
sqlite3 ~/newshack/data/news.db "VACUUM;"
```

---

## 🔒 Segurança

### Proteger arquivo .env

```bash
# Restringir permissões
chmod 600 ~/newshack/.env

# Verificar
ls -la ~/newshack/.env
# Deve mostrar: -rw------- (apenas dono pode ler/escrever)
```

### Firewall (Opcional)

```bash
# Permitir SSH
sudo ufw allow ssh

# Habilitar firewall
sudo ufw enable

# Verificar status
sudo ufw status
```

### Atualizar Sistema Regularmente

```bash
# Criar script de atualização
cat > ~/update-system.sh << 'EOF'
#!/bin/bash
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
EOF

chmod +x ~/update-system.sh

# Executar semanalmente
sudo crontab -e
# Adicionar: 0 3 * * 0 /home/seu_usuario/update-system.sh
```

---

## 📊 Monitoramento

### Verificar uso de recursos

```bash
# CPU e memória em tempo real
htop

# Espaço em disco
df -h

# Tamanho do banco de dados
du -h ~/newshack/data/news.db

# Número de notícias no banco
sqlite3 ~/newshack/data/news.db "SELECT COUNT(*) FROM news_entries;"
```

### Logs importantes

```bash
# Últimas 100 linhas do log
tail -n 100 ~/newshack/logs/newshack.log

# Erros apenas
grep ERROR ~/newshack/logs/newshack.log

# Estatísticas de feeds
grep "Feed check completed" ~/newshack/logs/newshack.log | tail -n 10
```

---

## 🎯 Configurações Avançadas

### Ajustar intervalo de verificação

Edite `.env`:
```bash
# Verificar a cada 15 minutos
CHECK_INTERVAL=15

# Verificar a cada 1 hora
CHECK_INTERVAL=60
```

Reinicie o serviço:
```bash
sudo systemctl restart newshack
```

### Adicionar novos feeds RSS

Edite `config/rss_feeds.py`:
```python
{
    "name": "Meu Blog de Segurança",
    "url": "https://meublog.com/feed",
    "category": "news",
    "priority": "medium"
}
```

Reinicie o serviço:
```bash
sudo systemctl restart newshack
```

### Configurar múltiplos destinos

Para enviar notícias para múltiplos chats/canais, você precisará modificar o código ou executar múltiplas instâncias.

---

## 📞 Suporte

### Recursos

- **README.md**: Documentação principal
- **GitHub Issues**: Reportar bugs
- **Logs**: Sempre verifique os logs primeiro

### Comandos de diagnóstico

```bash
# Informações do sistema
uname -a
python3 --version
pip3 --version

# Status do serviço
sudo systemctl status newshack

# Últimos logs
tail -n 50 ~/newshack/logs/newshack.log

# Processos Python
ps aux | grep python3

# Portas em uso
sudo netstat -tulpn | grep python
```

---

## ✅ Checklist de Instalação

- [ ] Sistema atualizado
- [ ] Python 3.8+ instalado
- [ ] Repositório clonado
- [ ] Script install.sh executado
- [ ] Bot criado no BotFather
- [ ] Token do bot obtido
- [ ] Chat ID obtido
- [ ] Arquivo .env configurado
- [ ] Bot testado manualmente
- [ ] Serviço systemd instalado
- [ ] Serviço habilitado e iniciado
- [ ] Logs verificados
- [ ] Comandos testados no Telegram
- [ ] Backup configurado (opcional)

---

## 🎉 Pronto!

Se você seguiu todos os passos, seu News Hack Bot está:

✅ Instalado e rodando
✅ Coletando notícias automaticamente
✅ Enviando para o Telegram
✅ Configurado para iniciar no boot
✅ Gerando logs para monitoramento

**Aproveite seu agregador de notícias de hacking!** 🔐

---

**Dúvidas?** Verifique o README.md ou abra uma issue no GitHub.
