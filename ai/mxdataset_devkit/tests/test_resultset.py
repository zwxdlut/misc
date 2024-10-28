# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

# import os
import unittest
import mxdataset.resultset as resultset


class TestCreateResultset(unittest.TestCase):

    def test_CreateResultset(self):
        rset = resultset.CreateResultset("testResultset.db", True, True)
        self.assertTrue(rset)
        resultset.ReleaseResultset(rset)

    def test_CreateResultsetTable(self):
        rset = resultset.CreateResultset("testResultset.db", True, True)
        self.assertTrue(rset)

        rset.create_annotation("segmentation")
        annotations = rset.list_annotations()
        self.assertTrue("segmentation" in annotations)

        segmentaion = rset.get_annotation("segmentation")
        self.assertTrue(segmentaion)
        self.assertTrue(segmentaion.get_len() == 0)
        self.assertTrue(segmentaion.get_lastid() == -1)
        resultset.ReleaseResultset(rset)
        rset = None

    def test_CreateRecord(self):
        rset = resultset.CreateResultset("testResultset.db", True, True)
        self.assertTrue(rset)

        rset.create_annotation("segmentation")
        annotations = rset.list_annotations()
        self.assertTrue("segmentation" in annotations)

        segmentaion = rset.get_annotation("segmentation")
        self.assertTrue(segmentaion)
        self.assertTrue(segmentaion.get_len() == 0)
        self.assertTrue(segmentaion.get_lastid() == -1)

        record = resultset.AnnotationRecord()
        record.set_ann("/ann.zip", "/ann.file")
        record.set_img("/ann.zip", "/ann.file")
        record.set_date("")
        record.set_flag("")
        record.set_rid(None)
        record.set_valid()
        segmentaion.add_records([record])
        segmentaion.flush()
        self.assertTrue(segmentaion.get_len() == 1)
        self.assertTrue(segmentaion.check_valid())

        r0 = segmentaion.get_record(0)
        self.assertTrue(r0.id == record.id)
        self.assertTrue(r0.date == record.date)
        self.assertTrue(r0.flag == record.flag)
        self.assertTrue(r0.ann_dir == record.ann_dir)
        self.assertTrue(r0.ann_zip == record.ann_zip)
        self.assertTrue(r0.ann_file == record.ann_file)
        self.assertTrue(r0.img_dir == record.img_dir)
        self.assertTrue(r0.img_zip == record.img_zip)
        self.assertTrue(r0.img_file == record.img_file)

        resultset.ReleaseResultset(rset)
        rset = None


if __name__ == '__main__':
    unittest.main()


# EOF
