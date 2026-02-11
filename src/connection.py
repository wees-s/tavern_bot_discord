import discord
from discord.ext import commands
import rpg_rules, rpg_dice

intents = discord.Intents.all()
bot = commands.Bot("rpg!", intents=intents, help_command=None)

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

bot.run("MTQ3MDkyMzI0NTkxNzMxMTA0OQ.GcajYe.bBGSj-7lEtuPpcUB6v-w-zq_xHF_LIto-MbNUI")