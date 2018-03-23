# coding=utf-8
import ast
import logging
import sys
from logging import Logger, StreamHandler

import discord.ext.commands.view


logging.TRACE = 5
logging.addLevelName(logging.TRACE, "TRACE")


def monkeypatch_trace(self, msg, *args, **kwargs):
    """
    Log 'msg % args' with severity 'TRACE'.

    To pass exception information, use the keyword argument exc_info with
    a true value, e.g.

    logger.trace("Houston, we have an %s", "interesting problem", exc_info=1)
    """
    if self.isEnabledFor(logging.TRACE):
        self._log(logging.TRACE, msg, args, **kwargs)


Logger.trace = monkeypatch_trace

# Set up logging
logging_handlers = [StreamHandler(stream=sys.stderr)]

logging.basicConfig(
    format="%(asctime)s Bot: | %(name)30s | %(levelname)8s | %(message)s",
    datefmt="%b %d %H:%M:%S",
    level=logging.TRACE,
    handlers=logging_handlers
)

log = logging.getLogger(__name__)

# Silence discord and websockets
logging.getLogger("discord.client").setLevel(logging.ERROR)
logging.getLogger("discord.gateway").setLevel(logging.ERROR)
logging.getLogger("discord.state").setLevel(logging.ERROR)
logging.getLogger("discord.http").setLevel(logging.ERROR)
logging.getLogger("websockets.protocol").setLevel(logging.ERROR)


def _skip_string(self, string: str) -> bool:
    """
    Our version of the skip_string method from
    discord.ext.commands.view; used to find
    the prefix in a message, but allowing prefix
    to ignore case sensitivity
    """

    strlen = len(string)
    if self.buffer.lower()[self.index:self.index + strlen] == string:
        self.previous = self.index
        self.index += strlen
        return True
    return False


def _get_word(self) -> str:
    """
    Invokes the get_word method from
    discord.ext.commands.view used to find
    the bot command part of a message, but
    allows the command to ignore case sensitivity,
    and allows commands to have Python syntax.

    Example of valid Python syntax calls:
    ------------------------------
    bot.tags.set("test", 'a dark, dark night')
    bot.help(tags.delete)
    bot.hELP(tags.delete)
    """

    pos = 0
    while not self.eof:
        try:
            current = self.buffer[self.index + pos]
            if current.isspace() or current == "(":
                break
            pos += 1
        except IndexError:
            break

    self.previous = self.index
    result = self.buffer[self.index:self.index + pos]
    self.index += pos
    next = None

    # Check what's after the '('
    if len(self.buffer) != self.index:
        next = self.buffer[self.index + 1]

    # Is it possible to parse this without syntax error?
    syntax_valid = True
    try:
        ast.literal_eval(self.buffer[self.index:])
    except SyntaxError:
        log.warning("The command cannot be parsed by ast.literal_eval because it raises a SyntaxError.")
        # TODO: It would be nice if this actually made the bot return a SyntaxError. ClickUp #1b12z  # noqa: T000
        syntax_valid = False

    # Conditions for a valid, parsable command.
    python_parse_conditions = (
        current == "("
        and next
        and next != ")"
        and syntax_valid
    )

    if python_parse_conditions:
        log.debug(f"A python-style command was used. Attempting to parse. Buffer is {self.buffer}. "
                  "A step-by-step can be found in the trace log.")

        # Parse the args
        log.trace("Parsing command with ast.literal_eval.")
        args = self.buffer[self.index:]
        args = ast.literal_eval(args)

        # Force args into container
        if isinstance(args, str):
            args = (args,)

        # Type validate and format
        new_args = []
        for arg in args:

            # Other types get converted to strings
            if not isinstance(arg, str):
                log.trace(f"{arg} is not a str, casting to str.")
                arg = str(arg)

            # Adding double quotes to every argument
            log.trace(f"Wrapping all args in double quotes.")
            new_args.append(f'"{arg}"')

        # Add the result to the buffer
        new_args = " ".join(new_args)
        self.buffer = f"{self.buffer[:self.index]} {new_args}"
        log.trace(f"Modified the buffer. New buffer is now {self.buffer}")

        # Recalibrate the end since we've removed commas
        self.end = len(self.buffer)

    elif current == "(" and next == ")":
        # Move the cursor to capture the ()'s
        log.debug("User called command without providing arguments.")
        pos += 2
        result = self.buffer[self.previous:self.index + (pos+2)]
        self.index += 2

    if isinstance(result, str):
        return result.lower()  # Case insensitivity, baby
    return result


# Monkey patch the methods
discord.ext.commands.view.StringView.skip_string = _skip_string
discord.ext.commands.view.StringView.get_word = _get_word
