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

## Tutorial: Synchronize Google Calendar to Notion

Currently, SNOW has only supported synchronize Google Calendar's events to a Notion Database. Every time you create, modify, or delete an event in Google Calendar, you would see the change on Notion right after running `snow`.

The first time you start SNOW, you will be prompted for configurations such as credentials, calendars/database to synchronize, etc. Later, you only need to run a single command `snow` and it will use the previous configurations.

### Step 0: Obtain Google Calendar credentials and Notion access token

Follow the steps in [this tutorial](src/service/gcal/README.md) to get Google credentials and save them as a JSON file. This credential enables you to use Google APIs and retrieve data from Google's servers.

Follow the steps in [this tutorial](src/service/notion/README.md) to get Notion access token and save it in a file. This grants SNOW access to a Notion Database.

### Step 1: Configure SNOW

In the command-line of your desktop, run `snow`. It will ask you interactively for the configurations, which includes:

- `gcal_creds_path`: The path to the previously saved Google credentials file in step 0.

- `gcal_token_path`: The path to a Google Calendar access token. You could just leave this field blank, and later it will pop a window to ask you to login to your Google account and grant access to SNOW.

- `notion_token_path`: The path to the previously saved Notion token file in step 0.

- `cal_list`: The list of calendars to synchronize. Use commas to separate. SNOW does not support multiple calendars with the exact same name.

- `db_name`: The name of the database to synchronize events. SNOW does not support multiple databases with the same name.

- `time_min`: Synchronize events from which date. Formatted as `YYYY-MM-DD`. Default is today.

- `field_col_map`: Map Google Calendar event fields to the database columns. Currently, an event has five fields: the name of the calendar it belongs to `cal_name`, the title of this event `title`, the start and end time of this event `time`, the location of this event `location`, the description of this event `description`. Formatted as `field1:col1,field2:col2,...`.

- `col_const`: Set some columns to be some constant value for all events synchronized. This is useful when the destination database has both rows synchronized from Google Calendar and rows added manually. You can tag all rows from Google Calendar to distinguish them from manually added ones. Formatted as `col1=const1,col2=const2,...`. Optional.

- `cal_merge`: Merge all events from one calendar to another calendar when handling `cal_name` in `field_col_map`. Formatted as `cal1>cal2,cal3>cal4,...`. Optional.

### Step 2: Perform synchronization

The first time you run `snow` and finish the configurations, SNOW will get all events starting from `time_min` and send them to Notion. Later every time you have updated your Google calendars, you simply run `snow` to synchronize these updates to Notion.

### Advanced usage

In step 1, instead of configuring SNOW interactively, you could also use command-line arguments (and you only need to provide these arguments for the first time).

For example, I have three calendars ("Research", "Course", and "Work") and a database named "Schedule" (with columns "Title", "Date", "Type", "Tag", "Location", and "Description"). I want to merge "Work" into "Research" and each event is tagged with either `Research` or `Course`. Since I also add some daily tasks to the database, I would like all event rows from Google Calendar to have the "Type" field as "Event" to distinguish from other tasks I added manually to the database. I want all events from 2022-01-01 to appear in the database.

Here is the command I use to initial my synchronization:

```shell
snow --gcal_creds_path ./creds.json \
  --notion_token_path ./token \
  --cal_list Course,Research,Work \
  --db_name=Schedule \
  --field_col_map cal_name:Tag,title:Title,time:Date,location:Location,description:Description \
  --col_const Type=Event \
  --cal_merge Work\>Research
  # note for `cal_merge`, '>' must escape from shell's grammar
```

If you are interested in what SNOW is doing during synchronization, you could set environment variable `SNOW_LOG_LEVEL` to `INFO`, which will show you which events it gets from Google and what it sends to Notion:

```shell
SNOW_LOG_LEVEL=INFO snow
```

### Limitation

SNOW performs incremental synchronization i.e. it only sends what is updated on Google servers to Notion servers. This requires SNOW to maintain a mapping from Google Calendar event ID to Notion page ID on your local desktop machine so that if an event is updated on Google, SNOW could know which page to update on Notion. This means you can only have one desktop to do such synchronization. It should be fine for most users. If you change your laptop, you could simply copy your local `~/.snow` to the new desktop.

Notion APIs have a restriction that a single piece of content must not be longer than 2000 characters. SNOW has to truncate the text if it finds one exceeding the limit.
