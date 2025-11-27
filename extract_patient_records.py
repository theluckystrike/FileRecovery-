#!/usr/bin/env python3
"""
Medical Records SFTP Extraction Script
Downloads patient documents from SFTP server and organizes by patient name.
"""

import csv
import os
import sys
import getpass
from pathlib import Path
import paramiko

# SFTP Configuration
SFTP_HOST = "s-e3199fe687574abf9.server.transfer.us-east-2.amazonaws.com"
SFTP_USERNAME = "premierliposuction_user1"
SFTP_PORT = 22

# File paths
CSV_PATH = os.path.expanduser("~/Downloads/PatientDocuments.csv")
OUTPUT_DIR = os.path.expanduser("~/Desktop/PatientRecords")

# Test patient IDs (testing with 1 patient first)
TEST_PATIENT_IDS = {1}  # Test, Patricia only


def connect_sftp(password):
    """Connect to SFTP server with password authentication."""
    print(f"Connecting to {SFTP_HOST}...")

    transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
    transport.connect(username=SFTP_USERNAME, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)

    print("Connected successfully!")
    return sftp, transport


def parse_csv(csv_path, patient_ids=None):
    """Parse PatientDocuments.csv and return list of documents to download."""
    documents = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            patient_id = int(row['Internal ID'])

            # Filter by patient IDs if specified
            if patient_ids and patient_id not in patient_ids:
                continue

            documents.append({
                'patient_id': patient_id,
                'last_name': row['Patient Last Name'].strip(),
                'first_name': row['Patient First Name'].strip(),
                'document_id': row['Document ID'],
                'description': row['Description'],
                'path': row['Path'],
                'is_active': row['IsActive']
            })

    return documents


def download_documents(sftp, documents, output_dir):
    """Download documents and organize by patient name."""
    os.makedirs(output_dir, exist_ok=True)

    success_count = 0
    error_count = 0
    errors = []

    # Group by patient for progress tracking
    patients = {}
    for doc in documents:
        key = (doc['last_name'], doc['first_name'])
        if key not in patients:
            patients[key] = []
        patients[key].append(doc)

    print(f"\nDownloading documents for {len(patients)} patients...")
    print(f"Total documents: {len(documents)}\n")

    for (last_name, first_name), patient_docs in patients.items():
        # Create patient folder: "LastName, FirstName"
        folder_name = f"{last_name}, {first_name}".strip(", ")
        patient_dir = os.path.join(output_dir, folder_name)
        os.makedirs(patient_dir, exist_ok=True)

        print(f"Processing: {folder_name} ({len(patient_docs)} documents)")

        for doc in patient_docs:
            remote_path = doc['path']
            filename = os.path.basename(remote_path)
            local_path = os.path.join(patient_dir, filename)

            try:
                sftp.get(remote_path, local_path)
                success_count += 1
                print(f"  Downloaded: {filename}")
            except Exception as e:
                error_count += 1
                error_msg = f"  ERROR: {filename} - {str(e)}"
                print(error_msg)
                errors.append({
                    'patient': folder_name,
                    'file': filename,
                    'remote_path': remote_path,
                    'error': str(e)
                })

    return success_count, error_count, errors


def main():
    print("=" * 60)
    print("Medical Records SFTP Extraction Tool")
    print("=" * 60)

    # Check if CSV exists
    if not os.path.exists(CSV_PATH):
        print(f"ERROR: CSV file not found: {CSV_PATH}")
        sys.exit(1)

    # Parse CSV for test patients
    print(f"\nParsing {CSV_PATH}...")
    documents = parse_csv(CSV_PATH, TEST_PATIENT_IDS)
    print(f"Found {len(documents)} documents for test patients (IDs: {TEST_PATIENT_IDS})")

    if not documents:
        print("No documents found for specified patient IDs")
        sys.exit(1)

    # Show summary before connecting
    patients = set((d['last_name'], d['first_name']) for d in documents)
    print("\nPatients to process:")
    for last, first in sorted(patients):
        count = sum(1 for d in documents if d['last_name'] == last and d['first_name'] == first)
        print(f"  - {last}, {first}: {count} documents")

    # Get password
    print(f"\nSFTP Server: {SFTP_HOST}")
    print(f"Username: {SFTP_USERNAME}")
    password = getpass.getpass("Password: ")

    if not password:
        print("ERROR: Password required")
        sys.exit(1)

    # Connect and download
    sftp = None
    transport = None

    try:
        sftp, transport = connect_sftp(password)

        # List root directory to verify connection
        print("\nVerifying connection - listing root directory...")
        try:
            root_contents = sftp.listdir('.')
            print(f"Root directory contents: {root_contents[:5]}..." if len(root_contents) > 5 else f"Root directory contents: {root_contents}")
        except Exception as e:
            print(f"Warning: Could not list root directory: {e}")

        # Download documents
        success, errors_count, error_list = download_documents(sftp, documents, OUTPUT_DIR)

        # Summary
        print("\n" + "=" * 60)
        print("EXTRACTION COMPLETE")
        print("=" * 60)
        print(f"Successfully downloaded: {success}")
        print(f"Errors: {errors_count}")
        print(f"Output directory: {OUTPUT_DIR}")

        if error_list:
            print("\nErrors encountered:")
            for err in error_list[:10]:  # Show first 10 errors
                print(f"  - {err['patient']}/{err['file']}: {err['error']}")
            if len(error_list) > 10:
                print(f"  ... and {len(error_list) - 10} more errors")

    except paramiko.AuthenticationException:
        print("\nERROR: Authentication failed. Please check your password.")
        sys.exit(1)
    except paramiko.SSHException as e:
        print(f"\nERROR: SSH connection failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)
    finally:
        if sftp:
            sftp.close()
        if transport:
            transport.close()
        print("\nConnection closed.")


if __name__ == "__main__":
    main()
