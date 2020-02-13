# -*- coding: utf-8 -*-

__author__ = 'Grzegorz Latuszek'
__copyright__ = 'Copyright (C) 2020, Nokia'
__email__ = 'grzegorz.latuszek@nokia.com'

import gc

import pytest


class Subscriber(object):
    def __init__(self):
        self.received_data = []

    def on_new_data(self, data):
        self.received_data.append(data)


def test_doesnt_subscribe_same_subscriber_twice():
    from moler.publisher import Publisher

    observer = Subscriber()
    notifier = Publisher()

    notifier.subscribe(subscriber=observer.on_new_data)
    notifier.subscribe(subscriber=observer.on_new_data)

    notifier.notify_subscribers(data=b"incoming data")

    assert len(observer.received_data) == 1


def test_can_notify_multiple_subscribers_about_data():
    from moler.publisher import Publisher

    observer1 = Subscriber()
    observer2 = Subscriber()
    notifier = Publisher()

    notifier.subscribe(subscriber=observer1.on_new_data)
    notifier.subscribe(subscriber=observer2.on_new_data)

    notifier.notify_subscribers(data=b"incoming data")

    assert b"incoming data" in observer1.received_data
    assert b"incoming data" in observer2.received_data


def test_notifies_only_subscribed_ones_about_data():
    from moler.publisher import Publisher

    observer1 = Subscriber()
    observer2 = Subscriber()
    observer3 = Subscriber()
    notifier = Publisher()

    notifier.subscribe(subscriber=observer1.on_new_data)
    notifier.subscribe(subscriber=observer2.on_new_data)

    notifier.notify_subscribers(data=b"incoming data")

    assert b"incoming data" in observer1.received_data
    assert b"incoming data" in observer2.received_data
    assert b"incoming data" not in observer3.received_data  # that one was not subscribed


def test_notified_subscriber_may_stop_subscription():
    from moler.publisher import Publisher

    notifier = Publisher()
    received_data = []

    def one_time_observer(data):
        received_data.append(data)
        notifier.unsubscribe(subscriber=one_time_observer)

    notifier.subscribe(subscriber=one_time_observer)

    notifier.notify_subscribers(data=b"data 1")
    notifier.notify_subscribers(data=b"data 2")

    assert b"data 1" in received_data
    assert b"data 2" not in received_data  # because of unsubscription during notification


def test_exception_in_subscriber_doesnt_break_publisher_nor_other_subscribers():
    from moler.publisher import Publisher

    notifier = Publisher()
    received_data = []

    def failing_observer(data):
        raise Exception("Fail inside observer")

    def one_time_observer(data):
        received_data.append(data)
        notifier.unsubscribe(subscriber=one_time_observer)

    notifier.subscribe(subscriber=failing_observer)
    notifier.subscribe(subscriber=one_time_observer)

    notifier.notify_subscribers(data=b"data 1")

    notifier.unsubscribe(subscriber=failing_observer)

    assert b"data 1" in received_data


def test_repeated_unsubscription_does_nothing_but_logs_warning():
    """
    Because of possible different concurrency models (and their races)
    we don't want to raise exception when there is already
    "no such subscription" - just put warning to logs
    """
    from moler.publisher import Publisher

    notifier = Publisher()
    received_data = []

    def one_time_observer(data):
        received_data.append(data)
        notifier.unsubscribe(subscriber=one_time_observer)

    notifier.subscribe(subscriber=one_time_observer)

    notifier.notify_subscribers(data=b"data 1")
    notifier.unsubscribe(subscriber=one_time_observer)
    # TODO: check warning in logs (when we set logging system)
    notifier.notify_subscribers(data=b"data 2")

    assert b"data 1" in received_data
    assert b"data 2" not in received_data  # because of unsubscription during notification


def test_single_unsubscription_doesnt_impact_other_subscribers():
    from moler.publisher import Publisher

    observer1 = Subscriber()
    observer2 = Subscriber()

    function_received_data = []

    def raw_fun1(data):
        function_received_data.append(data)

    def raw_fun2(data):
        function_received_data.append(data)

    class TheCallableClass(object):
        def __init__(self):
            self.received_data = []

        def __call__(self, data):
            self.received_data.append(data)

    callable1 = TheCallableClass()
    callable2 = TheCallableClass()

    notifier = Publisher()
    notifier.subscribe(subscriber=observer1.on_new_data)
    notifier.subscribe(subscriber=observer2.on_new_data)
    notifier.subscribe(subscriber=observer2.on_new_data)
    notifier.unsubscribe(subscriber=observer1.on_new_data)
    notifier.unsubscribe(subscriber=observer1.on_new_data)

    notifier.subscribe(subscriber=raw_fun1)
    notifier.subscribe(subscriber=raw_fun2)
    notifier.subscribe(subscriber=raw_fun2)
    notifier.unsubscribe(subscriber=raw_fun1)

    notifier.subscribe(subscriber=callable1)
    notifier.subscribe(subscriber=callable2)
    notifier.subscribe(subscriber=callable2)
    notifier.unsubscribe(subscriber=callable1)

    notifier.notify_subscribers("incoming data")

    assert observer1.received_data == []
    assert observer2.received_data == ["incoming data"]

    assert function_received_data == ["incoming data"]

    assert callable1.received_data == []
    assert callable2.received_data == ["incoming data"]


def test_subscription_doesnt_block_subscriber_to_be_garbage_collected():
    from moler.publisher import Publisher

    notifier = Publisher()
    garbage_collected_subscribers = []

    class GcSubscriber(object):
        def __del__(self):
            garbage_collected_subscribers.append('Subscriber')

    subscr = GcSubscriber()
    notifier.subscribe(subscr)

    del subscr
    gc.collect()

    assert 'Subscriber' in garbage_collected_subscribers


def test_garbage_collected_subscriber_is_not_notified():
    from moler.publisher import Publisher

    notifier = Publisher()
    received_data = []

    class GcSubscriber(object):
        def __call__(self, data):
            received_data.append(data)

    subscr1 = GcSubscriber()
    subscr2 = GcSubscriber()
    notifier.subscribe(subscriber=subscr1)
    notifier.subscribe(subscriber=subscr2)

    del subscr1
    gc.collect()

    notifier.notify_subscribers("data")
    assert len(received_data) == 1
