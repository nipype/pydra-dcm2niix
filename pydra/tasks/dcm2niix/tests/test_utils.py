from pydra.tasks.dcm2niix.utils import Dcm2Niix
from fileformats.medimage import DicomDir


def test_dcm2niix():
    task = Dcm2Niix()
    task.inputs.in_dir = DicomDir.mock("test-data/test_dicoms")
    task.inputs.out_dir = "test-data"
    task.inputs.compress = "y"
    assert (
        task.cmdline == "dcm2niix -o test-data -f out_file -z y test-data/test_dicoms"
    )
