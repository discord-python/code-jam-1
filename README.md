# snek it up

**[Python-Discord code jam 1](https://github.com/discord-python/code-jam-1) entry by Momo and kel/qrie** (Team 23)


## what is it

A Discord bot that:

- Finds snek species on the [ITIS database](https://itis.gov/) 🐍
- Hosts Snakes and Ladders games in concurrent channels 🎲
- Imitates your chat history, but with 105% more snekin 💬
- Lets you hatch snek eggs for your very own snek collection ≧◡≦
- Draws random sneks using Perlin noise 🖌️
- Plays snek rattles in your voice channel, on demand 🔊

## how u do that

- Snek lookup: `bot.snakes.get('snek name here')`, use `bot.snakes.get` for a random snek type
- Snakes and Ladders:
  - Create a game using `bot.sal create` (the author can cancel the game using `bot.sal cancel`)
  - Others join the game using `bot.sal join` (players can leave using `bot.sal leave`)
  - The author starts the match using `bot.sal start`
  - When a round begins, players use `bot.roll` to roll the dice
  - glhf

- Snake imitation: `bot.snakes.snakeme`
- Egg hatching: `bot.snakes.hatch`
- Snek drawing: `bot.snakes.draw`
- Rattle-up your voice channel: `bot.snakes.rattle`

## environment variables

You will need these environment variables to setup mr bot:

- `BOT_TOKEN`: The Discord API token for the bot.
- `FFMPEG`: A direct path to a `ffmpeg` executable. If not provided, it will assume the `ffmpeg` command is in your path.
- `LIBOPUS` The name of the `libopus` library file, located in the project folder. If not provided, defaults to `libopus`.
  - ffmpeg and libopus are only used for snek rattling (voice comms)

## random snek database

In order to be able to find random snakes, you need to use the provided tool to fetch a list of snake names. That list is stored inside a pickle-file that has to be in the project directory when starting the bot.

To generate the pickle-file, you use the `tools/snekfetcher.py` file inside the Pipenv shell:

```
pipenv run tools\snekfetcher.py
```

The output file will be `sneks.pickle`.

## note about libopus

The `libopus.dll` is compiled for 64-bit Windows only. If you're using a different OS/architecture, you will need to find/compile the library for your system. If the name of the file changes, you will need to provide the `LIBOPUS` env variable, as described above.

## extra configuration

#### snakes and ladders

It is possible to configure Snakes and Ladders to use your own board. Simply overwrite the `res/ladders/board.jpg` file and adjust the `res/ladders/board.py` file accordingly:

 - `BOARD_TILE_SIZE`: The size (width/height) of each tile on the board, in pixels
 - `BOARD_PLAYER_SIZE`: The size of each player icon on the board, in pixels
 - `BOARD_MARGIN`: Tuple (x, y) for extra margins on the board, relative to top-left corner
 - `PLAYER_ICON_IMAGE_SIZE`: The size of the user avatars to request from Discord. This should be a power of 2 (e.g. `32`, `64`, `128`...) and should be higher or equal to `BOARD_PLAYER_SIZE`.
 - `MAX_PLAYERS`: The maximum amount of players this board can support (i.e. how many players can you fit in each tile, at maximum capacity)
 - `BOARD`: Dictionary[int, int] that defines the "shortcuts" in the board (the snakes and the ladders), in the form `from: to`.

#### rattles

To change the rattle sounds, put audio files in the `res/rattle` directory and modify the `RATTLES` list inside `res/rattle/rattleconfig.py`.
