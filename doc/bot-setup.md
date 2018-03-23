# Setting up your bot

In order to test your project, you're going to need to set it up. There's a few steps to this. In short, they are:

1. Create a testing server for you and your teammates
1. Create an OAuth application under your Discord account
1. Add a bot to your OAuth application
1. Add the bot to your testing server
1. Save the bot token and test your bot

**Please note:** Only one of you needs to do all of these steps. The rest of the team should wait until the token is
given to them, and save that so that they can test as well.

## Create a testing server

First of all, you need somewhere to test your bot. Open Discord, and scroll to the bottom of your server list, to find
the following button. Click on it, and create your testing server.

![Create Server button](https://dl.dropboxusercontent.com/s/bbfmxkyaodo30ng/DiscordCanary_2018-03-22_10-40-21.png)

![Create Server dialog](https://dl.dropboxusercontent.com/s/m1nbq3tr871k6ws/DiscordCanary_2018-03-22_10-46-00.png)

Once your server is created, invite your teammates.

![Invite dialog](https://dl.dropboxusercontent.com/s/d1u5f3nlootix85/DiscordCanary_2018-03-22_10-47-32.png)

## Create an OAuth application

Head over to [https://discordapp.com/developers/applications/me](https://discordapp.com/developers/applications/me).
If you need to login, it'll end up taking you to the actual client, so navigate back to that page. Create a new 
application.

![New App button](https://dl.dropboxusercontent.com/s/t2blc2yt47wl4ax/vivaldi_2018-03-22_10-56-19.png)

![New App dialog](https://dl.dropboxusercontent.com/s/o1veymtov0s6i4v/vivaldi_2018-03-22_10-57-12.png)

## Add a bot to your OAuth application

Scroll down, and click on the "Create a Bot User" button. Confirm, and your application will now have a bot.
Make sure you **do not** enable the OAuth2 Code Grant option.

![Bot creation section](https://dl.dropboxusercontent.com/s/cn9zp8yg9m5uwx7/vivaldi_2018-03-22_10-58-26.png)

![Bot info section](https://dl.dropboxusercontent.com/s/kzwjlq73v9biof4/vivaldi_2018-03-22_10-59-25.png)

## Add the bot to your testing server

Scroll up, and find the "Generate OAuth2 URL" option. Click on it, and copy the link in the box that it generates for
you. Open it in a new browser tab, and add the bot to your server.

![App operations section](https://dl.dropboxusercontent.com/s/kjwgorjweimc8kh/vivaldi_2018-03-22_11-01-00.png)

![OAuth URL generator](https://dl.dropboxusercontent.com/s/k5oyvw1gowk00l1/vivaldi_2018-03-22_11-01-44.png)

![Bot addition page](https://dl.dropboxusercontent.com/s/33e7vit8kj0un58/vivaldi_2018-03-22_11-02-19.png)

![Server with bot joined](https://dl.dropboxusercontent.com/s/tm9fxgefi60rql8/DiscordCanary_2018-03-22_11-03-08.png)

## Save the bot token

In your copy of the repository, create a `.env` file. Do not try to push this file to GitHub - keep it on your machine.

Back on your application page, scroll down to the bot section. Reveal your bot token, and copy it.

Open your `.env` file, and add the following text to it, where `YOUR_TOKEN` is the bot token you got from the page.

```dotenv
BOT_TOKEN=YOUR_TOKEN
```

Share this token with the rest of your team, so that they can also fill out their `.env` file.

![Revealing the token](https://dl.dropboxusercontent.com/s/wjepk3okf8dvqmu/vivaldi_2018-03-22_11-06-22.png)

![Copying the token](https://dl.dropboxusercontent.com/s/859ut0jlm2xybly/vivaldi_2018-03-22_11-06-59.png)

![Filling out the .env file](https://dl.dropboxusercontent.com/s/28zqnrht21toawl/pycharm64_2018-03-22_11-07-35.png)

## Test your bot

Now that everything is set up, test your bot. Open a terminal in your copy of the repository, and run 
`pipenv sync --dev`, and then `pipenv run run.py`.

![Running the bot](https://dl.dropboxusercontent.com/s/mp4o5wptliczp7c/Hyper_2018-03-22_11-17-23.png)

![Bot is online](https://dl.dropboxusercontent.com/s/fanw68x5meoat2a/DiscordCanary_2018-03-22_11-11-54.png)

Press `CTRL+C` at any time to stop the bot, and use `pipenv run run.py` to start it again. You should do this whenever
you've edited the code and want to test it.

---

That's all there is to it! If you get stuck, don't be afraid to ask for help on the server - but please do take a stab 
at this yourself first!
