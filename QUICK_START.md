# ⚡ Quick Start Guide

Guia rápido para ter o bot funcionando em 5 minutos!

## 🚀 Instalação Rápida

### 1. Clone e Configure

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/newshack.git
cd newshack

# Configure o bot (interativo)
chmod +x quick_setup.sh
./quick_setup.sh
```

### 2. Instale

```bash
# Execute o instalador
chmod +x install.sh
./install.sh
```

### 3. Teste

```bash
# Teste os feeds RSS
./venv/bin/python3 test_feeds.py

# Execute o bot
./venv/bin/python3 main.py
```

### 4. Configure Systemd (Opcional)

```bash
# Instalar como serviço
sudo cp newshack.service.tmp /etc/systemd/system/newshack.service
sudo systemctl daemon-reload
sudo systemctl enable newshack
sudo systemctl start newshack

# Verificar status
sudo systemctl status newshack
```

## 📱 Obter Token e Chat ID

### Token do Bot

1. Abra o Telegram
2. Procure: `@BotFather`
3. Envie: `/newbot`
4. Siga as instruções
5. Copie o token fornecido

### Chat ID

**Método Rápido:**
1. Procure: `@userinfobot` no Telegram
2. Envie: `/start`
3. Copie seu ID

**Método Manual:**
```bash
# Envie uma mensagem para seu bot primeiro, depois:
curl https://api.telegram.org/bot<SEU_TOKEN>/getUpdates | grep -o '"id":[0-9]*' | head -1
```

## 🎯 Comandos do Bot

```
/start      - Iniciar bot
/news       - Últimas notícias
/recent     - Notícias 24h
/stats      - Estatísticas
/categories - Por categoria
/search     - Buscar
/update     - Atualizar feeds
```

## 🔧 Solução Rápida de Problemas

### Bot não inicia?
```bash
# Verificar logs
tail -f logs/newshack.log

# Verificar .env
cat .env
```

### Feeds não funcionam?
```bash
# Testar feeds
./venv/bin/python3 test_feeds.py
```

### Serviço não inicia?
```bash
# Ver logs
sudo journalctl -u newshack -n 50

# Reiniciar
sudo systemctl restart newshack
```

## 📚 Documentação Completa

- **README.md** - Documentação completa
- **INSTALL_GUIDE.md** - Guia detalhado de instalação
- **config/rss_feeds.py** - Lista de feeds RSS

## 💡 Dicas

1. **Teste primeiro**: Execute manualmente antes de configurar systemd
2. **Verifique logs**: Sempre consulte `logs/newshack.log`
3. **Backup**: Faça backup do `data/news.db` regularmente
4. **Ajuste intervalo**: Modifique `CHECK_INTERVAL` no `.env`

## 🆘 Precisa de Ajuda?

1. Verifique os logs
2. Leia o INSTALL_GUIDE.md
3. Abra uma issue no GitHub

---

**Pronto! Seu bot está funcionando! 🎉**
