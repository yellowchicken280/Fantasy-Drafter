# main.py

# =================================================================================
# 1. IMPORT LIBRARIES
# =================================================================================
# These are the necessary libraries for the bot to function.
# gspread: Interacts with the Google Sheets API.
# google.oauth2: Handles authentication with Google services.
# discord: Interacts with the Discord API.
# =================================================================================
import gspread
from google.oauth2.service_account import Credentials
import discord


# =================================================================================
# 2. BOT & SERVER CONFIGURATION (NEEDS TO BE EDITED)
# =================================================================================
# --- EDIT THESE VALUES FOR YOUR SERVER ---
# token: Your unique Discord bot token. Get this from the Discord Developer Portal.
# serverid: The ID of your Discord server (called a "Guild"). Enable Developer Mode in Discord, right-click your server icon, and click "Copy Server ID".
# =================================================================================
token = "GET_YOUR_DISCORD_
