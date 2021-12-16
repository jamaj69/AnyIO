#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 10 02:17:27 2021

@author: jamaj
"""
import sniffio
#import asyncio
import uvloop
#from trio import run
from anyio import TASK_STATUS_IGNORED, create_task_group, connect_tcp, create_tcp_listener, run
from anyio.abc import TaskStatus
from aioconsole import ainput
from tornado1 import start_tornado1
from tornado2 import start_tornado2
# from wxasync1 import main_wxasync as start_wxasync
import wx
from wxasync import AsyncBind, WxAsyncApp, StartCoroutine
from wxasync1 import SelectableFrame

class Scheduler():
    def __init__(self,tasks):
        self.tasks = tasks
    async def run(self):
        async with create_task_group() as self.tg:
            # a tcp listener task to communicate with itself.
            await self.tg.start(self.start_console_listener, 4000)
            await self.tg.start(self.start_wxasync_console, 4000)

            self.tg.start_soon(self.start_console_command, 4000)

            for task in self.tasks:
                self.tg.start_soon(task['task_func'], task['task_params'] )
            # and a tcp sender of messages

    async def handler(self,stream):
        lexit = False
        while not lexit:
            text = await stream.receive(512)
            text = text.decode('utf8') 
            lexit = (text == "exit")
            print(text)
        print("Exit from handler()")
        self.tg.cancel_scope.cancel()
        return 
    
    async def start_console_listener(self,port: int, *, task_status: TaskStatus = TASK_STATUS_IGNORED):  
        async with await create_tcp_listener(local_host='127.0.0.1', local_port=port) as listener:
            task_status.started()
            print('awaiting listener...')
            await listener.serve(self.handler)
        print("Exit from start_console_listener()")
        return
    
    async def start_console_command(self,port: int, *, task_status: TaskStatus = TASK_STATUS_IGNORED):
        lexit = False
        print("Entering connect tcp console()")
        async with await connect_tcp('127.0.0.1', 4000) as stream:
            while not lexit:
                text = await ainput("")
                lexit = (text == "exit")
                await stream.send(text.encode('utf8'))
            print("Exit from loop start_console_command()")
        return

    async def start_wxasync_console(self,params: dict, *, task_status: TaskStatus = TASK_STATUS_IGNORED):
        # see https://github.com/sirk390/wxasync
        print("Entering main_wxasync")
        app = WxAsyncApp()
        frame = SelectableFrame()
        frame.Show(True)
        app.SetTopWindow(frame)
        task_status.started()

        await app.MainLoop()


async def main():
    print("Entering main() using %s loop"%sniffio.current_async_library())    
    # create two tasks of tornado
    
    tasks = [ 
                {'task_func': start_tornado1, 'task_params': { 'port': 3000, 'debug': True}},
                {'task_func': start_tornado2, 'task_params': { 'port': 3001, 'debug': True}},
                ]
    
    sd = Scheduler(tasks)    
    await sd.run()
    print("Exit from main()")

if __name__ == "__main__":
    run(main, backend= 'asyncio',backend_options={'use_uvloop':True, 'debug': True})
    print("end of run(main)")
