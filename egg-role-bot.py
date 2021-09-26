#!/usr/bin/env python3

import discord
from discord.ext import commands
import pickle
import os
import csv
import sys
import json
import traceback


cwd = os.path.dirname(__file__)
os.chdir(cwd)

# get bot token from file
with open('erb-token.txt') as f:
	botkey = f.readline()
#backup_path = "erb.cfg" #no longer used
guildlist_path = "erb-guilds.csv"

# intents
intents = discord.Intents.default()
intents.members = True
intents.presences = True


"""def get_prefix(client, message):
	prefix = "§"
	try:
		with open('prefixes.json', 'r') as f: 
			prefixes = json.load(f) 
			prefix = prefixes[str(message.guild.id)] 
	except:
		pass
	return commands.when_mentioned_or(prefix)(client, message)
client = commands.Bot(command_prefix=get_prefix, intents=intents)"""
client = commands.Bot(command_prefix="§", intents=intents)

config = {}



### EVENTS

@client.event
async def on_ready():
	# load the list of servers from file
	try:
		global guildlist
		with open(guildlist_path,newline='') as csvfile:
			reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
			# this way of reading the csv file is kinda hacky but it works so :shrug:
			for row in reader:
				guildlist = row;
				break
			length = len(guildlist)
			for i in range(length):
				guildlist[i] = int(guildlist[i])
	except:
		guildlist=[]
		backup_guildlist()
		
	# read the data for all servers into memory.
	global config
	for guildid in guildlist:
		try:
			with open("erb-guilds/"+str(guildid)+".cfg", 'rb') as f:
				config[guildid] = pickle.load(f)
				
			# also set the menu, since this is now required due to the shutdown code
			for menu_name in config[guildid].keys():
				menu = await updatemenu2(guildid,menu_name)
				print(f"Set menu {menu_name} in {guildid}")
				#await role_correction (menu)
			
			# search the roles on the menu and update if necessary
		except Exception as e:
			print(e)
	print("ready")
	print(config)
		

# Events for adding / removing roles in response to reactions on the rolemenu
# I used *raw* events because on_reaction_remove requires extra permissions,
# and also using raw events avoids caching problems (c.f. the discord.py documentation)

@client.event
async def on_raw_reaction_add(payload):
	# get the current server and also its *id*,
	# which is what is used to identify servers in the config file 
	guild = await client.fetch_guild(payload.guild_id)
	guildid = guild.id;
	
	# ignore events triggered by the bot itself
	if payload.user_id == client.user.id:
		return
	
	# find the id of the rolemenu reacted to
	#mn = [cfg["menuid"] for cfg in config[guildid]].index(payload.message_id)
		
	try:
		# retrieve the role indicated by the react
		#roleid = config[guildid][mn]["roles"][payload.emoji.name]
		roleid = [cfg["roles"][payload.emoji.name] for cfg in config[guildid].values() if cfg["menuid"] == payload.message_id][0]
		role = discord.utils.get(guild.roles, id=roleid)
		
		# give the user the role, if it exists
		if role:
			user = await guild.fetch_member (payload.user_id)
			await user.add_roles(role)
			await user.send(content=f"Gave you the role `{role.name}` in server `{guild.name}`.",delete_after=180)
	except:
		pass
		
# removing roles is pretty much the same as adding.
@client.event
async def on_raw_reaction_remove(payload):
	guild = await client.fetch_guild(payload.guild_id)
	guildid = guild.id;
	
	if payload.user_id == client.user.id:
		return
	
	# find the id of the rolemenu reacted to
	#mn = [cfg["menuid"] for cfg in config[guildid]].index(payload.message_id)
	
	try:
		#roleid = config[guildid][mn]["roles"][payload.emoji.name]
		roleid = [cfg["roles"][payload.emoji.name] for cfg in config[guildid].values() if cfg["menuid"] == payload.message_id][0]
		role = discord.utils.get(guild.roles, id=roleid)
		if role:
			user = await guild.fetch_member (payload.user_id)
			await user.remove_roles(role)
			await user.send(content=f"Removed your role `{role.name}` in server `{guild.name}`.",delete_after=180)
	except:
		pass

# event to automatically re-add roles
@client.event
async def on_member_join(member):
	guildid = member.guild.id
	
	"""for cfg in config[guildid].values():
		chan = await client.fetch_channel(cfg["chanid"])
		menu = await chan.fetch_message(cfg["menuid"])
		
		# this isn't really necessary given the below, but it's a failsafe I guess.
		for react in menu.reactions:
			print (react.emoji)
			try:
				role = discord.utils.get(member.guild.roles, id=cfg["roles"][EName(react.emoji)])
			except Exception as e:
				print(e)
				continue
				
			async for user in react.users():
				if user.id == member.id:
					await member.add_roles(role)
					await user.send(content=f"Gave you the role `{role.name}` in server `{member.guild.name}`.",delete_after=180)
					break"""
	
	file_path = f"erb-bindings/{member.id}in{guildid}.csv"
	try:
		with open(file_path,'r',newline='') as csvfile:
			reader = csv.reader(csvfile, delimiter=' ', quotechar='|',quoting=csv.QUOTE_MINIMAL)
			for row in reader:
				rolelist = [int(r) for r in row]
				break
			
		rolesstr = ""
		for roleid in rolelist:
			try:
				role = discord.utils.get(member.guild.roles, id=roleid)
				await member.add_roles(role)
				rolesstr += "`"+role.name+"` "
			except:
				pass
		if rolesstr != "":
			await member.send(content="Restored you role(s) "+rolesstr+"in server `"+member.guild.name+"`.")
	
		print(rolelist)
		
		"""with open("people-to-insult.csv",'rt',newline='') as csvfile:
			reader = csv.reader(csvfile, delimiter=' ', quotechar='|',quoting=csv.QUOTE_MINIMAL)
			for row in reader:
				to_insult = [int(r) for r in row]
				break"""
		to_insult = [736005702371377292]
		
		if member.id in to_insult:
			"""with open("insults.txt",'rt') as f:
				ft = f.read()
			insults = ft.split("\n")
			welcome_text = random.choice(insults)
			print(welcome_text)
			welcome_text.replace("@", member.mention)
			print(welcome_text)"""
			
			# comment this out later
			welcome_text = "Eww "+member.mention+" is back 🤮"
		else:
			"""with open("welcomes.txt",'rt') as f:
				ft = f.read()
			welcomes = ft.split("\n")
			welcome_text = random.choice(welcomes)
			print(welcome_text)
			welcome_text.replace("@", member.mention)
			print(welcome_text)"""
			
			# comment this out later
			welcome_text = "Welcome back "+member.mention+" 😊"
		try:
			spamchan = discord.utils.get(member.guild.channels, name="spam")
			await spamchan.send(welcome_text)
		except:
			print("no spam channel")
		
	except Exception as e:
		print(e)
		traceback.print_exc()
		spamchan = discord.utils.get(member.guild.channels, name="spam")
		await spamchan.send(member.mention+" https://media.tenor.com/images/29fccd813a4d75d8d1a0684165ca6601/tenor.gif")
		
@client.event
async def on_member_remove(member):
	guildid=member.guild.id
	file_path = f"erb-bindings/{member.id}in{guildid}.csv"
	rolelist = [rol.id for rol in member.roles]
	print(rolelist)
	with open(file_path,'w',newline='') as csvfile:
		writer = csv.writer(csvfile, delimiter=' ', quotechar='|',quoting=csv.QUOTE_MINIMAL)
		writer.writerow (rolelist)

### HELPER FUNCTIONS

# helper functions to update the rolemenu
# this is split in two because of how I originally wrote the code.
async def updatemenu(guildid, mn, msg):
	guild = discord.utils.get(client.guilds, id=guildid)
	Text= config[guildid][mn]["head"];
	
	for em, rol in config[guildid][mn]["roles"].items():
		#role = discord.utils.get(guild.roles, id=rol)
		Text += f"\n{config[guildid][mn]['emotes'][em]} - <@&{rol}>\n"
		
	Text+=config[guildid][mn]["foot"];
	await msg.edit(content=Text)
	
async def updatemenu2(guildid,menu_name):
	chan = await client.fetch_channel(config[guildid][menu_name]["chanid"])
	msg = await chan.fetch_message(config[guildid][menu_name]["menuid"])
	await updatemenu(guildid,menu_name, msg)
	return msg
	
# function to "correct" the role menu which is called on startup
async def role_correction(menu):
	print("correcting roles")
	guild = menu.channel.guild
	for react in menu.reactions:
		print (react.emoji)
		try:
			role = discord.utils.get(guild.roles, id=config[guild.id]["roles"][EName(react.emoji)])
		except Exception as e:
			print(e)
			continue
			
		async for user in react.users():
			if user.id == client.user.id:
				continue
			member = await guild.fetch_member(user.id)
			if role in member.roles:
				continue
			else:
				await member.add_roles(role)
				await user.send(content="Gave you the role `"+role.name+"` in server `"+guild.name+"`.",delete_after=180)
	
	# code to REMOVE roles if the react is not there
	# probably doesn't even work because of the way emotes are stored,
	"""for roleid in config[guild.id]["roles"]:
		try:
			ems = [em for em, rol in config[guildid]["roles"].items() if (rol == role.id) or (print(em,rol))]
			ename = ems[0]
			reacts = [r for r in menu.reactions if EName(r.emoji) == ename]
			react = reacts[0]
			role = discord.utils.get(guild.roles, id=roleid)
		except Exception as e:
			print(e)
			continue
			
		for member in role.members:
			if member in react.members:
				await member.remove_roles(role)
				await member.send(content="Removed your role `"+role.name+"` in server `"+guild.name+"`.",delete_after=10)"""
				

# function to notify that the bot is down
async def downtime():
	for guildid in guildlist:
		try:
			# fetch the relevant objects
			chan = await client.fetch_channel(config[guildid]["chanid"])
			msg = await chan.fetch_message(config[guildid]["menuid"])
			await msg.edit(content="_Sorry, Egg Roles Bot is currently down._")
			print("Registered downtime in "+guildid)
		except:
			pass

# helper function to retrieve the emoji.name value from the text value of emojis that are passed as arguments
# this means custom server emotes work in addition to standard emotes.
# I haven't tested if flags work though.
def EName (emoji):
	try:
		if emoji.name:
			return emoji.name
	except:
		em = emoji.split(":")
		if len(em) == 3:
			return em[1]
		else:
			return emoji
		
		
# helper function that saves data to file
# was originally a command.
# in this version, the function only backs up data for the relevant server.
async def backup(ctx):
	guildid = ctx.guild.id;
	with open("erb-guilds/"+str(guildid)+".cfg", 'wb') as f:
		pickle.dump(config[guildid], f)

# helper function that saves the list of server ids to file
def backup_guildlist():
	with open(guildlist_path,'w',newline='') as csvfile:
		writer = csv.writer(csvfile, delimiter=' ', quotechar='|',quoting=csv.QUOTE_MINIMAL)
		writer.writerow (guildlist)

# helper function that takes a rolename or mention and gives a Role object.
def interpret_role (ctx, rolename):
	role = discord.utils.get(ctx.guild.roles, mention=rolename)
	if role:
		return role
	else:
		return discord.utils.get(ctx.guild.roles, name=rolename)

# helper function that takes a member's name or mention and gives the corresponding Member object
def interpret_member (ctx, membername):
	membername = membername.replace("!","")
	mem = discord.utils.get(ctx.guild.members, mention=membername)
	if mem:
		return mem
	else:
		return discord.utils.get(ctx.guild.members, name=membername)
	

### COMMANDS

# command to add roles to the role menu
# note that this does NOT create roles
@client.command(brief="Add a role to a named rolemenu, creating it if necessary.",description="Add role <rolename> to the rolemenu with name <menu_name>, with corresponding react <emoji>. The rolename *may* contain spaces and does *not* need to be surrounded by quotation marks.")
async def addrole(ctx, menu_name, emoji, *, rolename):
	if ctx.message.author.guild_permissions.administrator or ctx.message.author.id == 120125811259998208:
		# retrieve current server id and the role named by the rolename
		guildid = ctx.guild.id;
		
		chan = await client.fetch_channel(config[guildid][menu_name]["chanid"])
		msg = await chan.fetch_message(config[guildid][menu_name]["menuid"])
		
		if len(msg.reactions) >= 20:
			await ctx.send(f"Error: the rolemenu `{menu_name}` already has 20 reactions!")
			return
		
		# check if the role already exists, first by mention then by name, and if not then create it.
		role = interpret_role(ctx, rolename)
		if role:
			pass
		else:
			role = await ctx.guild.create_role(name=rolename)
			await ctx.send (f"created role {role.mention}")
		
		# throw error if the bot can't access the role
		# (note: ctx.me is a Member object)
		if ctx.me.top_role <= role:
			await ctx.send (f"Error: role {role.mention} cannot be accessed by the bot!")
			return
		
		# add this role option to the config file
		en = EName (emoji)
		
		# add the role to the roles dict; and the raw form of the emote to the emote dict
		config[guildid][menu_name]["roles"][en] = role.id
		config[guildid][menu_name]["emotes"][en] = emoji
		
		# update the rolemenu including adding the relevant reaction
		await updatemenu(guildid,menu_name,msg)
		await msg.add_reaction(emoji=emoji)
		
		# send a vanishing msg in the roles channel for the sake of pinging.
		await chan.send(content=f"Added role {role.mention} to rolemenu {menu_name}.",delete_after=1)
		
		# respond to the command and save the rolemenu data to file.
		await backup(ctx)
		await ctx.send (f"added {role.mention} to rolemenu {menu_name} with emoji {emoji}")
	else:
		await ctx.send ("Error: only administrators may use this command!")

# command to remove roles from the role menu
# this does not delete the role from the server, however.
@client.command(brief="Remove the role associated with a given emote from a named rolemenu, **without** deleting it.", description="Remove from the rolemenu with name <menu_name> the role associated to the react <emoji>.")
async def rmrole_by_emote(ctx, menu_name, emoji):
	if ctx.message.author.guild_permissions.administrator or ctx.message.author.id == 120125811259998208:
		guildid = ctx.guild.id; # retrieve server id
		try:
			# get the role indicated by the emoji 
			en = EName (emoji)
			role = discord.utils.get(ctx.guild.roles, id=config[guildid][menu_name]["roles"][en])
			
			# remove the role from the rolemenu data
			config[guildid][menu_name]["roles"].pop(en)
			
			# update the rolemenu, including clearing reactions (as perms allow)
			msg = await updatemenu2(guildid,menu_name)
			try:
				await msg.clear_reaction(emoji)
			except:
				await msg.remove_reaction(emoji,client.user)
			
			# respond to the command and save the rolemenu data to file.
			await ctx.send (f"Removed {role.mention} from rolemenu {menu_name}.")
			await backup(ctx)
				
		except:
			await ctx.send (f"Error: no role is associated to {emoji} in rolemenu {menu_name}!")
	else:
		await ctx.send ("Error: only administrators may use this command!")

"""# same but referencing by name or mention rather than emote
@client.command(brief="Remove a specified role from rolemenu, **without** deleting it.", description="Remove from the rolemenu the role <rolename>.")
async def rmrole_by_name(ctx, *, rolename):
	if ctx.message.author.guild_permissions.administrator:
		guildid = ctx.guild.id; # retrieve server id
		
		# get the role, first by mention then by name, throwing an error if it does not exist
		role = discord.utils.get(ctx.guild.roles, mention=rolename)
		if role:
			pass
		else:
			role = discord.utils.get(ctx.guild.roles, name=rolename)
			if role:
				pass
			else:
				await ctx.send ("Error: no role `"+rolename+"` exists!")
			
		# find the emote associated to this role
		reacts = [em for em, rol in config[guildid]["roles"].items() if (rol == role.id) or (print(em,rol))]
		emoji = reacts[0]
		
		# remove the role from the menu
		config[guildid]["roles"].pop(emoji)
		config[guildid]["emotes"].pop(emoji)
		
		# update the rolemenu, including clearing reactions (as perms allow)
		msg = await updatemenu2(guildid)
		try:
			await msg.clear_reaction(emoji)
		except:
			await msg.remove_reaction(emoji,client.user)
		
		# respond to the command and save the rolemenu data to file.
		await ctx.send ("Removed " +role.mention+" from rolemenu.")
		await backup(ctx)
	else:
		await ctx.send ("Error: only administrators may use this command!")"""
		

# commands which edit the stored value for the header and footer of the rolemenu for the sever

@client.command(brief="Set rolemenu settings.",description="Set the header or footer of a rolemenu. Syntax is §set <menu_name> <head/foot> to <text>.")
async def set(ctx, menu_name, option, to, *, text):
	if not (ctx.message.author.guild_permissions.administrator or ctx.message.author.id == 120125811259998208):
		await ctx.send ("Error: only administrators may use this command!")
		return
	if to!= "to" or not (option in ["head","foot"]):
		await ctx.send ("Syntax Error: Syntax is `set <menu name> <head/foot> to <text>`")
		return
	guildid = ctx.guild.id;
	config[guildid][menu_name][option] = text+"\n";
	await backup(ctx)
	await updatemenu2(guildid,menu_name)
	await ctx.send (f"Changed rolemenu {menu_name}'s {option} to:\n{text}")

# command to create the rolemenu message and also set up other stuff for the bot.
@client.command(brief="Create a rolemenu.",description="Creates a rolemenu with <menu_name> wherever the command is called. Note that <menu_name> may not contain spaces, or else must be surrounded by \"\".")
async def initialise(ctx, menu_name):
	if ctx.message.author.guild_permissions.administrator or ctx.message.author.id == 120125811259998208:
		guildid = ctx.guild.id;
		
		
		if not (guildid in config.keys()):
			config[guildid] = {}
			guildlist.append(guildid)
			backup_guildlist()
		
		# create the rolemenu
		msg = await ctx.send(f"Placeholder menu `{menu_name}` - add roles to update")
		
		# initialise the dictionary storing all the stuff required for the bot to function on the server,
		# then save the config dict to file.
		
		config[guildid][menu_name] = {"roles":{},
									"emotes":{},
									"menuid":msg.id,
									"chanid":msg.channel.id,
									"head":"React the following to get the respective role:\n",
									"foot":""}
		await backup(ctx)
	else: 
		await ctx.send ("Error: only administrators may use this command!")

	
# command to reboot the bot, for pushing updates.
@client.command(brief="Restart the bot.", description="Restarts the bot, for updating purposes.")
async def reboot(ctx):
	if ctx.message.author.id == 120125811259998208:
		await ctx.send ("Rebooting...")
		await downtime()
		await client.close()
		file_path = os.path.abspath(__file__)
		os.system("nohup python3 -u \""+file_path+"\" &")
		sys.exit()

# command to shutdown the bot, for running in terminal.
@client.command(brief="Shutdown the bot.", description="Shuts down the bot, for debugging purposes.")
async def shutdown(ctx):
	if ctx.message.author.id == 120125811259998208:
		await ctx.send ("Shutting down...")
		await downtime()
		await client.close()
		sys.exit()
		
@client.command()
async def convert(ctx):
	if ctx.message.author.id == 120125811259998208:
		guildid = ctx.guild.id;
		wrapper = {"default":config[guildid]}
		config[guildid] = wrapper
		await ctx.send("Conversion successful!")
		await backup(ctx)
		await ctx.send("Conversion saved!")
	else:
		await ctx.send("Error: you do not have permission to use this command!")

# command that checks role colours
@client.command(brief="Check a role's colour.")
async def whatcolouris(ctx, *, rolename):
	try:
		role = discord.utils.get(ctx.guild.roles, name=rolename)
		await ctx.send (content="Role "+role.mention+" has colour #"+hex(role.colour.value)[2:]+".",allowed_mentions=discord.AllowedMentions.none())
	except:
		await ctx.send ("Error: No role `"+rolename+"` found!")

# command that changes ones special role colour
@client.command(brief="Change the colour of your personal role.", description="Sets the colour of your personal role to the colour given by <hexcode> (both with and without # work). Your \"personal role\" is defined by 1) having a colour; 2) having only one member (you); 3) not being a colour-bot role and 4) being the highest such role. If you are Andrea this command won't work since your personal role is also an admin role.)")
async def personal_colour(ctx, hexcode):

	## ARTEM'S CODE TO CONVERT hexcode INTO COLOUR
	# try to convert hexcode
	try:
		if hexcode[0] == '#':
			hexcode = hexcode[1:]#
		c_int = int(hexcode, 16)
		
		# range check
		if not (c_int >= 0 and c_int <= 16777215):
			print("failed rangecheck")
			return False
			
		# set colour
		c = discord.Colour(int(hexcode, 16))
		txt = str(c) # hex code (std formatting)
	except Exception as e:
		print(e)
		return False
	
	# find the user's "special role", and change its colour
	try:
		member = ctx.author;
		highest_special_role = None
		length = len(member.roles)-1
		# member roles are listed in order of hierarchy, so start at the end (=highest role) for maximum efficiency.
		for i in range(length,-1,-1):
			role = member.roles[i]
			# role must have a colour and only one member to qualify as a "special role",
			# also not begin with # to not mess with colour bot
			if role.name[0] != "#" and role.colour.value != 0 and len(role.members) == 1 and (highest_special_role == None or role > highest_special_role):
				highest_special_role = role
				break
		
		if (highest_special_role == None): # if no special role found
			await ctx.send("Error: You have no personal role!")
			return False
		elif ctx.me.top_role <= highest_special_role: # if special role can't be accessed by the bot (i.e. Andrea's role)
			await ctx.send ("Error: Your personal role " + highest_special_role.name + " cannot be accessed by the bot!")
			return
		else: # if special role is found and can be accessed by the bot, change its colour
			await highest_special_role.edit(colour=c)
			await ctx.send ("Set the colour of role " + highest_special_role.name + " to #"+hexcode+".")
	except:
		await ctx.send("Something went wrong.")
		return False

def whohas_helper(ctx, roles):
	members = ctx.guild.members
	rolelist = roles.split("&")
	for rolename in rolelist:
		rolename = rolename.strip()
		if rolename[0] == "!":
			rolename = rolename[1:].lstrip()
			if rolename.lower() in ["online","offline","idle","dnd"]:
				members = [value for value in members if str(value.status) != rolename.lower()]
			else:
				role = interpret_role(ctx, rolename)
				if not role:
					raise Exception("Error: no role with name `"+rolename+"` found! Note the status names are `online`, `offline`, `idle` and `dnd`.")
				members = [value for value in members if not (value in role.members)]
			
		else:
			if rolename.lower() in ["online","offline","idle","dnd"]:
				members = [value for value in members if str(value.status) == rolename.lower()]
			else:
				role = interpret_role(ctx, rolename)
				if not role:
					raise Exception("Error: no role with name `"+rolename+"` found! Note the status names are `online`, `offline`, `idle` and `dnd`.")
					#return False
				members = [value for value in members if value in role.members]
	return members
	

# command to list members of a role
@client.command(brief="List members who have _all_ of a specified combination of roles and (optionally) status, separated by &",description="Returns a list of members with ALL of the specfified roles and status. Put `!` at the start of a role or status to search for members WITHOUT that role/status instead. Roles may be given by name or my mention. The status names are `online`, `offline`, `idle`, and `dnd`.")
async def whohas(ctx, *, roles):
	try:
		members = whohas_helper(ctx, roles)
	except Exception as e:
		await ctx.send(e)
		return
	
	if not members:
		await ctx.send("No members were found with roles/status "+roles+".")
		return
	list = "Members with the roles/status "+roles+":\n```"
	i = 1
	for mem in members:
		list += str(i)+". " + mem.name + "\n"
		i+=1
	list+="```"
	await ctx.send(list)

# command to ping a certain role combo
@client.command(brief="Pings members with a certain intersection of roles, using the same syntax as the `whohas` command.",description="""Pings the set of members members with ALL of the specfified roles and status. Put `!` at the start of a role or status to search for members WITHOUT that role/status instead. Roles may be given by name or my mention. The status names are `online`, `offline`, `idle`, and `dnd`.
Ping people with a particular message using WITH then the message after the list of roles/statuses.""")
async def ping(ctx, *, roles_WITH_message):
	split_char = " WITH "
	roles_WITH_message = roles_WITH_message.split(split_char)
	roles = roles_WITH_message[0]
	try:
		members = whohas_helper(ctx, roles)
	except Exception as e:
		await ctx.send(e)
		return
	
	temp_role = await ctx.guild.create_role(name=roles, mentionable=True)
	for mem in members:
		await mem.add_roles(temp_role)
	
	if len(roles_WITH_message) == 1:
		msg = ""
	else:
		msg = split_char.join(roles_WITH_message[1:])
		
	await ctx.send(temp_role.mention + " ("+roles+") " + msg)
	
	await temp_role.delete()
	
	

client.run(botkey)
"""try:
	client.loop.run_until_complete(client.run(botkey))
finally:
	await downtime()
	client.loop.close()"""