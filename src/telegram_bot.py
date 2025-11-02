"""
Telegram Bot module for News Hack Bot
Handles all Telegram interactions and message formatting
"""
import logging
from typing import List, Dict, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from telegram.constants import ParseMode
import html

logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram Bot handler for News Hack"""
    
    def __init__(self, token: str, database, rss_parser):
        """
        Initialize Telegram Bot
        
        Args:
            token: Telegram Bot API token
            database: Database instance
            rss_parser: RSS Parser instance
        """
        self.token = token
        self.db = database
        self.parser = rss_parser
        self.application = None
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🔐 <b>Bem-vindo ao News Hack Bot!</b>

Seu agregador de notícias de hacking e cibersegurança.

<b>📋 Comandos Disponíveis:</b>

🔹 /news - Ver últimas notícias não enviadas
🔹 /recent - Notícias das últimas 24 horas
🔹 /stats - Estatísticas do bot
🔹 /feeds - Status dos feeds RSS
🔹 /categories - Ver notícias por categoria
🔹 /search [termo] - Buscar notícias
🔹 /update - Forçar atualização dos feeds
🔹 /help - Mostrar esta ajuda

<b>🎯 Categorias Disponíveis:</b>
• News - Notícias gerais
• Research - Pesquisas técnicas
• Exploits - Vulnerabilidades e exploits
• Malware - Análise de malware
• Threat Intel - Inteligência de ameaças
• Tools - Ferramentas de hacking

O bot verifica automaticamente os feeds e envia novas notícias!
"""
        await update.message.reply_text(welcome_message, parse_mode=ParseMode.HTML)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        await self.start_command(update, context)
    
    async def news_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /news command - show unsent news"""
        await update.message.reply_text("🔍 Buscando notícias não enviadas...")
        
        news = self.db.get_unsent_news(limit=10)
        
        if not news:
            await update.message.reply_text("✅ Não há notícias novas no momento!")
            return
        
        await update.message.reply_text(f"📰 Encontradas {len(news)} notícias:\n")
        
        for entry in news:
            message = self._format_news_message(entry)
            try:
                await update.message.reply_text(message, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
                self.db.mark_as_sent(entry['id'])
            except Exception as e:
                logger.error(f"Error sending news: {e}")
    
    async def recent_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /recent command - show recent news"""
        await update.message.reply_text("🔍 Buscando notícias recentes...")
        
        news = self.db.get_recent_news(hours=24, limit=15)
        
        if not news:
            await update.message.reply_text("❌ Nenhuma notícia encontrada nas últimas 24 horas.")
            return
        
        await update.message.reply_text(f"📰 Últimas 24 horas - {len(news)} notícias:\n")
        
        for entry in news[:10]:  # Limit to 10 to avoid spam
            message = self._format_news_message(entry, include_source=True)
            try:
                await update.message.reply_text(message, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
            except Exception as e:
                logger.error(f"Error sending recent news: {e}")
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command - show statistics"""
        stats = self.db.get_stats()
        
        stats_message = f"""
📊 <b>Estatísticas do News Hack Bot</b>

📈 <b>Geral:</b>
• Total de notícias: {stats.get('total_entries', 0)}
• Enviadas: {stats.get('sent_entries', 0)}
• Pendentes: {stats.get('unsent_entries', 0)}
• Hoje: {stats.get('today_entries', 0)}

📂 <b>Por Categoria:</b>
"""
        
        by_category = stats.get('by_category', {})
        for category, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True)[:10]:
            stats_message += f"• {category}: {count}\n"
        
        await update.message.reply_text(stats_message, parse_mode=ParseMode.HTML)
    
    async def feeds_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /feeds command - show feed status"""
        feed_status = self.db.get_feed_status()
        
        if not feed_status:
            await update.message.reply_text("❌ Nenhum feed verificado ainda.")
            return
        
        # Separate active and error feeds
        active_feeds = [f for f in feed_status if f['error_count'] == 0]
        error_feeds = [f for f in feed_status if f['error_count'] > 0]
        
        message = f"""
📡 <b>Status dos Feeds RSS</b>

✅ <b>Ativos:</b> {len(active_feeds)}
❌ <b>Com Erros:</b> {len(error_feeds)}
📊 <b>Total:</b> {len(feed_status)}
"""
        
        if error_feeds:
            message += "\n⚠️ <b>Feeds com problemas:</b>\n"
            for feed in error_feeds[:5]:
                message += f"• {feed['feed_name']} (erros: {feed['error_count']})\n"
        
        await update.message.reply_text(message, parse_mode=ParseMode.HTML)
    
    async def categories_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /categories command - show categories"""
        keyboard = [
            [InlineKeyboardButton("🔥 News", callback_data="cat_news"),
             InlineKeyboardButton("🔬 Research", callback_data="cat_research")],
            [InlineKeyboardButton("💣 Exploits", callback_data="cat_exploits"),
             InlineKeyboardButton("🦠 Malware", callback_data="cat_malware")],
            [InlineKeyboardButton("🎯 Threat Intel", callback_data="cat_threat_intel"),
             InlineKeyboardButton("🛠️ Tools", callback_data="cat_tools")],
            [InlineKeyboardButton("📚 All Categories", callback_data="cat_all")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "📂 Selecione uma categoria:",
            reply_markup=reply_markup
        )
    
    async def category_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle category button callbacks"""
        query = update.callback_query
        await query.answer()
        
        category = query.data.replace("cat_", "")
        
        # Get news by category from database
        if category == "all":
            news = self.db.get_recent_news(hours=48, limit=20)
        else:
            # Filter by category - use 7 days for less frequent categories
            hours = 168 if category in ['tools', 'malware', 'cloud', 'crypto'] else 48
            all_news = self.db.get_recent_news(hours=hours, limit=100)
            news = [n for n in all_news if n.get('category') == category][:10]
        
        if not news:
            await query.edit_message_text(f"❌ Nenhuma notícia encontrada na categoria: {category}")
            return
        
        await query.edit_message_text(f"📰 Categoria: {category.upper()} - {len(news)} notícias")
        
        for entry in news[:5]:  # Limit to avoid spam
            message = self._format_news_message(entry, include_source=True)
            try:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=message,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
            except Exception as e:
                logger.error(f"Error sending category news: {e}")
    
    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /search command - search news"""
        if not context.args:
            await update.message.reply_text("❌ Use: /search [termo de busca]")
            return
        
        search_term = " ".join(context.args).lower()
        await update.message.reply_text(f"🔍 Buscando por: {search_term}")
        
        # Get recent news and filter by search term
        all_news = self.db.get_recent_news(hours=72, limit=200)
        results = [
            n for n in all_news 
            if search_term in n.get('title', '').lower() or 
               search_term in n.get('description', '').lower()
        ]
        
        if not results:
            await update.message.reply_text(f"❌ Nenhum resultado encontrado para: {search_term}")
            return
        
        await update.message.reply_text(f"✅ Encontrados {len(results)} resultados:\n")
        
        for entry in results[:8]:
            message = self._format_news_message(entry, include_source=True)
            try:
                await update.message.reply_text(message, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
            except Exception as e:
                logger.error(f"Error sending search result: {e}")
    
    async def update_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /update command - force feed update"""
        await update.message.reply_text("🔄 Iniciando atualização dos feeds RSS...")
        
        # This will be called by the scheduler
        from config.rss_feeds import get_all_feeds
        feeds = get_all_feeds()
        
        await update.message.reply_text(f"📡 Verificando {len(feeds)} feeds...")
        
        # Parse feeds
        new_entries = 0
        for feed in feeds[:20]:  # Limit to avoid timeout
            entries = self.parser.parse_feed(feed)
            for entry in entries:
                if self.db.add_news_entry(entry):
                    new_entries += 1
            self.db.update_feed_status(feed['name'], feed['url'], success=True)
        
        await update.message.reply_text(f"✅ Atualização concluída! {new_entries} novas notícias encontradas.")
    
    def _format_news_message(self, entry: Dict, include_source: bool = False) -> str:
        """
        Format a news entry for Telegram
        
        Args:
            entry: News entry dictionary
            include_source: Whether to include source information
        
        Returns:
            Formatted message string
        """
        # Escape HTML special characters
        title = html.escape(entry.get('title', 'No Title'))
        link = entry.get('link', '')
        description = html.escape(entry.get('description', '')[:300])
        
        # Priority emoji
        priority_emoji = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }.get(entry.get('priority', 'medium'), '🟡')
        
        # Category emoji
        category_emoji = {
            'news': '📰',
            'research': '🔬',
            'exploits': '💣',
            'malware': '🦠',
            'threat_intel': '🎯',
            'tools': '🛠️',
            'vulnerabilities': '🔓',
            'advisories': '⚠️',
            'pentest': '🔐',
            'crypto': '🔐',
            'cloud': '☁️'
        }.get(entry.get('category', 'news'), '📰')
        
        message = f"{priority_emoji} {category_emoji} <b>{title}</b>\n\n"
        
        if description:
            message += f"{description}...\n\n"
        
        if include_source:
            source = html.escape(entry.get('feed_name', 'Unknown'))
            message += f"📡 <i>Fonte: {source}</i>\n"
        
        message += f"🔗 <a href='{link}'>Ler mais</a>"
        
        return message
    
    def _format_news_caption(self, entry: Dict, include_source: bool = False) -> str:
        """
        Format a news entry for photo caption (max 1024 chars)
        
        Args:
            entry: News entry dictionary
            include_source: Whether to include source information
        
        Returns:
            Formatted caption string
        """
        title = html.escape(entry.get('title', 'No Title'))
        link = entry.get('link', '')
        description = html.escape(entry.get('description', '')[:200])  # Shorter for captions
        
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
            'vulnerabilities': '🔓',
            'advisories': '⚠️',
            'pentest': '🔐',
            'crypto': '🔐',
            'cloud': '☁️'
        }.get(entry.get('category', 'news'), '📰')
        
        caption = f"{priority_emoji} {category_emoji} <b>{title}</b>\n\n"
        
        if description:
            caption += f"{description}...\n\n"
        
        if include_source:
            source = html.escape(entry.get('feed_name', 'Unknown'))
            caption += f"📡 <i>Fonte: {source}</i>\n"
        
        caption += f"🔗 <a href='{link}'>Ler mais</a>"
        
        return caption[:1024]  # Telegram caption limit
    
    async def send_news_to_channel(self, chat_id: str, entries: List[Dict]) -> int:
        """
        Send news entries to a Telegram channel/chat
        
        Args:
            chat_id: Telegram chat ID
            entries: List of news entries
        
        Returns:
            Number of successfully sent messages
        """
        sent_count = 0
        
        for entry in entries:
            try:
                image_url = entry.get('image_url')
                
                if image_url:
                    # Send with image
                    caption = self._format_news_caption(entry, include_source=True)
                    await self.application.bot.send_photo(
                        chat_id=chat_id,
                        photo=image_url,
                        caption=caption,
                        parse_mode=ParseMode.HTML
                    )
                else:
                    # Send as text
                    message = self._format_news_message(entry, include_source=True)
                    await self.application.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True
                    )
                
                self.db.mark_as_sent(entry['id'])
                sent_count += 1
                
                # Delay to avoid rate limiting (Telegram: 30 msg/sec for groups, 1 msg/sec for users)
                import asyncio
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error sending news to channel: {e}")
        
        return sent_count
    
    def setup_handlers(self):
        """Setup command and callback handlers"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("news", self.news_command))
        self.application.add_handler(CommandHandler("recent", self.recent_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("feeds", self.feeds_command))
        self.application.add_handler(CommandHandler("categories", self.categories_command))
        self.application.add_handler(CommandHandler("search", self.search_command))
        self.application.add_handler(CommandHandler("update", self.update_command))
        self.application.add_handler(CallbackQueryHandler(self.category_callback, pattern="^cat_"))
        
        logger.info("Bot handlers configured successfully")
    
    async def initialize(self):
        """Initialize the bot application"""
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()
        await self.application.initialize()
        await self.application.start()
        logger.info("Telegram bot initialized successfully")
    
    async def shutdown(self):
        """Shutdown the bot application"""
        if self.application:
            await self.application.stop()
            await self.application.shutdown()
            logger.info("Telegram bot shutdown successfully")
