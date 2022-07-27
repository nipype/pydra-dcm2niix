from pydra.tasks.dcm2niix.utils import Dcm2Niix


def test_dcm2niix():
    task = Dcm2Niix()
    task.inputs.in_dir = "test-data/test_dicoms"
    task.inputs.out_dir = "test-data"
    task.inputs.compress = "y"
    assert (
        task.cmdline == "dcm2niix -o test-data -f out_file -z y test-data/test_dicoms"
    )
