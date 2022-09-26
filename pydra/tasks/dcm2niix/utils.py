import attrs
from pathlib import Path
from pydra import ShellCommandTask
from pydra.engine.specs import ShellSpec, ShellOutSpec, File, Directory, SpecInfo


def out_file_path(out_dir, filename, file_postfix, ext):
    """Attempting to handle the different suffixes that are appended to filenames
    created by Dcm2niix (see https://github.com/rordenlab/dcm2niix/blob/master/FILENAMING.md)
    """

    fpath = Path(out_dir) / (filename + (file_postfix if file_postfix else "") + ext)
    fpath = fpath.absolute()

    # Check to see if multiple echos exist in the DICOM dataset
    if not fpath.exists():
        if file_postfix is not None:  # NB: doesn't match attrs.NOTHING
            neighbours = [
                str(p) for p in fpath.parent.iterdir() if p.name.endswith(ext)
            ]
            raise ValueError(
                f"\nDid not find expected file '{fpath}' (file_postfix={file_postfix}) "
                "after DICOM -> NIfTI conversion, please see "
                "https://github.com/rordenlab/dcm2niix/blob/master/FILENAMING.md for the "
                "list of postfixes that dcm2niix produces and provide an appropriate "
                "postfix, or set postfix to None to ignore matching a single file and use "
                "the list returned in 'out_files' instead. Found the following files "
                "with matching extensions:\n" + "\n".join(neighbours)
            )
        else:
            fpath = attrs.NOTHING  # Did not find output path and

    return fpath


def dcm2niix_out_file(out_dir, filename, file_postfix, compress):

    ext = ".nii"
    # If compressed, append the zip extension
    if compress in ("y", "o", "i"):
        ext += ".gz"

    return out_file_path(out_dir, filename, file_postfix, ext)


def dcm2niix_out_json(out_dir, filename, file_postfix, bids):
    # Append echo number of NIfTI echo to select is provided
    if bids is attrs.NOTHING or bids in ("y", "o"):
        fpath = out_file_path(out_dir, filename, file_postfix, ".json")
    else:
        fpath = attrs.NOTHING
    return fpath


def dcm2niix_out_files(out_dir, filename):
    return [
        str(p.absolute())
        for p in Path(out_dir).iterdir()
        if p.name.startswith(filename)
    ]


input_fields = [
    (
        "in_dir",
        Directory,
        {
            "argstr": "'{in_dir}'",
            "position": -1,
            "help_string": ("The directory containing the DICOMs to be converted"),
            "mandatory": True,
        },
    ),
    (
        "out_dir",
        Directory,
        {
            "argstr": "-o '{out_dir}'",
            "help_string": "output directory",
            "mandatory": True,
        },
    ),
    (
        "filename",
        str,
        "out_file",
        {"argstr": "-f '{filename}'", "help_string": "The output name for the file"},
    ),
    (
        "file_postfix",
        str,
        {
            "help_string": (
                "The postfix appended to the output filename. Used to select which "
                "of the disambiguated nifti files created by dcm2niix to return "
                "in this field (see https://github.com/"
                "rordenlab/dcm2niix/blob/master/FILENAMING.md"
                "#file-name-post-fixes-image-disambiguation). Set to None to skip "
                "matching a single file (out_file will be set to attrs.NOTHING if the "
                "base path without postfixes doesn't exist) and handle the list of "
                "output files returned in 'out_files' instead."
            ),
        },
    ),
    (
        "compress",
        str,
        # "n",
        {
            "argstr": "-z {compress}",
            "allowed_values": ("y", "o", "i", "n", "3"),
            "help_string": (
                "gz compress images  [y=pigz, o=optimal pigz, "
                "i=internal:miniz, n=no, 3=no,3D]"
            ),
        },
    ),
    (
        "compression_level",
        int,
        # 6,
        {
            "argstr": "-{compression_level}",
            "allowed_values": tuple(range(1, 10)),
            "help_string": "gz compression level ",
        },
    ),
    (
        "adjacent",
        str,
        # "n",
        {"argstr": "-a {adjacent}", "help_string": "adjacent DICOMs "},
    ),
    (
        "bids",
        str,
        # "y",
        {
            "argstr": "-b {bids}",
            "allowed_values": ("y", "n", "o"),
            "help_string": "BIDS sidecar  [o=only: no NIfTI]",
        },
    ),
    (
        "anonymize_bids",
        str,
        # "y",
        {
            "argstr": "-ba {anonymize_bids}",
            "allowed_values": ("y", "n"),
            "help_string": "anonymize BIDS ",
        },
    ),
    (
        "store_comments",
        bool,
        {"argstr": "-c", "help_string": "comment stored in NIfTI aux_file "},
    ),
    (
        "search_depth",
        int,
        # 5,
        {
            "argstr": "-d {search_depth}",
            "help_string": (
                "directory search depth. Convert DICOMs in "
                "sub-folders of "
                "in_folder? "
            ),
        },
    ),
    (
        "export_nrrd",
        str,
        # "n",
        {
            "argstr": "-e {export_nrrd}",
            "allowed_values": ("y", "n"),
            "help_string": "export as NRRD instead of NIfTI ",
        },
    ),
    (
        "generate_defaults",
        str,
        # "n",
        {
            "argstr": "-g {generate_defaults}",
            "allowed_values": ("y", "n", "o", "i"),
            "help_string": (
                "generate defaults file  [o=only: reset and write "
                "defaults; i=ignore: reset defaults]"
            ),
        },
    ),
    (
        "ignore_derived",
        str,
        # "n",
        {
            "argstr": "-i {ignore_derived}",
            "allowed_values": ("y", "n"),
            "help_string": "ignore derived, localizer and 2D images ",
        },
    ),
    (
        "losslessly_scale",
        str,
        # "n",
        {
            "argstr": "-l {losslessly_scale}",
            "allowed_values": ("y", "n", "o"),
            "help_string": (
                "losslessly scale 16-bit integers to use dynamic range "
                "[yes=scale, no=no, but uint16->int16, o=original]"
            ),
        },
    ),
    (
        "merge_2d",
        int,
        # 2,
        {
            "argstr": "-m {merge_2d}",
            "allowed_values": ("y", "n", "0", "1", "2"),
            "help_string": (
                "merge 2D slices from same series regardless of echo, "
                "exposure, etc.  no, yes, auto"
            ),
        },
    ),
    (
        "only",
        int,
        {
            "argstr": "-n {only}",
            "help_string": (
                "only convert this series CRC number - can be used up " "to 16 times"
            ),
        },
    ),
    (
        "philips_scaling",
        str,
        # "y",
        {
            "argstr": "-p {philips_scaling}",
            "help_string": "Philips precise float (not display) scaling",
        },
    ),
    (
        "rename_instead",
        str,
        # "n",
        {
            "argstr": "-r {rename_instead}",
            "allowed_values": ("y", "n"),
            "help_string": "rename instead of convert DICOMs ",
        },
    ),
    (
        "single_file_mode",
        str,
        # "n",
        {
            "argstr": "-s {single_file_mode}",
            "allowed_values": ("y", "n"),
            "help_string": (
                "single file mode, do not convert other images in " "folder "
            ),
        },
    ),
    (
        "private_text_notes",
        str,
        # "n",
        {
            "argstr": "-t {private_text_notes}",
            "allowed_values": ("y", "n"),
            "help_string": ("text notes includes private patient details"),
        },
    ),
    ("up_to_date_check", bool, {"argstr": "-u", "help_string": "up-to-date check"}),
    (
        "verbose",
        str,
        # "0",
        {
            "argstr": "-v {verbose}",
            "allowed_values": ("y", "n", "0", "1", "2"),
            "help_string": "verbose  no, yes, logorrheic",
        },
    ),
    (
        "name_conflicts",
        int,
        # 2,
        {
            "argstr": "-w {name_conflicts}",
            "allowed_values": tuple(range(3)),
            "help_string": (
                "write behavior for name conflicts "
                "[0=skip duplicates, 1=overwrite, 2=add suffix]"
            ),
        },
    ),
    (
        "crop_3d",
        str,
        # "n",
        {
            "argstr": "-x {crop_3d}",
            "allowed_values": ("y", "n", "i"),
            "help_string": (
                "crop 3D acquisitions (use ignore to neither crop nor "
                "rotate 3D acquistions)"
            ),
        },
    ),
    (
        "big_endian",
        str,
        # "o",
        {
            "argstr": "--big-endian {big_endian}",
            "allowed_values": ("y", "n", "o"),
            "help_string": "byte order  [y=big-end, n=little-end, o=optimal/native]",
        },
    ),
    (
        "progress",
        str,
        # "n",
        {
            "argstr": "--progress {progress}",
            "allowed_values": ("y", "n"),
            "help_string": "Slicer format progress information ",
        },
    ),
    ("terse", bool, {"argstr": "--terse", "help_string": "omit filename post-fixes "}),
    ("version", bool, {"argstr": "--version", "help_string": "report version"}),
    ("xml", bool, {"argstr": "--xml", "help_string": "Slicer format features"}),
]

Dcm2NiixInputSpec = SpecInfo(
    name="Dcm2NiixInputs", fields=input_fields, bases=(ShellSpec,)
)


output_fields = [
    (
        "out_file",
        File,
        {
            "help_string": (
                "output NIfTI image. If multiple nifti files are created (e.g. for "
                "different echoes), then the 'file_postfix' input can be provided to "
                "select which of them is considered the 'out_file'. Otherwise it "
                "should be set to None and 'out_files' used instead (in which case "
                "'out_file' will be set to attrs.NOTHING)",
            ),
            "callable": dcm2niix_out_file,
            "mandatory": True,
        },
    ),
    (
        "out_json",
        File,
        {
            "help_string": "output BIDS side-car JSON corresponding to 'out_file'",
            # "requires": [("bids", 'y')],  FIXME: should be either 'y' or 'o'
            "callable": dcm2niix_out_json,
        },
    ),
    (
        "out_bval",
        File,
        {
            "help_string": "output dMRI b-values in FSL format",
            "output_file_template": "{out_dir}/{filename}.bval",
        },
    ),
    (
        "out_bvec",
        File,
        {
            "help_string": "output dMRI b-bectors in FSL format",
            "output_file_template": "{out_dir}/{filename}.bvec",
        },
    ),
    (
        "out_files",
        list,
        {
            "help_string": (
                "all output files in a list, including files disambiguated "
                "by their suffixes (e.g. echoes, phase-maps, etc... see "
                "https://github.com/rordenlab/dcm2niix/blob/master/FILENAMING.md"
            ),
            "callable": dcm2niix_out_files,
        },
    ),
]

Dcm2NiixOutputSpec = SpecInfo(
    name="Dcm2niixOutputs", fields=output_fields, bases=(ShellOutSpec,)
)


class Dcm2Niix(ShellCommandTask):
    """
    Example
    -------
    >>> task = Dcm2Niix()
    >>> task.inputs.in_dir = "test-data/test_dicoms"
    >>> task.inputs.out_dir = "test-data"
    >>> task.inputs.compress = "y"
    >>> task.cmdline
    'dcm2niix -o test-data -f out_file -z y test-data/test_dicoms'
    """

    input_spec = Dcm2NiixInputSpec
    output_spec = Dcm2NiixOutputSpec
    executable = "dcm2niix"
