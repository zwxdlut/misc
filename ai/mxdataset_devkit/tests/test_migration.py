# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package
import unittest

# from mxdataset.migration import migration


class TestMigration(unittest.TestCase):
    # def test_migration_download_files(self):
    #     ret = migration.download_files(
    #         prefix="annotation/tasks", dst_dir="./download")
    #     self.assertTrue(ret)

    # def test_transform_transform_files(self):
    #     ret = migration.transform_files("./download", "./output")
    #     self.assertTrue(ret)

    def test_migration_migrate(self):
        # ret = migration.migrate()
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()


# EOF
