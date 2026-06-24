from pathlib import Path


def classify_document(document_name: str) -> dict:
    """
    Classifies a document using its file name.

    This is intentionally simple for now.
    Later we can improve it by reading title pages and document headings.
    """
    name = document_name.lower()

    metadata = {
        "document_type": "unknown",
        "provider_or_regulator": "unknown",
        "product_type": "general",
        "jurisdiction": "australia",
        "source_category": "insurance",
    }

    if "nrma" in name and "car" in name:
        metadata.update(
            {
                "document_type": "policy_pds",
                "provider_or_regulator": "NRMA",
                "product_type": "car_insurance",
                "source_category": "policy_wording",
            }
        )

    elif "nrma" in name and "home" in name:
        metadata.update(
            {
                "document_type": "policy_pds",
                "provider_or_regulator": "NRMA",
                "product_type": "home_insurance",
                "source_category": "policy_wording",
            }
        )

    elif "afca" in name:
        metadata.update(
            {
                "document_type": "claims_guidance",
                "provider_or_regulator": "AFCA",
                "product_type": "general_insurance",
                "source_category": "claims_handling_guidance",
            }
        )

    elif "rg 271" in name or "rg271" in name:
        metadata.update(
            {
                "document_type": "regulatory_guidance",
                "provider_or_regulator": "ASIC",
                "product_type": "complaints_dispute_resolution",
                "source_category": "regulatory_obligation",
            }
        )

    elif "info 253" in name or "info253" in name:
        metadata.update(
            {
                "document_type": "regulatory_guidance",
                "provider_or_regulator": "ASIC",
                "product_type": "claims_handling",
                "source_category": "regulatory_obligation",
            }
        )

    elif "general insurance code" in name or "code of practice" in name:
        metadata.update(
            {
                "document_type": "industry_code",
                "provider_or_regulator": "Insurance Council of Australia",
                "product_type": "general_insurance",
                "source_category": "industry_code",
            }
        )

    elif "cps 230" in name or "cps230" in name or "apra" in name:
        metadata.update(
            {
                "document_type": "prudential_standard",
                "provider_or_regulator": "APRA",
                "product_type": "operational_risk",
                "source_category": "enterprise_risk_control",
            }
        )

    return metadata


def build_source_reference(document_name: str, page_number: int) -> str:
    """
    Creates a simple citation-friendly source reference.
    """
    stem = Path(document_name).stem
    return f"{stem}, page {page_number}"
