import os
import sys
import string
import requests
from Queue import Queue
import multiprocessing

loop = string.ascii_lowercase
site = ""
pool = ''
pool_size = 512

class WorkerPool:
    def __init__(self, capacity, target, args=(), kwargs={}):
        self.capacity = capacity
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.queue = Queue(capacity)
        self.queue = multiprocessing.Queue(capacity)
        self.workers = []

        for i in range(capacity):
            worker = multiprocessing.Process(target=handle_work,
                                                      args=(self.queue, self.target,))
            self.workers.append(worker)
            worker.start()

    def get_queue(self):
        return self.queue

    def get_workers(self):
        return self.workers

    def submit(self, work):
        self.queue.put(work)

def handle_work(queue, target):
        while True:
            work = queue.get()
            if work == "quit":
                return
            else:
                target(work)

def check_site(url_req):
    try:
        r = requests.get(url_req)
        if r.status_code == 200:
            if len(r.text) > 1000:
                print "Sucess: " + url_req
    except Exception, e:
        pass

def check_site_ext(ext):
    global site, pool
    url_req = site + ext
    pool.submit(url_req)

def check_sites_loop2(c):
    for c1 in loop:
        for c2 in loop:
            ext = "%s%s%s" % (c, c1, c2)
            check_site_ext(ext)

def check_sites_loop3():
    for c in loop:
        check_sites_loop2(c)

def kill_threads():
    for i in range(pool_size):
        pool.submit("quit")

def print_usage(p):
    print "Usage: python %s <http or https> <site name>" % p
    print "Sample: python %s http google" % p
    print "Sample: python %s https google" % p

if __name__ == "__main__":
    l = len(sys.argv)
    if l < 3:
        print_usage(sys.argv[0])
        exit(0)
    site = sys.argv[1] + "://" + sys.argv[2] + "."
    if "http" not in site:
        print_usage()
        exit(0)
    print "Successful domains for the site name with more than 1000 bytes will appear in the result"
    pool = WorkerPool(capacity=pool_size, target=check_site)
    if l == 3 or (l == 4 and (sys.argv[3] == "2" or sys.argv[3] == 23)):
        check_sites_loop2("")
    if l == 3 or (l == 4 and (sys.argv[3] == "3" or sys.argv[3] == 23)):
        check_sites_loop3()
    kill_threads()
    threads = pool.get_workers()
    for t in threads:
        t.join()
