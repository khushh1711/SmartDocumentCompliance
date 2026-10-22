import os
import time
import shutil
import requests
import csv
from datetime import datetime


INCOMING_FOLDER = "../contracts/incoming"
PROCESSED_FOLDER = "../contracts/processed"
REPORT_FOLDER = "../contracts/reports"

API_URL = "http://127.0.0.1:8000/upload"

LOG_FILE = "../contracts/processing_log.csv"


def create_log_file():

    if not os.path.exists(LOG_FILE):

        with open(
            LOG_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "Date",
                "Time",
                "Contract",
                "Compliance Score",
                "Risk Level",
                "Status"
            ])


def write_log(
    filename,
    score,
    risk,
    status
):

    now = datetime.now()

    with open(
        LOG_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            now.strftime("%Y-%m-%d"),
            now.strftime("%H:%M:%S"),
            filename,
            score,
            risk,
            status
        ])


def process_contract(file_path):

    filename = os.path.basename(file_path)

    print()
    print("=" * 55)
    print("NEW CONTRACT DETECTED")
    print("=" * 55)

    print(f"File: {filename}")

    try:

        with open(file_path, "rb") as file:

            response = requests.post(
                API_URL,
                files={
                    "file": (
                        filename,
                        file,
                        "application/octet-stream"
                    )
                }
            )

        if response.status_code == 200:

            result = response.json()

            score = result["compliance_score"]
            risk = result["risk_level"]
            report = result["report"]


            print()
            print("✓ Contract analyzed successfully")

            print(
                f"Compliance Score: {score}%"
            )

            print(
                f"Risk Level: {risk}"
            )


            # Move contract

            destination = os.path.join(
                PROCESSED_FOLDER,
                filename
            )

            shutil.move(
                file_path,
                destination
            )

            print(
                f"✓ Contract moved to processed/"
            )


            # Move report

            backend_report = os.path.join(
                "../output",
                report
            )

            report_destination = os.path.join(
                REPORT_FOLDER,
                report
            )


            if os.path.exists(
                backend_report
            ):

                shutil.move(
                    backend_report,
                    report_destination
                )

                print(
                    "✓ Compliance report moved to reports/"
                )

            else:

                print(
                    "⚠ Report file not found"
                )


            # Write log

            write_log(
                filename,
                score,
                risk,
                "Completed"
            )

            print(
                "✓ Processing log updated"
            )

            print()
            print("PROCESSING COMPLETE")
            print("=" * 55)


        else:

            print()
            print("✗ Analysis failed")

            print(response.text)

            write_log(
                filename,
                "",
                "",
                "Failed"
            )


    except Exception as e:

        print()
        print("✗ Automation error:")
        print(e)

        write_log(
            filename,
            "",
            "",
            "Error"
        )


def monitor_folder():

    print("=" * 55)
    print("SMART DOCUMENT AUTOMATION BOT")
    print("=" * 55)

    print()

    print(
        "Monitoring folder:"
    )

    print(
        os.path.abspath(
            INCOMING_FOLDER
        )
    )

    print()

    print(
        "Status: RUNNING"
    )

    print(
        "Waiting for new contracts..."
    )


    while True:

        files = os.listdir(
            INCOMING_FOLDER
        )

        for filename in files:

            file_path = os.path.join(
                INCOMING_FOLDER,
                filename
            )

            if os.path.isfile(
                file_path
            ):

                if filename.lower().endswith(
                    (".pdf", ".docx")
                ):

                    process_contract(
                        file_path
                    )

        time.sleep(3)


if __name__ == "__main__":

    os.makedirs(
        INCOMING_FOLDER,
        exist_ok=True
    )

    os.makedirs(
        PROCESSED_FOLDER,
        exist_ok=True
    )

    os.makedirs(
        REPORT_FOLDER,
        exist_ok=True
    )

    create_log_file()

    monitor_folder()