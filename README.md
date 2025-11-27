Patient Records SFTP Extractor
==============================

A lightweight Python utility that connects to an AWS SFTP server, downloads medical records, and organizes them into patient folders.


Status
------

Awaiting SFTP authentication credentials from the data provider.


Connection Details
------------------

    Server      s-e3199fe687574abf9.server.transfer.us-east-2.amazonaws.com
    Username    premierliposuction_user1
    Port        22
    Auth        Password or SSH key (pending)


Data Sources
------------

The extraction script reads from local CSV index files that map document metadata to remote file paths.

    PatientDocuments.csv        80,079 records      Primary document index
    PatientAppointments.csv      7,879 records      Appointment history
    PatientCurrentMedical.csv    4,681 records      Medical information
    PatientInvoices.csv          2,689 records      Billing records
    PatientMedicalHistory.csv    8,051 records      Patient history
    PatientSurgeries.csv           521 records      Surgery records
    PatientTreatments.csv            2 records      Treatment images


Before and After
----------------

The raw CSV contains document paths scattered across the SFTP server.

Before

```
ClinicalDocuments/File/2022/0308/2.rtf
ClinicalDocuments/File/2022/0316/5.rtf
ClinicalDocumentsPages/2022/1005/3464_1.jpeg
ClinicalDocuments/File/2022/1005/3465.pdf
```

After running the extraction, files are organized by patient name.

After

```
PatientRecords/
    Test, Patricia/
        2.rtf
        5.rtf
        3464_1.jpeg
        3465.pdf
    Allred, Kristian/
        3_1.png
        4.rtf
        9.rtf
```


Installation
------------

```bash
pip3 install paramiko
```


Usage
-----

```bash
python3 extract_patient_records.py
```

The script prompts for the SFTP password, connects to the server, and downloads files into organized patient folders at ~/Desktop/PatientRecords/


Configuration
-------------

Edit the TEST_PATIENT_IDS variable in the script to control which patients to process.

Single patient test

```python
TEST_PATIENT_IDS = {1}
```

Multiple patients

```python
TEST_PATIENT_IDS = {1, 2, 3}
```

Full extraction of all patients

```python
TEST_PATIENT_IDS = None
```


Workflow
--------

1. Obtain SFTP password or SSH key from the data provider
2. Run test extraction with one patient
3. Verify downloaded files
4. Run full extraction for all 4,107 patients


Technical Notes
---------------

The script uses paramiko for SFTP connectivity. File paths are parsed from the Path column in PatientDocuments.csv. Patient folders are named using the format LastName, FirstName.

Approximately 80,000 files across two directories on the remote server

    ClinicalDocuments/          RTF consent forms, PDFs, EML emails, XML
    ClinicalDocumentsPages/     PNG and JPEG scanned documents and photos
