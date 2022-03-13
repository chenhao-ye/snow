# Notion APIs

Notion has APIs [document](https://developers.notion.com/) published. We use [notion-sdk-py](https://github.com/ramnes/notion-sdk-py), an open-source implementation of Python client. To begin with, install `notion-sdk-pyy`.

```shell
pip install --upgrade notion-client
```

To enable SNOW to access Notion, one need to add SNOW as integration (step 1) and grant the access to a database (step 2). Below is Notion's [official tutorial](https://developers.notion.com/docs/getting-started) on these two steps.

<details>
<summary>Add SNOW as the integration</summary>

For the substep 3 below, you may use name "SNOW" instead. Additional, in "User Capabilities", choose "No user information" since we won't need your user information and it's a good idea to not grant unnecessary access.

> 1. Go to <https://www.notion.com/my-integrations>.
> 2. Click the "+ New integration" button.
> 3. Give your integration a name - I chose "Vacation Planner".
> 4. Select the workspace where you want to install this integration.
> 5. Select the capabilities that your integration will have.
> 6. Click "Submit" to create the integration.
> 7. Copy the "Internal Integration Token" on the next page and save it somewhere secure, e.g. a password manager.
>
> ![notion-add-integration](https://files.readme.io/2ec137d-093ad49-create-integration.gif)

</details>

<details>
<summary>Grant the access of a database to SNOW</summary>

> Integrations don't have access to any pages (or databases) in the workspace at first. A user must share specific pages with an integration in order for those pages to be accessed using the API. This helps keep you and your team's information in Notion secure.
> Start from a new or existing page in your workspace. Insert a new database by typing `/table` and selecting a full page table. Give it a title. I've called mine "Weekend getaway destinations". Click on the `Share` button and use the selector to find your integration by its name, then click `Invite`.
> ![notion-grant-access](https://files.readme.io/0a267dd-share-database-with-integration.gif)
> Your integration now has the requested permissions on the new database. Once an integration is added to a workspace, any member can share pages and databases with that integration - there's no requirement to be an Admin for this step.

</details>
