#!/usr/bin/env python -u

use_multiprocessing = True

if use_multiprocessing:
    from multiprocessing import Process as Thread, Event, Lock
else:
    from threading import Thread, Event, Lock

import sys
from random import random
from time import sleep

stdout_lock = Lock()

def debug_log(line):
    stdout_lock.acquire()
    sys.stdout.write(line + '\n')
    stdout_lock.release()

class MyThread(Thread):
    def __init__(self, num):
        super(MyThread, self).__init__()
        debug_log('Thread %d: init' % num)
        self.num = num
        self.stopped = Event()

    def run(self):
        debug_log('Thread %d: started' % self.num)
        iterations = 0
        while not self.stopped.is_set():
            debug_log('Thread %d: I am running for %d iterations' % (self.num, iterations))
            iterations += 1
            try:
                sleep(random()*0.5)
                debug_log('Thread %d: I finished sleeping' % self.num)
            except (KeyboardInterrupt, SystemExit):
                debug_log('\nThread %d: received keyboard interrupt or system exit' % self.num)
                pass
        print('Thread %d: stopped' % self.num)


def main(num_threads=4):
    if use_multiprocessing:
        debug_log('Using multiprocessing')
    else:
        debug_log('Using threading')

    threads = []

    debug_log('\nCreating %d threads' % num_threads)

    for i in range(num_threads):
        t = MyThread(i+1)
        threads.append(t)

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
