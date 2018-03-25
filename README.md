# Code Jam 1

This is the repository for all code relating to our first code jam, in March 2018. Participants should fork this repository, and submit their code in a pull request.

**This code jam runs from the 23rd of March to the 25th of March, measured using the UTC timezone.** Make sure you open your pull request by then. Once the deadline is up, stop pushing commits - we will not accept any submissions made after this date.

## What does it do?
Searches Wikipedia for snake information, but first it **converts** your search to a valid snake result. You get a nice table when you invoke the search command.
**bot.snakes.get("viper")**

![Multiple_search_results](https://i.imgur.com/9Lij5Jp.png)

You can off-course search directly for the scientific name.
**bot.snakes.get("Bothriechis schlegelii")

![Scientific_search](https://i.imgur.com/M7WdO18.png)

**bot.snakes.get()** returns a random snake from wikipedia

There is also a guessing game here

**bot.snakes.guess()**

![guess_the_snake](https://i.imgur.com/JWHrDbk.png)

Alas, if you are in a voice channel and type **bot.zen** you are greeted with a little easter-egg
