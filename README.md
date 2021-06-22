# Pydra Dcm2Niix Task

This repository contains Pydra task interface for the `dcm2niix`
DICOM to NIfTI converter tool (https://github.com/rordenlab/dcm2niix).

Part of this effort is to establish a (mostly) declarative language for describing tasks that
potentially have intricate rules for determining the availability and names from the choice of
inputs.

## Installation
```
pip install /path/to/pydra-dcm2niix/
```

### Installation for developers
```
pip install -e /path/to/pydra-dcm2niix/[dev]
```

## Basic Use

To run the `dcm2niix` task

```
from pydra.tasks.dcm2niix import Dcm2Niix

task = Dcm2Niix(in_dir='/path/to/dicom/dir', out_dir='/path/to/create/nifti/output')
result = task()
```

However, the converter task interface will typically be used as the first step within larger Pydra workflows

```
from pydra import Workflow
from pydra.tasks.dcm2niix import Dcm2Niix

my_workflow = Workflow(name='my_workflow', input_spec=['in_dicom'])

my_workflow.add(
    Dcm2Niix(name='converter', in_dir=my_workflow.lzin.in_dicom, out_dir='.'))
my_workflow.add(...)

my_workflow()
```
