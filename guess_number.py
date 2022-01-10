import random
from discord.ext import commands

client = commands.Bot(command_prefix="!")

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.command(name='play')
async def play(ctx):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.message.channel

    number = random.randint(1, 100)
    await ctx.send('I have a number in mind between 1 and 100, guess')

    for i in range(0, 5):
        guess = await client.wait_for('message', check=check)

        if guess.content == number:
            await ctx.send('You got it!')

        elif guess.content < str(number):
            await ctx.send('Higher!')

        elif guess.content > str(number):
            await ctx.send('Lower!')

        else:
            return  # Or something else

    else:
        await ctx.send("You lost, type !play to play again.")

client.run('OTI4MDQ5NjYzMjA5MjYzMTQ1.YdTHmg.xnEXp5AjvU5YcKIN3YG5FrE3THE')
