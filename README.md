Patient Records SFTP Extractor
==============================

A custom-built utility that automates the retrieval of medical records from the MyPatientNOW cloud storage system. Instead of manually downloading 80,000 files one by one through FileZilla, this script handles the entire process automatically and organizes everything into patient folders.


The Problem
-----------

Medical records are stored on a remote SFTP server in a flat structure organized by date, not by patient. A single patient's documents might be scattered across hundreds of folders

    ClinicalDocuments/File/2022/0308/2.rtf
    ClinicalDocuments/File/2023/0510/15257.rtf
    ClinicalDocumentsPages/2022/1005/3464_1.jpeg

This makes it nearly impossible to find all records for a specific patient. The CSV index file maps which files belong to which patient, but downloading and organizing them manually would take weeks.


How The Script Works
--------------------

Step 1 - Parse the Index

The script reads PatientDocuments.csv which contains 80,079 rows. Each row links a patient to a document on the server.

```python
def parse_csv(csv_path, patient_ids=None):
    documents = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            documents.append({
                'patient_id': int(row['Internal ID']),
                'last_name': row['Patient Last Name'].strip(),
                'first_name': row['Patient First Name'].strip(),
                'path': row['Path']
            })
    return documents
```

This function reads the CSV and extracts the patient name and file path for each document.


Step 2 - Connect to SFTP

The script establishes a secure connection to the AWS Transfer Family server using the paramiko library.

```python
def connect_sftp(password):
    transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
    transport.connect(username=SFTP_USERNAME, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    return sftp, transport
```

This creates an encrypted tunnel to the server, authenticates with the provided credentials, and returns a connection object for downloading files.


Step 3 - Download and Organize

For each patient, the script creates a folder and downloads all their documents into it.

```python
def download_documents(sftp, documents, output_dir):
    for (last_name, first_name), patient_docs in patients.items():
        folder_name = f"{last_name}, {first_name}"
        patient_dir = os.path.join(output_dir, folder_name)
        os.makedirs(patient_dir, exist_ok=True)

        for doc in patient_docs:
            remote_path = doc['path']
            filename = os.path.basename(remote_path)
            local_path = os.path.join(patient_dir, filename)
            sftp.get(remote_path, local_path)
```

This loops through each patient, creates their folder using LastName, FirstName format, then downloads each of their files from the server into that folder.


Before and After
----------------

Running the extraction transforms scattered cloud storage into organized patient folders

Before

```
Server (flat structure by date)

ClinicalDocuments/2022/0308/2.rtf
ClinicalDocuments/2022/0316/5.rtf
ClinicalDocuments/2022/0322/6.rtf
ClinicalDocuments/2022/0322/7.rtf
ClinicalDocumentsPages/2022/1005/3464.jpeg
...80,000 more files
```

After

```
Local (organized by patient)

PatientRecords/
    Test, Patricia/
        2.rtf
        5.rtf
        6.rtf
        7.rtf
        3464.jpeg
    Allred, Kristian/
        3.png
        4.rtf
    ...4,105 more patient folders
```


Data Summary
------------

    Total Documents         80,079
    Total Patients           4,107
    File Types              RTF, PDF, PNG, JPEG, EML, XML

    ClinicalDocuments/          Consent forms, PDFs, emails
    ClinicalDocumentsPages/     Scanned documents and photos


Requirements
------------

    Python 3
    paramiko library

```bash
pip3 install paramiko
```


Usage
-----

```bash
python3 extract_patient_records.py
```

The script prompts for the SFTP password, connects to the server, and downloads files into ~/Desktop/PatientRecords/


Configuration
-------------

Edit TEST_PATIENT_IDS in the script to control which patients to process

Single patient test

```python
TEST_PATIENT_IDS = {1}
```

Multiple patients

```python
TEST_PATIENT_IDS = {1, 2, 3}
```

Full extraction

```python
TEST_PATIENT_IDS = None
```


Current Status
--------------

Awaiting SFTP authentication credentials from the data provider.


Next Steps
----------

1. Obtain SFTP password or SSH key from the data provider
2. Run test extraction with one patient to verify connectivity
3. Verify downloaded files match expected content
4. Run full extraction for all 4,107 patients
