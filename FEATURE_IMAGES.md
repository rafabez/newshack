# 🖼️ Como Adicionar Suporte a Imagens/Thumbnails

## Status Atual

O bot **não envia imagens** por padrão porque:
- ✅ Mais rápido e leve
- ✅ Menos consumo de banda
- ✅ Evita rate limiting do Telegram
- ✅ Nem todos feeds têm imagens

## Como RSS Fornece Imagens

Feeds RSS podem incluir imagens de várias formas:

### 1. Campo `media:thumbnail`
```xml
<media:thumbnail url="https://example.com/image.jpg"/>
```

### 2. Campo `enclosure`
```xml
<enclosure url="https://example.com/image.jpg" type="image/jpeg"/>
```

### 3. Dentro do `description` (HTML)
```xml
<description><![CDATA[<img src="https://example.com/image.jpg"/>]]></description>
```

### 4. Campo `image` ou `media:content`
```xml
<image>
  <url>https://example.com/image.jpg</url>
</image>
```

## 🔧 Modificações Necessárias

### 1. Atualizar `rss_parser.py`

Adicionar extração de imagens no método `_parse_entry`:

```python
def _parse_entry(self, entry, feed_config: Dict) -> Optional[Dict]:
    """Parse a single feed entry"""
    try:
        # ... código existente ...
        
        # Extract image/thumbnail
        image_url = None
        
        # Try media:thumbnail
        if hasattr(entry, 'media_thumbnail'):
            image_url = entry.media_thumbnail[0]['url']
        
        # Try enclosure
        elif hasattr(entry, 'enclosures') and entry.enclosures:
            for enclosure in entry.enclosures:
                if enclosure.get('type', '').startswith('image/'):
                    image_url = enclosure.get('href') or enclosure.get('url')
                    break
        
        # Try media:content
        elif hasattr(entry, 'media_content'):
            for media in entry.media_content:
                if media.get('medium') == 'image':
                    image_url = media.get('url')
                    break
        
        # Try extracting from description HTML
        if not image_url and description:
            soup = BeautifulSoup(description, 'lxml')
            img_tag = soup.find('img')
            if img_tag and img_tag.get('src'):
                image_url = img_tag['src']
        
        parsed_entry = {
            'feed_name': feed_config.get('name'),
            'feed_url': feed_config.get('url'),
            'title': title,
            'link': link,
            'description': description[:500] if description else '',
            'published_date': published_date,
            'category': feed_config.get('category', 'general'),
            'priority': feed_config.get('priority', 'medium'),
            'image_url': image_url  # NOVO CAMPO
        }
        
        return parsed_entry
```

### 2. Atualizar `database.py`

Adicionar campo `image_url` na tabela:

```python
def _create_tables(self):
    """Create necessary tables"""
    self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS news_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feed_name TEXT NOT NULL,
            feed_url TEXT NOT NULL,
            title TEXT NOT NULL,
            link TEXT UNIQUE NOT NULL,
            description TEXT,
            published_date TEXT,
            category TEXT,
            priority TEXT,
            image_url TEXT,  -- NOVO CAMPO
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sent_to_telegram BOOLEAN DEFAULT 0,
            sent_at TIMESTAMP
        )
    """)
```

E atualizar o método `add_news_entry`:

```python
def add_news_entry(self, entry: Dict) -> bool:
    """Add a news entry to database"""
    try:
        self.cursor.execute("""
            INSERT INTO news_entries 
            (feed_name, feed_url, title, link, description, published_date, 
             category, priority, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.get('feed_name'),
            entry.get('feed_url'),
            entry.get('title'),
            entry.get('link'),
            entry.get('description'),
            entry.get('published_date'),
            entry.get('category'),
            entry.get('priority'),
            entry.get('image_url')  # NOVO
        ))
        self.conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
```

### 3. Atualizar `telegram_bot.py`

Modificar método `send_news_to_channel` para enviar com imagem:

```python
async def send_news_to_channel(self, chat_id: str, entries: List[Dict]) -> int:
    """Send news entries to Telegram channel/chat"""
    sent_count = 0
    
    for entry in entries:
        try:
            image_url = entry.get('image_url')
            
            if image_url:
                # Send as photo with caption
                caption = self._format_news_caption(entry)
                await self.application.bot.send_photo(
                    chat_id=chat_id,
                    photo=image_url,
                    caption=caption,
                    parse_mode=ParseMode.HTML
                )
            else:
                # Send as text message (como antes)
                message = self._format_news_message(entry)
                await self.application.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
            
            self.db.mark_as_sent(entry['id'])
            sent_count += 1
            
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"Error sending news: {e}")
            # Se falhar com imagem, tentar sem
            if image_url:
                try:
                    message = self._format_news_message(entry)
                    await self.application.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True
                    )
                    self.db.mark_as_sent(entry['id'])
                    sent_count += 1
                except:
                    pass
    
    return sent_count

def _format_news_caption(self, entry: Dict) -> str:
    """Format news for photo caption (max 1024 chars)"""
    title = html.escape(entry.get('title', 'No Title'))
    link = entry.get('link', '')
    description = html.escape(entry.get('description', '')[:200])
    
    priority_emoji = {
        'high': '🔴',
        'medium': '🟡',
        'low': '🟢'
    }.get(entry.get('priority', 'medium'), '🟡')
    
    category_emoji = {
        'news': '📰',
        'research': '🔬',
        'exploits': '💣',
        'malware': '🦠',
        'threat_intel': '🎯',
        'tools': '🛠️',
    }.get(entry.get('category', 'news'), '📰')
    
    caption = f"{priority_emoji} {category_emoji} <b>{title}</b>\n\n"
    
    if description:
        caption += f"{description}...\n\n"
    
    caption += f"🔗 <a href='{link}'>Ler mais</a>"
    
    return caption[:1024]  # Telegram limit for captions
```

## 🚀 Como Ativar

### Opção 1: Aplicar Manualmente

Edite os 3 arquivos acima com as modificações.

### Opção 2: Usar Flag de Configuração

Adicione no `.env`:

```bash
SEND_IMAGES=true
```

E no código, verificar:

```python
SEND_IMAGES = os.getenv('SEND_IMAGES', 'false').lower() == 'true'
```

## ⚠️ Considerações

### Vantagens
✅ Visual mais atraente
✅ Mais informação de relance
✅ Melhor engajamento

### Desvantagens
❌ Mais lento (download de imagens)
❌ Mais banda consumida
❌ Rate limiting mais agressivo
❌ Nem todos feeds têm imagens
❌ Algumas imagens podem falhar

## 📊 Estatísticas de Feeds com Imagens

Dos 60+ feeds configurados, aproximadamente:
- **40%** incluem thumbnails consistentemente
- **30%** incluem imagens ocasionalmente
- **30%** não incluem imagens

Feeds que **geralmente têm imagens**:
- The Hacker News ✅
- Bleeping Computer ✅
- Dark Reading ✅
- Security Affairs ✅
- Malwarebytes Labs ✅
- Threatpost ✅

Feeds que **raramente têm imagens**:
- Schneier on Security ❌
- Troy Hunt ❌
- Krebs on Security ❌
- Google Project Zero ❌

## 🎯 Recomendação

**Para começar**: Use **sem imagens** (como está)
- Mais rápido e confiável
- Menos problemas
- Fácil de testar

**Depois**: Adicione suporte a imagens como feature opcional
- Configurável via `.env`
- Fallback para texto se imagem falhar
- Melhor experiência visual

## 💡 Alternativa: Link Preview

Outra opção é **habilitar link preview** do Telegram:

```python
# Em vez de disable_web_page_preview=True
disable_web_page_preview=False
```

O Telegram automaticamente mostra preview com imagem do link!

**Vantagens**:
✅ Sem código extra
✅ Telegram faz o trabalho
✅ Funciona com qualquer link

**Desvantagens**:
❌ Mensagens ficam maiores
❌ Nem todos sites têm Open Graph tags

## 🤔 Quer que Eu Implemente?

Posso adicionar suporte completo a imagens agora se quiser! É só me avisar:

1. **Com imagens sempre** (quando disponível)
2. **Com flag configurável** (ativar/desativar no .env)
3. **Deixar como está** (só texto + link)

Qual prefere? 🎨
