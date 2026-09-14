# Posting thank-yous into a Google Chat space

The board can announce every thank-you in a Google Chat space as it is sent.
This is optional. Leave `var CHAT_RELAY` blank in `index.html` and nothing is posted.

## Why there is a relay in the middle

A Google Chat webhook URL is a password. Anyone who has it can post into your
space as often as they like. `index.html` is served from a public GitHub repo,
so anything written in it is readable by the whole internet.

So the board never sees the webhook. It posts to a Google Apps Script web app
instead, and that script holds the webhook and forwards the message. Only the
Apps Script URL appears in the public page, and on its own that URL can do
nothing except post a correctly shaped thank-you into your space.

Apps Script is free, runs inside your Google account, and needs no server.

## Step 1 — create the webhook in the space

1. Open the Google Chat space in a browser, not the mobile app.
2. Click the space name at the top to open the dropdown.
3. Choose **Apps & integrations**, then **Webhooks**, then **Add webhooks**.
4. Name it `Thank you Board`. An avatar URL is optional.
5. Click **Save** and copy the URL it gives you. Keep it to yourself.

If you do not see a Webhooks option, your Workspace admin has turned webhooks
off for the domain, and they will need to allow it.

## Step 2 — create the relay

1. Go to `script.google.com` and click **New project**.
2. Delete whatever is in the editor and paste the whole script below.
3. Put the webhook URL from step 1 between the quotes on the `CHAT_WEBHOOK` line.
4. Rename the project to `Thank you Board relay` so you can find it later.
5. Click **Deploy**, then **New deployment**.
6. Click the gear next to "Select type" and pick **Web app**.
7. Set **Execute as** to `Me`, and **Who has access** to `Anyone`.
8. Click **Deploy**. Google will ask you to authorise it the first time. It will
   warn that the app is not verified; that is normal for your own script. Choose
   **Advanced**, then **Go to Thank you Board relay (unsafe)**, then **Allow**.
9. Copy the **Web app URL**. It ends in `/exec`. That is the URL the board needs.

"Who has access: Anyone" sounds alarming but only means the script can be called
without a Google login, which the board needs. The script does one thing, and the
webhook stays hidden inside it.

## Step 3 — wire it into the board

Send me the `/exec` URL and I will put it in and push, or do it yourself: open
`index.html`, find the line starting `var CHAT_RELAY`, paste the URL between the
quotes, then commit and push. GitHub Pages redeploys in about a minute.

## The relay script

```javascript
// Thank you Board -> Google Chat relay
// Receives a thank-you from the board and posts it into a Chat space.
// The webhook below is a password. Keep this project private.

var CHAT_WEBHOOK = 'PASTE_THE_WEBHOOK_URL_FROM_STEP_1_HERE';
var BOARD_URL    = 'https://uplers-ai.github.io/thank-you-board/';

function doPost(e) {
  try {
    if (!e || !e.postData || !e.postData.contents) return reply({ ok: false, error: 'empty' });

    var d      = JSON.parse(e.postData.contents);
    var from   = clean(d.from, 60);
    var to     = clean(d.to, 60);
    var reason = clean(d.reason, 280);
    if (!from || !to || !reason) return reply({ ok: false, error: 'missing fields' });

    var text = '*' + from + '* thanked *' + to + '*\n' +
               '_"' + reason + '"_\n' +
               '<' + BOARD_URL + '|Thank you Board>';

    UrlFetchApp.fetch(CHAT_WEBHOOK, {
      method: 'post',
      contentType: 'application/json; charset=UTF-8',
      payload: JSON.stringify({ text: text }),
      muteHttpExceptions: true
    });

    return reply({ ok: true });
  } catch (err) {
    return reply({ ok: false, error: String(err) });
  }
}

// Strip the characters Chat treats as formatting so a reason cannot
// fake bold text, inject a link, or break the message layout.
function clean(v, max) {
  return String(v == null ? '' : v)
    .replace(/[<>*_~`]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, max);
}

function reply(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
```

## Testing it

In the Apps Script editor you cannot run `doPost` directly because it needs a
request. Paste this extra function, select it in the dropdown and press Run. A
test message should appear in the space.

```javascript
function testPost() {
  doPost({ postData: { contents: JSON.stringify({
    from: 'Test Sender', to: 'Test Receiver', reason: 'Checking the relay works.'
  }) } });
}
```

Delete `testPost` once you are happy, or leave it; it is never reachable from
the web app.

## If you change the script later

Editing the code is not enough. Click **Deploy**, then **Manage deployments**,
then the pencil icon, set **Version** to **New version**, and **Deploy**. The
`/exec` URL stays the same.

## Turning it off

Clear `var CHAT_RELAY` back to `""` in `index.html` and push. The board stops
posting immediately. You can leave the Apps Script project in place.
