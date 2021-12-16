#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 10 02:17:27 2021

@author: jamaj
"""

import wx
import time
from anyio import TASK_STATUS_IGNORED, create_task_group, connect_tcp, create_tcp_listener, run

from wxasync import AsyncBind, WxAsyncApp, StartCoroutine
import asyncio
from asyncio.events import get_event_loop
from wx.adv import TaskBarIcon, EVT_TASKBAR_LEFT_DCLICK

ASYNC_VERSION = True


class MyTaskBarIcon(TaskBarIcon):
    def __init__(self, frame):
        TaskBarIcon.__init__(self)

        self.frame = frame

        self.SetIcon(wx.Icon('favicon.ico', wx.BITMAP_TYPE_ICO))
        #------------
        
        self.Bind(wx.EVT_MENU, self.OnTaskBarActivate, id=1)
        self.Bind(wx.EVT_MENU, self.OnTaskBarDeactivate, id=2)
        self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=3)

    #-----------------------------------------------------------------------
        
    def CreatePopupMenu(self):
        menu = wx.Menu()
        menu.Append(1, 'Show')
        menu.Append(2, 'Hide')
        menu.Append(3, 'Close')

        return menu


    def OnTaskBarClose(self, event):
        if self.frame.IsShown():
            self.frame.Hide()


    def OnTaskBarActivate(self, event):
        if not self.frame.IsShown():
            self.frame.Show()


    def OnTaskBarDeactivate(self, event):
        if self.frame.IsShown():
            self.frame.Hide()



class SelectableFrame(wx.Frame):

    c1 = None
    c2 = None

    def __init__(self, parent=None, id=-1, title="Jamaj cluster hypervisor"):
        # wx.Frame.__init__(self, parent, id, title, size=wx.DisplaySize())
        wx.Frame.__init__(self, parent, id, title, size=(800,800))

        self.SetIcon(wx.Icon('favicon.ico', wx.BITMAP_TYPE_ICO))

        self.tskic = MyTaskBarIcon(self)

        self.CreateStatusBar()

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        vbox = wx.BoxSizer(wx.VERTICAL)

        button1 =  wx.Button(self, label="AsyncBind")
        vbox.Add(button1, 1, wx.EXPAND|wx.ALL)
        AsyncBind(wx.EVT_BUTTON, self.async_callback, button1)

        self.panel = wx.Panel(self, size=self.GetSize())
        
        vbox.Add(self.panel, 2, wx.EXPAND|wx.ALL)

        self.panel.Bind(wx.EVT_MOTION, self.OnMouseMove)
        self.panel.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.panel.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseRDown)
        self.panel.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.panel.Bind(wx.EVT_PAINT, self.OnPaint)

        self.SetCursor(wx.Cursor(wx.CURSOR_CROSS))

        self.SetSizer(vbox)
        self.Layout()
        self.clock_on = False       


    def OnMouseMove(self, event):
        if event.Dragging():
            self.c2 = event.GetPosition()
        self.Refresh()

    def OnMouseDown(self, event):
        self.c1 = event.GetPosition()

    def OnMouseRDown(self, event):
        self.c1 = event.GetPosition()
        if ASYNC_VERSION:
            StartCoroutine(self.update_clock, self)

    def OnMouseUp(self, event):
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        self.c2 = None  # ANDY
        print("mouse up")
        self.Refresh()

    def OnPaint(self, event):
        dc = wx.PaintDC(self.panel)
        dc.SetTextForeground((204, 102, 0))  # dark orange
        dc.DrawText("right click once to start timer", 2, 2)

        if self.c1 is None or self.c2 is None: return

        # Fun - draw crosshairs
        maxx = 2000
        maxy = 2000
        dc.SetPen(wx.Pen('BLACK', 1, wx.DOT))
        dc.SetBrush(wx.Brush("BLACK", wx.TRANSPARENT))
        dc.DrawLine(0, self.c2.y, maxx, self.c2.y)  # horizontal line
        dc.DrawLine(self.c2.x, 0, self.c2.x, maxy)  # vert line

        # Draw rubber band
        dc.SetPen(wx.Pen('red', 1, wx.SHORT_DASH))
        dc.SetBrush(wx.Brush("BLACK", wx.TRANSPARENT))
        dc.DrawRectangle(self.c1.x, self.c1.y, self.c2.x - self.c1.x, self.c2.y - self.c1.y)

    def PrintPosition(self, pos):
        return str(pos.x) + " " + str(pos.y)

    async def async_callback(self, event):
        self.SetStatusText("Button clicked")
        await asyncio.sleep(1)
        self.SetStatusText("Working")
        await asyncio.sleep(1)
        self.SetStatusText("Completed")

    async def update_clock(self):
        while True:
            self.SetStatusText(time.strftime('%H:%M:%S'))
            await asyncio.sleep(0.5)

    def OnClose(self,event):
        print("Received OnClose evet")
        self.Hide()
        # self.Iconize()

def main_wxasync(params : dict):
    # see https://github.com/sirk390/wxasync
    print("Entering main_wxasync")
    app = WxAsyncApp()
    frame = SelectableFrame()
    frame.Show(True)
    app.SetTopWindow(frame)

    app.MainLoop()

    # loop = get_event_loop()
    # loop.run_until_complete(app.MainLoop())

if __name__ == "__main__":
    main_wxasync()

        
