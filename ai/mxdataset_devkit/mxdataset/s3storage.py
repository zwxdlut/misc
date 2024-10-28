import os
import sys
import threading

import boto3


class S3Storage:
    """
    S3 storage.

    Parameters
    ----------
    url : str
        The root directory.

    access_key_id : str
        The access key id(username).

    secret_access_key : str
        The secret access key(password).

    Returns
    -------

    Attributes
    ----------

    See Also
    --------

    Examples
    --------
    Create a s3 storage accessor.

    >> s3store = S3Storage("http://192.168.70.202:32709", None, None)
    >> s3store.get_buckets()
    [{'Name': 'data1', 'CreationDate':
    datetime.datetime(2022, 4, 28, 1, 36, 37, 205000, tzinfo=tzutc())},
     {'Name': 'data2', 'CreationDate':
     datetime.datetime(2023, 8, 24, 1, 34, 51, 22000, tzinfo=tzutc())}]
    """

    def __init__(self,
                 url,
                 access_key_id=None,
                 secret_access_key=None) -> None:
        self.s3 = boto3.client(
            's3',
            endpoint_url=url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key)

    def __del__(self) -> None:
        pass

    def get_buckets(self, name=None):
        """
        Get buckets by bucket name, if name is None, get all buckets.
        """

        buckets = list()

        for bucket in self.s3.list_buckets()["Buckets"]:
            if name is None or bucket['Name'] == name:
                buckets.append(bucket)

        return buckets

    def get_objects(self, bucket_name, prefix=""):
        """
        Get objects by filter prefix path.
        """

        print("[S3Storage.get_objects] start getting files from s3")

        files = []
        objs = {'NextContinuationToken': None}

        while 'NextContinuationToken' in objs:
            if objs['NextContinuationToken']:
                objs = self.s3.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix=prefix,
                    ContinuationToken=objs['NextContinuationToken'])
            else:
                objs = self.s3.list_objects_v2(
                    Bucket=bucket_name, Prefix=prefix)

            if objs.get("Contents") is None:
                print("[S3Storage.get_objects] no object contents!")
                continue

            contents = objs["Contents"]
            print("[S3Storage.get_objects] list {} files".
                  format(len(contents)))

            for i in range(len(contents)):
                file = contents[i]['Key']
                print("[S3Storage.get_objects: {}/{}"
                      .format(bucket_name, file))
                files.append(file)

        print("[S3Storage.get_objects] get {} files".format(len(files)))

        return files

    def download_objects(self, bucket_name=None,
                         prefix="", dst_dir="./download"):
        """
        Download objects.
        """

        dst_dir = os.path.join(dst_dir, bucket_name)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

        print("[S3Storage.download_objects] start download files from s3")

        objs = {'NextContinuationToken': None}
        while 'NextContinuationToken' in objs:
            if objs['NextContinuationToken']:
                objs = self.s3.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix=prefix,
                    ContinuationToken=objs['NextContinuationToken'])
            else:
                objs = self.s3.list_objects_v2(
                    Bucket=bucket_name, Prefix=prefix)

            if objs.get("Contents") is None:
                print("[S3Storage.download_objects] no object contents!")
                continue

            contents = objs["Contents"]
            count = len(contents)
            print("[S3Storage.download_objects] list {} files".format(count))

            for i in range(count):
                file = contents[i]["Key"]
                size = contents[i]["Size"]
                index = file.rfind('/')

                if -1 != index:
                    path = os.path.join(dst_dir, file[:index])
                    if not os.path.exists(path):
                        os.makedirs(path)

                path = os.path.join(dst_dir, file)
                if os.path.isdir(path) \
                        or os.path.exists(path):
                    continue

                # print(f"download {i+1}/{count} {bucket_name}/{file}")
                s = f"[S3Storage.download_objects] download \
                    {i+1}/{count} | {bucket_name}/{file}"
                self.s3.download_file(
                    bucket_name, file, path,
                    Callback=ProgressPercentage(s, size))

        print("[S3Storage.download_objects] download files successfully")

        return True


class ProgressPercentage(object):
    def __init__(self, prefix, size) -> None:
        self.prefix = prefix
        self._size = float(size)
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __del__(self) -> None:
        pass

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s %s/%s  (%.2f%%)" % (
                    self.prefix,
                    self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()


# EOF
