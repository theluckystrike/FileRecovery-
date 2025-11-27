# Patient Records SFTP Extractor

Extract medical records from AWS SFTP server and organize by patient name.

## Status: PENDING AUTHENTICATION

Waiting for SFTP credentials (password or SSH key) from data provider.

## SFTP Connection Details
- **Server**: s-e3199fe687574abf9.server.transfer.us-east-2.amazonaws.com
- **Username**: premierliposuction_user1
- **Auth**: Pending (need password or SSH key)

## Files

| File | Description |
|------|-------------|
| `extract_patient_records.py` | Main extraction script |
| `README.md` | This file |

## Data Sources (Local)
- `~/Downloads/PatientDocuments.csv` - 80,079 document records with SFTP paths
- `~/Downloads/File Recovery  Kenn/` - Additional CSV files (appointments, invoices, etc.)

## Usage

Once you have the password:

```bash
python3 extract_patient_records.py
```

The script will:
1. Parse PatientDocuments.csv
2. Connect to SFTP with password
3. Download files to `~/Desktop/PatientRecords/LastName, FirstName/`

## Test Configuration

Currently set to test with Patient ID 1 (Test, Patricia - 68 documents).

To change test patients, edit `TEST_PATIENT_IDS` in the script:
```python
TEST_PATIENT_IDS = {1}  # Single patient test
TEST_PATIENT_IDS = {1, 2}  # Two patients
TEST_PATIENT_IDS = None  # All patients (full extraction)
```

## Requirements

```bash
pip3 install paramiko
```

## Next Steps

1. Obtain SFTP password or SSH key from MyPatientNOW/data provider
2. Run test extraction with 1-2 patients
3. Verify downloads
4. Run full extraction (~80,000 files, ~4,107 patients)
