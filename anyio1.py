#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 10 02:17:27 2021

@author: jamaj
"""

from anyio import TASK_STATUS_IGNORED, create_task_group, connect_tcp, create_tcp_listener, run
from anyio.abc import TaskStatus
from aioconsole import ainput


async def handler(stream):
    lexit = False
    while not lexit:
        text = await stream.receive(512)
        text = text.decode('utf8') 
        lexit = (text == "exit")
        print(text)
    print("Exit from handler()")
    return 

async def start_some_service(port: int, *, task_status: TaskStatus = TASK_STATUS_IGNORED):
    async with await create_tcp_listener(local_host='127.0.0.1', local_port=port) as listener:
        task_status.started()
        print('awaiting listener...')
        await listener.serve(handler)
    print("Exit from start_some_service()")


async def main():
    lexit = False
    print("Entering main()")
    async with create_task_group() as tg:
        await tg.start(start_some_service, 4000)
        async with await connect_tcp('127.0.0.1', 4000) as stream:
            while not lexit:
                text = await ainput("")
                lexit = (text == "exit")
                await stream.send(text.encode('utf8'))
            print("Exit from loop main()")
            await stream.aclose()
            await tg.cancel_scope.cancel()
    print("Exit from main()")
            

run(main)
print("end of run(main)")
