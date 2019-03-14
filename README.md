# dicom_anonymous_tool
Python code to read DICOMDIR and create anonymous file mapping

### Installation
No need to install

### Package Requirement
* python3.x+
* pydicom

### RUN EXAMPLE
1. Parse DICOMDIR and create mapping file (also remove sensitive fields)
```python
python make_anonymous.py --dicomdir_path PATH_TO_FOLDER_WITH_DICOMDIR
```
It will create a 
* anonymous_mapping.csv (file)：info that should be keep by maintainer (ex. doctor)
* anonymous (folder)
--patient_ids
	-- parsed folder with dicom files

2. Fast copy relative folders
Because program will parse all files that can be scaned by DICOMDIR, irrelative folders will not need to dump for clients.
Maintainer can open the `anonymous_mapping.csv` and change the flag of "select" (first column) from 0 -> 1. and run the `fast_movefolder.py`
<NOTE> dicom files can be viewed with imageJ. Maintainer should check required images of folders and mark them in the anonymous_mapping.csv.
```python
python fast_movefolder.py --dicomdir_path PATH_TO_FOLDER_WITH_DICOMDIR
```
It will create a new folder `convert` that contains folders that been selected.

Finally, give the `convert` to people who needs it and keep the anonymous_mapping.csv.