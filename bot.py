import discord
from discord.ext import commands
import sqlite3

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    conn = sqlite3.connect('banned_users.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM banned_users WHERE user_id = ?", (str(member.id),))
    result = cursor.fetchone()

    if result:
        await member.ban(reason=f"Auto-ban: {result[1]}")
        print(f"{member} was auto-banned.")

    conn.close()

@bot.command()
@commands.has_permissions(administrator=True)
async def autoban(ctx, user_id: str, *, reason="No reason given"):
    conn = sqlite3.connect('banned_users.db')
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS banned_users (
            user_id TEXT PRIMARY KEY,
            reason TEXT,
            banned_by TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("INSERT OR REPLACE INTO banned_users (user_id, reason, banned_by) VALUES (?, ?, ?)",
                   (user_id, reason, str(ctx.author)))
    conn.commit()
    conn.close()

    guild = ctx.guild
    member = guild.get_member(int(user_id))
    if member:
        await member.ban(reason=f"Auto-ban: {reason}")
        await ctx.send(f"✅ User with ID `{user_id}` has been added to the auto-ban list and banned immediately.")
    else:
        await ctx.send(f"✅ User with ID `{user_id}` has been added to the auto-ban list.")

@bot.command()
@commands.has_permissions(administrator=True)
async def autounban(ctx, user_id: str):
    conn = sqlite3.connect('banned_users.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM banned_users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if result:
       
        cursor.execute("DELETE FROM banned_users WHERE user_id = ?", (user_id,))
        conn.commit()
        await ctx.send(f"✅ User with ID `{user_id}` has been removed from the auto-ban list.")
    else:
        await ctx.send(f"⚠️ User with ID `{user_id}` was not found in the auto-ban list.")

    conn.close()

    
    try:
        bans = await ctx.guild.bans()
        for ban_entry in bans:
            if ban_entry.user.id == int(user_id):
                await ctx.guild.unban(ban_entry.user, reason="Manual unban via !autounban")
                await ctx.send(f"✅ User `{user_id}` has also been unbanned from the server.")
                return
        await ctx.send(f"ℹ️ User `{user_id}` is not currently banned in this server.")
    except Exception as e:
        await ctx.send(f"⚠️ Error while unbanning: {e}")

@bot.command()
@commands.has_permissions(administrator=True)
async def listbans(ctx):
    conn = sqlite3.connect('banned_users.db')
    cursor = conn.cursor()

  
    cursor.execute("SELECT user_id, reason, banned_by, timestamp FROM banned_users")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await ctx.send("📋 The auto-ban list is currently empty.")
        return

   
    message = "**Auto-ban List:**\n"
    for user_id, reason, banned_by, timestamp in rows:
        message += f"- `{user_id}` | Reason: {reason} | Added by: {banned_by} | At: {timestamp}\n"

    
    if len(message) > 2000:
        chunks = [message[i:i+1990] for i in range(0, len(message), 1990)]
        for chunk in chunks:
            await ctx.send(chunk)
    else:
        await ctx.send(message)

@bot.command()
@commands.has_permissions(administrator=True)
async def viewautobanlist(ctx):
    conn = sqlite3.connect('banned_users.db')
    cursor = conn.cursor()

   
    cursor.execute("SELECT user_id FROM banned_users")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await ctx.send("📋 The auto-ban ID list is currently empty.")
        return

    ids = ", ".join(f"`{row[0]}`" for row in rows)

    
    if len(ids) > 2000:
        chunks = [ids[i:i+1990] for i in range(0, len(ids), 1990)]
        for chunk in chunks:
            await ctx.send(chunk)
    else:
        await ctx.send(f"**Auto-ban User IDs:**\n{ids}")

# Put your bot token below to run it
bot.run("YOUR BOT TOKEN")
