import discord
from discord.ext import commands
import rpg_rules, rpg_dice, rpg_simulator

intents = discord.Intents.all()
bot = commands.Bot("rp!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def help(ctx):
    msg = (rpg_rules.rules())
    await ctx.send(msg)

@bot.command()
async def d2(ctx):
    await ctx.send(f"{ctx.author.mention} **🎲 rolled: {rpg_dice.d2()}**")

@bot.command()
async def d4(ctx):
    await ctx.send(f"{ctx.author.mention} **🎲 rolled: {rpg_dice.d4()}**")

@bot.command()
async def d10(ctx):
    await ctx.send(f"{ctx.author.mention} **🎲 rolled: {rpg_dice.d10()}**")

@bot.command()
async def d20(ctx):
    await ctx.send(f"{ctx.author.mention} **🎲 rolled: {rpg_dice.d20()}**")

@bot.command()
async def d100(ctx):
    await ctx.send(f"{ctx.author.mention} **🎲 rolled: {rpg_dice.d100()}**")

@bot.command()
async def battle(ctx, player1: discord.Member, hp1: int, player2: discord.Member, hp2: int):
    if player1 == player2:
        await ctx.send("❌ Os jogadores devem ser diferentes!")
        return
    
    if player1.bot or player2.bot:
        await ctx.send("❌ Bots não podem participar de batalhas!")
        return
    
    await rpg_simulator.start_battle(ctx, player1, player2, hp1, hp2)

@bot.command()
async def forfeit(ctx):
    await rpg_simulator.forfeit_battle(ctx)

@bot.command()
async def resume(ctx):
    await rpg_simulator.resume_battle(ctx)

@bot.command()
async def log(ctx):
    await rpg_simulator.show_battle_log(ctx)

@bot.command()
async def debug(ctx):
    await rpg_simulator.debug_battles(ctx)

@bot.command()
async def clear(ctx):
    await rpg_simulator.clear_battles(ctx)

bot.run("xxxx")
