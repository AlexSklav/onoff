#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       Copyright 2014 Liftoff Software Corporation
#
# For license information see LICENSE.txt

# Meta
__version__ = '1.0.1'
__version_info__ = (1, 0, 1)
__license__ = "Apache 2.0 (see LICENSE.txt)"
__author__ = 'Dan McDougall <daniel.mcdougall@liftoffsoftware.com>'

__doc__ = """\
onoff.py - A really handy way to add ``on()``, ``off()``, and ``trigger()``
styled events to any Python class.  A quick example::

    >>> from onoff import OnOffMixin
    >>> class Foo(OnOffMixin):
    ...     def __init__(self):
    ...         self.on("hello", self.hello)
    ...     def hello(self, *args):
    ...         print("Hello: %s" % args)
    ...     def test(self, *args):
    ...         self.trigger("hello", *args)
    ...
    >>> f = Foo()
    >>> f.test("Triggered events rock!")
    Hello: Triggered events rock!
"""

from typing import List, Union, Callable
import logging


class OnOffMixin:
    """
    A mixin to add :func:`on`, :func:`off`, and :func:`trigger` event handling
    methods to any class.

    For an example, let's pretend we've got a basic WebSocket server that can
    perform a number of functions based on the incoming message::

        class ActionWebSocket(WebSocketHandler):
            def open(self):
                print("WebSocket opened")

            def on_message(self, message):
                if message == 'hello':
                    self.hello()
                elif message == 'ping':
                    self.pong()

            def on_close(self):
                print("WebSocket closed")

            def pong(self, timestamp):
                self.write_message('pong')

            def hello(self):
                self.write_message('Hey there!')

    This works OK for the most simple of stuff.  We could use string parsing of
    various sorts (startswith(), json, etc) to differentiate messages from each
    other but our conditionals will quickly grow into a giant mess.

    There's a better way, using the OnOffMixin:

    .. code-block:: python

        class ActionWebSocket(WebSocketHandler, OnOffMixin):
            "Calls an appropriate 'action' based on the incoming message."
            def __init__(self, *args, **kwargs):
                super(ActionWebSocket, self).__init__(*args, **kwargs)
                self.on("ping", self.pong)      # Register a "ping" event
                self.on("hello", self.heythere) # Register a "hello" event

            def on_message(self, message):
                # Assume we're sent a json-encoded dict:
                message_obj = json.loads(message)
                # message_obj would be something like '{"eventname": <args>}'
                for key, value in message_obj.items(): # If more than one
                    self.trigger(key, value)

            def pong(self, timestamp):
                "Responds to meesages like ``{"ping": <timestamp>}``"
                self.write_message('{"pong": %s}' % timestamp)

            def heythere(self, *args):
                print("heythere() got args: %s" % args)
                for arg in args:
                    self.write_message('Hey there, %s!' % arg)

    In the above example we used the `OnOffMixin` to add :func:`on`,
    :func:`off`, and :func:`trigger` methods to our `ActionWebSocket` class.
    """

    def __init__(self):
        self._on_off_events = {}
        self.exc_info = None

    def on(self, events: Union[str, List[str]], callback: Callable, times: int = None) -> None:
        """
        Registers the given *callback* with the given *events* (string or list
        of strings) that will get called whenever the given *event* is triggered
        (using :meth:`self.trigger`).

        If *times* is given the *callback* will only be fired that many times
        before it is automatically removed from :attr:`self._on_off_events`.
        """
        if isinstance(events, str):
            events = [events]

        callback_obj = {'callback': callback, 'times': times, 'calls': 0}

        for event in events:
            self._on_off_events.setdefault(event, []).append(callback_obj.copy())

    def off(self, events: Union[str, List[str]], callback: Callable) -> None:
        """
        Removes the given *callback* from the given *events* (string or list of
        strings).
        """
        if isinstance(events, str):
            events = [events]

        for event in events:
            self._on_off_events[event] = [callback_obj for callback_obj in self._on_off_events[event]
                                          if callback_obj['callback'] != callback]

    def once(self, events: Union[str, List[str]], callback: Callable) -> None:
        """
        A shortcut for `self.on(events, callback, 1)`
        """
        self.on(events, callback, 1)

    def trigger(self, events: Union[str, List[str]], *args, **kwargs) -> None:
        """
        Fires the given *events* (string or list of strings).  All callbacks
        associated with these *events* will be called and if their respective
        objects have a *times* value set it will be used to determine when to
        remove the associated callback from the event.

        If given, callbacks associated with the given *events* will be called
        with *args* and *kwargs*.
        """
        logging.debug(f"OnOffMixin triggering event(s): {events}")

        if isinstance(events, str):
            events = [events]

        for event in events:
            if event in self._on_off_events:
                for callback_obj in self._on_off_events[event]:
                    callback_obj['callback'](*args, **kwargs)
                    callback_obj['calls'] += 1
                    if callback_obj['calls'] == callback_obj['times']:
                        self.off(event, callback_obj['callback'])
