import attrs
from pathlib import Path
from pydra.engine.specs import ShellDef, ShellOutputs
from fileformats.generic import File, Directory
from pydra.design import shell


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
            if len(neighbours) == 1 and file_postfix is attrs.NOTHING:
                fpath = neighbours[0]
            else:
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


@shell.define
class Dcm2Niix(ShellDef["Dcm2Niix.Outputs"]):
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

    executable = "dcm2niix"

    in_dir: Directory = shell.arg(
        argstr="'{in_dir}'",
        position=-1,
        help=("The directory containing the DICOMs to be converted"),
    )
    out_dir: Path = shell.arg(
        argstr="-o '{out_dir}'",
        help="output directory",
    )
    filename: str = shell.arg(
        argstr="-f '{filename}'",
        help="The output name for the file",
        default="out_file",
    )
    file_postfix: str = shell.arg(
        help=(
            "The postfix appended to the output filename. Used to select which "
            "of the disambiguated nifti files created by dcm2niix to return "
            "in this field (see https://github.com/"
            "rordenlab/dcm2niix/blob/master/FILENAMING.md"
            "#file-name-post-fixes-image-disambiguation). Set to None to skip "
            "matching a single file (out_file will be set to attrs.NOTHING if the "
            "base path without postfixes doesn't exist) and handle the list of "
            "output files returned in 'out_files' instead."
        ),
    )
    compress: str = shell.arg(
        argstr="-z {compress}",
        allowed_values=("y", "o", "i", "n", "3"),
        help=(
            "gz compress images  [y=pigz, o=optimal pigz, "
            "i=internal:miniz, n=no, 3=no,3D]"
        ),
    )
    compression_level: int = shell.arg(
        argstr="-{compression_level}",
        allowed_values=tuple(range(1, 10)),
        help="gz compression level ",
    )
    adjacent: str = shell.arg(argstr="-a {adjacent}", help="adjacent DICOMs ")
    bids: str = shell.arg(
        argstr="-b {bids}",
        allowed_values=("y", "n", "o"),
        help="BIDS sidecar  [o=only: no NIfTI]",
    )
    anonymize_bids: str = shell.arg(
        argstr="-ba {anonymize_bids}",
        allowed_values=("y", "n"),
        help="anonymize BIDS ",
    )
    store_comments: bool = shell.arg(
        argstr="-c", help="comment stored in NIfTI aux_file "
    )
    search_depth: int = shell.arg(
        argstr="-d {search_depth}",
        help=(
            "directory search depth. Convert DICOMs in " "sub-folders of " "in_folder? "
        ),
    )
    export_nrrd: str = shell.arg(
        argstr="-e {export_nrrd}",
        allowed_values=("y", "n"),
        help="export as NRRD instead of NIfTI ",
    )
    generate_defaults: str = shell.arg(
        argstr="-g {generate_defaults}",
        allowed_values=("y", "n", "o", "i"),
        help=(
            "generate defaults file  [o=only: reset and write "
            "defaults; i=ignore: reset defaults]"
        ),
    )
    ignore_derived: str = shell.arg(
        argstr="-i {ignore_derived}",
        allowed_values=("y", "n"),
        help="ignore derived, localizer and 2D images ",
    )
    losslessly_scale: str = shell.arg(
        argstr="-l {losslessly_scale}",
        allowed_values=("y", "n", "o"),
        help=(
            "losslessly scale 16-bit integers to use dynamic range "
            "[yes=scale, no=no, but uint16->int16, o=original]"
        ),
    )
    merge_2d: int = shell.arg(
        argstr="-m {merge_2d}",
        allowed_values=("y", "n", "0", "1", "2"),
        help=(
            "merge 2D slices from same series regardless of echo, "
            "exposure, etc.  no, yes, auto"
        ),
    )
    only: int = shell.arg(
        argstr="-n {only}",
        help=("only convert this series CRC number - can be used up " "to 16 times"),
    )
    philips_scaling: str = shell.arg(
        argstr="-p {philips_scaling}",
        help="Philips precise float (not display) scaling",
    )
    rename_instead: str = shell.arg(
        argstr="-r {rename_instead}",
        allowed_values=("y", "n"),
        help="rename instead of convert DICOMs ",
    )
    single_file_mode: str = shell.arg(
        argstr="-s {single_file_mode}",
        allowed_values=("y", "n"),
        help=("single file mode, do not convert other images in " "folder "),
    )
    private_text_notes: str = shell.arg(
        argstr="-t {private_text_notes}",
        allowed_values=("y", "n"),
        help=("text notes includes private patient details"),
    )
    up_to_date_check: bool = shell.arg(argstr="-u", help="up-to-date check")
    verbose: str = shell.arg(
        argstr="-v {verbose}",
        allowed_values=("y", "n", "0", "1", "2"),
        help="verbose  no, yes, logorrheic",
    )
    name_conflicts: int = shell.arg(
        argstr="-w {name_conflicts}",
        allowed_values=tuple(range(3)),
        help=(
            "write behavior for name conflicts "
            "[0=skip duplicates, 1=overwrite, 2=add suffix]"
        ),
    )
    crop_3d: str = shell.arg(
        argstr="-x {crop_3d}",
        allowed_values=("y", "n", "i"),
        help=(
            "crop 3D acquisitions (use ignore to neither crop nor "
            "rotate 3D acquistions)"
        ),
    )
    big_endian: str = shell.arg(
        argstr="--big-endian {big_endian}",
        allowed_values=("y", "n", "o"),
        help="byte order  [y=big-end, n=little-end, o=optimal/native]",
    )
    progress: str = shell.arg(
        argstr="--progress {progress}",
        allowed_values=("y", "n"),
        help="Slicer format progress information ",
    )
    terse: bool = shell.arg(argstr="--terse", help="omit filename post-fixes ")
    version: bool = shell.arg(argstr="--version", help="report version")
    xml: bool = shell.arg(argstr="--xml", help="Slicer format features")

    class Outputs(ShellOutputs):
        out_file: File = shell.out(
            help=(
                "output NIfTI image. If multiple nifti files are created (e.g. for "
                "different echoes), then the 'file_postfix' input can be provided to "
                "select which of them is considered the 'out_file'. Otherwise it "
                "should be set to None and 'out_files' used instead (in which case "
                "'out_file' will be set to attrs.NOTHING)",
            ),
            callable=dcm2niix_out_file,
        )
        out_json: File = shell.out(
            help="output BIDS side-car JSON corresponding to 'out_file'",
            # requires=[("bids", 'y')],  FIXME: should be either 'y' or 'o'
            callable=dcm2niix_out_json,
        )
        out_bval: File = shell.outarg(
            help="output dMRI b-values in FSL format",
            path_template="{out_dir}/{filename}.bval",
        )
        out_bvec: File = shell.outarg(
            help="output dMRI b-bectors in FSL format",
            path_template="{out_dir}/{filename}.bvec",
        )
        out_files: list[File] = shell.out(
            help=(
                "all output files in a list, including files disambiguated "
                "by their suffixes (e.g. echoes, phase-maps, etc... see "
                "https://github.com/rordenlab/dcm2niix/blob/master/FILENAMING.md"
            ),
            callable=dcm2niix_out_files,
        )
