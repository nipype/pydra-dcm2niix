import attr
import typing as ty
from pydra import ShellCommandTask
from pydra.engine.specs import ShellSpec, ShellOutSpec, File, Directory


@attr.s(auto_attribs=True, kw_only=True)
class Dcm2NiixInputSpec(ShellSpec):

    in_dir: File = attr.ib(
        metadata={
            'argstr': "{in_dir}",
            'position': -1,
            'help_string': (
                "The directory containing the DICOMs to be converted")})

    out_dir: Directory = attr.ib(
        metadata={'argstr': '-o {out_dir}',
                  'help_string': (
                      'output directory (omit to save to input folder)')})

    filename: ty.Optional[bool] = attr.ib(
        default='out_file',
        metadata={'argstr': '-f {filename}',
                  'usedefault': True,
                  'help_string': (
                      r"(%a=antenna (coil) name, %b=basename, %c=comments, "
                      r"%d=description, %e=echo number, %f=folder name, %i=ID "
                      r"of patient, %j=seriesInstanceUID, %k=studyInstanceUID,"
                      r"%m=manufacturer, %n=name of patient, "
                      r"%o=mediaObjectInstanceUID, %p=protocol, %r=instance "
                      r"number, %s=series number, %t=time, %u=acquisition "
                      r"number, %v=vendor, %x=study ID; %z=sequence name; )")})    

    compression_level: ty.Optional[int] = attr.ib(
        default=6,
        metadata={'argstr': '-{compression_level}',
                  'choices': tuple(range(1, 10)),
                  'help_string': 'gz compression level '})

    adjacent: ty.Optional[str] = attr.ib(
        default='n',
        metadata={'argstr': '-a {adjacent}',
                  'help_string': 'adjacent DICOMs '})

    bids: ty.Optional[str] = attr.ib(
        default='y',
        metadata={'argstr': '-b {bids}',
                  'choices': ('y', 'n', 'o'),
                  'help_string': 'BIDS sidecar  [o=only: no NIfTI]'})

    anonymize_bids: ty.Optional[str] = attr.ib(
        default='y',
        metadata={'argstr': '-ba {anonymize_bids}',
                  'choices': ('y', 'n'),
                  'help_string': 'anonymize BIDS '})

    store_comments: ty.Optional[bool] = attr.ib(
        metadata={'argstr': '-c',
                  'help_string': 'comment stored in NIfTI aux_file '})

    search_depth: ty.Optional[int] = attr.ib(
        default=5,
        metadata={'argstr': '-d {search_depth}',
                  'help_string': (
                      'directory search depth. Convert DICOMs in '
                      'sub-folders of ' 'in_folder? ')})

    export_nrrd: ty.Optional[str] = attr.ib(
        default='n',
        metadata={'argstr': '-e {export_nrrd}',
                  'choices': ('y', 'n'),
                  'help_string': 'export as NRRD instead of NIfTI '})

    generate_defaults: ty.Optional[str] = attr.ib(
        default='n',
        metadata={'argstr': '-g {generate_defaults}',
                  'choices': ('y', 'n', 'o', 'i'),
                  'help_string': (
                      'generate defaults file  [o=only: reset and write '
                      'defaults; i=ignore: reset defaults]')})

    ignore_derived: ty.Optional[str] = attr.ib(
        default='n',
        metadata={'argstr': '-i {ignore_derived}',
                  'choices': ('y', 'n'),
                  'help_string': 'ignore derived, localizer and 2D images '})

    losslessly_scale: ty.Optional[str] = attr.ib(
        default='n',
        metadata={'argstr': '-l {losslessly_scale}',
                  'choices': ('y', 'n', 'o'),
                  'help_string': (
                      'losslessly scale 16-bit integers to use dynamic range '
                      '[yes=scale, no=no, but uint16->int16, o=original]')})

    merge_2d: ty.Optional[int] = attr.ib(
        default=2,
        metadata={'argstr': '-m {merge_2d}',
                  'choices': ('y', 'n', '0', '1', '2'),
                  'help_string': (
                      'merge 2D slices from same series regardless of echo, '
                      'exposure, etc.  no, yes, auto')})

    only: ty.Optional[int] = attr.ib(
        metadata={'argstr': '-n {only}',
                  'help_string': (
                      'only convert this series CRC number - can be used up '
                      'to 16 times')})

    philips_scaling: ty.Optional[str] = attr.ib(
        default='y',
        metadata={'argstr': '-p {philips_scaling}',
                  'help_string': 'Philips precise float (not display) scaling'})

    rename_instead: ty.Optional[str] = attr.ib(
        default='n',
        metadata={'argstr': '-r {rename_instead}',
                  'choices': ('y', 'n'),
                  'help_string': 'rename instead of convert DICOMs '})

    single_file_mode: ty.Optional[str] = attr.ib(
        default='n',
        metadata={'argstr': '-s {single_file_mode}',
                  'choices': ('y', 'n'),
                  'help_string': (
                      'single file mode, do not convert other images in '
                      'folder ')})

    private_text_notes: ty.Optional[str] = attr.ib(
        default='n',
        metadata={'argstr': '-t {private_text_notes}',
                  'choices': ('y', 'n'),
                  'help_string': (
                      'text notes includes private patient details')})

    up_to_date_check: ty.Optional[bool] = attr.ib(
        metadata={'argstr': '-u',
                  'help_string': 'up-to-date check'})

    verbose: ty.Optional[str] = attr.ib(
        default='0',
        metadata={'argstr': '-v {verbose}',
                  'choices': ('y', 'n', '0', '1', '2'),
                  'help_string': 'verbose  no, yes, logorrheic'})

    name_conflicts: ty.Optional[int] = attr.ib(
        default=2,
        metadata={'argstr': '-w {name_conflicts}',
                  'choices': tuple(range(3)),
                  'help_string': (
                      'write behavior for name conflicts '
                      '[0=skip duplicates, 1=overwrite, 2=add suffix]')})

    crop_3d: ty.Optional[str] = attr.ib(
        default='n',
        metadata={'argstr': '-x {crop_3d}',
                  'choices': ('y', 'n', 'i'),
                  'help_string': (
                      'crop 3D acquisitions (use ignore to neither crop nor '
                      'rotate 3D acquistions)')})

    compress: ty.Optional[str] = attr.ib(
        default='n',
        metadata={'argstr': '-z {compress}',
                  'choices': ('y', 'o', 'i', 'n', '3'),
                  'help_string': (
                      'gz compress images  [y=pigz, o=optimal pigz, '
                      'i=internal:miniz, n=no, 3=no,3D]')})

    big_endian: ty.Optional[str] = attr.ib(
        default='o',
        metadata={'argstr': '--big-endian {big_endian}',
                  'choices': ('y', 'n', 'o'),
                  'help_string':
                  'byte order  [y=big-end, n=little-end, o=optimal/native]'})

    progress: ty.Optional[str] = attr.ib(
        default='n',
        metadata={'argstr': '--progress {progress}',
                  'choices': ('y', 'n'),
                  'help_string': 'Slicer format progress information '})

    terse: ty.Optional[bool] = attr.ib(
        metadata={'argstr': '--terse',
                  'help_string': 'omit filename post-fixes '})

    version: ty.Optional[bool] = attr.ib(
        metadata={'argstr': '--version',
                  'help_string': 'report version'})

    xml: ty.Optional[bool] = attr.ib(
        metadata={'argstr': '--xml',
                  'help_string': 'Slicer format features'})


@attr.s(auto_attribs=True, kw_only=True)
class Dcm2NiixOutputSpec(ShellOutSpec):

    out_file: File = attr.ib(
        metadata={
            "help_string": "output NIfTI image",
            "output_file_template": "{out_dir}/{filename}.nii.gz"})

    out_json: File = attr.ib(
        metadata={
            "help_string": "output BIDS side-car JSON",
            "output_file_template": "{out_dir}/{filename}.json"})


class Dcm2Niix(ShellCommandTask):
    """
    Example
    -------
    >>> task = Dcm2Niix()
    >>> task.inputs.in_dir = "test_dicoms"
    >>> task.inputs.out_file = "test.nii.gz"
    >>> task.cmdline
    'mrconvert -f out_file -o out_dir test_dicoms'
    """
    input_spec = Dcm2NiixInputSpec
    output_spec = Dcm2NiixOutputSpec
    executable = "dcm2niix"
