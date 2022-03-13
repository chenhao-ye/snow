# SNOW

SNOW, short for SyNchronized workflOW, is an open-source tool to synchronize workflow applications, e.g. Google Calendar, Notion.

For example, you may create an event on Google Calendar and expect this event to appear on your Notion database. There have been commercial productions like [automate.io](https://automate.io/) and [Zapier](https://zapier.com/) to do such jobs, but they typically suffer from three drawbacks:

- Expensive: Deploy 20 bots can cost $19 monthly on [automate.io](https://automate.io/). It might not be a problem for many, but at least one poor graduate student was unhappy about it and decided to write some code...

- Inefficient: The typical way these bots work is: one bot periodically (~5 min for $19 pricing plan) asks Google's servers if there is anything updated on your Google Calendar; if yes, it sends such updates to Notion's servers. However, you won't really update the calendar very often, and such polling is just wasteful.

- Slow: After updating your Google Calendar, you may need to wait up to 5 min to have it synchronized to Notion. This is unpleasantly slow. You may be more willing to explicitly ask for such synchronization and expect to see the update on Notion immediately, instead of just waiting.

- Insecure: You have to trust a thirty-party to access your Google Calendar and Notion data. The trustiness includes: 1) they won't use your data for evil purposes, 2) they are smart and careful enough so that their servers won't get breached in the future.

SNOW is designed to address the problems above. Every time you update the Google Calendar, you run `snow` on your desktop, which fetches the updates from Google's servers and forwards them to Notion's servers. There is no third-party machine involved and thus, no unnecessary cost to pay and no trustiness issue to worry about.

SNOW is highly customizable. Currently, the development focuses on the synchronization between Google Calendar and Notion. If you would like to have more applications included, feel free to post an issue.

## Install

Required Python version >=3.6.

```shell
bash ./install.sh
```

This will install SNOW to `~/.snow`. You could simply remove `~/.snow` to uninstall SNOW.

After running the install script, make sure `~/.snow/bin` is in your shell's path:

```shell
echo 'export PATH="$PATH:$HOME/.snow/bin"' >> ~/.bashrc # OR ~/.zshrc
```
