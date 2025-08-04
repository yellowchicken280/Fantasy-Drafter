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
token = "GET_YOUR_DISCORD_BOT_TOKEN_HERE"
intents = discord.Intents.default()
intents.message_content = True  # Allows the bot to read message content.
client = discord.Client(intents=intents)
serverid = 123456789012345678 # <-- ENTER YOUR SERVER ID HERE (AS AN INTEGER, NOT A STRING)


# =================================================================================
# 3. GOOGLE SHEETS CONFIGURATION (NEEDS TO BE EDITED)
# =================================================================================
# --- EDIT THESE VALUES FOR YOUR SPREADSHEET ---
# sheet_id: The unique ID of your Google Sheet. You can find this in the sheet's URL.
#           (e.g., in "docs.google.com/spreadsheets/d/THIS_IS_THE_ID/edit", copy "THIS_IS_THE_ID")
#
# --- HOW TO SET UP GOOGLE API ACCESS ---
# 1.  Create a project in the Google Cloud Platform.
# 2.  Enable the "Google Sheets API" and "Google Drive API".
# 3.  Create a "Service Account" under "Credentials".
# 4.  Generate a JSON key file for the service account and download it. Rename it to "credentials.json" and place it in the same folder as this script.
# 5.  Share your Google Sheet with the `client_email` found inside the "credentials.json" file, giving it "Editor" permissions.
# =================================================================================
scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
gclient = gspread.authorize(creds)

sheet_id = '1Im_Hyz9AN-IhXKS7LmZjo3YSsiuceBSXm19qk3fw7N4' # <-- ENTER YOUR GOOGLE SHEET ID HERE
sheet = gclient.open_by_key(sheet_id)
# This accesses the second tab (worksheet) in your Google Sheet, which is assumed to hold player rankings.
# Python is 0-indexed, so get_worksheet(1) gets the *second* sheet.
tab2 = sheet.get_worksheet(1)


# =================================================================================
# 4. HELPER FUNCTIONS
# =================================================================================
# Converts a Discord mention string like "<@12345>" into an integer 12345.
def getint(id):
    try:
        return int(id[2:-1])
    except:
        return 0

# Converts a user ID integer like 12345 into a Discord mention string "<@12345>".
def getstr(id):
    return "<@" + str(id) + ">"


# =================================================================================
# 5. GLOBAL DRAFT STATE VARIABLES
# =================================================================================
# These variables track the state of the draft.
row = 5             # Current row on the main draft board (Sheet1).
prow = 0            # Previous row, used for the !change command.
col = 4             # Current column on the main draft board.
pcol = 0            # Previous column, used for the !change command.
picknum = 1         # The current overall pick number.
tradecount = 0      # Tracks the number of trades to log them correctly.
drafted = []        # A list to store the names of players who have been drafted.
order = []          # Initially empty, can be used if needed.


# =================================================================================
# 6. LOAD PLAYER & DRAFT ORDER DATA (NEEDS TO BE EDITED)
# =================================================================================
# Loads player names from your rankings sheet (tab2).
# Assumes QBs are in column C, RBs in H, WRs in M, and TEs in R, starting from row 4.
# --- EDIT THE COLUMN AND ROW NUMBERS IF YOUR SHEET IS FORMATTED DIFFERENTLY ---
qbs = tab2.col_values(3)[3:]
rbs = tab2.col_values(8)[3:]
wrs = tab2.col_values(13)[3:]
tes = tab2.col_values(18)[3:]
players = qbs + rbs + wrs + tes

# Converts all player names to uppercase for case-insensitive matching.
for i in range(len(players)):
    players[i] = players[i].upper()

# --- EDIT THIS LIST WITH YOUR LEAGUE'S DRAFT ORDER ---
# Get each user's Discord ID (Enable Developer Mode, right-click name, "Copy User ID").
# Format must be "<@USER_ID_HERE>". The list should contain 12 managers.
draftOrder = ["<@USER_ID_1>", "<@USER_ID_2>", "<@USER_ID_3>", "<@USER_ID_4>",
              "<@USER_ID_5>", "<@USER_ID_6>", "<@USER_ID_7>", "<@USER_ID_8>",
              "<@USER_ID_9>", "<@USER_ID_10>", "<@USER_ID_11>", "<@USER_ID_12>"]

# Creates the full "snake" draft order for 14 rounds.
rdo = draftOrder[::-1] # Reversed draft order for even rounds.
draft = []
for i in range(14):
    if i % 2 == 0:
        draft += draftOrder # Odd rounds (1, 3, 5...)
    else:
        draft += rdo         # Even rounds (2, 4, 6...)

# --- STARTER CODE ---
# **IMPORTANT**: Run this block of code ONCE and SEPARATELY before the draft starts.
# It pre-populates your Google Sheet with the full draft order.
# After running it once, comment it out or delete it.
"""
tempdraft = [[pick] for pick in draft]
# Assumes you want the draft order in column T, starting at T3.
sheet.sheet1.update("T3:T170", tempdraft)
"""

# =================================================================================
# 7. DISCORD BOT EVENTS
# =================================================================================

# This function runs when the bot successfully connects to Discord.
@client.event
async def on_ready():
    global row, col, picknum, drafted, draft, prow, pcol, tradecount
    # --- EDIT THIS VALUE FOR YOUR SERVER ---
    # Get the ID of the channel where the draft will take place.
    # Right-click the channel name and "Copy Channel ID".
    channel = client.get_channel(123456789012345678) # <-- ENTER DRAFT CHANNEL ID HERE
    print(f'Bot is ready and has logged in as {client.user}')
    # Sends the !restart command to itself to sync its state with the spreadsheet.
    # This is useful if the bot disconnects and reconnects mid-draft.
    await channel.send("!restart")

# This function runs every time a message is sent in a channel the bot can see.
@client.event
async def on_message(message):
    # Make sure we can modify the global state variables from within this function.
    global row, col, picknum, drafted, draft, prow, pcol, tradecount
    
    # Ignore messages from the bot itself to prevent loops.
    if message.author == client.user:
        return
    
    # Check if the message has content to avoid errors from pins, images, etc.
    if len(message.content) > 0:
        command = message.content.split()[0]

        #-------------------
        # !restart COMMAND
        #-------------------
        # Syncs the bot's state with the spreadsheet.
        # This is crucial for recovering from a crash or daily Heroku restart.
        if command == "!restart":
            # Fetches the current pick number from cell Q3 in the sheet.
            # --- EDIT "Q3" (col 17, row 3) IF YOU STORE THE PICK NUMBER ELSEWHERE ---
            picknum = int((sheet.sheet1.col_values(17)[2]))
            await message.channel.send(f"Beep boop... Bot relaunch initiated. We are at pick {picknum}.")

            # Complex logic to calculate the correct row/col on the draft grid based on the pick number.
            if picknum % 12 == 0:
                row = 4 + int(picknum / 12)
            else:
                row = 5 + int(picknum / 12)
            
            if row % 2 == 1: # Odd round
                col = (picknum % 12) + 3 if picknum % 12 != 0 else 15
            else: # Even (snake) round
                col = 16 - (picknum % 12) if picknum % 12 != 0 else 4

            # Calculate the position of the *previous* pick for the !change command.
            if picknum > 1:
                temp = picknum - 1
                prow = 5 + int(temp / 12)
                if prow % 2 == 1:
                    pcol = (temp % 12) + 3 if temp % 12 != 0 else 15
                else:
                    pcol = 16 - (temp % 12) if temp % 12 != 0 else 4
            
            # Reload the list of drafted players and the current draft order from the sheet.
            # Assumes drafted players are in column R (18) and the trade-updated draft order is in column T (20).
            drafted = [x.upper() for x in sheet.sheet1.col_values(18)[2:]]
            draft = sheet.sheet1.col_values(20)[2:]
            
            # Announce the current pick.
            round_num = (picknum - 1) // 12 + 1
            pick_in_round = (picknum - 1) % 12 + 1
            await message.channel.send(f"Relaunch complete. It is Round {round_num}, Pick {pick_in_round}. {draft[picknum-1]} is on the clock!")

        #-------------------
        # !hello COMMAND
        #-------------------
        elif command == "!hello":
            await message.channel.send(f"Hi, {message.author.mention}! Use `!help` to see what I can do.")

        #-------------------
        # !ovr COMMAND
        #-------------------
        elif command == "!ovr":
            await message.channel.send(f"The current overall pick is #{picknum}.")

        #-------------------
        # !start COMMAND
        #-------------------
        elif command == "!start":
            await message.channel.send(f"The draft shall commence! {draft[0]}, you are on the clock. Use `!draft [Player Name]` to make your selection!")

        #-------------------
        # !help COMMAND
        #-------------------
        elif command == "!help":
            help_message = """
Hello! I'm the draft bot. Here are my commands:
`!start`: Officially begins the draft.
`!draft [Player Name]`: Make your draft pick. e.g., `!draft Patrick Mahomes`.
`!change [Player Name]`: Change your *most recent* pick, but only if the next pick hasn't been made.
`!trade [pick1] [pick2] ...`: Log a trade of future picks. The bot will swap the owners for all specified picks. e.g., `!trade 25 48`.
`!ovr`: Shows the current overall pick number.
`!whopick`: Shows who is on the clock for the current pick.
`!hello`: Say hi to me!
            """
            await message.channel.send(help_message)

        #-------------------
        # !draft COMMAND
        #-------------------
        elif command == "!draft":
            txt = message.content
            # Combine all parts of the message after "!draft" into a single player name.
            spick = " ".join(txt.split()[1:])
            
            # --- PICK VALIDATION ---
            # 1. Check if the drafter is the correct person.
            if message.author.id != getint(draft[picknum-1]):
                 await message.channel.send(f"Hold on, it's not your turn! We're waiting on {draft[picknum-1]}.")
                 return
            
            # 2. Check if the player is valid (is in our list and not already drafted).
            if spick.upper() in players and spick.upper() not in drafted:
                # Update the Google Sheet with the pick.
                sheet.sheet1.update_cell(row, col, spick)
                
                # Log the drafted player in column R (18) and the pick number in column Q (17).
                sheet.sheet1.update_cell(1 + picknum, 18, spick)
                sheet.sheet1.update_cell(3, 17, picknum + 1)
                
                drafted.append(spick.upper())
                
                # Announce the successful pick.
                await message.channel.send(f"With pick #{picknum}, {message.author.mention} selects **{spick}**!")
                
                # --- UPDATE STATE FOR NEXT PICK ---
                picknum += 1
                prow, pcol = row, col # Save the current position as the "previous" position.
                
                # Check for the end of the draft. Assumes 168 total picks.
                if picknum > 168:
                    await message.channel.send("And that's a wrap! The draft is complete. Good luck this season!")
                    # Consider adding a quit() or a way to stop the bot here.
                    return
                    
                # Move the spreadsheet cursor to the next pick's location.
                if row % 2 == 1: # Odd round, move right
                    col += 1
                else: # Even round, move left
                    col -= 1
                
                # If we've reached the end of a row, move to the next row.
                if col > 15: # End of an odd round
                    col = 15
                    row += 1
                elif col < 4: # End of an even round
                    col = 4
                    row += 1
                
                # Announce the next pick.
                round_num = (picknum - 1) // 12 + 1
                pick_in_round = (picknum - 1) % 12 + 1
                await message.channel.send(f"Next up: Round {round_num}, Pick {pick_in_round}. {draft[picknum-1]}, you're on the clock!")

            else:
                # Handle invalid picks.
                if spick.upper() in drafted:
                    await message.channel.send(f"Invalid pick. **{spick}** has already been drafted. Please pick again.")
                else:
                    await message.channel.send(f"Invalid pick. I can't find **{spick}** in the player list. Check your spelling and try again.")
        
        #-------------------
        # !change COMMAND
        #-------------------
        elif command == "!change":
            spick = " ".join(message.content.split()[1:])

            # Check if the user trying to change the pick is the one who made the last pick.
            if message.author.id != getint(draft[picknum-2]):
                await message.channel.send("Error: You can only change your own most recent pick.")
            # Check if the new player is valid and available.
            elif spick.upper() in players and spick.upper() not in drafted:
                # Update the previous cell on the sheet.
                sheet.sheet1.update_cell(prow, pcol, spick)
                # Update the master list of drafted players.
                sheet.sheet1.update_cell(picknum, 18, spick)
                # Update the local list of drafted players.
                drafted[-1] = spick.upper()
                await message.channel.send(f"Pick changed successfully to **{spick}**.")
            else:
                await message.channel.send("Invalid player. They might already be drafted or you misspelled their name.")

        #-------------------
        # !whopick COMMAND
        #-------------------
        elif command == "!whopick":
             await message.channel.send(f"{draft[picknum-1]} is currently on the clock.")

        #-------------------
        # !trade COMMAND
        #-------------------
        elif command == "!trade":
            picks_to_trade_str = message.content.split()[1:]
            involved_picks = []
            valid = True

            # Convert all pick numbers to integers.
            for p in picks_to_trade_str:
                try:
                    pick_num = int(p)
                    # You can't trade picks that have already happened.
                    if pick_num < picknum:
                        await message.channel.send(f"Error: Pick #{pick_num} has already passed.")
                        valid = False
                        break
                    involved_picks.append(pick_num)
                except ValueError:
                    await message.channel.send(f"Error: '{p}' is not a valid pick number.")
                    valid = False
                    break
            
            if not valid: return # Stop if there was an error.

            # Identify the owners of the picks being traded.
            parties = set()
            for p in involved_picks:
                parties.add(getint(draft[p-1]))
            
            # The bot only supports two-team trades.
            if len(parties) != 2:
                await message.channel.send("Error: Trades must involve exactly two teams. Please log multi-team trades as separate two-team deals.")
                return

            # Log the trade to the spreadsheet (assumes column S, or 19).
            log = message.content[7:]
            sheet.sheet1.update_cell(3 + tradecount, 19, log)
            tradecount += 1

            # Swap the owners for each pick involved in the trade.
            party_list = list(parties)
            p1_id, p2_id = party_list[0], party_list[1]
            
            for p in involved_picks:
                current_owner_id = getint(draft[p-1])
                if current_owner_id == p1_id:
                    draft[p-1] = getstr(p2_id) # Swap to p2
                else:
                    draft[p-1] = getstr(p1_id) # Swap to p1
            
            # Update the entire draft order in the Google Sheet (column T, or 20).
            tempdraft = [[pick] for pick in draft]
            sheet.sheet1.update("T3:T170", tempdraft)
            await message.channel.send(f"Trade processed! The draft order has been updated. {draft[picknum-1]} is now on the clock.")

# =================================================================================
# 8. RUN THE BOT
# =================================================================================
# This is the final line that starts the bot. The `token` variable must be set correctly.
client.run(token)
