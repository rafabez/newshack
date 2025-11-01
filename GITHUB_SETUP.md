# 🐙 Como Publicar no GitHub

## Criar Repositório no GitHub

### 1. Acesse GitHub.com
- Faça login na sua conta
- Clique em "New repository" (botão verde)

### 2. Configure o Repositório
- **Repository name**: `newshack`
- **Description**: `🔐 Bot Telegram agregador de notícias de hacking e cibersegurança`
- **Visibility**: Public (ou Private se preferir)
- **NÃO** marque "Initialize with README" (já temos)
- Clique em "Create repository"

### 3. Conectar Repositório Local

```bash
cd /home/max/Github/newshack

# Adicionar remote
git remote add origin https://github.com/SEU_USUARIO/newshack.git

# Ou se usar SSH:
git remote add origin git@github.com:SEU_USUARIO/newshack.git

# Verificar
git remote -v
```

### 4. Fazer Push

```bash
# Renomear branch para main (opcional, mas recomendado)
git branch -M main

# Push inicial
git push -u origin main
```

### 5. Verificar no GitHub
- Acesse: `https://github.com/SEU_USUARIO/newshack`
- Verifique se todos os arquivos estão lá

---

## 📝 Adicionar Descrição no GitHub

No repositório, clique em "About" (engrenagem) e adicione:

**Description:**
```
🔐 Bot Telegram agregador de notícias de hacking e cibersegurança
```

**Topics (tags):**
```
telegram-bot, rss, cybersecurity, hacking, infosec, python, news-aggregator, security-tools
```

**Website:**
```
(deixe em branco ou adicione seu site)
```

---

## 🎨 Melhorar README no GitHub

O README.md já está completo com:
- ✅ Badges
- ✅ Índice
- ✅ Características
- ✅ Instalação
- ✅ Uso
- ✅ Documentação

---

## 🔒 Configurar .gitignore

Já configurado! O arquivo `.env` com suas credenciais **NÃO** será enviado ao GitHub.

Arquivos ignorados:
- `.env` (credenciais)
- `*.db` (banco de dados)
- `logs/` (logs)
- `__pycache__/` (cache Python)
- `venv/` (ambiente virtual)

---

## 📦 Releases (Opcional)

### Criar primeira release:

1. No GitHub, vá em "Releases" → "Create a new release"
2. Tag: `v1.0.0`
3. Title: `News Hack Bot v1.0.0 - Initial Release`
4. Description:
```markdown
## 🎉 First Release!

### Features
- ✅ 60+ RSS feeds (mainstream + underground)
- ✅ Telegram bot with 8 interactive commands
- ✅ SQLite database with duplicate control
- ✅ Automatic scheduling system
- ✅ Systemd service for permanent execution
- ✅ Complete documentation

### Installation
See [INSTALL_GUIDE.md](INSTALL_GUIDE.md) for detailed instructions.

### Quick Start
See [QUICK_START.md](QUICK_START.md) for 5-minute setup.
```

---

## 🌟 Adicionar ao GitHub Stars (Opcional)

Peça para amigos darem star no seu projeto! ⭐

---

## 📢 Compartilhar

Compartilhe seu bot em:
- Reddit: r/Python, r/netsec, r/cybersecurity
- Twitter/X: #Python #Cybersecurity #TelegramBot
- LinkedIn
- Fóruns de segurança

---

## 🔄 Workflow de Atualizações

### Fazer mudanças:
```bash
# Editar arquivos
nano src/telegram_bot.py

# Adicionar mudanças
git add .

# Commit
git commit -m "Add new feature: X"

# Push
git push origin main
```

### No servidor VPS:
```bash
cd ~/newshack
git pull
sudo systemctl restart newshack
```

---

## 🤝 Aceitar Contribuições

### Criar arquivo CONTRIBUTING.md:

```markdown
# Contributing to News Hack Bot

We welcome contributions! Here's how:

1. Fork the repository
2. Create a branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Open a Pull Request

## Guidelines
- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Keep commits atomic and descriptive
```

---

## 📊 GitHub Actions (CI/CD - Opcional)

### Criar `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Test feeds
      run: |
        python test_feeds.py
```

---

## ✅ Checklist de Publicação

- [ ] Repositório criado no GitHub
- [ ] Remote adicionado
- [ ] Push realizado
- [ ] README visível
- [ ] .gitignore funcionando
- [ ] Descrição e topics adicionados
- [ ] License visível (MIT)
- [ ] Documentação completa
- [ ] Release criada (opcional)
- [ ] Compartilhado (opcional)

---

## 🎉 Pronto!

Seu projeto está no GitHub e pronto para ser clonado em qualquer servidor!

**URL do repositório:**
```
https://github.com/SEU_USUARIO/newshack
```

**Clone command:**
```bash
git clone https://github.com/SEU_USUARIO/newshack.git
```
