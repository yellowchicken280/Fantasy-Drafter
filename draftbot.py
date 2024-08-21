import gspread
from google.oauth2.service_account import Credentials
import discord


token = "get ur discord token number here"
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents = intents)
serverid = "enter ur server id as an int"


SPREADSHEET_ID = 'get ur spreadsheet id'
RANGE_NAME = 'Sheet1!D5:O18'
API_KEY = 'get ur api key'

scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]

creds = Credentials.from_service_account_file("credentials.json", scopes = scopes)
gclient = gspread.authorize(creds)
sheet_id = '1Im_Hyz9AN-IhXKS7LmZjo3YSsiuceBSXm19qk3fw7N4'
sheet = gclient.open_by_key(sheet_id)
tab2 = sheet.get_worksheet(1)
#values_list = sheet.sheet1.row_values(1)
#print(values_list) 

#sheet.sheet1.update_cell(4,5, "this works")

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
tradecount = 0

qbs = tab2.col_values(3)[3:]
rbs = tab2.col_values(8)[3:]
wrs = tab2.col_values(13)[3:]
tes = tab2.col_values(18)[3:]
players = qbs+rbs+wrs+tes
for i in range(len(players)):
    players[i] = players[i].upper()

draftOrder = ["<@ENTER EACH DISCORD ID OF THE DRAFTERS IN DRAFT ORDER IN THIS FORMAT FOR THIS LIST, LENGTH MUST BE 12>"]
rdo = draftOrder[::-1]
draft = []
for i in range(14):
    if i%2==0:
        draft+=draftOrder
    else:
        draft += rdo

"""starter code RUN THIS CODE SEPERATELY TO FILL OUT SPREADSHEET PROPERLY
tempdraft = [[pick] for pick in draft]
sheet.sheet1.update("T3:T170", tempdraft)
"""

@client.event
async def on_ready():
    global row, col, picknum, drafted, draft, prow, pcol, tradecount
    channel = client.get_channel("enter id of draft channel as an int")
    await channel.send("!restart")
    

@client.event
async def on_message(message):
    global row, col, picknum, drafted, draft, prow, pcol, tradecount
    
    id = client.get_guild(serverid)
    if len(message.content)>0: #avoids exceptiosn for pins/images getting sent
        command = message.content.split()[0]    
        if command == "!restart":
            #when using heroku there is a restart every 24 hours which is kinda annoying
            picknum = int((sheet.sheet1.col_values(17)[2]))
            await message.channel.send("beep bop bot relaunch proccess initiated. we are at pick "+str(picknum))
            if picknum % 12 == 0:
                row = 4+int(picknum/12)
            else:
                row = 5+int(picknum/12)
            if row%2==1:
                if picknum%12==0:
                    col = 15
                else:
                    col = (picknum%12)+3
            else:
                if picknum % 12 == 0:
                    col = 4
                else:
                    col = 16 - (picknum%12)
            if picknum>1:
                temp = picknum - 1
                prow = 5+int(temp/12)
                if prow%2==1:
                    if temp%12==0:
                        pcol = 15
                    else:
                        pcol = (temp%12)+3
                else:
                    if temp % 12 == 0:
                        pcol = 4
                    else:
                        pcol = 16 - (temp%12)
            drafted = sheet.sheet1.col_values(18)[2:]
            drafted = [x.upper() for x in drafted]
            draft = sheet.sheet1.col_values(20)[2:]
            if picknum%12==0:
                await message.channel.send("now that that's out of the way, it is still round"+ str(row - 4)+" pick " + "12"+", is " +draft[picknum-1])
            elif col>15 or col<4:
                await message.channel.send("now that that's out of the way, it is still round"+ str(row - 3)+" pick " + str(picknum%12) +", is " +draft[picknum-1])
            else:
                await message.channel.send("now that that's out of the way, it is still round"+ str(row - 4)+" pick " + str(picknum%12)+", is "+draft[picknum-1])
            await message.channel.send("relaunch proccess completed")
        elif command == "!hello":
            bob = "hi " + "<@" + str(message.author.id)+"> \nuse !help to see what i can do"
            await message.channel.send(bob)
        
        elif command == "!ovr":
            try:
                pick = txt.split()[1:]
                if pick[0]=="help":
                    await message.channel.send("just put in !ovr dimwit. u alr cant do basic arithmetic so at least do this proper")
            except:
                await message.channel.send(str(picknum))

        elif command == "!start":

            await message.channel.send("the 2024 draft shall commence! "+draft[0] + " time to !draft you first pick of the 2024 Stonkers Fantasy Draft!")

        elif command == "!help":
            #tell users each function

            await message.channel.send("Wassup I'm the ultimate discord fantasy draft helper, I will help facilitate and tabulate the draft while simultaneously updating the google sheet so yall dont have to : ) here is how my functions work:\n!hello: it's always polite to say hello\n!start: use this command to commence the draft on the agreed upon start date\nto see how my other functions work, enter the function name plus help, e.g. !hello help \nmy other wonderful commands include !ovr, !draft, !whopick !change, and !trade")

        
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
                if spick.upper() not in drafted and spick.upper() in players:
                    sheet.sheet1.update_cell(row,col, spick)
                    picknum+=1
                    sheet.sheet1.update_cell(3,17, picknum)
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
                    drafted.append(spick.upper())
                    sheet.sheet1.update_cell(1+picknum, 18, spick)
                    
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

                elif spick.upper() not in drafted and spick.upper() in players:
                    sheet.sheet1.update_cell(prow,pcol, spick)
                    sheet.sheet1.update_cell(picknum+1, 18, spick)

                    drafted[-1]=spick.upper()
                    await message.channel.send("switch proccessed")
                    if picknum%12==0:
                        await message.channel.send("good pick! next pick, round "+ str(row - 4)+" pick " + "12"+", is still" +draft[picknum-1])
                    elif col>15 or col<4:
                        await message.channel.send("good pick! next pick, round "+ str(row - 3)+" pick " + str(picknum%12) +", is still" +draft[picknum-1])
                    else:
                        await message.channel.send("good pick! next pick, round "+ str(row - 4)+" pick " + str(picknum%12)+", is still"+draft[picknum-1])
                else:
                    await message.channel.send("dimwit you couldn't even enter a valid player, ACTION INVALID")

        elif command == "!whopick":
            txt = message.content
            pick = txt.split()[1:]
            try:
                pick = txt.split()[1:]
                if pick[0]=="help":
                    await message.channel.send("this returns who currently owns the pick, format !whopick [pick number], plz use the overall pick num not round/pick")
            except:
                await message.channel.send(draft[picknum-1])
                

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
                        log = txt[6:]
                        sheet.sheet1.update_cell(3+tradecount,19, log)
                        if len(parties)==1:
                            for i in involved:
                                draft[i-1]=getstr(message.author.id)
                            await message.channel.send("trade proccessed!")
                            tradecount +=1
                        else:
                            party = list(parties)
                            for i in involved:
                                if getint(draft[i-1])==party[0]:
                                    draft[i-1]=getstr(party[1])
                                else:
                                    draft[i-1]= getstr(party[0])
                            await message.channel.send("trade proccessed!")
                            tradecount+=1
                        tempdraft = [[pick] for pick in draft]
                        sheet.sheet1.update("T3:T170", tempdraft)
client.run(token)
