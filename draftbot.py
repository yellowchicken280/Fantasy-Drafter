import requests
import gspread
from google.oauth2.service_account import Credentials
import discord
import os


token = "get ur discord token"
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents = intents)
serverid = "put the id of ur own server here as an int"


SPREADSHEET_ID = 'get a spreadsheet id'
RANGE_NAME = 'optional'
API_KEY = 'get api from google cloud console'

scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]

creds = Credentials.from_service_account_file("credentials.json", scopes = scopes)
gclient = gspread.authorize(creds)
sheet_id = 'google sheet id'
sheet = gclient.open_by_key(sheet_id)
tab2 = sheet.get_worksheet(1)


def getint(id):
    try:
        return int(id[2:-1])
    except:
        return 0
def getstr(id):
    return "<@"+str(id)+">"

row = 5
prow = 0
col = 4
pcol = 0
picknum = 1
drafted = []
order = []

qbs = tab2.col_values(3)[3:]
rbs = tab2.col_values(8)[3:]
wrs = tab2.col_values(13)[3:]
tes = tab2.col_values(18)[3:]
players = qbs+rbs+wrs+tes
for i in range(len(players)):
    players[i] = players[i].upper()

#manually enter discord id's here as a string, <@(number)> (don't include paretheses obviously)
draftOrder = []

#this sets the order for the draft

rdo = draftOrder[::-1]
draft = []
for i in range(14):
    if i%2==0:
        draft+=draftOrder
    else:
        draft += rdo


#the help funcitons explain the commands so just read that so i don't have to comment all of them

@client.event
async def on_message(message):
    global row, col, picknum, drafted, draft, prow, pcol
    
    id = client.get_guild(serverid)

    command = message.content.split()[0]    

    if command == "!hello":
        bob = "hi " + "<@" + str(message.author.id)+"> \nuse !help to see what i can do"
        await message.channel.send(bob)

    elif command == "!start":

        await message.channel.send("the 2024 draft shall commence! "+draft[0] + " time to !draft you first pick of the 2024 Stonkers Fantasy Draft!")

    elif command == "!help":
        #tell users each function

        await message.channel.send("Wassup I'm the ultimate discord fantasy draft helper, I will help facilitate and tabulate the draft while simultaneously updating the google sheet so yall dont have to : ) here is how my functions work:\n!hello: it's always polite to say hello\n!start: use this command to commence the draft on the agreed upon start date\nto see how my other functions work, enter the function name plus help, e.g. !hello help \nmy other wonderful commands include !draft, !change, and !trade")

    
    elif command == "!draft":
        txt = message.content
        pick = txt.split()[1:]
        if pick[0]=="help":
            await message.channel.send("use !draft to make a selection in the format !draft [player name]\ne.g. !draft Booger Macfarland \nNOTE: make sure you spell the name exactly correct, so that the spreadsheet can automatically update")
        else:
            spick = ""
            for i in pick:
                spick += i + " "
            spick = spick[:-1]
            #should add pick validation
            if spick not in drafted and spick.upper() in players:
                sheet.sheet1.update_cell(row,col, spick)
                picknum+=1
                if picknum==169:
                        #end draft proccess
                        await message.channel.send("And that is wraps for this years draft! good luck to all (other than dixon). I will commit suicide and cease to run in this server any longer.")
                        quit()
                pcol = col
                prow = row
                if row%2==1:
                    col +=1
                else:
                    col-=1
                drafted.append(spick)
                
                if picknum%12==0:
                    await message.channel.send("good pick! next pick, round "+ str(row - 4)+" pick " + "12"+", is " +draft[picknum-1])
                elif col>15 or col<4:
                    await message.channel.send("good pick! next pick, round "+ str(row - 3)+" pick " + str(picknum%12) +", is " +draft[picknum-1])
                else:
                    await message.channel.send("good pick! next pick, round "+ str(row - 4)+" pick " + str(picknum%12)+", is "+draft[picknum-1])
                
                
                if col>15:
                    col = 15
                    row+=1
                    
                elif col<4:
                    col = 4
                    row+=1
                    
            else:
                await message.channel.send("Draft pick is invalid, pick again. Please make sure you didn't pick someone already drafted or misspelled the name. NOTE: player names must be entered exactly to be valid, e.g. C.J. Stroud, DJ Moore, D'Andre Swift must have dots and apostrophes precisely. just be thankful i am not caSE SEnSITivE when it comes to player names")
        
    elif command == "!change":
        txt = message.content
        pick = txt.split()[1:]
        if pick[0]=="help":
            await message.channel.send("!change: you are only allowed to change a pick if the next person hasn't gone yet. enter the format !change [player to change into] e.g. !change Younghoe Koo (don't do that we don't have a kicker i'm looking at you toby) you can change your pick into any not yet drafted player")
        else:
            spick = ""
            for i in pick:
                spick += i + " "
            spick = spick[:-1]
            if message.author.id != getint (draft[picknum-2]):
                await message.channel.send("error: wrong person, too late man, no takesies backsies for you")

            elif spick not in drafted and spick.upper() in players:
                sheet.sheet1.update_cell(prow,pcol, spick)
                drafted[-1]=spick
                await message.channel.send("switch proccessed")
                if picknum%12==0:
                    await message.channel.send("good pick! next pick, round "+ str(row - 4)+" pick " + "12"+", is still" +draft[picknum-1])
                elif col>15 or col<4:
                    await message.channel.send("good pick! next pick, round "+ str(row - 3)+" pick " + str(picknum%12) +", is still" +draft[picknum-1])
                else:
                    await message.channel.send("good pick! next pick, round "+ str(row - 4)+" pick " + str(picknum%12)+", is still"+draft[picknum-1])
            else:
                await message.channel.send("dimwit you couldn't even enter a valid player, ACTION INVALID")

    elif command == "!trade":
        txt = message.content
        pick = txt.split()[1:]
        if pick[0]=="help":
            await message.channel.send("!trade: use this command to log trades of future picks so that the queue can be updated. For trades involving already drafted players, the already drafted portion has to be manually updated on the spreadsheet. However, you still must log the future picks involved with the trade. \nUse the format !trade [pick number] [pick number], numbers seperated by spaces, for however many future picks are invovled in the trade, at least one (e.g. if you trade two players for a player and a pick, use !trade [pick you are recieving]). Trades logged must be limited to two parties, and they will be swapped in the queue accordingly. the order you enter the pick numbers don't matter. trades are un-undoable so be careful, no takesies backsies for realsies. To calculate pick number for round x pick y = 12*(x-1)+y")
        else:
            involved = []
            valid = True
            for i in pick:
                try:
                    involved.append(int(i))
                except:
                    await message.channel.send("invalid formatting, use '!trade help' if you need a refersher")
                    valid = False
            if valid:
                parties = set()
                for i in involved:
                    if i < picknum:
                        await message.channel.send("invalid trade i can't proccess trading previous picks")
                        valid = False
                        break
                    parties.add(getint(draft[i-1]))
                if len(parties)>2 or len(parties)<1:
                    valid = False
                    await message.channel.send("ur kinky but we don't accept threesomes")
                if valid:
                    if len(parties)==1:
                        for i in involved:
                            draft[i-1]=getstr(message.author.id)
                        await message.channel.send("trade proccessed!")
                    else:
                        party = list(parties)
                        for i in involved:
                            if getint(draft[i-1])==party[0]:
                                draft[i-1]=getstr(party[1])
                            else:
                                draft[i-1]= getstr(party[0])
                        await message.channel.send("trade proccessed!")
                






            


        



    



client.run(token)



