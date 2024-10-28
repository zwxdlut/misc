import os
import time
from threading import Thread, Lock
import concurrent.futures as concurrent_

upload_count = 0


def ulthread(worker):
    return worker.run()


def upload_url(poolkey, task):
    task.lake.upload2stage(task.url, task.path, task.branch, task.timeout)
    global upload_count
    upload_count += 1
    print("[upload_url] [{}]uploaded({}): {}"
          .format(poolkey, upload_count, task.path))


class MXDatasetUploader:
    def __init__(self, root) -> None:
        self.stop = False
        self.rootdir = root
        self.uploader = Thread(target=ulthread, args=(self,))
        self.ul_waitlock = Lock()

    def __del__(self) -> None:
        pass

    def close(self):
        if self.uploader.is_alive():
            self.stop = True
            self.uploader.join()
        self.uploader = None
        self.resultset = None
        self.lakestore = None

    def set_resultset(self, resultset):
        if resultset is None:
            return False

        if self.uploader.is_alive():
            self.stop = True
            self.uploader.join()
        self.uploader = Thread(target=ulthread, args=(self,))
        self.stop = False

        self.resultset = resultset
        self.ul_waiting = []
        self.ul_running = {}
        self.ul_threadpools = {}
        self.ul_poolid = 1
        self.uploader.start()
        return True

    def run(self):
        while not self.stop:
            self.ul_waitlock.acquire()
            num_waiting = len(self.ul_waiting)
            self.ul_waitlock.release()

            # check wether in waiting status
            if num_waiting == 0:
                if len(self.ul_threadpools) == 0:
                    pass
                else:
                    time.sleep(1)
                continue

            # check running thread pools
            self.check_threadpools()

            # check wether to create new thread pool
            if (len(self.ul_running) < 10 and num_waiting > 10) \
               or len(self.ul_threadpools) == 0:
                # create a new thread pool to upload
                self.create_threadpool()

        # finish all threads
        self.ul_waitlock.acquire()
        num_waiting = len(self.ul_waiting)
        self.ul_waitlock.release()
        if 0 != num_waiting:
            self.create_threadpool()
        self.check_threadpools()

        # stop: stop all thread pools
        self.stop_threadpools()
        return True

    def upload2staging(self, lakestore, tables, branch, timeout=-1):
        global upload_count
        upload_count = 0

        for table in tables:
            isview = table[1]
            tablename = table[0]
            annotation = self.resultset.get_table(tablename, isview)
            for annrecord in annotation:
                self.ul_waitlock.acquire()
                tasks = UploadTask.get_tasks(self.rootdir, branch, annrecord)
                for task in tasks:
                    if not os.path.exists(task.path):
                        print("[MXDatasetUploader.upload2staging] "
                              "path {} not exists!".format(task.path))
                        continue
                    task.set_lake(lakestore)
                    task.set_timeout(timeout)
                    self.ul_waiting.append(task)
                num_waiting = len(self.ul_waiting)
                self.ul_waitlock.release()

                if num_waiting > 100:
                    time.sleep(num_waiting // 100)
        return

    def create_threadpool(self):
        self.ul_waitlock.acquire()
        tasks = self.ul_waiting
        self.ul_waiting = []
        self.ul_waitlock.release()

        nworker = min(10, len(tasks))
        executor = concurrent_.ThreadPoolExecutor(max_workers=nworker)
        poolkey = str(self.ul_poolid)
        self.ul_poolid += 1
        future_to_url = {}
        for task in tasks:
            if not os.path.exists(task.path):
                print("[MXDatasetUploader.create_threadpool] "
                      "path {} not exists!".format(task.path))
                continue
            if (task.path not in self.ul_running):
                future = executor.submit(upload_url, poolkey, task)
                future_to_url[future] = task
                self.ul_running[task.path] = task
        self.ul_threadpools[poolkey] = (executor, future_to_url)

    def check_threadpools(self):
        remove_pools = []
        for (key, pool) in self.ul_threadpools.items():
            # executor = pool[0]
            futures = pool[1]
            num_completed = 0
            for future in concurrent_.as_completed(futures):
                task = futures[future]
                del self.ul_running[task.path]
                num_completed += 1
                try:
                    future.result()
                except Exception as e:
                    print("[MXDatasetUploader.check_threadpools] \
                        url: {}, exception: {}".format(task.url, e))
            if num_completed == len(futures):
                remove_pools.append(key)
        for key in remove_pools:
            del self.ul_threadpools[key]

    def stop_threadpools(self):
        for (_, pool) in self.ul_threadpools:
            executor = pool[0]
            # futures = pool[1]
            executor.shutdown()
        self.ul_threadpools.clear()


class UploadTask:
    def __init__(self, url, path, zip=False) -> None:
        self.url = url
        self.path = path
        self.timeout = -1
        self.zip = zip

    def __del__(self) -> None:
        pass

    def set_lake(self, lakestore):
        self.lake = lakestore

    def set_timeout(self, timeout):
        self.timeout = timeout

    def set_branch(self, branch):
        self.branch = branch

    @staticmethod
    def get_tasks(root, branch, annrecord):
        tasks = []
        if annrecord.img_zip:
            url = os.path.join(annrecord.img_dir, annrecord.img_zip)
            path = os.path.join(root, url)
            task = UploadTask(url, path, True)
            task.set_branch(branch)
            tasks.append(task)
        elif annrecord.img_file:
            url = os.path.join(annrecord.img_dir, annrecord.img_file)
            path = os.path.join(root, url)
            task = UploadTask(url, path)
            task.set_branch(branch)
            tasks.append(task)
        if annrecord.ann_zip:
            url = os.path.join(annrecord.ann_dir, annrecord.ann_zip)
            path = os.path.join(root, url)
            task = UploadTask(url, path, True)
            task.set_branch(branch)
            tasks.append(task)
        elif annrecord.ann_file:
            url = os.path.join(annrecord.ann_dir, annrecord.ann_file)
            path = os.path.join(root, url)
            task = UploadTask(url, path)
            task.set_branch(branch)
            tasks.append(task)
        return tasks


# EOF
