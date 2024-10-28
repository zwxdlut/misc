import os
import time
from threading import Thread, Lock
import concurrent.futures as concurrent_

download_count = 0


def dlthread(worker):
    return worker.run()


def download_url(poolkey, task):
    # tmppath = "/tmp/mxdataset_" + poolkey
    # if not os.path.exists(tmppath):
    #     os.makedirs(tmppath)
    task.lake.download(task.url, task.path, task.branch, task.timeout)
    # shutil.move(task.path, tmppath)
    if task.zip:
        dir = os.path.dirname(task.path)
        os.system("unzip " + task.path + " -d " + dir)
    global download_count
    download_count += 1
    print("[MXDatasetDownloader.download_url] [{}]downloaded({}): {}"
          .format(poolkey, download_count, task.path))


class MXDatasetDownloader:
    def __init__(self, root) -> None:
        self.stop = False
        self.rootdir = root
        self.downloader = Thread(target=dlthread, args=(self,))
        self.dl_waitlock = Lock()

    def __del__(self) -> None:
        pass

    def close(self):
        if self.downloader.is_alive():
            self.stop = True
            self.downloader.join()
        self.downloader = None
        self.resultset = None
        self.lakestore = None

    def set_resultset(self, resultset):
        if resultset is None:
            return False

        if self.downloader.is_alive():
            self.stop = True
            self.downloader.join()
        self.downloader = Thread(target=dlthread, args=(self,))
        self.stop = False

        self.resultset = resultset
        self.dl_waiting = []
        self.dl_running = {}
        self.dl_threadpools = {}
        self.dl_poolid = 1
        self.downloader.start()
        return True

    def set_branch(self, branch):
        self.branchroot = branch

    def run(self):
        while not self.stop:
            self.dl_waitlock.acquire()
            num_waiting = len(self.dl_waiting)
            self.dl_waitlock.release()

            # check wether in waiting status
            if num_waiting == 0:
                if len(self.dl_threadpools) == 0:
                    pass
                else:
                    time.sleep(1)
                continue

            # check running thread pools
            self.check_threadpools()

            # check wether to create new thread pool
            if (len(self.dl_running) < 10 and num_waiting > 10) \
               or len(self.dl_threadpools) == 0:
                # create a new thread pool to download
                self.create_threadpool()

        # finish all threads
        self.dl_waitlock.acquire()
        num_waiting = len(self.dl_waiting)
        self.dl_waitlock.release()
        if 0 != num_waiting:
            self.create_threadpool()
        self.check_threadpools()

        # stop: stop all thread pools
        self.stop_threadpools()
        return True

    def download(self, lakestore, timeout=-1):
        global download_count
        download_count = 0

        for ann_cls in self.resultset.list_annotations():
            annotation = self.resultset.get_annotation(ann_cls)
            for annrecord in annotation:
                self.dl_waitlock.acquire()
                tasks = DownloadTask.get_tasks(self.rootdir,
                                               self.branchroot,
                                               annrecord)
                for task in tasks:
                    if not os.path.exists(task.path):
                        task.set_lake(lakestore)
                        task.set_timeout(timeout)
                        self.dl_waiting.append(task)
                num_waiting = len(self.dl_waiting)
                self.dl_waitlock.release()

                if num_waiting > 100:
                    time.sleep(num_waiting // 100)
        return

    def create_threadpool(self):
        self.dl_waitlock.acquire()
        tasks = self.dl_waiting
        self.dl_waiting = []
        self.dl_waitlock.release()

        nworker = min(10, len(tasks))
        executor = concurrent_.ThreadPoolExecutor(max_workers=nworker)
        poolkey = str(self.dl_poolid)
        self.dl_poolid += 1
        future_to_url = {}
        for task in tasks:
            if (not os.path.exists(task.path)) \
               and (task.url not in self.dl_running):
                future = executor.submit(download_url, poolkey, task)
                future_to_url[future] = task
                self.dl_running[task.url] = task
        self.dl_threadpools[poolkey] = (executor, future_to_url)

    def check_threadpools(self):
        remove_pools = []
        for (key, pool) in self.dl_threadpools.items():
            # executor = pool[0]
            futures = pool[1]
            num_completed = 0
            for future in concurrent_.as_completed(futures):
                task = futures[future]
                del self.dl_running[task.url]
                num_completed += 1
                try:
                    future.result()
                except Exception as e:
                    print("[MXDatasetDownloader.check_threadpools] \
                        url: {}, exception: {}".format(task.url, e))
            if num_completed == len(futures):
                remove_pools.append(key)
        for key in remove_pools:
            del self.dl_threadpools[key]

    def stop_threadpools(self):
        for (_, pool) in self.dl_threadpools.items():
            executor = pool[0]
            # futures = pool[1]
            executor.shutdown()
        self.dl_threadpools.clear()


class DownloadTask:
    def __init__(self, url, path, zip=False) -> None:
        self.url = url
        self.path = path
        self.timeout = -1
        self.zip = zip

        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            os.makedirs(dir)

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
        branchroot = os.path.join(root, branch)
        if annrecord.img_zip:
            url = os.path.join(annrecord.img_dir, annrecord.img_zip)
            path = os.path.join(root, url)
            task = DownloadTask(url, path, True)
            task.set_branch(branch)
            tasks.append(task)
        elif annrecord.img_file:
            url = os.path.join(annrecord.img_dir, annrecord.img_file)
            path = os.path.join(root, url)
            task = DownloadTask(url, path)
            task.set_branch(branch)
            tasks.append(task)
        if annrecord.ann_zip:
            url = os.path.join(annrecord.ann_dir, annrecord.ann_zip)
            path = os.path.join(branchroot, url)
            task = DownloadTask(url, path, True)
            task.set_branch(branch)
            tasks.append(task)
        elif annrecord.ann_file:
            url = os.path.join(annrecord.ann_dir, annrecord.ann_file)
            path = os.path.join(branchroot, url)
            task = DownloadTask(url, path)
            task.set_branch(branch)
            tasks.append(task)
        return tasks


# EOF
