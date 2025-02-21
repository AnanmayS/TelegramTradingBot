from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import re
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get environment variables
TOKEN: Final = os.getenv('TELEGRAM_TOKEN')
BOT_USERNAME: Final = os.getenv('BOT_USERNAME')

if not TOKEN or not BOT_USERNAME:
    raise ValueError("Please set TELEGRAM_TOKEN and BOT_USERNAME in .env file")

# Add API endpoints
SOLSCAN_API_BASE = "https://api.solscan.io/token"
JUPITER_API_BASE = "https://price.jup.ag/v4/price"


# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = ("Hello! I can help you get information about Solana tokens.\n"
                      "Just send me a token address, and I will fetch the details for you!")
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_message = ("To use this bot:\n\n"
                   "1. Send a Solana token address\n"
                   "   (e.g., EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v)\n\n"
                   "2. I will return information about:\n"
                   "   • Token name and symbol\n"
                   "   • Market statistics\n"
                   "   • Price information\n"
                   "   • Historical data\n"
                   "   • Relevant links")
    await update.message.reply_text(help_message)

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is a custom command')


# Response Handler

def is_valid_solana_address(address: str) -> bool:
    # Basic validation for Solana addresses
    return bool(re.match(r'^[1-9A-HJ-NP-Za-km-z]{32,44}$', address))

def get_token_info(address: str) -> dict:
    try:
        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        
        # Try DexScreener API for price and token info
        dexscreener_response = requests.get(
            f"https://api.dexscreener.com/latest/dex/tokens/{address}",
            headers=headers,
            timeout=10  # Add timeout
        )
        
        # Initialize with empty data structure
        dexscreener_data = {"pairs": []} 
        if dexscreener_response.ok:
            try:
                dexscreener_data = dexscreener_response.json()
            except:
                pass

        # Try pump.fun API as backup
        pump_response = requests.get(
            f"https://api.pump.fun/token/{address}",
            headers=headers,
            timeout=10  # Add timeout
        )
        
        # Initialize with empty data structure
        pump_data = {"data": {}}
        if pump_response.ok:
            try:
                pump_data = pump_response.json()
            except:
                pass

        return {
            "success": True,
            "dexscreener_data": dexscreener_data,
            "pump_data": pump_data,
            "address": address  # Store the original address
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def format_token_info(token_info: dict) -> str:
    if not token_info["success"]:
        return f"Error fetching token information: {token_info.get('error', 'Unknown error')}"

    dexscreener_data = token_info["dexscreener_data"]
    pump_data = token_info["pump_data"]
    address = token_info.get("address", "N/A")

    # Format the response
    response = "📊 Token Information:\n\n"
    
    # Initialize variables
    token_name = "N/A"
    token_symbol = "N/A"
    price = "N/A"
    has_data = False
    
    # Get data from DexScreener if available
    if dexscreener_data and "pairs" in dexscreener_data and dexscreener_data["pairs"]:
        has_data = True
        pair = dexscreener_data["pairs"][0]  # Get the first trading pair
        token_name = pair.get("baseToken", {}).get("name", "N/A")
        token_symbol = pair.get("baseToken", {}).get("symbol", "N/A")
        price = pair.get("priceUsd", "N/A")
        
        response += f"Name: {token_name}\n"
        response += f"Symbol: {token_symbol}\n"
        response += f"Blockchain: Solana\n"
        response += f"Address: {address}\n\n"
        
        # Price and market info
        response += "💰 Market Information:\n"
        response += f"Price: ${price}\n"
        if "priceChange" in pair:
            response += f"24h Change: {pair['priceChange'].get('h24', 'N/A')}%\n"
        
        # Safely get volume and liquidity with default 0
        try:
            volume = float(pair.get('volume', {}).get('h24', 0))
            response += f"24h Volume: ${volume:,.2f}\n"
        except (ValueError, TypeError):
            response += "24h Volume: N/A\n"
            
        try:
            liquidity = float(pair.get('liquidity', {}).get('usd', 0))
            response += f"Liquidity: ${liquidity:,.2f}\n"
        except (ValueError, TypeError):
            response += "Liquidity: N/A\n"
        
        # DEX info
        response += f"\n📈 Trading Information:\n"
        response += f"DEX: {pair.get('dexId', 'N/A')}\n"
        response += f"Pair: {pair.get('pairAddress', 'N/A')}\n"
    
    # Fallback to pump.fun data if DexScreener doesn't have info
    if not has_data and pump_data and "data" in pump_data:
        has_data = True
        pump_info = pump_data["data"]
        token_name = pump_info.get("name", "N/A")
        token_symbol = pump_info.get("symbol", "N/A")
        
        response += f"Name: {token_name}\n"
        response += f"Symbol: {token_symbol}\n"
        response += f"Blockchain: Solana\n"
        response += f"Address: {address}\n\n"
        
        response += "📈 Trading Information:\n"
        try:
            market_cap = float(pump_info.get("marketCap", 0))
            response += f"Market Cap: ${market_cap:,.2f}\n"
        except (ValueError, TypeError):
            response += "Market Cap: N/A\n"
            
        try:
            volume = float(pump_info.get("volume24h", 0))
            response += f"24h Volume: ${volume:,.2f}\n"
        except (ValueError, TypeError):
            response += "24h Volume: N/A\n"
            
        if "holders" in pump_info:
            response += f"Holders: {pump_info['holders']}\n"

    # If no data was found from either source
    if not has_data:
        response += f"Name: Not Found\n"
        response += f"Symbol: Not Found\n"
        response += f"Blockchain: Solana\n"
        response += f"Address: {address}\n\n"
        response += "No trading data available for this token.\n"

    # Add links section
    response += "\n🔗 Links:\n"
    response += "Trading: https://pump.fun\n"
    
    if pump_data and "data" in pump_data and "socials" in pump_data["data"]:
        socials = pump_data["data"]["socials"]
        if "twitter" in socials:
            response += f"Twitter: {socials['twitter']}\n"
        if "telegram" in socials:
            response += f"Telegram: {socials['telegram']}\n"
        if "website" in socials:
            response += f"Website: {socials['website']}\n"
    
    # Add DexScreener link
    response += f"DexScreener: https://dexscreener.com/solana/{address}\n"

    return response

def handle_response(text: str) -> str:
    processed: str = text.strip()
    
    if is_valid_solana_address(processed):
        token_info = get_token_info(processed)
        return format_token_info(token_info)
    
    return ("Please send a valid Solana token address.\n"
            "Example: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}" ')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return

    else:
        response: str = handle_response(text)

    print('Bot:', response)
    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


if __name__ == '__main__':
    print("Starting Bot...")
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))


    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))


    # Errors
    app.add_error_handler(error)

    print("Polling...")
    app.run_polling(poll_interval=3)
