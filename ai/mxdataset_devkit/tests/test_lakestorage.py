# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package
import unittest
import os  # noqa: F401

from mxdataset.lakestorage import LakeStorage


class TestLakestorage(unittest.TestCase):
    lakestore = LakeStorage(
        "mxdataset",
        "main",
        "http://192.168.70.202:30495/api/v1",
        None,
        None)

    # def test_branch(self):
    #     self.lakestore.create_branch("test", "main")
    #     bs = self.lakestore.list_branches()
    #     self.assertTrue("test" in bs)

    #     self.lakestore.delete_branch("test")
    #     bs = self.lakestore.list_branches()
    #     self.assertTrue("test" not in bs)

    # def test_tag(self):
    #     self.lakestore.create_tag("test", "main")
    #     tags = self.lakestore.list_tags()
    #     self.assertTrue("test" in tags)

    #     self.lakestore.delete_tag("test")
    #     tags = self.lakestore.list_tags()
    #     self.assertTrue("test" not in tags)

    # def test_object(self):
    #     with open("./lakefs_test.txt", "w") as f:
    #         f.write("Test lakefs.")
    #     self.lakestore.upload2stage(
    #         "lakefs_test.txt", "./lakefs_test.txt", "main")
    #     objs = self.lakestore.list_objects("main", "lakefs_test")
    #     self.assertTrue("lakefs_test.txt" in objs)
    #     os.remove("./lakefs_test.txt")

    #     self.lakestore.download(
    #         "lakefs_test.txt", "./lakefs_test_.txt", "main")
    #     self.assertTrue(os.path.exists("./lakefs_test_.txt"))
    #     os.remove("./lakefs_test_.txt")

    #     self.lakestore.delete_objects(["lakefs_test.txt"], "main")
    #     objs = self.lakestore.list_objects("main", "lakefs_test")
    #     self.assertTrue("lakefs_test.txt" not in objs)


if __name__ == '__main__':
    unittest.main()


# EOF
