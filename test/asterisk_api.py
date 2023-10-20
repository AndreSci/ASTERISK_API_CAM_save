import asyncio
import aioari
from aioari import Client
from aioari.model import Channel
from contextlib import suppress
import logging
from typing import Dict


async def on_dtmf(channel: Channel, event: Dict) -> None:
    print(type(channel), type(event))
    digit = event['digit']
    if digit == '#':
        await channel.play(media='sound:goodbye')
        await channel.continueInDialplan()
    elif digit == '*':
        await channel.play(media='sound:asterisk-friend')
    else:
        await channel.play(media='sound:digits/%s' % digit)


async def on_start(objs: Dict, event: Dict, client: Client) -> None:
    channel = objs['channel']
    channel.on_event('ChannelDtmfReceived', on_dtmf)
    await channel.answer()
    await channel.play(media='sound:hello-world')


async def on_end(objs: Dict, event: Dict, client: Client) -> None:
    print('Exit from Stasis')


async def main():
    client = await aioari.connect('http://192.168.48.63:5060/', 'test', 'test_password')
    client.on_channel_event('StasisStart', on_start, client)
    client.on_channel_event('StasisEnd', on_end, client)

    try:
        await client.run(apps="hello-world")
    finally:
        await client.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    with suppress(KeyboardInterrupt):
        asyncio.run(main())
