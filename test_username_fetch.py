#!/usr/bin/env python3
"""
Script de teste para verificar se conseguimos buscar usernames via API do Telegram
"""
import asyncio
import os
import sys
from dotenv import load_dotenv
from telegram import Bot

# Load environment variables
load_dotenv()

async def test_fetch_username():
    """Test fetching username from Telegram API"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN não encontrado no .env")
        return
    
    bot = Bot(token=token)
    
    # Get a chat_id to test (you can replace this with a real chat_id from your database)
    print("🔍 Digite um chat_id para testar (ou pressione Enter para pular):")
    test_chat_id = input().strip()
    
    if not test_chat_id:
        print("⏭️  Pulando teste individual")
        return
    
    try:
        print(f"\n🔄 Buscando informações do chat_id: {test_chat_id}")
        chat = await bot.get_chat(test_chat_id)
        
        print("\n✅ Informações obtidas:")
        print(f"   ID: {chat.id}")
        print(f"   Username: @{chat.username}" if chat.username else "   Username: None")
        print(f"   First Name: {chat.first_name}")
        print(f"   Last Name: {chat.last_name}")
        print(f"   Type: {chat.type}")
        
        if chat.username:
            print("\n✅ Username encontrado com sucesso!")
        else:
            print("\n⚠️  Este usuário não tem username público")
            
    except Exception as e:
        print(f"\n❌ Erro ao buscar informações: {e}")
        print(f"   Tipo do erro: {type(e).__name__}")

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Teste de Busca de Username via API do Telegram")
    print("=" * 60)
    asyncio.run(test_fetch_username())
