"""
Telegram Bot module for News Hack Bot
Handles all Telegram interactions and message formatting
"""
import logging
import os
import asyncio
from typing import List, Dict, Optional
from functools import wraps
from datetime import datetime
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


def admin_only(func):
    """Decorator to restrict commands to admin only"""
    @wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        admin_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        if not admin_chat_id:
            return
        
        user_chat_id = str(update.effective_chat.id)
        if user_chat_id != admin_chat_id:
            await update.message.reply_text("⛔ Este comando é restrito ao administrador.")
            return
        
        return await func(self, update, context)
    return wrapper


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
    
    def _track_user(self, update: Update, command: str):
        """Track user activity"""
        try:
            user = update.effective_user
            chat_id = update.effective_chat.id
            self.db.register_user(
                chat_id=chat_id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
            self.db.log_command(chat_id=chat_id, command=command)
        except Exception as e:
            logger.error(f"Error tracking user: {e}")
    
    def _is_admin(self, chat_id: int) -> bool:
        """Check if user is admin"""
        admin_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        return admin_chat_id and str(chat_id) == admin_chat_id
    
    def _get_news_keyboard(self, entry: Dict, chat_id: int) -> Optional[InlineKeyboardMarkup]:
        """Get inline keyboard for news entry (with broadcast button for admin)"""
        if not self._is_admin(chat_id):
            return None
        
        # Create broadcast button with news entry ID
        keyboard = [
            [InlineKeyboardButton("📢 Broadcast para Todos", callback_data=f"broadcast_{entry.get('id')}")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        self._track_user(update, "start")
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
• Exploits - Exploits e PoCs
• Vulnerabilities - CVEs e vulnerabilidades
• Malware - Análise de malware
• Threat Intel - Inteligência de ameaças
• Tools - Ferramentas de hacking
• Tutorials - Tutoriais e guias
• Pentest - Testes de penetração
• Advisories - Alertas de segurança
• Analysis - Análises de segurança
• Cloud - Segurança em nuvem
• Crypto - Criptografia
• Community - Comunidade e discussões

O bot verifica automaticamente os feeds e envia novas notícias!
"""
        
        # Add admin commands if user is admin
        admin_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        if admin_chat_id and str(update.effective_chat.id) == admin_chat_id:
            welcome_message += """
<b>👑 Comandos Admin:</b>

🔸 /adminstats - Estatísticas detalhadas (usuários, uso)
🔸 /users - Listar todos os usuários do bot
🔸 /broadcast [msg] - Enviar mensagem para todos
🔸 /feedstatus - Status detalhado dos feeds RSS
"""
        
        await update.message.reply_text(welcome_message, parse_mode=ParseMode.HTML)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        self._track_user(update, "help")
        await self.start_command(update, context)
    
    async def news_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /news command - show unsent news"""
        self._track_user(update, "news")
        await update.message.reply_text("🔍 Buscando notícias não enviadas...")
        
        news = self.db.get_unsent_news(limit=10)
        
        if not news:
            await update.message.reply_text("✅ Não há notícias novas no momento!")
            return
        
        await update.message.reply_text(f"📰 Encontradas {len(news)} notícias:\n")
        
        for entry in news:
            message = self._format_news_message(entry)
            keyboard = self._get_news_keyboard(entry, update.effective_chat.id)
            try:
                await update.message.reply_text(
                    message, 
                    parse_mode=ParseMode.HTML, 
                    disable_web_page_preview=True,
                    reply_markup=keyboard
                )
                self.db.mark_as_sent(entry['id'])
            except Exception as e:
                logger.error(f"Error sending news: {e}")
    
    async def recent_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /recent command - show recent news"""
        self._track_user(update, "recent")
        await update.message.reply_text("🔍 Buscando notícias recentes...")
        
        news = self.db.get_recent_news(hours=24, limit=15)
        
        if not news:
            await update.message.reply_text("❌ Nenhuma notícia encontrada nas últimas 24 horas.")
            return
        
        await update.message.reply_text(f"📰 Últimas 24 horas - {len(news)} notícias:\n")
        
        for entry in news:
            message = self._format_news_message(entry, include_source=True)
            keyboard = self._get_news_keyboard(entry, update.effective_chat.id)
            try:
                await update.message.reply_text(
                    message, 
                    parse_mode=ParseMode.HTML, 
                    disable_web_page_preview=True,
                    reply_markup=keyboard
                )
            except Exception as e:
                logger.error(f"Error sending recent news: {e}")
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command - show statistics"""
        self._track_user(update, "stats")
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
        self._track_user(update, "feeds")
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
        """Handle /categories command - show categories with news count"""
        self._track_user(update, "categories")
        
        # Get category statistics from database
        stats = self.db.get_stats()
        categories_count = stats.get('by_category', {})
        
        # Category emoji mapping
        category_emojis = {
            'news': '🔥',
            'research': '🔬',
            'exploits': '💣',
            'vulnerabilities': '🛆',
            'malware': '🦠',
            'threat_intel': '🎯',
            'tools': '🛠️',
            'tutorials': '📖',
            'pentest': '🎯',
            'advisories': '⚠️',
            'analysis': '📊',
            'cloud': '☁️',
            'crypto': '🔐',
            'community': '👥'
        }
        
        # Category name mapping (for display)
        category_names = {
            'news': 'News',
            'research': 'Research',
            'exploits': 'Exploits',
            'vulnerabilities': 'Vulnerabilities',
            'malware': 'Malware',
            'threat_intel': 'Threat Intel',
            'tools': 'Tools',
            'tutorials': 'Tutorials',
            'pentest': 'Pentest',
            'advisories': 'Advisories',
            'analysis': 'Analysis',
            'cloud': 'Cloud',
            'crypto': 'Crypto',
            'community': 'Community'
        }
        
        # Build keyboard with only categories that have news
        # Sort by count (descending)
        sorted_categories = sorted(categories_count.items(), key=lambda x: x[1], reverse=True)
        
        keyboard = []
        row = []
        for category, count in sorted_categories:
            if count > 0:  # Only show categories with news
                emoji = category_emojis.get(category, '📰')
                name = category_names.get(category, category.capitalize())
                button_text = f"{emoji} {name} ({count})"
                row.append(InlineKeyboardButton(button_text, callback_data=f"cat_{category}"))
                
                # Create rows of 2 buttons
                if len(row) == 2:
                    keyboard.append(row)
                    row = []
        
        # Add remaining button if odd number
        if row:
            keyboard.append(row)
        
        # Add "All Categories" button at the end
        total_news = sum(categories_count.values())
        keyboard.append([InlineKeyboardButton(f"📚 Todas ({total_news})", callback_data="cat_all")])
        
        if not keyboard or len(keyboard) == 1:  # Only "All" button
            await update.message.reply_text("❌ Nenhuma notícia disponível no momento.")
            return
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "📂 <b>Selecione uma categoria:</b>\n\n"
            "<i>Mostrando apenas categorias com notícias disponíveis</i>",
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
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
            keyboard = self._get_news_keyboard(entry, query.message.chat_id)
            try:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=message,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                    reply_markup=keyboard
                )
            except Exception as e:
                logger.error(f"Error sending category news: {e}")
    
    async def broadcast_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle broadcast button callback (admin only)"""
        query = update.callback_query
        
        # Check if admin
        if not self._is_admin(query.message.chat_id):
            await query.answer("⛔ Apenas o administrador pode fazer broadcast.", show_alert=True)
            return
        
        await query.answer()
        
        # Extract news ID from callback data
        try:
            news_id = int(query.data.replace("broadcast_", ""))
        except:
            await query.answer("❌ Erro ao processar ID da notícia.", show_alert=True)
            return
        
        # Get news entry from database
        try:
            self.db.cursor.execute("SELECT * FROM news_entries WHERE id = ?", (news_id,))
            row = self.db.cursor.fetchone()
            if not row:
                await query.answer("❌ Notícia não encontrada.", show_alert=True)
                return
            entry = dict(row)
        except Exception as e:
            logger.error(f"Error getting news for broadcast: {e}")
            await query.answer("❌ Erro ao buscar notícia.", show_alert=True)
            return
        
        # Get all active users
        users = self.db.get_all_users(days=30)
        
        await query.edit_message_text(
            f"📤 Enviando broadcast para {len(users)} usuários...\n\n"
            f"📰 {entry.get('title', '')[:50]}..."
        )
        
        # Broadcast to all users
        sent = 0
        failed = 0
        
        message = self._format_news_message(entry, include_source=True)
        broadcast_message = f"📢 <b>Notícia Importante:</b>\n\n{message}"
        
        for user in users:
            try:
                # Skip admin (already has it)
                if self._is_admin(user['chat_id']):
                    continue
                
                image_url = entry.get('image_url')
                if image_url:
                    caption = self._format_news_caption(entry, include_source=True)
                    await self.application.bot.send_photo(
                        chat_id=user['chat_id'],
                        photo=image_url,
                        caption=f"📢 <b>Notícia Importante:</b>\n\n{caption}",
                        parse_mode=ParseMode.HTML
                    )
                else:
                    await self.application.bot.send_message(
                        chat_id=user['chat_id'],
                        text=broadcast_message,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True
                    )
                sent += 1
                await asyncio.sleep(0.5)  # Rate limiting
            except Exception as e:
                logger.error(f"Error broadcasting to {user['chat_id']}: {e}")
                failed += 1
        
        # Send confirmation
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"✅ <b>Broadcast Concluído!</b>\n\n"
                 f"📤 Enviado: {sent}\n"
                 f"❌ Falhou: {failed}\n"
                 f"📰 Notícia: {entry.get('title', '')[:80]}...",
            parse_mode=ParseMode.HTML
        )
    
    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /search command - search news"""
        self._track_user(update, "search")
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
            keyboard = self._get_news_keyboard(entry, update.effective_chat.id)
            try:
                await update.message.reply_text(
                    message, 
                    parse_mode=ParseMode.HTML, 
                    disable_web_page_preview=True,
                    reply_markup=keyboard
                )
            except Exception as e:
                logger.error(f"Error sending search result: {e}")
    
    async def update_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /update command - force feed update"""
        self._track_user(update, "update")
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
        
        # Get keyboard for admin (if chat_id is admin)
        try:
            chat_id_int = int(chat_id)
        except:
            chat_id_int = None
        
        for entry in entries:
            max_retries = 3
            retry_delay = 3  # Start with 3 seconds delay between messages
            
            for attempt in range(max_retries):
                try:
                    image_url = entry.get('image_url')
                    keyboard = self._get_news_keyboard(entry, chat_id_int) if chat_id_int else None
                    
                    if image_url:
                        # Send with image
                        caption = self._format_news_caption(entry, include_source=True)
                        await self.application.bot.send_photo(
                            chat_id=chat_id,
                            photo=image_url,
                            caption=caption,
                            parse_mode=ParseMode.HTML,
                            reply_markup=keyboard
                        )
                    else:
                        # Send as text
                        message = self._format_news_message(entry, include_source=True)
                        await self.application.bot.send_message(
                            chat_id=chat_id,
                            text=message,
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview=True,
                            reply_markup=keyboard
                        )
                    
                    self.db.mark_as_sent(entry['id'])
                    sent_count += 1
                    
                    # Success - break retry loop
                    break
                    
                except Exception as e:
                    error_str = str(e)
                    
                    # Handle flood control / rate limiting
                    if "flood control" in error_str.lower() or "retry after" in error_str.lower():
                        # Extract wait time from error message (e.g., "Retry in 11 seconds")
                        import re
                        match = re.search(r'(\d+)\s*second', error_str)
                        wait_time = int(match.group(1)) if match else 15
                        
                        if attempt < max_retries - 1:
                            logger.warning(f"Flood control hit, waiting {wait_time}s before retry (attempt {attempt + 1}/{max_retries})")
                            await asyncio.sleep(wait_time)
                        else:
                            logger.error(f"Failed to send after {max_retries} attempts due to flood control: {e}")
                    else:
                        # Other errors - don't retry
                        logger.error(f"Error sending news to channel: {e}")
                        break
            
            # Delay between messages to avoid rate limiting (increased from 2s to 3s)
            await asyncio.sleep(retry_delay)
        
        return sent_count
    
    @admin_only
    async def admin_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Admin command - detailed statistics"""
        stats = self.db.get_user_stats()
        
        # Format time ago
        last_command = stats.get('last_command_at', 'Nunca')
        if last_command and last_command != 'Nunca':
            try:
                last_dt = datetime.fromisoformat(last_command)
                delta = datetime.now() - last_dt
                if delta.seconds < 60:
                    last_command = f"há {delta.seconds}s"
                elif delta.seconds < 3600:
                    last_command = f"há {delta.seconds // 60}m"
                else:
                    last_command = f"há {delta.seconds // 3600}h"
            except:
                pass
        
        message = f"""
📊 <b>Estatísticas Admin</b>

👥 <b>Usuários:</b>
• Total: {stats.get('total_users', 0)} usuários
• Ativos (7 dias): {stats.get('active_users_7d', 0)} usuários
• Novos hoje: {stats.get('new_users_today', 0)} usuários

💬 <b>Uso:</b>
• Comandos executados: {stats.get('total_commands', 0)}
• Comando mais usado: {stats.get('most_used_command', 'N/A')} ({stats.get('most_used_count', 0)}x)
• Último uso: {last_command}

📰 <b>Notícias:</b>
• No banco: {stats.get('total_news', 0)} notícias
• Adicionadas hoje: {stats.get('news_today', 0)} notícias
"""
        
        await update.message.reply_text(message, parse_mode=ParseMode.HTML)
    
    @admin_only
    async def admin_users_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Admin command - list users"""
        users = self.db.get_all_users(days=30)
        
        if not users:
            await update.message.reply_text("❌ Nenhum usuário registrado.")
            return
        
        message = f"👥 <b>Usuários do Bot ({len(users)} total)</b>\n\n"
        
        for user in users[:20]:  # Limit to 20
            username = f"@{user['username']}" if user.get('username') else f"ID:{user['chat_id']}"
            name = user.get('first_name', 'Anônimo')
            
            # Calculate time ago
            try:
                last_seen = datetime.fromisoformat(user['last_seen'])
                delta = datetime.now() - last_seen
                if delta.days > 0:
                    time_ago = f"{delta.days}d atrás"
                elif delta.seconds >= 3600:
                    time_ago = f"{delta.seconds // 3600}h atrás"
                elif delta.seconds >= 60:
                    time_ago = f"{delta.seconds // 60}m atrás"
                else:
                    time_ago = f"{delta.seconds}s atrás"
            except:
                time_ago = "?"
            
            message += f"• {name} ({username}) - {time_ago}\n"
        
        if len(users) > 20:
            message += f"\n... e mais {len(users) - 20} usuários"
        
        await update.message.reply_text(message, parse_mode=ParseMode.HTML)
    
    @admin_only
    async def admin_broadcast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Admin command - broadcast message to all users"""
        if not context.args:
            await update.message.reply_text(
                "📢 <b>Uso:</b> /broadcast sua mensagem aqui\n\n"
                "Enviará a mensagem para todos os usuários ativos (últimos 30 dias).",
                parse_mode=ParseMode.HTML
            )
            return
        
        message_text = " ".join(context.args)
        users = self.db.get_all_users(days=30)
        
        await update.message.reply_text(f"📤 Enviando para {len(users)} usuários...")
        
        sent = 0
        failed = 0
        
        for user in users:
            try:
                await self.application.bot.send_message(
                    chat_id=user['chat_id'],
                    text=f"📢 <b>Mensagem do Admin:</b>\n\n{message_text}",
                    parse_mode=ParseMode.HTML
                )
                sent += 1
                await asyncio.sleep(0.5)  # Rate limiting
            except Exception as e:
                logger.error(f"Error broadcasting to {user['chat_id']}: {e}")
                failed += 1
        
        await update.message.reply_text(
            f"✅ Broadcast concluído!\n\n"
            f"Enviado: {sent}\n"
            f"Falhou: {failed}"
        )
    
    @admin_only
    async def admin_feedstatus_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Admin command - detailed feed status"""
        feed_status = self.db.get_feed_status()
        
        if not feed_status:
            await update.message.reply_text("❌ Nenhum feed verificado ainda.")
            return
        
        active_feeds = [f for f in feed_status if f['error_count'] == 0]
        error_feeds = [f for f in feed_status if f['error_count'] > 0]
        
        # Count news per feed
        from collections import defaultdict
        news_count = defaultdict(int)
        try:
            self.db.cursor.execute("""
                SELECT feed_name, COUNT(*) as count 
                FROM news_entries 
                GROUP BY feed_name 
                ORDER BY count DESC 
                LIMIT 10
            """)
            for row in self.db.cursor.fetchall():
                news_count[row[0]] = row[1]
        except:
            pass
        
        message = f"""
📡 <b>Status Detalhado dos Feeds</b>

✅ <b>Funcionando:</b> {len(active_feeds)} feeds
❌ <b>Com Erro:</b> {len(error_feeds)} feeds

🔝 <b>Top feeds (por notícias):</b>
"""
        
        for feed_name, count in sorted(news_count.items(), key=lambda x: x[1], reverse=True)[:5]:
            message += f"• {feed_name}: {count} notícias\n"
        
        if error_feeds:
            message += f"\n❌ <b>Com problemas:</b>\n"
            for feed in error_feeds[:5]:
                error_msg = feed.get('last_error', 'Unknown')[:50]
                message += f"• {feed['feed_name']}\n  Erro: {error_msg}\n"
        
        await update.message.reply_text(message, parse_mode=ParseMode.HTML)
    
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
        self.application.add_handler(CallbackQueryHandler(self.broadcast_callback, pattern="^broadcast_"))
        
        # Admin commands
        self.application.add_handler(CommandHandler("adminstats", self.admin_stats_command))
        self.application.add_handler(CommandHandler("users", self.admin_users_command))
        self.application.add_handler(CommandHandler("broadcast", self.admin_broadcast_command))
        self.application.add_handler(CommandHandler("feedstatus", self.admin_feedstatus_command))
        
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
