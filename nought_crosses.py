import asyncio

import discord
from discord.ext import commands
import random

client = commands.Bot(command_prefix="!")

@client.command(aliases = ["nc", "n&c", "noughtsandcrosses", "noughts&crosses"])
async def tictactoe(ctx):
    channel = ctx.channel
    board = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    output = await output_board(board)

    turn = random.randint(PLAYER, SKY_NET)

    if turn == PLAYER:
        em = discord.Embed(title = f"{ctx.author.name}'s Noughts and Crosses Game", description = output, color = discord.Color(0x0000ff))
        em.set_footer(text = "Your turn! Type a number from 1-9 representing each space, 1 being the topleft corner, 2 being the top center, 3 being the topright corner up to 9 being the bottom right corner.")
        await ctx.send(embed = em)
    else:
        board = [0, 0, 0, 0, 0, 0, 0, 0, AI_PIECE]
        output = await output_board(board)
        em = discord.Embed(title = f"{ctx.author.name}'s Noughts and Crosses Game", description = output, color = discord.Color(0x0000ff))
        em.set_footer(text = "Your turn! Type a number from 1-9 representing each space, 1 being the topleft corner, 2 being the top center, 3 being the topright corner up to 9 being the bottom right corner.")
        await ctx.send(embed = em)
        turn = PLAYER

    while True:
        if turn == PLAYER:
            def check(m):
                return m.author == ctx.author and m.channel == channel
            try:
                message = await client.wait_for('message', timeout = 30.00, check = check)
            except asyncio.TimeoutError:
                output = await output_board(board)
                em = discord.Embed(title = f"{ctx.author.name}, timeout!", description = output, color = discord.Color(0xff0000))
                em.set_footer(text = "you took more than 30s to respond")
                await ctx.send(embed = em)
                return

            try:
                e = int(message.content)
                if e > 0 and 10 > e:
                    valid = True
                    pos = e-1
                else:
                    #raise error
                    pos = 1/0
            except:
                output = await output_board(board)
                em = discord.Embed(title = f"{ctx.author.name}, invalid space!", description = output, color = discord.Color(0xff0000))
                em.set_footer(text = "only integers from 1 to 9 allowed")
                await ctx.send(embed = em)
                valid = False

            if valid:
                if await is_valid_position(board, pos):
                    board[pos] = PLAYER_PIECE
                    output = await output_board(board)

                    if await game_won(board) == PLAYER_PIECE:
                        em = discord.Embed(title = f"{ctx.author.name}, you win!", description = output, color = discord.Color(0x00ff00))
                        await ctx.send(embed = em)
                        return

                    if "⬛" not in output:
                        em = discord.Embed(title = f"{ctx.author.name}, it's a draw!", description = output, color = discord.Color(0xffff00))
                        await ctx.send(embed = em)
                        return

                    turn = SKY_NET

                    em = discord.Embed(title = f"{ctx.author.name}'s Noughts and Crosses Game", description = output, color = discord.Color(0x0000ff))
                    em.set_footer(text = "I'm thinking...")
                    my_msg = await ctx.send(embed = em)
                else:
                    output = await output_board(board)
                    em = discord.Embed(title = f"{ctx.author.name}, invalid column!", description = output, color = discord.Color(0xff0000))
                    em.set_footer(text = "that space is already occupied")
                    await ctx.send(embed = em)

        if turn == SKY_NET:
            pos = await find_best_move(board)
            board[pos] = AI_PIECE
            output = await output_board(board)

            if await game_won(board) == AI_PIECE:
                em = discord.Embed(title = f"{ctx.author.name}, the AI wins!", description = output, color = discord.Color(0xff0000))
                em.set_footer(text = "Better luck next time!")
                await my_msg.edit(embed = em)
                return

            if "⬛" not in output:
                em = discord.Embed(title = f"{ctx.author.name}, it's a draw!", description = output, color = discord.Color(0xffff00))
                await my_msg.edit(embed = em)
                return

            turn = PLAYER
            await asyncio.sleep(1.2)
            em = discord.Embed(title = f"{ctx.author.name}'s Connect Four Game", description = output, color = discord.Color(0x0000ff))
            em.set_footer(text = "Your turn! Type a number from 1-9! You are the circles.")
            await my_msg.edit(embed = em)

async def output_board(board):
    output = ""
    for i in range(0,9):
        if board[i] == 0:
            output = f"{output}⬛"
        elif board[i] == 1:
            output = f"{output}⭕"
        elif board[i] == 2:
            output = f"{output}❌"
        if i == 2 or i == 5:
            output = f"{output}\n"
    return output

async def is_valid_position(board, pos):
    return board[pos] == 0

async def game_won(board):
    for i in range(0,3):
        r = i*3
        if board[r] == board[r+1] and board[r+1] == board[r+2] and board[r] != 0:
            return board[r]
    for i in range(0,3):
        if board[i] == board[i+3] and board[i+3] == board[i+6] and board[i] != 0:
            return board[i]
    if board[0] == board[4] and board[4] == board[8] and board[0] != 0:
        return board[0]
    if board[2] == board[4] and board[4] == board[6] and board[2] != 0:
        return board[2]
    return 0

async def find_best_move(board):
    move = await find_winning_move(board, AI_PIECE)
    if move != None:
        #if the move wins the bot plays it: highest priority
        return move
    move = await find_winning_move(board, PLAYER_PIECE)
    if move != None:
        #if the oppoenent wins by playing this move the bot blocks it
        return move
    move_count = 0
    for item in board:
        if item != 0:
            move_count += 1
    if move_count == 1:
        if await is_valid_position(board, 4):
            return 4
        else:
            return 2
    elif move_count == 2:
        if board[0] == PLAYER_PIECE or board[1] == PLAYER_PIECE or board[6] == PLAYER_PIECE or board[7] == PLAYER_PIECE:
            return 2
        elif board[2] == PLAYER_PIECE or board[3] == PLAYER_PIECE or board[5] == PLAYER_PIECE:
            return 6
        elif board[4] == PLAYER_PIECE:
            return 0
    elif move_count == 3:
        if (board[0] == PLAYER_PIECE and board[8] == PLAYER_PIECE) or (board[2] == PLAYER_PIECE and board[6] == PLAYER_PIECE):
            return 1
        elif (board[0] == PLAYER_PIECE and board[5] == PLAYER_PIECE) or (board[2] == PLAYER_PIECE and board[5] == PLAYER_PIECE) or (board[2] == PLAYER_PIECE and board[8] == PLAYER_PIECE):
            return 2
        elif (board[2] == PLAYER_PIECE and board[3] == PLAYER_PIECE) or (board[1] == PLAYER_PIECE and board[3] == PLAYER_PIECE) or (board[1] == PLAYER_PIECE and board[6] == PLAYER_PIECE):
            return 0
        elif (board[0] == PLAYER_PIECE and board[7] == PLAYER_PIECE) or (board[3] == PLAYER_PIECE and board[7] == PLAYER_PIECE) or (board[3] == PLAYER_PIECE and board[8] == PLAYER_PIECE):
            return 6
        elif (board[2] == PLAYER_PIECE and board[7] == PLAYER_PIECE) or (board[5] == PLAYER_PIECE and board[6] == PLAYER_PIECE) or (board[7] == PLAYER_PIECE and board[5] == PLAYER_PIECE):
            return 8
        else:
            moves = await find_valid_moves(board)
            return random.choice(moves)
    elif move_count == 4:
        if board[0] != PLAYER_PIECE and board[2] != PLAYER_PIECE and board[6] != PLAYER_PIECE:
            return 4
        elif await is_valid_position(board, 0):
            return 0
        elif await is_valid_position(board, 2):
            return 2
        elif await is_valid_position(board, 6):
            return 6
    else:
        moves = await find_valid_moves(board)
        return random.choice(moves)

async def find_valid_moves(board):
    moves = []
    for i in range(0,9):
        if await is_valid_position(board,i):
            moves.append(i)
    return moves

async def find_winning_move(board,player):
    if ((board[5] == player and board[5] == board[8]) or (board[0] == player and board[1] == board[0]) or (board[4] == player and board[4] == board[6])) and await is_valid_position(board, 2):
        return 2
    elif ((board[4] == player and board[4] == board[7]) or (board[0] == player and board[2] == board[0])) and await is_valid_position(board, 1):
        return 1
    elif ((board[3] == player and board[3] == board[6]) or (board[1] == player and board[1] == board[2]) or (board[4] == player and board[4] == board[8])) and await is_valid_position(board, 0):
        return 0
    elif ((board[2] == player and board[2] == board[8]) or (board[3] == player and board[3] == board[4])) and await is_valid_position(board, 5):
        return 5
    elif ((board[1] == player and board[1] == board[7]) or (board[3] == player and board[3] == board[5]) or (board[0] == player and board[0] == board[8]) or (board[2] == player and board[2] == board[6])) and await is_valid_position(board, 4):
        return 4
    elif ((board[0] == player and board[0] == board[6]) or (board[4] == player and board[5] == board[4])) and await is_valid_position(board, 3):
        return 3
    elif ((board[0] == player and board[0] == board[3]) or (board[7] == player and board[7] == board[8]) or (board[4] == player and board[4] == board[2])) and await is_valid_position(board, 6):
        return 6
    elif ((board[2] == player and board[2] == board[5]) or (board[7] == player and board[7] == board[6]) or (board[4] == player and board[4] == board[0])) and await is_valid_position(board, 8):
        return 8
    elif ((board[1] == player and board[1] == board[4]) or (board[8] == player and board[6] == board[8])) and await is_valid_position(board, 7):
        return 7
    return None

ROW_COUNT = 6
COLUMN_COUNT = 6

PLAYER_PIECE = 1
AI_PIECE = 2
EMPTY = 0

PLAYER = 0
SKY_NET = 1


client.run('OTI4MDQ5NjYzMjA5MjYzMTQ1.YdTHmg.xnEXp5AjvU5YcKIN3YG5FrE3THE')

