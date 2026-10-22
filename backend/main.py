from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import re
from pypdf import PdfReader
from docx import Document
from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

app = FastAPI(title="Smart Document Compliance Checker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

INPUT_DIR = Path("../input")
INPUT_DIR.mkdir(exist_ok=True)


# -----------------------------
# Clause Rules
# -----------------------------

CLAUSE_RULES = {
    "Confidentiality": [
        [
            "confidential",
            "confidentiality",
            "non-disclosure",
            "proprietary information",
            "trade secret"
        ]
    ],

    "Termination": [
        [
            "termination",
            "terminate",
            "terminated"
        ],
        [
            "notice period",
            "notice of termination",
            "terminate this agreement"
        ]
    ],

    "Payment": [
        [
            "payment",
            "salary",
            "compensation",
            "remuneration",
            "fees"
        ],
        [
            "monthly salary",
            "payment terms",
            "payment shall",
            "compensation shall"
        ]
    ],

    "Data Protection": [
        [
            "data protection",
            "data privacy",
            "personal data",
            "privacy"
        ],
        [
            "processing of personal data",
            "protection of personal information",
            "data security"
        ]
    ],

    "Governing Law": [
        [
            "governing law",
            "applicable law",
            "jurisdiction"
        ],
        [
            "laws of",
            "governed by the laws"
        ]
    ],

    "Dispute Resolution": [
        [
            "dispute resolution",
            "arbitration",
            "dispute"
        ],
        [
            "resolve disputes",
            "settlement of disputes",
            "disputes shall"
        ]
    ]
}

CLAUSE_RECOMMENDATIONS = {
    "Confidentiality":
        "Add a clause defining how confidential company information must be protected and not disclosed.",

    "Termination":
        "Add a clause specifying termination conditions and the required notice period.",

    "Payment":
        "Add a clause defining payment terms, salary or compensation, and payment conditions.",

    "Data Protection":
        "Add a clause covering the collection, processing, storage, and protection of personal data.",

    "Governing Law":
        "Add a clause specifying which country's or state's laws will govern the contract.",

    "Dispute Resolution":
        "Add a clause explaining how disputes will be handled, such as negotiation, arbitration, or court proceedings."
}


# -----------------------------
# Text Extraction
# -----------------------------

def extract_pdf_text(file_path):
    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text


def extract_docx_text(file_path):
    document = Document(file_path)

    text = []

    for paragraph in document.paragraphs:
        text.append(paragraph.text)

    return "\n".join(text)


# -----------------------------
# Clause Detection
# -----------------------------

def extract_clause_evidence(text, keywords):
    """
    Find the most useful paragraph/sentence containing
    one of the clause keywords.

    If a clause heading is detected, also try to include
    the content immediately following that heading.
    """

    # Normalize line breaks
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Split document into non-empty lines
    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    keyword_pattern = re.compile(
        r"\b(" +
        "|".join(re.escape(k) for k in keywords) +
        r")\b",
        re.IGNORECASE
    )

    for i, line in enumerate(lines):

        if not keyword_pattern.search(line):
            continue

        # Check whether this looks like a section heading
        heading_pattern = re.compile(
            r"^(\d+(\.\d+)*[\.\)]?\s*)?[A-Z][A-Z0-9\s&/\-]{3,}$"
        )

        is_heading = bool(
            heading_pattern.match(line)
        )

        # --------------------------------------------------
        # CASE 1: Heading found
        # --------------------------------------------------

        if is_heading:

            evidence_parts = [line]

            # Collect following lines until another
            # probable heading is encountered.
            for next_line in lines[i + 1:i + 6]:

                next_is_heading = bool(
                    heading_pattern.match(next_line)
                )

                if next_is_heading:
                    break

                evidence_parts.append(next_line)

            evidence = " ".join(evidence_parts)

            if len(evidence) > len(line):
                return evidence

        # --------------------------------------------------
        # CASE 2: Normal sentence/paragraph
        # --------------------------------------------------

        return line

    return None


def detect_clauses(text):

    results = {}

    for clause, keyword_groups in CLAUSE_RULES.items():

        # Flatten keyword groups
        keywords = []

        for group in keyword_groups:
            keywords.extend(group)

        # Remove duplicates
        keywords = list(
            dict.fromkeys(keywords)
        )

        # Find evidence
        evidence = extract_clause_evidence(
            text,
            keywords
        )

        # Find all matched keywords
        matched_keywords = []

        text_lower = text.lower()

        for keyword in keywords:

            if keyword.lower() in text_lower:
                matched_keywords.append(keyword)

        matched_keywords = list(
            dict.fromkeys(matched_keywords)
        )

        # --------------------------------------------------
        # Determine result
        # --------------------------------------------------

        if evidence:

            if len(matched_keywords) >= 3:
                strength = "Strong"

            elif len(matched_keywords) == 2:
                strength = "Moderate"

            else:
                strength = "Weak"

            results[clause] = {
                "found": True,
                "matched_keywords": matched_keywords,
                "match_strength": strength,
                "evidence": evidence
            }

        else:

            results[clause] = {
                "found": False,
                "matched_keywords": [],
                "match_strength": "None",
                "evidence": None
            }

    return results



# -----------------------------
# Compliance Calculation
# -----------------------------

def calculate_compliance(clause_results):

    total = len(clause_results)

    found = sum(
        1
        for result in clause_results.values()
        if result["found"]
    )

    score = round((found / total) * 100, 2)

    if score >= 80:
        risk = "LOW"

    elif score >= 50:
        risk = "MEDIUM"

    else:
        risk = "HIGH"

    return score, risk


# -----------------------------
# Home
# -----------------------------

@app.get("/")
def home():

    return {
        "message": "Smart Document Compliance Checker API is running"
    }


def generate_report(
    filename,
    compliance_score,
    risk_level,
    clause_results,
    missing_clauses,
    recommendations
):
    output_dir = Path("../output")
    output_dir.mkdir(exist_ok=True)

    report_name = Path(filename).stem + "_compliance_report.pdf"
    report_path = output_dir / report_name

    styles = getSampleStyleSheet()

    document = SimpleDocTemplate(
        str(report_path),
        pagesize=A4
    )

    content = []

    content.append(
        Paragraph(
            "Smart Document Compliance Report",
            styles["Title"]
        )
    )

    content.append(Spacer(1, 20))

    content.append(
        Paragraph(
            f"<b>Document:</b> {filename}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"<b>Compliance Score:</b> {compliance_score}%",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"<b>Risk Level:</b> {risk_level}",
            styles["Normal"]
        )
    )

    content.append(Spacer(1, 20))

    content.append(
        Paragraph(
            "Clause Analysis",
            styles["Heading2"]
        )
    )

    for clause, result in clause_results.items():

        if result["found"]:

            content.append(
                Paragraph(
                    f"✓ <b>{clause}</b> - Found",
                    styles["Normal"]
                )
            )

            if result["evidence"]:
                content.append(
                    Paragraph(
                        f"Evidence: {result['evidence']}",
                        styles["Normal"]
                    )
                )

        else:

            content.append(
                Paragraph(
                    f"✗ <b>{clause}</b> - Missing",
                    styles["Normal"]
                )
            )

        content.append(Spacer(1, 8))

    if missing_clauses:

        content.append(
            Paragraph(
                "Recommendations",
                styles["Heading2"]
            )
        )

        for clause in missing_clauses:

            content.append(
                Paragraph(
                    f"<b>{clause}</b>: "
                    f"{recommendations[clause]}",
                    styles["Normal"]
                )
            )

            content.append(Spacer(1, 8))

    document.build(content)

    return report_path


# -----------------------------
# Upload & Analyze
# -----------------------------

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    allowed_extensions = [".pdf", ".docx"]

    extension = Path(file.filename).suffix.lower()

    if extension not in allowed_extensions:

        return {
            "error": "Only PDF and DOCX files are supported"
        }

    file_path = INPUT_DIR / file.filename

    contents = await file.read()

    with open(file_path, "wb") as f:
        f.write(contents)

    # Extract text
    if extension == ".pdf":

        extracted_text = extract_pdf_text(file_path)

    else:

        extracted_text = extract_docx_text(file_path)

    # Detect clauses
    clause_results = detect_clauses(extracted_text)

    # Calculate compliance
    score, risk = calculate_compliance(clause_results)

    # Find missing clauses
    missing_clauses = [
    clause
    for clause, result in clause_results.items()
    if not result["found"]
]

    recommendations = {
    clause: CLAUSE_RECOMMENDATIONS[clause]
    for clause in missing_clauses
}

    report_path = generate_report(
    file.filename,
    score,
    risk,
    clause_results,
    missing_clauses,
    recommendations
)

    return {
    "filename": file.filename,
    "message": "Document analyzed successfully",
    "compliance_score": score,
    "risk_level": risk,
    "clauses": clause_results,
    "missing_clauses": missing_clauses,
    "recommendations": recommendations,
    "report": report_path.name,
    "extracted_text": extracted_text
}


@app.get("/report/{filename}")
def download_report(filename: str):

    report_path = Path("../output") / filename

    if not report_path.exists():
        return {
            "error": "Report not found"
        }

    return FileResponse(
        report_path,
        media_type="application/pdf",
        filename=filename
    )


@app.get("/dashboard")
async def get_dashboard():

    import csv
    import os

    log_file = "../contracts/processing_log.csv"

    records = []

    if os.path.exists(log_file):

        with open(
            log_file,
            "r",
            encoding="utf-8"
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:
                records.append(row)


    total = len(records)

    low = sum(
        1
        for row in records
        if row.get("Risk Level", "").upper() == "LOW"
    )

    medium = sum(
        1
        for row in records
        if row.get("Risk Level", "").upper() == "MEDIUM"
    )

    high = sum(
        1
        for row in records
        if row.get("Risk Level", "").upper() == "HIGH"
    )


    return {
        "total_processed": total,
        "low_risk": low,
        "medium_risk": medium,
        "high_risk": high,
        "records": records
    }