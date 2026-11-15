"""Seed data module to populate initial legal knowledge, references, templates, and admin accounts."""

import json
import bcrypt
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.reference import LegalReference
from app.models.template import DocumentTemplate


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


INITIAL_USERS = [
    {
        "email": "admin@spectre.legal",
        "full_name": "System Administrator",
        "role": UserRole.ADMIN,
        "password": "Admin@SPECTRE2026!",
        "is_active": True,
    },
    {
        "email": "lawyer@spectre.legal",
        "full_name": "Adv. Ananya Rao",
        "role": UserRole.ADVOCATE,
        "password": "Lawyer@SPECTRE2026!",
        "is_active": True,
    },
    {
        "email": "citizen@spectre.legal",
        "full_name": "Rahul Sharma",
        "role": UserRole.USER,
        "password": "User@SPECTRE2026!",
        "is_active": True,
    },
]


INITIAL_REFERENCES = [
    {
        "title": "Bharatiya Nyaya Sanhita, 2023 (BNS)",
        "citation": "Act No. 45 of 2023",
        "source": "Parliament of India / Ministry of Law and Justice",
        "legal_domain": "criminal",
        "year": 2023,
        "court": "Supreme Court and High Courts of India",
        "url": "https://www.mha.gov.in/en/commoncontent/new-criminal-laws",
        "status": "active",
        "summary": "Substantive criminal law of India replacing the Indian Penal Code (IPC), 1860 with modernized definitions, community service penalties, and organized crime provisions.",
    },
    {
        "title": "Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)",
        "citation": "Act No. 46 of 2023",
        "source": "Parliament of India / Ministry of Law and Justice",
        "legal_domain": "criminal",
        "year": 2023,
        "court": "Supreme Court and High Courts of India",
        "url": "https://www.mha.gov.in/en/commoncontent/new-criminal-laws",
        "status": "active",
        "summary": "Governs criminal procedure in India replacing the CrPC, 1973. Mandates forensic investigation for severe offences, timelines for inquiries, and electronic/zero FIR registration under Section 173.",
    },
    {
        "title": "Bharatiya Sakshya Adhiniyam, 2023 (BSA)",
        "citation": "Act No. 47 of 2023",
        "source": "Parliament of India / Ministry of Law and Justice",
        "legal_domain": "evidence",
        "year": 2023,
        "court": "Supreme Court and High Courts of India",
        "url": "https://www.mha.gov.in/en/commoncontent/new-criminal-laws",
        "status": "active",
        "summary": "Law of evidence replacing the Indian Evidence Act, 1872. Recognizes electronic and digital records as primary evidence under Section 61 and 63.",
    },
    {
        "title": "Consumer Protection Act, 2019 (CPA)",
        "citation": "Act No. 35 of 2019",
        "source": "Ministry of Consumer Affairs, Food and Public Distribution",
        "legal_domain": "consumer",
        "year": 2019,
        "court": "NCDRC / SCDRC / DCDRC",
        "url": "https://consumeraffairs.nic.in/acts-and-rules/consumer-protection",
        "status": "active",
        "summary": "Provides for enhanced protection of consumer rights, establishment of the Central Consumer Protection Authority (CCPA), e-commerce rules, product liability, and online filing via E-Daakhil.",
    },
    {
        "title": "Information Technology Act, 2000 (Amended 2008)",
        "citation": "Act No. 21 of 2000",
        "source": "Ministry of Electronics and Information Technology (MeitY)",
        "legal_domain": "cyber",
        "year": 2000,
        "court": "Supreme Court of India / Cyber Appellate Tribunal",
        "url": "https://www.meity.gov.in/content/information-technology-act-2000",
        "status": "active",
        "summary": "Primary statute governing cybercrimes, electronic commerce, digital signatures, hacking (Sec 66), identity theft (Sec 66C), and intermediary liability (Sec 79).",
    },
    {
        "title": "Protection of Children from Sexual Offences (POCSO) Act, 2012",
        "citation": "Act No. 32 of 2012",
        "source": "Ministry of Women and Child Development",
        "legal_domain": "criminal",
        "year": 2012,
        "court": "Special POCSO Courts / High Courts",
        "url": "https://wcd.nic.in/act/protection-children-sexual-offences-pocso-act-2012",
        "status": "active",
        "summary": "Special law enacted to protect children from sexual assault, harassment, and pornography, mandating child-friendly reporting and designated Special Courts.",
    },
    {
        "title": "Right to Information Act, 2005 (RTI)",
        "citation": "Act No. 22 of 2005",
        "source": "Department of Personnel and Training (DoPT)",
        "legal_domain": "constitutional",
        "year": 2005,
        "court": "Central Information Commission / High Courts",
        "url": "https://rtionline.gov.in",
        "status": "active",
        "summary": "Mandates timely response to citizen requests for government information, upholding democratic transparency and freedom of speech under Article 19(1)(a).",
    },
]


INITIAL_TEMPLATES = [
    {
        "name": "Legal Notice for Defective Goods / Consumer Grievance",
        "slug": "consumer-legal-notice",
        "category": "consumer",
        "description": "Formal legal notice sent to a manufacturer, distributor, or seller demanding refund or replacement for defective products or deficient services before approaching the Consumer Disputes Redressal Commission.",
        "version": "1.0",
        "variables_json": json.dumps([
            {"key": "complainant_name", "label": "Consumer Full Name", "type": "string", "required": True},
            {"key": "complainant_address", "label": "Consumer Address", "type": "string", "required": True},
            {"key": "opposite_party_name", "label": "Company / Seller Name", "type": "string", "required": True},
            {"key": "opposite_party_address", "label": "Seller Address", "type": "string", "required": True},
            {"key": "product_name", "label": "Product / Service Description", "type": "string", "required": True},
            {"key": "invoice_number", "label": "Invoice / Bill Number", "type": "string", "required": True},
            {"key": "purchase_date", "label": "Purchase Date", "type": "string", "required": True},
            {"key": "amount_paid", "label": "Amount Paid (INR)", "type": "string", "required": True},
            {"key": "defect_description", "label": "Description of Defect / Grievance", "type": "string", "required": True},
            {"key": "demand_summary", "label": "Specific Relief Demanded", "type": "string", "required": True},
            {"key": "notice_period_days", "label": "Notice Cure Period (Days)", "type": "integer", "required": True, "default": 15},
        ]),
        "content": """LEGAL NOTICE UNDER SECTION 35 / 84 OF THE CONSUMER PROTECTION ACT, 2019

Date: {{purchase_date}}

TO,
{{opposite_party_name}}
{{opposite_party_address}}

FROM:
{{complainant_name}}
{{complainant_address}}

SUBJECT: LEGAL NOTICE FOR DEFICIENCY IN SERVICE AND DEFECTIVE PRODUCT IN RESPECT OF {{product_name}} (INVOICE NO: {{invoice_number}})

Sir / Madam,

Under instructions and on behalf of my client / undersigned {{complainant_name}}, I hereby serve upon you this formal Legal Notice:

1. That the undersigned purchased {{product_name}} on {{purchase_date}} against Invoice No. {{invoice_number}} for a total consideration of INR {{amount_paid}}.
2. That soon after purchase, the said product exhibited severe defects and deficiency, namely: {{defect_description}}.
3. That despite repeated communications, your company has failed and neglected to rectify the defect or provide a lawful replacement or refund.
4. That your acts constitute an 'Unfair Trade Practice' and 'Deficiency of Service' as defined under the Consumer Protection Act, 2019.

THEREFORE, you are hereby called upon to:
{{demand_summary}}
within a period of {{notice_period_days}} days from the date of receipt of this notice, failing which the undersigned shall be constrained to initiate appropriate legal proceedings before the competent District Consumer Disputes Redressal Commission under the Consumer Protection Act, 2019, holding you liable for all costs and consequences thereof.

Yours sincerely,

{{complainant_name}}
""",
    },
    {
        "name": "Application for Information under Section 6(1) of RTI Act, 2005",
        "slug": "rti-application-6-1",
        "category": "constitutional",
        "description": "Standard citizen application to Public Information Officers (PIO) under the Right to Information Act, 2005.",
        "version": "1.0",
        "variables_json": json.dumps([
            {"key": "applicant_name", "label": "Applicant Name", "type": "string", "required": True},
            {"key": "applicant_address", "label": "Postal Address", "type": "string", "required": True},
            {"key": "pio_designation", "label": "Public Information Officer Designation", "type": "string", "required": True},
            {"key": "department_name", "label": "Public Authority / Department", "type": "string", "required": True},
            {"key": "department_address", "label": "Department Address", "type": "string", "required": True},
            {"key": "subject_matter", "label": "Subject Matter of Information", "type": "string", "required": True},
            {"key": "specific_queries", "label": "Numbered Queries / Questions", "type": "string", "required": True},
            {"key": "fee_payment_details", "label": "Fee Payment Details (IPO / DD / Online Ref)", "type": "string", "required": True},
        ]),
        "content": """APPLICATION UNDER SECTION 6(1) OF THE RIGHT TO INFORMATION ACT, 2005

To,
The Central / State Public Information Officer (PIO),
{{pio_designation}},
{{department_name}},
{{department_address}}

1. Full Name of the Applicant: {{applicant_name}}
2. Address for Correspondence: {{applicant_address}}
3. Subject Matter of Information: {{subject_matter}}

4. Specific Information Required:
{{specific_queries}}

5. Period to which the information relates: Current / Relevant Financial Year.
6. Mode of Delivery: Registered Post / Speed Post / By Hand.
7. Application Fee Details: An application fee of Rs. 10/- has been paid via {{fee_payment_details}}.

8. Declaration: I am a citizen of India and the requested information does not fall within the exemptions specified under Section 8 or Section 9 of the RTI Act, 2005.

Place:
Date:

Signature of the Applicant
({{applicant_name}})
""",
    },
    {
        "name": "Formal Police Complaint / Zero FIR Application under BNSS Section 173",
        "slug": "police-complaint-bnss-173",
        "category": "criminal",
        "description": "Written complaint format submitted to the Station House Officer (SHO) for reporting cognizable offences under Section 173 of the Bharatiya Nagarik Suraksha Sanhita, 2023.",
        "version": "1.0",
        "variables_json": json.dumps([
            {"key": "complainant_name", "label": "Complainant Name", "type": "string", "required": True},
            {"key": "complainant_contact", "label": "Phone & Address", "type": "string", "required": True},
            {"key": "police_station", "label": "Police Station Jurisdiction", "type": "string", "required": True},
            {"key": "incident_date_time", "label": "Date & Time of Incident", "type": "string", "required": True},
            {"key": "incident_location", "label": "Location / Place of Incident", "type": "string", "required": True},
            {"key": "accused_details", "label": "Suspect / Accused Details (if known)", "type": "string", "required": True},
            {"key": "incident_narration", "label": "Detailed Factual Narration", "type": "string", "required": True},
            {"key": "offence_type", "label": "Suspected Offence (Theft, Assault, Cyber Fraud)", "type": "string", "required": True},
        ]),
        "content": """WRITTEN COMPLAINT UNDER SECTION 173 OF THE BHARATIYA NAGARIK SURAKSHA SANHITA, 2023 (BNSS)

To,
The Station House Officer (SHO),
{{police_station}}

Subject: Written Complaint regarding commission of cognizable offence ({{offence_type}}) under the Bharatiya Nyaya Sanhita, 2023.

Respected Sir / Madam,

I, {{complainant_name}}, residing at {{complainant_contact}}, wish to report the following cognizable offence for registration of FIR:

1. DATE, TIME & PLACE OF INCIDENT:
The incident occurred on or about {{incident_date_time}} at {{incident_location}}.

2. DETAILS OF ACCUSED PERSON(S):
{{accused_details}}

3. NARRATION OF FACTS:
{{incident_narration}}

4. PRAYER:
In light of the statutory mandate under Section 173 of the Bharatiya Nagarik Suraksha Sanhita, 2023, you are requested to register a First Information Report (FIR) / Zero FIR forthwith and initiate investigation in accordance with law.

Yours faithfully,

Signature: ______________________
Name: {{complainant_name}}
Contact: {{complainant_contact}}
""",
    },
]


def seed_database(db: Session) -> None:
    """Populate database with initial users, references, and document templates."""
    # Seed Users
    for user_data in INITIAL_USERS:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing:
            hashed = hash_password(user_data["password"])
            user = User(
                email=user_data["email"],
                full_name=user_data["full_name"],
                role=user_data["role"],
                hashed_password=hashed,
                is_active=user_data["is_active"],
            )
            db.add(user)

    # Seed References
    for ref_data in INITIAL_REFERENCES:
        existing_ref = db.query(LegalReference).filter(LegalReference.title == ref_data["title"]).first()
        if not existing_ref:
            ref = LegalReference(**ref_data)
            db.add(ref)

    # Seed Templates
    for tpl_data in INITIAL_TEMPLATES:
        existing_tpl = db.query(DocumentTemplate).filter(DocumentTemplate.slug == tpl_data["slug"]).first()
        if not existing_tpl:
            tpl = DocumentTemplate(**tpl_data)
            db.add(tpl)

    db.commit()
