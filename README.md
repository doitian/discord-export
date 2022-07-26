# Export Discord Channel Messages as Markdown

## Usage

### Get User Token

- Login Discord App in Chrome
- Open Developer Tool. Search `api` in the Network tab. Find any API request having the request header `Authorization`, copy the header value.
- Export the header value in the last step as the environment variable `DISCORD_USER_TOKEN`.

### Copy Message Link

Right click any message and copy the link, which looks like `https://discord.com/channels/123456789518408213/123456789047021571/1234567896626376714`.

### Run the Script

First install dependencies.

```
pip install -r requirements.txt
```

Then use the script `discord-export.py`.

```
./discord-export.py -h
usage: discord-export.py [-h] [--context {around,after,before}] [--limit N] URL

Export Discord Messages

positional arguments:
  URL                   Discord Message URL

optional arguments:
  -h, --help            show this help message and exit
  --context {around,after,before}
                        How to fetch messages relative to the specified message
  --limit N             Number of messages to export
```
