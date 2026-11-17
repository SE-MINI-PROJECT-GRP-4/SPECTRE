"""Seed data module to populate initial legal knowledge, references, templates, and admin accounts."""

import json
import bcrypt
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.reference import LegalReference
from app.models.template import DocumentTemplate
from app.models.knowledge import KnowledgeEntry


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
    {
        "email": "admin@spectre.dev",
        "full_name": "Admin Dev",
        "role": UserRole.ADMIN,
        "password": "admin123",
        "is_active": True,
    },
    {
        "email": "demo@spectre.dev",
        "full_name": "Demo User",
        "role": UserRole.USER,
        "password": "demo1234",
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
    {
        "title": "Transfer of Property Act, 1882",
        "citation": "Act No. 4 of 1882",
        "source": "India Code",
        "legal_domain": "Tenancy & Property",
        "year": 1882,
        "court": "Supreme Court and High Courts of India",
        "url": "https://www.indiacode.nic.in",
        "status": "active",
        "summary": "Governs the transfer of immovable property by act of parties, including leases, mortgages, and landlord-tenant rights.",
    },
    {
        "title": "Model Tenancy Act, 2021",
        "citation": "MoHUA Model Legislation 2021",
        "source": "Ministry of Housing and Urban Affairs",
        "legal_domain": "Tenancy & Property",
        "year": 2021,
        "court": "Rent Authorities and Tribunals",
        "url": "https://mohua.gov.in",
        "status": "active",
        "summary": "Framework for tenancy agreements, security deposit caps, eviction procedures, and establishment of Rent Courts.",
    },
    {
        "title": "Industrial Disputes Act, 1947",
        "citation": "Act No. 14 of 1947",
        "source": "India Code",
        "legal_domain": "Employment",
        "year": 1947,
        "court": "Labour Courts / Industrial Tribunals",
        "url": "https://www.indiacode.nic.in",
        "status": "active",
        "summary": "Provides for investigation and settlement of industrial disputes, unfair labor practices, and compensation for layoff/retrenchment.",
    },
    {
        "title": "Hindu Marriage Act, 1955",
        "citation": "Act No. 25 of 1955",
        "source": "India Code",
        "legal_domain": "Family",
        "year": 1955,
        "court": "Family Courts / High Courts",
        "url": "https://www.indiacode.nic.in",
        "status": "active",
        "summary": "Codifies the law relating to marriage, restitution of conjugal rights, judicial separation, divorce, and maintenance.",
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
    {
        "name": "Rental agreement",
        "slug": "rental-agreement",
        "category": "Tenancy & Property",
        "description": "Basic residential leave-and-license / rent agreement outline.",
        "version": "1.2",
        "variables_json": json.dumps([
            {"key": "landlord_name", "label": "Landlord Name", "type": "string", "required": True},
            {"key": "tenant_name", "label": "Tenant Name", "type": "string", "required": True},
            {"key": "premises_address", "label": "Premises Address", "type": "string", "required": True},
            {"key": "rent_amount", "label": "Monthly Rent (INR)", "type": "string", "required": True},
            {"key": "security_deposit", "label": "Security Deposit (INR)", "type": "string", "required": True},
        ]),
        "content": """RENT AGREEMENT

This agreement is made between {{landlord_name}} (Landlord) and {{tenant_name}} (Tenant).

1. Premises: {{premises_address}}
2. Monthly rent: Rs. {{rent_amount}}, payable by 5th of each month.
3. Security deposit: Rs. {{security_deposit}}, refundable on vacating after lawful deductions.
4. Notice period: 30 days by either party.

Signed:
{{landlord_name}} (Landlord)            {{tenant_name}} (Tenant)
""",
    },
    {
        "name": "Unpaid wages demand letter",
        "slug": "unpaid-wages-demand-letter",
        "category": "Employment",
        "description": "Written demand to an employer for pending salary or dues under labor laws.",
        "version": "1.0",
        "variables_json": json.dumps([
            {"key": "company_name", "label": "Company / Employer Name", "type": "string", "required": True},
            {"key": "employee_name", "label": "Employee Name", "type": "string", "required": True},
            {"key": "designation", "label": "Designation", "type": "string", "required": True},
            {"key": "pending_amount", "label": "Pending Dues Amount (INR)", "type": "string", "required": True},
        ]),
        "content": """To,
The HR Manager / Management,
{{company_name}}

Subject: Request and formal demand for payment of pending salary dues

Sir / Madam,

I worked as {{designation}} at {{company_name}}. The following salary dues amounting to Rs. {{pending_amount}} remain unpaid.

Kindly disburse these dues within 10 days of receipt of this notice, failing which I will approach the competent Labour Commissioner under the Payment of Wages Act.

Sincerely,
{{employee_name}}
""",
    },
    {
        "name": "Cyber crime complaint",
        "slug": "cyber-crime-complaint",
        "category": "Cyber",
        "description": "Draft complaint for online financial fraud or harassment to accompany a police / 1930 portal report.",
        "version": "1.0",
        "variables_json": json.dumps([
            {"key": "victim_name", "label": "Complainant Name", "type": "string", "required": True},
            {"key": "transaction_id", "label": "Transaction ID / UTR", "type": "string", "required": True},
            {"key": "fraud_amount", "label": "Defrauded Amount (INR)", "type": "string", "required": True},
            {"key": "platform_used", "label": "Platform / Website / App", "type": "string", "required": True},
        ]),
        "content": """To,
The Station House Officer / Cyber Crime Cell,

Subject: Formal complaint regarding online financial fraud / cyber offence

I, {{victim_name}}, wish to report an incident of financial cyber fraud on {{platform_used}} involving fraudulent transaction reference {{transaction_id}} for an amount of Rs. {{fraud_amount}}.

I request urgent action to trace the fraudulent account and freeze proceeds under Section 66D of the IT Act, 2000.

Name: {{victim_name}}
Date: [DD/MM/YYYY]
""",
    },
]


INITIAL_KNOWLEDGE = [
    {
        "id": "kb-1",
        "domain": "Consumer",
        "title": "Defective product or deficient service",
        "explanation": "If a product is defective or a service is deficient, you can seek a repair, replacement, refund or compensation from the seller or service provider, and approach a Consumer Disputes Redressal Commission if they do not resolve it.",
        "keywords": ["refund", "defective", "consumer", "warranty", "product", "seller", "service", "e-commerce"],
        "prerequisites": ["Invoice / proof of purchase", "Photos or evidence of the defect", "Written communication with the seller"],
        "steps": [
            "Complain to the seller or service provider in writing and keep a copy.",
            "Send a legal notice if there is no response within a reasonable time.",
            "File a complaint with the appropriate District Consumer Disputes Redressal Commission (online filing is available through e-Daakhil).",
            "Attend hearings or mediation as scheduled."
        ],
        "ref_ids": ["ref-1"],
        "template_hint": "Legal notice for consumer complaint"
    },
    {
        "id": "kb-2",
        "domain": "Tenancy & Property",
        "title": "Security deposit and eviction disputes",
        "explanation": "Rights and duties between landlord and tenant depend mainly on your rent agreement and the rent-control or tenancy law of your state. Deposits are normally refundable after lawful deductions once possession is handed back.",
        "keywords": ["rent", "landlord", "tenant", "deposit", "evict", "lease", "tenancy", "property"],
        "prerequisites": ["Signed rent / leave-and-license agreement", "Rent payment records", "Notice or messages exchanged with the landlord"],
        "steps": [
            "Read the notice period and deposit clauses in your agreement.",
            "Send a written demand or notice to the landlord stating your claim.",
            "Try mediation or a rent authority / civil court in your state if the dispute continues."
        ],
        "ref_ids": ["ref-2", "ref-3"],
        "template_hint": "Rental agreement"
    },
    {
        "id": "kb-3",
        "domain": "Employment",
        "title": "Unpaid wages and wrongful termination",
        "explanation": "Employees can raise unpaid wages or an unfair termination first with the employer, and then with the labour authorities of their state. The applicable law depends on your role, sector and state.",
        "keywords": ["salary", "wages", "employer", "terminated", "fired", "job", "employee", "notice period", "unpaid"],
        "prerequisites": ["Appointment letter / contract", "Salary slips and bank statements", "Termination letter or emails, if any"],
        "steps": [
            "Send a written representation to HR or the employer asking for dues.",
            "If unresolved, approach the Labour Commissioner or labour office with your documents.",
            "Seek advice from a labour lawyer for conciliation or tribunal options."
        ],
        "ref_ids": ["ref-4"],
        "template_hint": "Unpaid wages demand letter"
    },
    {
        "id": "kb-4",
        "domain": "Cyber",
        "title": "Online fraud and cyber harassment",
        "explanation": "Online financial fraud and cyber harassment can be reported quickly through the national cybercrime channels. Speed matters, especially for money transfers.",
        "keywords": ["cyber", "online", "fraud", "scam", "hacked", "upi", "phishing", "harassment", "instagram", "otp"],
        "prerequisites": ["Screenshots, transaction IDs and URLs", "Bank / platform communication", "Your ID and contact details"],
        "steps": [
            "Inform your bank immediately so the transaction can be flagged.",
            "Report on the national cybercrime portal (cybercrime.gov.in) or call 1930 for financial fraud.",
            "File a complaint at the local police / cyber cell with your evidence."
        ],
        "ref_ids": ["ref-5"],
        "template_hint": "Cyber crime complaint"
    },
    {
        "id": "kb-5",
        "domain": "Criminal",
        "title": "Filing an FIR",
        "explanation": "A cognizable offence can be reported by lodging an FIR at a police station. If the police refuse, there are escalation routes available.",
        "keywords": ["fir", "police", "theft", "crime", "complaint", "assault", "arrest", "criminal"],
        "prerequisites": ["Details of the incident (date, place, persons involved)", "Any evidence or witness details", "Your identification"],
        "steps": [
            "Go to the police station with jurisdiction (or lodge a Zero FIR at any station).",
            "Give a clear written or oral statement and ask for a free copy of the FIR.",
            "If refused, escalate in writing to the senior police officer or approach the Magistrate."
        ],
        "ref_ids": ["ref-6"],
        "template_hint": None
    },
    {
        "id": "kb-6",
        "domain": "Family",
        "title": "Marriage, divorce and maintenance",
        "explanation": "Family matters depend heavily on personal law, the facts of your case and the court. This is an area where individual legal advice is strongly recommended.",
        "keywords": ["divorce", "marriage", "maintenance", "custody", "spouse", "alimony", "family"],
        "prerequisites": ["Marriage certificate", "Identity and address proof", "Details of children, income and assets"],
        "steps": [
            "Consult a family lawyer about the correct ground and forum.",
            "Consider mediation or counselling where suitable.",
            "File the petition in the competent Family Court."
        ],
        "ref_ids": ["ref-7"],
        "template_hint": None
    },
    {
        "id": "kb-7",
        "domain": "RTI",
        "title": "Filing an RTI application",
        "explanation": "Any citizen can request information held by a public authority by writing to its Public Information Officer.",
        "keywords": ["rti", "right to information", "government information", "public authority"],
        "prerequisites": ["Name of the public authority", "Specific information requested", "Application fee (as applicable)"],
        "steps": [
            "Draft a clear, specific application addressed to the PIO.",
            "Submit it online or in person with the fee and keep proof.",
            "If there is no reply in the statutory time, file a first appeal."
        ],
        "ref_ids": ["ref-8"],
        "template_hint": "RTI application"
    },
]


def seed_database(db: Session) -> None:
    """Populate database with initial users, references, templates, and knowledge."""
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

    # Seed Knowledge
    for kb in INITIAL_KNOWLEDGE:
        existing_kb = db.query(KnowledgeEntry).filter(KnowledgeEntry.id == kb["id"]).first()
        if not existing_kb:
            entry = KnowledgeEntry(
                id=kb["id"],
                domain=kb["domain"],
                title=kb["title"],
                explanation=kb["explanation"],
                keywords_json=json.dumps(kb["keywords"]),
                prerequisites_json=json.dumps(kb["prerequisites"]),
                steps_json=json.dumps(kb["steps"]),
                ref_ids_json=json.dumps(kb["ref_ids"]),
                template_hint=kb["template_hint"],
            )
            db.add(entry)

    db.commit()
