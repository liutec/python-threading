#!/usr/bin/env python -u

use_multiprocessing = True
use_manager_queue = False

if use_multiprocessing:
    from multiprocessing import Process as Thread, Event, Lock, Manager
    if use_manager_queue:
        Queue = Manager().Queue
    else:
        from Queue import Queue
else:
    from threading import Thread, Event, Lock
    from Queue import Queue

import sys
from random import random
from time import sleep
from Queue import Empty as QueueEmpty

stdout_lock = Lock()

def debug_log(line):
    stdout_lock.acquire()
    sys.stdout.write(line + '\n')
    stdout_lock.release()

class MyThread(Thread):
    def __init__(self, queue, num):
        super(MyThread, self).__init__()
        debug_log('Thread %d: init' % num)
        self.num = num
        self.queue = queue
        self.stopped = Event()

    def run(self):
        debug_log('Thread %d: started' % self.num)
        iterations = 0
        while not self.stopped.is_set():
            try:
                message = self.queue.get(True, 0.1)
                rand_wait = random()*3
                debug_log('Thread %d: got message %s. Waiting %.2f sec' % (self.num, message, rand_wait))
                sleep(rand_wait)
            except (KeyboardInterrupt, SystemExit):
                debug_log('\nThread %d: received keyboard interrupt or system exit' % self.num)
            except IOError:
                debug_log('\nThread %d: Queue went away' % self.num)
            except QueueEmpty:
                pass  # get(True, 0.1) will wait for 0.1 seconds before raising QueueEmpty
        print('Thread %d: stopped' % self.num)
        if not use_manager_queue:
            sleep(1)  # prevent Exception in thread QueueFeederThread (most likely raised during interpreter shutdown)


def main(num_threads=4, num_messages=100):
    if use_multiprocessing:
        debug_log('Using multiprocessing')
    else:
        debug_log('Using threading')

    threads = []
    queue = Queue()

    debug_log('\nCreating %d threads' % num_threads)

    for i in range(num_threads):
        t = MyThread(queue, i+1)
        threads.append(t)

    debug_log('\nPublishing %d messages' % num_messages)
    for i in range(num_messages):
        queue.put('<%d>' % (i+1))

    debug_log('\nStarting threads')

    for thread in threads:
        thread.start()

    debug_log('\nWaiting for threads to finish')

    may_interrupt = True
    while True:
        keep_waiting = False
        for thread in threads:
            try:
                if thread.is_alive():
                    keep_waiting = True
                    thread.join(0.1)
            except (KeyboardInterrupt, SystemExit):
                keep_waiting = True
                if may_interrupt:
                    debug_log('\nMain Process: Received keyboard interrupt, stopping threads')
                    for thread in threads:
                        thread.stopped.set()
                    debug_log('\nWaiting for threads to stop themselves')
                    may_interrupt = False
        if not keep_waiting:
            break

    debug_log('\nFinished\n')
    sys.stdout.flush()


if __name__ == "__main__":
    main()
