import discord
from discord.ext import commands
from discord.ui import View
import asyncio
import rpg_dice
MAX_LOGS = 10

class BattleState:
    def __init__(self, player1, player2, hp1, hp2, channel_id):
        self.player1 = player1
        self.player2 = player2
        self.hp1 = hp1
        self.hp2 = hp2
        self.max_hp1 = hp1
        self.max_hp2 = hp2
        self.current_turn = player1.id
        self.channel_id = channel_id
        self.lock = asyncio.Lock()
        self.active = True
        self.message = None
        self.auto_battle_task = None
        self.battle_log = []
        
    def get_current_player(self):
        return self.player1 if self.current_turn == self.player1.id else self.player2
    
    def get_opponent(self, player):
        return self.player2 if player.id == self.player1.id else self.player1
    
    def get_hp(self, player):
        return self.hp1 if player.id == self.player1.id else self.hp2
    
    def set_hp(self, player, hp):
        if player.id == self.player1.id:
            self.hp1 = max(0, min(hp, self.max_hp1))
        else:
            self.hp2 = max(0, min(hp, self.max_hp2))
    
    def switch_turn(self):
        self.current_turn = self.player2.id if self.current_turn == self.player1.id else self.player1.id

class BattleView(View):
    def __init__(self, battle_state, bot):
        super().__init__(timeout=None)
        self.battle_state = battle_state
        self.bot = bot
        battle_state.view = self
        
    def calculate_attack_damage(self, roll):
        if roll == 0:
            return 1, "ataque totalmente ineficiente (dano a si mesmo)"
        elif 1 <= roll <= 4:
            return roll, "ataque ineficiente"
        elif 5 <= roll <= 10:
            return roll, "ataque fraco"
        elif 11 <= roll <= 15:
            return roll, "ataque eficiente"
        elif 16 <= roll <= 19:
            return roll, "ataque muito eficiente"
        elif roll == 20:
            return 25, "ataque crítico"
        elif roll == 21:
            return 20, "ataque crítico com recuperação"
    
    def calculate_defense(self, roll):
        if 0 <= roll <= 4:
            return 0, "defesa falhou"
        elif 5 <= roll <= 17:
            if roll == 5:
                return 1, "defesa quase inútil"
            elif roll < 10 and roll > 5:
                return roll - 2, "defesa parcial"
            elif roll >= 10:
                return 10, "defesa quase perfeita"
        elif roll == 18:
            return 100, "esquiva crítica"
        elif roll == 19:
            return 100, "esquiva perfeita"
        elif roll == 20:
            return -5, "contra-ataque (parry)"
        elif roll == 21:
            return 5, "esquiva com maestria"

async def execute_turn(battle_state):
    while True:
        async with battle_state.lock:
            if not battle_state.active:
                return
                
            attacker = battle_state.get_current_player()
            defender = battle_state.get_opponent(attacker)
            
            attack_roll = rpg_dice.d22()
            damage, attack_description = BattleView.calculate_attack_damage(None, attack_roll)
            
            embed = discord.Embed(
                title="⚔️ Turno de Batalha!",
                color=discord.Color.red()
            )
            embed.add_field(name="Atacante", value=attacker.mention, inline=True)
            embed.add_field(name="Defensor", value=defender.mention, inline=True)
            embed.add_field(name="Rolagem de Ataque", value=f"🎲 {attack_roll}", inline=True)
            embed.add_field(name="Resultado do Ataque", value=attack_description, inline=True)
            
            if attack_roll == 0:
                battle_state.set_hp(attacker, battle_state.get_hp(attacker) - damage)
                embed.add_field(name="Dano", value=f"{attacker.mention} recebeu {damage} de dano próprio!", inline=False)
                log_entry = f"⚔️ {attacker.display_name} atacou {defender.display_name} (🎲{attack_roll} → {attack_description}) | 💥 {damage} dano próprio"
            else:
                defense_roll = rpg_dice.d22()
                defense_reduction, defense_desc = BattleView.calculate_defense(None, defense_roll)
                
                log_entry = f"⚔️ {attacker.display_name} atacou {defender.display_name} (🎲{attack_roll} → {attack_description}) | 🛡️ {defender.display_name} defendeu (🎲{defense_roll} → {defense_desc})"
                
                embed.add_field(name="Rolagem de Defesa", value=f"🛡️ {defense_roll}", inline=True)
                embed.add_field(name="Resultado da Defesa", value=defense_desc, inline=True)
                
                if defense_reduction == 100:
                    final_damage = 0
                    embed.add_field(name="Defesa", value=f"🛡️ {defense_desc}! Dano totalmente evitado!", inline=False)
                    log_entry += " | ✅ Dano evitado"
                elif defense_reduction < 0:
                    final_damage = damage + abs(defense_reduction)
                    embed.add_field(name="Defesa", value=f"⚔️ {defense_desc}! Dano refletido: {abs(defense_reduction)}", inline=False)
                    log_entry += f" | ⚔️ {abs(defense_reduction)} dano refletido"
                else:
                    final_damage = max(0, damage - defense_reduction)
                    embed.add_field(name="Defesa", value=f"🛡️ {defense_desc}! Redução: {defense_reduction}", inline=False)
                    log_entry += f" | 🛡️ {defense_reduction} dano reduzido"
                
                if final_damage > 0:
                    battle_state.set_hp(defender, battle_state.get_hp(defender) - final_damage)
                    embed.add_field(name="Dano causado", value=str(final_damage), inline=False)
                    log_entry += f" | 💔 {final_damage} dano"
                
                if attack_roll == 21:
                    battle_state.set_hp(attacker, battle_state.get_hp(attacker) + 5)
                    embed.add_field(name="Recuperação", value="Atacante recuperou 5 HP!", inline=False)
                    log_entry += " | 💚 +5 HP"
                
                if defense_roll == 21:
                    battle_state.set_hp(defender, battle_state.get_hp(defender) + 5)
                    embed.add_field(name="Recuperação", value="Defensor recuperou 5 HP!", inline=False)
                    log_entry += " | 💚 +5 HP"
            
            hp_attacker = battle_state.get_hp(attacker)
            hp_defender = battle_state.get_hp(defender)
            
            embed.add_field(
                name="HP Atual", 
                value=f"{attacker.mention}: {hp_attacker}/{battle_state.max_hp1 if attacker.id == battle_state.player1.id else battle_state.max_hp2}\n"
                      f"{defender.mention}: {hp_defender}/{battle_state.max_hp2 if defender.id == battle_state.player2.id else battle_state.max_hp1}",
                inline=False
            )
            
            await battle_state.message.edit(embed=embed)
            battle_state.battle_log.append(log_entry)
                
            # Verificar se algum jogador chegou a HP 0
            if hp_attacker <= 0 or hp_defender <= 0:
                if hp_attacker <= 0 and hp_defender <= 0:
                    # Empate - atacante perde por ter atacado por último
                    await end_battle(defender, attacker, battle_state)
                elif hp_attacker <= 0:
                    await end_battle(defender, attacker, battle_state)
                else:
                    await end_battle(attacker, defender, battle_state)
                return
            else:
                battle_state.switch_turn()
        
        await asyncio.sleep(3)

async def end_battle(winner, loser, battle_state):
    battle_state.active = False
    
    if battle_state.auto_battle_task:
        battle_state.auto_battle_task.cancel()
    
    embed = discord.Embed(
        title="🏆 Batalha Encerrada!",
        color=discord.Color.gold()
    )
    
    embed.description = f"{loser.mention} foi derrotado!"
    embed.add_field(name="🥇 Vencedor", value=winner.mention, inline=True)
    embed.add_field(name="HP Restante", value=str(battle_state.get_hp(winner)), inline=True)
    
    await battle_state.message.edit(embed=embed, view=None)
    
    # Remover batalha do active_battles
    battle_id = f"{battle_state.channel_id}"
    if battle_id in active_battles:
        del active_battles[battle_id]

active_battles = {}

async def start_battle(ctx, player1, player2, hp1, hp2):
    channel_id = str(ctx.channel.id)
    
    if channel_id in active_battles:
        await ctx.send("❌ Já existe uma batalha ativa neste canal!")
        return None
    
    if not (1 <= hp1 <= 100) or not (1 <= hp2 <= 100):
        await ctx.send("❌ HP deve estar entre 1 e 100!")
        return None
    
    battle_state = BattleState(player1, player2, hp1, hp2, channel_id)
    
    # Adicionar ao active_battles apenas após todas as validações
    active_battles[channel_id] = battle_state
    
    view = BattleView(battle_state, ctx.bot)
    
    embed = discord.Embed(
        title="⚔️ Batalha Iniciada!",
        description="Batalha automática iniciando em 3 segundos...",
        color=discord.Color.gold()
    )
    
    embed.add_field(name=f"{player1.display_name}", value=f"HP: {hp1}", inline=True)
    embed.add_field(name=f"{player2.display_name}", value=f"HP: {hp2}", inline=True)
    embed.add_field(name="Regras", value="Batalha automática com turnos de 3 segundos", inline=False)
    
    message = await ctx.send(embed=embed)
    battle_state.message = message
    
    await asyncio.sleep(3)
    
    if battle_state.active:
        try:
            battle_state.auto_battle_task = asyncio.create_task(execute_turn(battle_state))
        except Exception as e:
            # Remover do active_battles se houver erro
            if channel_id in active_battles:
                del active_battles[channel_id]
            await ctx.send(f"❌ Erro ao iniciar batalha: {str(e)}")
            return None
    
    return battle_state

async def resume_battle(ctx):
    channel_id = str(ctx.channel.id)
    
    if channel_id not in active_battles:
        await ctx.send("❌ Não há batalha ativa para retomar neste canal!")
        return
    
    battle_state = active_battles[channel_id]
    
    if not battle_state.active:
        await ctx.send("❌ Esta batalha já foi encerrada!")
        return
    
    view = BattleView(battle_state, ctx.bot)
    
    embed = discord.Embed(
        title="⚔️ Batalha Retomada!",
        description="Batalha automática continuando em 3 segundos...",
        color=discord.Color.gold()
    )
    
    embed.add_field(name=f"{battle_state.player1.display_name}", value=f"HP: {battle_state.hp1}/{battle_state.max_hp1}", inline=True)
    embed.add_field(name=f"{battle_state.player2.display_name}", value=f"HP: {battle_state.hp2}/{battle_state.max_hp2}", inline=True)
    
    message = await ctx.send(embed=embed)
    battle_state.message = message
    
    await asyncio.sleep(3)
    
    if battle_state.active:
        battle_state.auto_battle_task = asyncio.create_task(execute_turn(battle_state))

async def forfeit_battle(ctx):
    channel_id = str(ctx.channel.id)
    
    if channel_id not in active_battles:
        await ctx.send("❌ Não há batalha ativa neste canal!")
        return
    
    battle_state = active_battles[channel_id]
    
    if not battle_state.active:
        await ctx.send("❌ Esta batalha já foi encerrada!")
        return
    
    if ctx.author.id not in [battle_state.player1.id, battle_state.player2.id]:
        await ctx.send("❌ Você não está participando desta batalha!")
        return
    
    loser = ctx.author
    winner = battle_state.get_opponent(loser)
    
    battle_state.active = False
    
    if battle_state.auto_battle_task:
        battle_state.auto_battle_task.cancel()
    
    embed = discord.Embed(
        title="🏆 Batalha Encerrada!",
        description=f"{loser.mention} desistiu da batalha!",
        color=discord.Color.gold()
    )
    
    embed.add_field(name="🥇 Vencedor", value=winner.mention, inline=True)
    embed.add_field(name="HP Restante", value=str(battle_state.get_hp(winner)), inline=True)
    
    await battle_state.message.edit(embed=embed, view=None)
    
    del active_battles[channel_id]

async def show_battle_log(ctx):
    channel_id = str(ctx.channel.id)
    
    if channel_id not in active_battles:
        await ctx.send("❌ Não há batalha ativa neste canal!")
        return
    
    battle_state = active_battles[channel_id]
    
    if not battle_state.battle_log:
        await ctx.send("📜 Nenhuma ação registrada ainda!")
        return
    
    embed = discord.Embed(
        title="📜 Última 10 ações da batalha",
        description=f"Total de ações: {len(battle_state.battle_log)}",
        color=discord.Color.blue()
    )
    
    for i, log_entry in enumerate(battle_state.battle_log[-MAX_LOGS:], 
                              len(battle_state.battle_log) - MAX_LOGS + 1):
        embed.add_field(
            name=f"Turno:",
            value=log_entry[:1024],
            inline=False
    )
    
    await ctx.send(embed=embed)

async def debug_battles(ctx):
    embed = discord.Embed(
        title="🔍 Debug - Active Battles",
        color=discord.Color.orange()
    )
    
    if not active_battles:
        embed.description = "Nenhuma batalha ativa encontrada."
        await ctx.send(embed=embed)
        return
    
    embed.description = f"Total de batalhas ativas: {len(active_battles)}"
    
    for channel_id, battle_state in active_battles.items():
        status = "✅ Ativa" if battle_state.active else "❌ Inativa"
        embed.add_field(
            name=f"Canal {channel_id}",
            value=f"{battle_state.player1.display_name} vs {battle_state.player2.display_name}\n"
                  f"Status: {status}\n"
                  f"HP: {battle_state.hp1}/{battle_state.max_hp1} - {battle_state.hp2}/{battle_state.max_hp2}\n"
                  f"Turno atual: {battle_state.get_current_player().display_name}",
            inline=False
        )
    
    await ctx.send(embed=embed)

async def clear_battles(ctx):
    channel_id = str(ctx.channel.id)
    
    if channel_id in active_battles:
        battle_state = active_battles[channel_id]
        battle_state.active = False
        
        if battle_state.auto_battle_task:
            battle_state.auto_battle_task.cancel()
        
        del active_battles[channel_id]
        await ctx.send("✅ Batalha do canal atual foi limpa!")
    else:
        await ctx.send("❌ Nenhuma batalha ativa neste canal para limpar.")
