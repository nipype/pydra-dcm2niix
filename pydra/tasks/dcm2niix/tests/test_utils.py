import os
from pydra.tasks.dcm2niix.utils import Dcm2Niix
from fileformats.medimage import DicomDir


def test_dcm2niix():
    task = Dcm2Niix()
    task.in_dir = DicomDir.mock("test-data/test_dicoms")
    task.out_dir = "test-data"
    task.compress = "y"
    assert (
        task.cmdline
        == f"dcm2niix -b y -z y -f out_file -o test-data {os.getcwd()}/test-data/test_dicoms"
    )
