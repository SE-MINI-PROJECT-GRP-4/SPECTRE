"""Procedural Guidance Engine for Indian Legal Framework."""

from typing import List, Optional
from fastapi import HTTPException, status
from app.core.config import settings
from app.schemas.procedure import ProcedureGuideResponse, ProcedureStep, ProcedureSummary

INDIAN_LEGAL_PROCEDURES = [
    {
        "id": "proc-01",
        "slug": "fir-registration-bnss",
        "title": "Filing a First Information Report (FIR) / Zero FIR under BNSS 2023",
        "legal_domain": "criminal",
        "overview": (
            "A structured procedural guide for citizens seeking to register a First Information Report (FIR) "
            "for cognizable criminal offences under Section 173 of the Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)."
        ),
        "prerequisites": [
            "Occurrence of a cognizable offence (e.g., theft, assault, cheating, cyber fraud, robbery).",
            "Clear factual recollection of date, time, location, sequence of events, and suspected individuals (if known)."
        ],
        "required_documents": [
            "Written complaint signed by the informant/victim.",
            "Government identity proof (Aadhaar Card, Voter ID, Passport, or Driving License).",
            "Supporting material evidence (photos, video footage, medical examination reports, digital logs)."
        ],
        "jurisdiction_notes": (
            "Under BNSS Section 173, an FIR can be registered at ANY police station irrespective of territorial "
            "jurisdiction (Zero FIR). The receiving station must record it and transfer the case diary to the jurisdictional station."
        ),
        "estimated_timeline": "Immediate registration upon submission; inquiry within 14 days if preliminary inquiry is mandated for offences punishable between 3 to 7 years.",
        "statutory_references": [
            "Bharatiya Nagarik Suraksha Sanhita, 2023 — Section 173 (Information in cognizable cases)",
            "Bharatiya Nagarik Suraksha Sanhita, 2023 — Section 175 (Power of police to investigate)",
            "Bharatiya Nyaya Sanhita, 2023 (Substantive offences)"
        ],
        "escalation_advice": (
            "If the Station House Officer (SHO) refuses to register the FIR, send the substance of information in writing "
            "by registered post to the Superintendent of Police (SP) under Section 173(4). If unresolved, file an application "
            "before the Judicial Magistrate under Section 175(3) of the BNSS with assistance from a criminal defense advocate."
        ),
        "steps": [
            ProcedureStep(
                step_number=1,
                title="Drafting the Written Complaint",
                description="Prepare a clear, factual written narrative specifying the exact date, time, and location of the incident.",
                relevant_statute="BNSS Section 173(1)",
                action_items=[
                    "Clearly state complainant identity and address.",
                    "Describe the role of each accused person chronologically.",
                    "List all witnesses present."
                ]
            ),
            ProcedureStep(
                step_number=2,
                title="Lodge Complaint at Police Station (or Zero FIR)",
                description="Present the complaint in person to the Station House Officer (SHO) or duty officer at the nearest police station.",
                relevant_statute="BNSS Section 173(1)",
                action_items=[
                    "If oral, ensure the officer reads over the statement before you sign.",
                    "Request immediate entry into the general diary."
                ]
            ),
            ProcedureStep(
                step_number=3,
                title="Obtain Free Stamped Copy of FIR",
                description="The police officer is statutorily mandated to provide a signed copy of the FIR free of cost immediately.",
                relevant_statute="BNSS Section 173(2)",
                action_items=[
                    "Ensure the FIR Number, date, police station name, and applied penal sections are visible."
                ]
            ),
            ProcedureStep(
                step_number=4,
                title="Follow-up and Investigation Updates",
                description="The investigating officer (IO) must inform the informant/victim of progress within 90 days under BNSS provisions.",
                relevant_statute="BNSS Section 193",
                action_items=[
                    "Coordinate with the IO for submission of additional documentary or forensic evidence."
                ]
            ),
        ]
    },
    {
        "id": "proc-02",
        "slug": "consumer-complaint-cpa",
        "title": "Filing a Consumer Complaint under Consumer Protection Act, 2019",
        "legal_domain": "consumer",
        "overview": (
            "Step-by-step guidance on initiating legal proceedings against a manufacturer, trader, or service provider "
            "for unfair trade practices, product defects, or deficiency of service before the Consumer Commission."
        ),
        "prerequisites": [
            "Proof of purchase / transaction establishing status as a 'consumer' under Section 2(7) of CPA 2019.",
            "Evidence of defect in goods or deficiency in services.",
            "Failure or refusal by opposite party to provide cure after formal communication."
        ],
        "required_documents": [
            "Invoice / Cash Memo / Bill of Sale.",
            "Warranty / Guarantee card (if applicable).",
            "Copy of Legal Notice sent to the seller/manufacturer with postal delivery proof.",
            "Written reply received from the opposite party (if any).",
            "Affidavit in support of the complaint."
        ],
        "jurisdiction_notes": (
            "Pecuniary Jurisdiction: District Commission up to Rs. 50 Lakhs; State Commission from Rs. 50 Lakhs to Rs. 2 Crores; "
            "National Commission (NCDRC) exceeding Rs. 2 Crores. Territorial jurisdiction includes where the complainant resides or works."
        ),
        "estimated_timeline": "Admissibility decided within 21 days; target disposal within 3 to 5 months.",
        "statutory_references": [
            "Consumer Protection Act, 2019 — Section 35 (Manner in which complaint shall be made)",
            "Consumer Protection Act, 2019 — Section 38 (Procedure on admission of complaint)",
            "Consumer Protection Act, 2019 — Section 84 (Product liability of manufacturer)"
        ],
        "escalation_advice": (
            "For complex commercial contracts or claims exceeding Rs. 50 Lakhs, consult an advocate practicing before the State or National Commission."
        ),
        "steps": [
            ProcedureStep(
                step_number=1,
                title="Service of Legal Notice",
                description="Send a formal legal notice giving the opposite party 15 to 30 days to resolve the grievance or refund payment.",
                action_items=["Dispatch notice via Speed Post with Acknowledgment Due (AD) or registered email."]
            ),
            ProcedureStep(
                step_number=2,
                title="Online Registration on E-Daakhil Portal",
                description="Access edaakhil.nic.in, create a consumer account, and fill out complainant and opposite party details.",
                relevant_statute="CPA 2019 Section 35",
                action_items=["Upload complaint petition in PDF format along with indexed annexures."]
            ),
            ProcedureStep(
                step_number=3,
                title="Payment of Statutory Court Fee",
                description="Pay the nominal prescribed fee online based on the claim amount (Fee is Nil up to Rs. 5 Lakhs).",
                action_items=["Download and save payment receipt for court records."]
            ),
            ProcedureStep(
                step_number=4,
                title="Admission Hearing and Notice Issuance",
                description="Commission reviews admissibility within 21 days and issues statutory notice to opposite party to file written version within 30 days.",
                relevant_statute="CPA 2019 Section 38",
                action_items=["Track hearings online and appear virtually or in person on scheduled dates."]
            ),
        ]
    },
    {
        "id": "proc-03",
        "slug": "rti-application-filing",
        "title": "Filing an RTI Application under Right to Information Act, 2005",
        "legal_domain": "constitutional",
        "overview": (
            "A comprehensive walkthrough for exercising citizen transparency rights to inspect public records or obtain "
            "information from Central and State public authorities."
        ),
        "prerequisites": [
            "Applicant must be a Citizen of India.",
            "Information sought must be held by or under control of a 'Public Authority' as defined under Section 2(h)."
        ],
        "required_documents": [
            "Application in writing or electronic format in English, Hindi, or official local language.",
            "Application fee of Rs. 10/- (Indian Postal Order, Demand Draft, or online payment). BPL cardholders are exempt."
        ],
        "jurisdiction_notes": "Central public authorities via rtionline.gov.in; State public authorities via designated State RTI portals or by post.",
        "estimated_timeline": "Mandatory response within 30 calendar days (48 hours if concerning personal life and liberty).",
        "statutory_references": [
            "RTI Act, 2005 — Section 6 (Request for obtaining information)",
            "RTI Act, 2005 — Section 7 (Disposal of request)",
            "RTI Act, 2005 — Section 19 (Appeals)"
        ],
        "escalation_advice": (
            "If no response is received within 30 days or information is rejected without valid Section 8 exemption, "
            "file a First Appeal before the First Appellate Authority (FAA) within 30 days. Second Appeal lies before the Central/State Information Commission."
        ),
        "steps": [
            ProcedureStep(
                step_number=1,
                title="Identify Public Authority and PIO",
                description="Ascertain the correct ministry or government department holding the requested records.",
                action_items=["Check the department's proactive disclosure under Section 4(1)(b)."]
            ),
            ProcedureStep(
                step_number=2,
                title="Formulate Point-wise Queries",
                description="Draft concise, numbered questions seeking factual records rather than opinions or explanations.",
                relevant_statute="RTI Act Section 6(1)",
                action_items=["Avoid asking 'why' or hypothetical scenarios; ask for certified copies of orders, logs, or minutes."]
            ),
            ProcedureStep(
                step_number=3,
                title="Submit Application & Remit Fee",
                description="Submit online via rtionline.gov.in or send physically with an Indian Postal Order of Rs. 10/-.",
                action_items=["Note down the registration reference number for status tracking."]
            ),
        ]
    },
]


class ProcedureService:
    """Service providing legal procedural workflows."""

    def list_procedures(self, domain: Optional[str] = None) -> List[ProcedureSummary]:
        results = []
        for p in INDIAN_LEGAL_PROCEDURES:
            if domain and p["legal_domain"].lower() != domain.lower().strip():
                continue
            results.append(
                ProcedureSummary(
                    id=p["id"],
                    title=p["title"],
                    slug=p["slug"],
                    legal_domain=p["legal_domain"],
                    overview=p["overview"],
                    step_count=len(p["steps"]),
                )
            )
        return results

    def get_procedure_by_slug(self, slug: str) -> ProcedureGuideResponse:
        for p in INDIAN_LEGAL_PROCEDURES:
            if p["slug"] == slug or p["id"] == slug:
                return ProcedureGuideResponse(
                    id=p["id"],
                    title=p["title"],
                    slug=p["slug"],
                    legal_domain=p["legal_domain"],
                    overview=p["overview"],
                    prerequisites=p["prerequisites"],
                    required_documents=p["required_documents"],
                    jurisdiction_notes=p["jurisdiction_notes"],
                    estimated_timeline=p["estimated_timeline"],
                    steps=p["steps"],
                    statutory_references=p["statutory_references"],
                    escalation_advice=p["escalation_advice"],
                    disclaimer=settings.STANDARD_DISCLAIMER,
                )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Procedure guidance for '{slug}' not found.",
        )
