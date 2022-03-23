# Google Calendar APIs

Google has detailed [documents](https://developers.google.com/calendar/api) on Google Calendar APIs. To use these APIs, first install the Google client library

```shell
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

One motivation of SNOW is to run it directly on your personal computer, instead of an additional server managed by a third party. Thus, one may view SNOW as a service with a single user (i.e. you).

To use SNOW, there are two authentications to take care of:

1. Before SNOW can access any Google APIs and retrieve user data, SNOW must prove to Google that it's really SNOW, not some malicious applications that pretend to be SNOW. This authentication is to prove your identity as the *developer* of SNOW.

2. The user then must grant SNOW access to the user's data on Google. This authentication is to prove your identity as the *user* of SNOW.

For authentication (1), one must create a project for SNOW, within which then create [credentials](https://developers.google.com/workspace/guides/create-credentials#desktop-app) and enables Google Calendar APIs.

For authentication (2), SNOW will prompt a window to ask for Google Calendar read-only access permission. Google may show a warning that "Google hasn't verified this app", because you haven't submitted SNOW to Google for verification. It's okay and just click **Continue**. Ideally, you only need to do it once, and SNOW will refresh the token automatically. Sometimes it may fail to refresh and require you to retry login.

Click the toggle list below for step-by-step help.

<details>
<summary>Create a project</summary>

  1. Open [Google Cloud Console - APIs & Services](https://console.cloud.google.com/apis).

  2. At the top-left, click **Select a project**.

  3. At the top-right corner of the popped window, click **NEW PROJECT**.

  4. In the "Project name" field, type "SNOW". Then click **CREATE**.

  You then have a project named "SNOW" created. Before the following step, make sure you select "SNOW" as the project you are working on.

  Then we need to configure the project.

  1. Open [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent).

  2. In "User Type", select **External**. Then click **CREATE**.

  3. In "App information - App name", type "SNOW". Fill in the rest of necessary fields and click **SAVE AND CONTINUE**.

  4. Click **ADD OR REMOVE SCOPES**. In "Manually add scopes", type "https://www.googleapis.com/auth/calendar.readonly" and click **ADD TO TABLE**. Click **UPDATE**. Click **SAVE AND CONTINUE**.

  5. In "Test users", click **ADD USERS**. Type your own Gmail and click **ADD**. Click **SAVE AND CONTINUE**.

  6. In "Summary" page, click **BACK TO DASHBOARD**.

  Now you have finished configuring your project!
</details>

<details>
<summary>Create credentials</summary>

  The official [document](https://developers.google.com/workspace/guides/create-credentials#desktop-app) has detailed instructions on how to create credentials. Below is a simplified version.

  1. Open [Google Cloud Console - APIs & Services - Credential](https://console.cloud.google.com/apis/credentials).
  2. Click **Create Credentials** > **OAuth client ID**.
  3. Click **Application type** > **Desktop app**.
  4. In the "Name" field, type a name for the credential. This name is only shown in the Cloud Console.
  5. Click **Create**. The OAuth client created screen appears, showing your new Client ID and Client secret.
  6. Click **OK**. The newly created credential appears under "OAuth 2.0 Client IDs."

  After the steps above, you will be provided the credentials (client ID and client secret). Download them as a JSON file.
</details>

<details>
<summary>Enable Google Calendar APIs</summary>

  This is very similar to the step above.

  1. Open the [Google Cloud Console - APIs & Services - Enabled APIs & services](https://console.cloud.google.com/apis/dashboard).
  2. At the top, **ENABLE APIS AND SERVICES**.
  3. Search "Google Calendar API". Click the search result and enable it.

</details>
