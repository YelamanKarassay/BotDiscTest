import asyncio
import math

import discord
import numpy as np
from discord.ext import commands
import random

ROW_COUNT = 6
COLUMN_COUNT = 6

PLAYER_PIECE = 1
AI_PIECE = 2
EMPTY = 0

PLAYER = 0
SKY_NET = 1

client = commands.Bot(command_prefix="!")

@client.command(aliases = ["connect4", "c4"])
async def connectfour(ctx, opponent : discord.Member = None):
    channel = ctx.channel
    board = np.zeros((ROW_COUNT, COLUMN_COUNT))
    output = await print_board(board)
    game_over = False
    turn = random.randint(PLAYER, SKY_NET)

    if turn == PLAYER:
        em = discord.Embed(title = f"{ctx.author.name}'s Connect Four Game", description = output, color = discord.Color(0x0000ff))
        em.set_footer(text = "Your turn! Type a number from 1-6 representing each column, 1 being the column on the leftmost and 6 being the one on the rightmost")
        await ctx.send(embed = em)

    while not game_over:
        if turn == PLAYER and not game_over:
            def check(m):
                return m.author == ctx.author and m.channel == channel
            try:
                message = await client.wait_for('message', timeout = 30.00, check = check)
            except asyncio.TimeoutError:
                output = await print_board(board)
                em = discord.Embed(title = f"{ctx.author.name}, timeout!", description = output, color = discord.Color(0xff0000))
                em.set_footer(text = "you took more than 30s to respond")
                await ctx.send(embed = em)
                game_over = True
                return
            try:
                e = int(message.content)
                if e > 0 and 7 > e:
                    valid = True
                    col = e-1
                else:
                    #raise error
                    col = 1/0
            except:
                output = await print_board(board)
                em = discord.Embed(title = f"{ctx.author.name}, invalid column!", description = output, color = discord.Color(0xff0000))
                em.set_footer(text = "only integers from 1 to 6 allowed")
                await ctx.send(embed = em)
                valid = False

            if valid:
                if await is_valid_location(board, col):
                    row = await get_valid_row(board, col)
                    await drop_piece(board, row, col, PLAYER_PIECE)
                    output = await print_board(board)

                    if await wining_move(board, PLAYER_PIECE):
                        em = discord.Embed(title = f"{ctx.author.name}, you win!", description = output, color = discord.Color(0x00ff00))
                        await ctx.send(embed = em)
                        game_over = True
                        return

                    if "⚫" not in output:
                        em = discord.Embed(title = f"{ctx.author.name}, it's a draw!", description = output, color = discord.Color(0xffff00))
                        await ctx.send(embed = em)
                        game_over = True
                        return

                    turn = SKY_NET

                    em = discord.Embed(title = f"{ctx.author.name}'s Connect Four Game", description = output, color = discord.Color(0x0000ff))
                    em.set_footer(text = "I'm thinking...")
                    my_msg = await ctx.send(embed = em)
                else:
                    output = await print_board(board)
                    em = discord.Embed(title = f"{ctx.author.name}, invalid column!", description = output, color = discord.Color(0xff0000))
                    em.set_footer(text = "that column is full")
                    await ctx.send(embed = em)

        if turn == SKY_NET and not game_over:
            col, minimax_score = await minimax(board, 4, True, -math.inf, math.inf)
            if await is_valid_location(board, col):
                row = await get_valid_row(board, col)
                await drop_piece(board, row, col, AI_PIECE)
                output = await print_board(board)

                if "⚫" not in output:
                    em = discord.Embed(title = f"{ctx.author.name}, it's a draw!", description = output, color = discord.Color(0xffff00))
                    await my_msg.edit(embed = em)
                    game_over = True
                    return

                if await wining_move(board, AI_PIECE):
                    em = discord.Embed(title = f"{ctx.author.name}, the AI wins!", description = output, color = discord.Color(0xff0000))
                    em.set_footer(text = "Better luck next time!")
                    await my_msg.edit(embed = em)
                    game_over = True
                    return

                turn = PLAYER

                try:
                    e = my_msg
                    await asyncio.sleep(1.2)
                    em = discord.Embed(title = f"{ctx.author.name}'s Connect Four Game", description = output, color = discord.Color(0x0000ff))
                    em.set_footer(text = "Your turn! Type a number from 1-6!")
                    await my_msg.edit(embed = em)
                except:
                    em = discord.Embed(title = f"{ctx.author.name}'s Connect Four Game", description = output, color = discord.Color(0x0000ff))
                    em.set_footer(text = "Your turn! Type a number from 1-6 representing each column, 1 being the column on the leftmost and 6 being the one on the rightmost")
                    await ctx.send(embed = em)

async def drop_piece(board, row, col, piece):
    board[row][col] = piece

async def is_valid_location(board, col):
    return board[5][col] == 0

async def get_valid_row(board, col):
    for r in range(6):
        if board[r][col] == 0:
            return r

async def print_board(board):
    flipped = np.flip(board, 0)
    output = ""
    for i in range(0,6):
        for item in flipped[i]:
            if item == 1:
                output = f"{output}🔴"
            elif item == 2:
                output = f"{output}🟡"
            elif item == 0:
                output = f"{output}⚫"
        output = f"{output}\n"
    return output

async def evaluate(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE
    # 4 in a row
    if window.count(piece) == 4:
        score += 100
    # 3 in a row
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score

async def wining_move(board, piece):
    for c in range(3):
        for r in range(6):
            if board[r][c] == piece and board[r][c + 1] == piece and \
                    board[r][c + 2] == piece and board[r][c + 3] == piece:
                return True

    for c in range(6):
        for r in range(3):
            if board[r][c] == piece and board[r + 1][c] == piece and \
                    board[r + 2][c] == piece and board[r + 3][c] == piece:
                return True

    for c in range(3):
        for r in range(3):
            if board[r][c] == piece and board[r + 1][c + 1] == piece and \
                    board[r + 2][c + 2] == piece and board[r + 3][c + 3] == piece:
                return True

    for c in range(3):
        for r in range(3, 6):
            if board[r][c] == piece and board[r - 1][c + 1] == piece and \
                    board[r - 2][c + 2] == piece and board[r - 3][c + 3] == piece:
                return True

async def score_position(board, piece):
    score = 0

    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c + 4]
            score += await evaluate(window, piece)

    for c in range(COLUMN_COUNT):
        column_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = column_array[r:r + 4]
            score += await evaluate(window, piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + i][c + i] for i in range(4)]
            score += await evaluate(window, piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + 3 - i][c + i] for i in range(4)]
            score += await evaluate(window, piece)

    return score

async def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if await is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

async def pick_best_move(board, piece):
    valid_locations = await get_valid_locations(board)
    best_score = -10000
    best_col = random.choice(valid_locations)
    for column in valid_locations:
        row = await get_valid_row(board, column)
        temp_board = board.copy()
        await drop_piece(temp_board, row, column, piece)
        score = await score_position(temp_board, piece)
        if score > best_score:
            best_score = score
            best_col = column

    return best_col

async def is_terminal_node(board):
    return await wining_move(board, PLAYER_PIECE) or await wining_move(board, AI_PIECE) or len(await get_valid_locations(board)) == 0

async def minimax(board, depth, maximizing_player, alpha, beta):
    valid_locations = await get_valid_locations(board)
    is_terminal = await is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if await wining_move(board, AI_PIECE):
                return None, 9999999999999999
            elif await wining_move(board, PLAYER_PIECE):
                return None, -9999999999999999
            else:  # no more valid moves
                return None, 0
        else:
            return None, await score_position(board, AI_PIECE)
    if maximizing_player:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = await get_valid_row(board, col)
            b_copy = board.copy()
            await drop_piece(b_copy, row, col, AI_PIECE)
            new_score = (await minimax(b_copy, depth - 1, False, alpha, beta))[1]
            if float(new_score) > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha > beta:
                break
        return column, value
    else:  # minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = await get_valid_row(board, col)
            b_copy = board.copy()
            await drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = (await minimax(b_copy, depth - 1, True, alpha, beta))[1]
            if float(new_score) < value:
                value = new_score
                column = col
            beta = min(beta,value)
            if beta <= alpha:
                break
        return column, value
