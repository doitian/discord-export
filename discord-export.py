#!/usr/bin/env python3
import os
import sys
import argparse
import requests
import re
import textwrap
from datetime import datetime
from urllib.parse import urlparse

ESCAPE_RE = re.compile(r'[\[\]]')
SCRUB_RE = re.compile(r'[\u2028]')
MENTION_RE = re.compile(r'<@([\d]+)>')


def escape_text(text):
    return re.sub(ESCAPE_RE, r'\\\g<0>', text)


def scrub_text(text):
    return re.sub(SCRUB_RE, '', text)


def indent_text(text, prefix):
    if text != '':
        return textwrap.indent(text, prefix)

    return ''


def format_one_embed(embed):
    lines = []

    if 'title' in embed:
        if 'url' in embed:
            title = f'[**{escape_text(embed["title"])}**]({embed["url"]})'
        else:
            title = f'**{escape_text(embed["title"])}**'
        lines.append(f'    > {title}')
    elif 'url' in embed:
        lines.append(f'    > <{embed["url"]}>')

    if 'description' in embed and embed['description'].strip() != '':
        if len(lines) > 0:
            lines.append('    >')
        lines.append(indent_text(scrub_text(embed['description']), "    > "))
    if 'thumbnail' in embed:
        lines.append("    >")
        lines.append(f'    > ![]({embed["thumbnail"]["proxy_url"]})')
    return "\n".join(lines)


def format_embeds(embeds):
    if len(embeds) > 0:
        return "\n" + "\n\n".join(map(format_one_embed, embeds)) + "\n"

    return ""


def format_attachments(attachments):
    lines = []

    for attachment in attachments:
        if attachment.get('width') is not None:
            lines.append(f'   ![]({attachment["proxy_url"]})')
        else:
            lines.append(
                f'   [{attachment["name"]}]({attachment["proxy_url"]})')

    if len(lines) > 0:
        lines.append("")

    return "\n".join(lines)


def handle_user_mentions(text, mentions):
    def repl(match):
        if match.group(1) in mentions:
            return f'@{mentions[match.group(1)]}'
        else:
            return match.group(0)
    return re.sub(MENTION_RE, repl, text)


def format_date(isodate):
    return datetime.fromisoformat(isodate).strftime('%c')


def format_one_message(message):
    indexed_mentions = {}
    for mention in message['mentions']:
        indexed_mentions[mention['id']] = mention['username']
    embeds = format_embeds(message['embeds'])
    attachments = format_attachments(message['attachments'])

    if 'referenced_message' in message:
        reply_to_user = message['referenced_message']['author']['username']
        shorten_text = textwrap.shorten(scrub_text(message['referenced_message']['content']), width=32, placeholder="...")
        reply_to = f'    > r @{reply_to_user}: {shorten_text}\n'
    else:
        reply_to = ''

    return "\n".join([
        f'- **{message["author"]["username"]}** ({format_date(message["timestamp"])}): ',
        reply_to,
        indent_text(scrub_text(handle_user_mentions(
            message['content'], indexed_mentions)), "    "),
        embeds,
        attachments
    ])


parser = argparse.ArgumentParser(
    description='Export Discord Messages')
parser.add_argument('url', metavar='URL',
                    help='Discord Message URL')
parser.add_argument('--context', choices=['around', 'after', 'before'], default='around',
                    help='How to fetch messages relative to the specified message')
parser.add_argument('--limit', metavar='N', type=int, default=11, choices=range(1, 101),
                    help='Number of messages to export')

args = parser.parse_args()
url = urlparse(args.url)
guild_id, channel_id, message_id = url.path.split('/')[2:]

messages_json = requests.get(f'https://discordapp.com/api/v9/channels/{channel_id}/messages?limit={args.limit}&{args.context}={message_id}', headers={
    'Authorization': os.environ['DISCORD_USER_TOKEN']
}).json()
if 'code' in messages_json:
    print(messages_json, file=sys.stderr)
    sys.exit(127)

messages = list(map(format_one_message, reversed(messages_json)))

print(f'[※ Open Thread in Discord]({args.url})\n\n' + "\n".join(messages))
