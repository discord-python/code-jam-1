# Code Jam 1 - Team 23

**This is the code jam entry for Momo & kel**

This is the repository for all code relating to our first code jam, in March 2018. Participants should fork this repository, and submit their code in a pull request.

**This code jam runs from the 23rd of March to the 25th of March, measured using the UTC timezone.** Make sure you open your pull request by then. Once the deadline is up, stop pushing commits - we will not accept any submissions made after this date.

## How To Participate

First things first - set up your repository. Read [this guide on our site](https://pythondiscord.com/info/jams) for information on how to set yourself up for a code jam.
Remember, only one teammate needs to fork the repository - everyone else should be granted access to that fork as a contributor, so that they can work on it directly.

Make sure you have the following things installed:

* Python 3.6 or later (installed with the PATH option enabled if you're on Windows)
* Pip - make sure you can run `pip` in a terminal or command prompt
* Pipenv - you can install this by running `pip install pipenv` in a terminal or command prompt
    * Like before, make sure you can run `pipenv` in a terminal or command prompt

Next up, set up your project with `pipenv`. We've [compiled some documentation](./doc) for you to read over if you get stuck - you can find it in the `doc/` folder,
and you absolutely should read all of it, and it will likely answer some of the questions that you have.

Use `pipenv run run.py` to start your project. You can press `CTRL+C` with the bot window selected to stop it.

Remember, if you need help, you can always ask on the server!

## The Task

This month's theme is: **Snakes**.

For this code jam, your task will be to create a Snake cog for a [Discord.py rewrite bot](https://github.com/Rapptz/discord.py/tree/rewrite). 
You can find the [documentation for Discord.py rewrite here](https://discordpy.readthedocs.io/en/rewrite/). The best cog commands will be 
added to the official Python Discord bot and made available to everyone on the server. The overall best cog will be awarded custom Code Jam 
Champion roles, but the best commands from the teams who did not win will also be added to our bot, and any users who write something that 
ends up in the bot will be awarded Contributor roles on the server.

We have prepared some Discord.py rewrite boilerplate for you in this repo. Fork the repo and work in the file called **snakes.py**, in **bot/cogs**.

This means you won't have to write the basic bot itself, you'll just have to write the stuff that goes in the cog. For those of you with no 
discord.py experience, cogs are like little modules that the bot can load, and contain a class with methods that are hooked up to bot commands 
(like **bot.tags.get**). That way, when you type `bot.snakes.get('python')`, it will run the method inside the cog that corresponds to this command.

Your initial task will be to write **get_snek**. This is the minimum requirement for this contest, and everyone must do it. **get_snek** will be a 
method that goes online and fetches information about a snake. If you run it without providing an argument, it should fetch information about a 
random snake, including the name of the snake, a picture of the snake, and various information about it. Is it venomous? Where can it be found? 
What information you choose to get is up to you.

`get_snek()` should also take an optional argument `name`, which should be a string that contains the name of a snake. For example, if you do 
`get_snek('cobra')`, it should get information about a cobra. `name` should be case insensitive.

If `get_snek('Python')` is called, the method should instead return information about the programming language, but making sure to return the 
same type of information as for all the other snakes. Fill in this information in any way you want, try to have some fun with it.

The information should be returned as a dictionary, so that other methods in the Snake class can call it and make use of it.

Once you have finished `get_snek()`, you should make at least two bot commands. The first command, `get()`, should simply call `get_snek()` 
with whatever arguments the user provided, and then make a nice embed that it returns to Discord. For example, if the user in the Discord 
channel says `bot.snakes.get('anaconda')`, the bot should post an embed that shows a picture of an anaconda and some information about the 
snake.

The second command is entirely up to you. You can choose to use `get_snek` for this command as well, or you can come up with something entirely 
different. The only requirement is that it is snake related in some way or other. Here is your chance to be creative. It is these commands that 
will win or lose you this code jam. The best original ideas for these commands will probably walk away with the victory.

You are allowed to make as many additional commands as you want, but try to keep it a reasonable amount. The team that writes the most commands is 
not automatically going to win. One really excellent command is much better than 10 mediocre ones.

---

Have fun, and don't be afraid to ask for help in the usual places if you need it!
