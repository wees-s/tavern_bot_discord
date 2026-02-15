# 🎲 Bot de RPG para Discord

Instalação do bot para uso: https://discord.com/oauth2/authorize?client_id=1470923245917311049
Bot de Discord com sistema de dados e batalhas automáticas para RPG, desenvolvido em Python usando discord.py.

## 📋 Índice

- [Características](#-características)
- [Requisitos](#-requisitos)
- [Instalação](#-instalação)
- [Configuração](#️-configuração)
- [Comandos](#-comandos)
- [Sistema de Batalha](#️-sistema-de-batalha)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Como Funciona](#-como-funciona)

## ✨ Características

- 🎲 Sistema completo de rolagem de dados (d2, d4, d6, d10, d20, d100)
- ⚔️ Sistema de batalhas automáticas 1x1
- 🤖 Batalhas completamente automatizadas com turnos de 3 segundos
- 📊 Sistema de HP e dano balanceado
- 🛡️ Mecânica de ataque e defesa com rolagens críticas
- 📜 Sistema de logs de batalha
- 🔧 Comandos de administração e debug

## 🔧 Requisitos

- Python 3.8 ou superior
- discord.py 2.0+
- Conta de desenvolvedor do Discord
- Token de bot do Discord

## 📦 Instalação

1. Clone o repositório:
```bash
git clone <seu-repositorio>
cd <nome-do-diretorio>
```

2. Instale as dependências:
```bash
pip install discord.py
```

3. Configure o token do bot no arquivo `connection.py`:
```python
bot.run("SEU_TOKEN_AQUI")
```

## ⚙️ Configuração

1. Crie um bot no [Discord Developer Portal](https://discord.com/developers/applications)
2. Habilite as seguintes intents no painel:
   - Presence Intent
   - Server Members Intent
   - Message Content Intent
3. Copie o token do bot
4. Substitua `"xxxx"` no arquivo `connection.py` pelo seu token
5. Convide o bot para seu servidor usando o OAuth2 URL Generator

## 📖 Comandos

### Comandos Gerais

| Comando | Descrição |
|---------|-----------|
| `rp!help` | Exibe a lista completa de comandos |

### Rolagem de Dados

| Comando | Descrição |
|---------|-----------|
| `rp!d2` | Rola um dado de 2 lados |
| `rp!d4` | Rola um dado de 4 lados |
| `rp!d10` | Rola um dado de 10 lados |
| `rp!d20` | Rola um dado de 20 lados |
| `rp!d100` | Rola um dado de 100 lados |

### Sistema de Batalha

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `rp!battle @jogador1 hp1 @jogador2 hp2` | Inicia uma batalha automática | `rp!battle @User1 50 @User2 50` |
| `rp!forfeit` | Desiste da batalha atual | `rp!forfeit` |
| `rp!resume` | Retoma uma batalha pausada | `rp!resume` |
| `rp!log` | Mostra os últimos 10 turnos da batalha | `rp!log` |

### Comandos de Administração

| Comando | Descrição |
|---------|-----------|
| `rp!debug` | Mostra informações sobre batalhas ativas |
| `rp!clear` | Limpa a batalha do canal atual |

## ⚔️ Sistema de Batalha

### Mecânica

O sistema de batalha é completamente automático:
- ⏱️ **Turnos automáticos** a cada 3 segundos
- 🎯 **Rolagens automáticas** de ataque e defesa
- 💔 **Sistema de HP** entre 1 e 100
- 🔄 **Batalha contínua** até um jogador chegar a 0 HP

### Tabela de Dano (Ataque)

| Rolagem | Dano | Descrição |
|---------|------|-----------|
| 0 | 1 (próprio) | Causa 1 de dano a si mesmo |
| 1-4 | 1-4 | Ataque ineficiente |
| 5-10 | 5-10 | Ataque fraco |
| 11-15 | 11-15 | Ataque eficiente |
| 16-19 | 16-19 | Ataque muito eficiente |
| 20 | 25 | **Crítico!** Dano massivo |
| 21 | 20 | **Crítico especial!** Dano alto + recupera 5 HP |

### Tabela de Defesa

| Rolagem | Redução | Descrição |
|---------|---------|-----------|
| 0-4 | 0 | Defesa falhou |
| 5 | 1 | Defesa quase inútil |
| 6-9 | Valor - 2 | Defesa parcial |
| 10-17 | 10 | Defesa quase perfeita |
| 18-19 | 100% | **Esquiva perfeita!** Evita todo o dano |
| 20 | 100% + 5 | **Parry!** Esquiva e retorna 5 de dano |
| 21 | 100% | **Maestria!** Esquiva e recupera 5 HP |

### Regras da Batalha

1. ✅ HP deve estar entre 1 e 100
2. ❌ Bots não podem participar
3. ❌ Jogadores devem ser diferentes
4. 🔒 Apenas uma batalha por canal por vez
5. 🏳️ Jogadores podem desistir a qualquer momento
6. 🏆 Vencedor é quem tem HP > 0 ao final

## 📁 Estrutura do Projeto

```
src/
├── connection.py      # Configuração principal do bot e comandos
├── rpg_dice.py       # Sistema de rolagem de dados
├── rpg_rules.py      # Mensagens de help e regras
└── rpg_simulator.py  # Lógica do sistema de batalha
```

### Descrição dos Módulos

- **connection.py**: Gerencia a conexão com o Discord e registra todos os comandos
- **rpg_dice.py**: Fornece funções para rolar diferentes tipos de dados
- **rpg_simulator.py**: Implementa toda a lógica de batalha, incluindo:
  - Estado da batalha (BattleState)
  - Cálculo de dano e defesa
  - Gerenciamento de turnos automáticos
  - Sistema de logs
- **rpg_rules.py**: Contém as mensagens de ajuda formatadas

## 🎯 Como Funciona

### Fluxo de uma Batalha

1. **Início**: Jogador usa `rp!battle @adversario hp_proprio hp_adversario`
2. **Validação**: Sistema valida os parâmetros e jogadores
3. **Criação**: Cria um estado de batalha no canal
4. **Automação**: Inicia loop automático de turnos
5. **Turno**:
   - Atacante rola d22 para ataque
   - Defensor rola d22 para defesa
   - Sistema calcula dano final
   - Atualiza HP dos jogadores
   - Registra no log
6. **Verificação**: Checa se algum jogador chegou a 0 HP
7. **Fim**: Declara vencedor e limpa o estado da batalha

### Dado d22 Especial

O sistema usa um dado de 22 lados (0-21) para mecânicas especiais:
- Valores 0-19 são padrão
- Valor 20 é o primeiro crítico
- Valor 21 é um crítico especial único

## 🐛 Troubleshooting

### Bot não responde
- Verifique se o token está correto
- Confirme que as intents estão habilitadas
- Verifique se o bot tem permissões no canal

### Batalha não inicia
- Certifique-se de que não há batalha ativa no canal
- Verifique se os HP estão entre 1 e 100
- Confirme que ambos os jogadores não são bots

### Batalha travou
- Use `rp!debug` para verificar o estado
- Use `rp!clear` para limpar batalhas travadas

## 📝 Licença

Este projeto é fornecido como está, sem garantias. Sinta-se livre para modificar e usar conforme necessário.

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir novas funcionalidades
- Melhorar a documentação
- Enviar pull requests

## 📧 Suporte

Para questões ou suporte, abra uma issue no repositório.

---

Desenvolvido com ❤️ usando Python e discord.py
