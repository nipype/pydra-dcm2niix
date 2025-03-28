from pathlib import Path
import typing as ty
from fileformats.application import Json
from fileformats.medimage import DicomDir, Nifti1, NiftiGz, Bvec, Bval
from pydra.compose import shell

FS = ty.TypeVar("FS", bound=Nifti1 | NiftiGz | Json | Bval | Bvec)


def get_out_file(
    out_dir: Path,
    fileformat: ty.Type[FS],
    filename: str,
    file_postfix: str | None,
    required: bool = False,
) -> FS | None:
    """Attempting to handle the different suffixes that are appended to filenames
    created by Dcm2niix (see https://github.com/rordenlab/dcm2niix/blob/master/FILENAMING.md)
    """

    assert fileformat.ext, f"File format {fileformat} does not have an extension"

    fpath = Path(out_dir) / (
        filename + (file_postfix if file_postfix else "") + fileformat.ext
    )
    fpath = fpath.absolute()

    # Check to see if multiple echos exist in the DICOM dataset
    if fpath.exists():
        fileset = fileformat(fpath)
    else:
        if required:
            neighbours = [
                p for p in fpath.parent.iterdir() if p.name.endswith(fileformat.ext)
            ]
            if len(neighbours) == 1:
                fpath = neighbours[0]
            else:
                raise ValueError(
                    f"\nDid not find expected file '{fpath}' (file_postfix={file_postfix}) "
                    "after DICOM -> NIfTI conversion, please see "
                    "https://github.com/rordenlab/dcm2niix/blob/master/FILENAMING.md for the "
                    "list of postfixes that dcm2niix produces and provide an appropriate "
                    "postfix, or set postfix to None to ignore matching a single file and use "
                    "the list returned in 'out_files' instead. Found the following files "
                    "with matching extensions:\n"
                    + "\n".join(str(p) for p in neighbours)
                )
        else:
            fileset = None  # Did not find output path and
    return fileset


def dcm2niix_out_file(
    out_dir: Path, filename: str, file_postfix: str, compress: str
) -> Nifti1 | NiftiGz:
    fileformat: ty.Type[Nifti1 | NiftiGz] = (
        NiftiGz if compress in ("y", "o", "i") else Nifti1
    )
    return get_out_file(out_dir, fileformat, filename, file_postfix, True)  # type: ignore[return-value]


def dcm2niix_out_json(
    out_dir: Path, filename: str, file_postfix: str, bids: str
) -> Json | None:
    # Append echo number of NIfTI echo to select is provided
    if bids in ("y", "o"):
        return get_out_file(out_dir, Json, filename, file_postfix)
    return None


def dcm2niix_out_bvec(
    out_dir: Path, filename: str, file_postfix: str, bids: str
) -> Bvec | None:
    # Append echo number of NIfTI echo to select is provided
    if bids in ("y", "o"):
        return get_out_file(out_dir, Bvec, filename, file_postfix)
    return None


def dcm2niix_out_bval(
    out_dir: Path, filename: str, file_postfix: str, bids: str
) -> Bval | None:
    # Append echo number of NIfTI echo to select is provided
    if bids in ("y", "o"):
        return get_out_file(out_dir, Bval, filename, file_postfix)
    return None


def dcm2niix_out_files(out_dir: Path, filename: str) -> list[str]:
    return [
        str(p.absolute())
        for p in Path(out_dir).iterdir()
        if p.name.startswith(filename)
    ]


@shell.define
class Dcm2Niix(shell.Task["Dcm2Niix.Outputs"]):
    """
    Example
    -------
    >>> task = Dcm2Niix()
    >>> task.in_dir = "test-data/test_dicoms"
    >>> task.out_dir = "test-data"
    >>> task.compress = "y"
    >>> task.cmdline
    'dcm2niix -b y -z y -f out_file -o test-data test-data/test_dicoms'
    """

    executable = "dcm2niix"

    in_dir: DicomDir = shell.arg(
        argstr="'{in_dir}'",
        position=-1,
        help=("The directory containing the DICOMs to be converted"),
    )
    out_dir: Path | None = shell.arg(
        default=None,
        argstr="-o '{out_dir}'",
        help="output directory",
    )
    filename: str | None = shell.arg(
        argstr="-f '{filename}'",
        help="The output name for the file",
        default="out_file",
    )
    file_postfix: str | None = shell.arg(
        default=None,
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
    compress: str | None = shell.arg(
        default=None,
        argstr="-z {compress}",
        allowed_values=("y", "o", "i", "n", "3"),
        help=(
            "gz compress images  [y=pigz, o=optimal pigz, "
            "i=internal:miniz, n=no, 3=no,3D]"
        ),
    )
    compression_level: int | None = shell.arg(
        default=None,
        argstr="-{compression_level}",
        allowed_values=tuple(range(1, 10)),
        help="gz compression level ",
    )
    adjacent: str | None = shell.arg(
        default=None, argstr="-a {adjacent}", help="adjacent DICOMs "
    )
    bids: str = shell.arg(
        default="y",
        argstr="-b {bids}",
        allowed_values=("y", "n", "o"),
        help="BIDS sidecar  [o=only: no NIfTI]",
    )
    anonymize_bids: str | None = shell.arg(
        default=None,
        argstr="-ba {anonymize_bids}",
        allowed_values=("y", "n"),
        help="anonymize BIDS ",
    )
    store_comments: bool = shell.arg(
        default=False, argstr="-c", help="comment stored in NIfTI aux_file "
    )
    search_depth: int | None = shell.arg(
        default=None,
        argstr="-d {search_depth}",
        help=(
            "directory search depth. Convert DICOMs in " "sub-folders of " "in_folder? "
        ),
    )
    export_nrrd: str | None = shell.arg(
        default=None,
        argstr="-e {export_nrrd}",
        allowed_values=("y", "n"),
        help="export as NRRD instead of NIfTI ",
    )
    generate_defaults: str | None = shell.arg(
        default=None,
        argstr="-g {generate_defaults}",
        allowed_values=("y", "n", "o", "i"),
        help=(
            "generate defaults file  [o=only: reset and write "
            "defaults; i=ignore: reset defaults]"
        ),
    )
    ignore_derived: str | None = shell.arg(
        default=None,
        argstr="-i {ignore_derived}",
        allowed_values=("y", "n"),
        help="ignore derived, localizer and 2D images ",
    )
    losslessly_scale: str | None = shell.arg(
        default=None,
        argstr="-l {losslessly_scale}",
        allowed_values=("y", "n", "o"),
        help=(
            "losslessly scale 16-bit integers to use dynamic range "
            "[yes=scale, no=no, but uint16->int16, o=original]"
        ),
    )
    merge_2d: int | None = shell.arg(
        default=None,
        argstr="-m {merge_2d}",
        allowed_values=("y", "n", "0", "1", "2"),
        help=(
            "merge 2D slices from same series regardless of echo, "
            "exposure, etc.  no, yes, auto"
        ),
    )
    only: int | None = shell.arg(
        default=None,
        argstr="-n {only}",
        help=("only convert this series CRC number - can be used up " "to 16 times"),
    )
    philips_scaling: str | None = shell.arg(
        default=None,
        argstr="-p {philips_scaling}",
        help="Philips precise float (not display) scaling",
    )
    rename_instead: str | None = shell.arg(
        default=None,
        argstr="-r {rename_instead}",
        allowed_values=("y", "n"),
        help="rename instead of convert DICOMs ",
    )
    single_file_mode: str | None = shell.arg(
        default=None,
        argstr="-s {single_file_mode}",
        allowed_values=("y", "n"),
        help=("single file mode, do not convert other images in " "folder "),
    )
    private_text_notes: str | None = shell.arg(
        default=None,
        argstr="-t {private_text_notes}",
        allowed_values=("y", "n"),
        help=("text notes includes private patient details"),
    )
    up_to_date_check: bool = shell.arg(
        default=False, argstr="-u", help="up-to-date check"
    )
    verbose: str | None = shell.arg(
        default=None,
        argstr="-v {verbose}",
        allowed_values=("y", "n", "0", "1", "2"),
        help="verbose  no, yes, logorrheic",
    )
    name_conflicts: int | None = shell.arg(
        default=None,
        argstr="-w {name_conflicts}",
        allowed_values=tuple(range(3)),
        help=(
            "write behavior for name conflicts "
            "[0=skip duplicates, 1=overwrite, 2=add suffix]"
        ),
    )
    crop_3d: str | None = shell.arg(
        default=None,
        argstr="-x {crop_3d}",
        allowed_values=("y", "n", "i"),
        help=(
            "crop 3D acquisitions (use ignore to neither crop nor "
            "rotate 3D acquistions)"
        ),
    )
    big_endian: str | None = shell.arg(
        default=None,
        argstr="--big-endian {big_endian}",
        allowed_values=("y", "n", "o"),
        help="byte order  [y=big-end, n=little-end, o=optimal/native]",
    )
    progress: str | None = shell.arg(
        default=None,
        argstr="--progress {progress}",
        allowed_values=("y", "n"),
        help="Slicer format progress information ",
    )
    terse: bool = shell.arg(
        default=False, argstr="--terse", help="omit filename post-fixes "
    )
    version: bool = shell.arg(default=False, argstr="--version", help="report version")
    xml: bool = shell.arg(default=False, argstr="--xml", help="Slicer format features")

    class Outputs(shell.Outputs):
        out_file: Nifti1 | NiftiGz = shell.out(
            help=(
                "output NIfTI image. If multiple nifti files are created (e.g. for "
                "different echoes), then the 'file_postfix' input can be provided to "
                "select which of them is considered the 'out_file'. Otherwise it "
                "should be set to None and 'out_files' used instead (in which case "
                "'out_file' will be set to attrs.NOTHING)",
            ),
            callable=dcm2niix_out_file,
        )
        out_json: Json | None = shell.out(
            help="output BIDS side-car JSON corresponding to 'out_file'",
            # requires=[("bids", "y")],  # FIXME: should be either 'y' or 'o'
            callable=dcm2niix_out_json,
        )
        out_bval: Bval | None = shell.out(
            help="output dMRI b-values in FSL format",
            # requires=[("bids", "y")],  # FIXME: should be either 'y' or 'o'
            callable=dcm2niix_out_bval,
        )
        out_bvec: Bvec | None = shell.out(
            help="output dMRI b-bectors in FSL format",
            # requires=[("bids", "y")],  # FIXME: should be either 'y' or 'o'
            callable=dcm2niix_out_bvec,
        )
        out_files: list[Nifti1 | NiftiGz | Json | Bval | Bvec] = shell.out(
            help=(
                "all output files in a list, including files disambiguated "
                "by their suffixes (e.g. echoes, phase-maps, etc... see "
                "https://github.com/rordenlab/dcm2niix/blob/master/FILENAMING.md"
            ),
            callable=dcm2niix_out_files,
        )
