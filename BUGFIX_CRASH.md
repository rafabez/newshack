# 🐛 Bug Fix: Bot Crashando

## 🔍 Problemas Identificados

### ❌ Problema 1: CISA Feed Travando o Bot
**Sintoma:** Bot para de responder após parsing do feed CISA Advisories  
**Causa:** Feed CISA demora muito ou trava sem timeout  
**Solução:** Adicionado timeout de 30s em todas as requisições HTTP

### ❌ Problema 2: Flood Control (Rate Limiting)
**Sintoma:** `Flood control exceeded. Retry in 11 seconds` (20+ vezes)  
**Causa:** Bot envia mensagens muito rápido (delay de 2s insuficiente)  
**Solução:** 
- Aumentado delay para 3s entre mensagens
- Adicionado retry logic automático (3 tentativas)
- Extração inteligente do tempo de espera da mensagem de erro

### ❌ Problema 3: Graceful Shutdown Não Funciona
**Sintoma:** `State 'stop-sigterm' timed out. Killing.` (processo morto com SIGKILL)  
**Causa:** Bot travado esperando CISA, não responde ao SIGTERM  
**Solução:**
- Reduzido `TimeoutStopSec` de 90s para 45s
- Adicionado `KillMode=mixed` para melhor controle

---

## 🔧 Correções Aplicadas

### 1. `src/rss_parser.py`
```python
# ANTES: Sem timeout (podia travar indefinidamente)
feed = feedparser.parse(feed_url)

# DEPOIS: Com timeout de 30s
response = self.session.get(feed_url, timeout=self.timeout)  # 30s
feed = feedparser.parse(response.content)

# + Retry com exponential backoff
# + Tratamento específico para Timeout
```

### 2. `src/telegram_bot.py`
```python
# ANTES: Sem retry, delay de 2s
await self.bot.send_message(...)
await asyncio.sleep(2)

# DEPOIS: Com retry logic + delay de 3s
for attempt in range(max_retries):  # 3 tentativas
    try:
        await self.bot.send_message(...)
        break
    except Exception as e:
        if "flood control" in str(e):
            # Extrai tempo da mensagem: "Retry in 11 seconds"
            wait_time = extract_wait_time(e)
            await asyncio.sleep(wait_time)

await asyncio.sleep(3)  # Delay aumentado para 3s
```

### 3. `newshack.service`
```ini
# Adicionado:
TimeoutStopSec=45       # Timeout para shutdown (antes: 90s default)
KillMode=mixed          # Tenta SIGTERM, depois SIGKILL
KillSignal=SIGTERM      # Sinal padrão
```

---

## 🚀 Deploy no Servidor

### Passo 1: Atualizar Código
```bash
cd ~/bots/newshack
git pull
```

### Passo 2: Atualizar Serviço Systemd
```bash
# Copiar novo arquivo de serviço
sudo cp ~/bots/newshack/newshack.service /etc/systemd/system/newshack.service

# OU editar manualmente
sudo nano /etc/systemd/system/newshack.service

# Adicionar estas linhas na seção [Service]:
#   TimeoutStopSec=45
#   KillMode=mixed
#   KillSignal=SIGTERM

# Recarregar systemd
sudo systemctl daemon-reload
```

### Passo 3: Reiniciar Bot
```bash
# Reiniciar serviço
sudo systemctl restart newshack

# Verificar status
sudo systemctl status newshack

# Monitorar logs em tempo real
sudo journalctl -u newshack -f
```

---

## 📊 Monitoramento Pós-Deploy

### Verificar se CISA não trava mais
```bash
# Monitorar logs e procurar por CISA
tail -f ~/bots/newshack/logs/newshack.log | grep -i "CISA"

# Deve aparecer:
# "Parsing feed: CISA Advisories"
# "Successfully parsed X entries from CISA Advisories"
# OU
# "Timeout fetching feed CISA Advisories after 30s"
```

### Verificar se Flood Control está resolvido
```bash
# Procurar por flood control nos logs
grep -i "flood control" ~/bots/newshack/logs/newshack.log | tail -n 10

# Deve aparecer (se houver):
# "Flood control hit, waiting 11s before retry (attempt 1/3)"
# "Flood control hit, waiting 11s before retry (attempt 2/3)"
# Sem sequências de 20+ erros
```

### Verificar shutdown limpo
```bash
# Testar restart
sudo systemctl restart newshack

# Ver logs de shutdown
sudo journalctl -u newshack -n 20

# Deve aparecer:
# "Shutdown signal received, stopping tasks..."
# "News Hack Bot stopped"
# "Stopped newshack.service"
# 
# NÃO deve aparecer:
# "State 'stop-sigterm' timed out. Killing."
```

---

## 🎯 Resultados Esperados

✅ **CISA Feed:**
- Timeout após 30s se travar
- Bot continua funcionando com outros feeds
- 3 tentativas antes de desistir

✅ **Flood Control:**
- Detecção automática de rate limit
- Espera o tempo solicitado pelo Telegram
- Máximo 3 tentativas por mensagem
- Delay de 3s entre mensagens (reduz ocorrências)

✅ **Graceful Shutdown:**
- Bot para em 45s ou menos
- Sem necessidade de SIGKILL
- Logs mostram shutdown limpo

---

## 🔄 Se o Problema Persistir

### Opção A: Desabilitar Feed CISA Temporariamente
```bash
# Editar feeds
nano ~/bots/newshack/config/rss_feeds.py

# Comentar ou remover CISA:
# {
#     "name": "CISA Advisories",
#     "url": "https://www.cisa.gov/cybersecurity-advisories/all.xml",
#     "category": "advisories",
#     "priority": "medium"  # Já está em medium, não high
# },

# Reiniciar
sudo systemctl restart newshack
```

### Opção B: Reduzir Timeout ainda mais
```bash
# Editar main.py
nano ~/bots/newshack/main.py

# Linha 73: Reduzir timeout de 30s para 15s
parser = RSSParser(timeout=15, max_retries=3)

# Reiniciar
sudo systemctl restart newshack
```

### Opção C: Aumentar Delay entre mensagens
```bash
# Editar telegram_bot.py
nano ~/bots/newshack/src/telegram_bot.py

# Linha 562: Aumentar de 3 para 5
retry_delay = 5  # 5 segundos entre mensagens

# Reiniciar
sudo systemctl restart newshack
```

---

## 📈 Logs para Análise Futura

### Comando Completo de Diagnóstico
```bash
{
  echo "=== STATUS ==="
  sudo systemctl status newshack
  echo -e "\n=== ÚLTIMAS 100 LINHAS ==="
  sudo journalctl -u newshack -n 100 --no-pager
  echo -e "\n=== ERROS ==="
  grep -i "error\|exception\|timeout" ~/bots/newshack/logs/newshack.log | tail -n 50
  echo -e "\n=== FLOOD CONTROL ==="
  grep -i "flood" ~/bots/newshack/logs/newshack.log | tail -n 20
  echo -e "\n=== CISA STATUS ==="
  grep -i "cisa" ~/bots/newshack/logs/newshack.log | tail -n 10
} > ~/newshack-status-$(date +%Y%m%d-%H%M%S).log

echo "Relatório salvo em: ~/newshack-status-*.log"
```

---

## ✅ Checklist de Deployment

- [ ] `git pull` executado
- [ ] Arquivo `newshack.service` atualizado
- [ ] `systemctl daemon-reload` executado
- [ ] Bot reiniciado com `systemctl restart newshack`
- [ ] Status verificado: `systemctl status newshack` → "active (running)"
- [ ] Logs monitorados: sem "timeout" no CISA
- [ ] Logs monitorados: sem sequências de "flood control"
- [ ] Shutdown testado: sem "timed out. Killing"
- [ ] Comandos no Telegram funcionando: `/news`, `/categories`, `/recent`

---

**Data da Correção:** 2025-11-02  
**Versão:** v1.2.1  
**Status:** ✅ Pronto para deploy
