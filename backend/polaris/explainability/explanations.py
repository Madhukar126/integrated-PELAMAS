from __future__ import annotations


def summarize_risk(score: float, contributors: list[dict], scenario: str = "Transport delay") -> str:
    summary = [
        f"{scenario} produced an overall operational risk score of {score:.1f}/100.",
        "Key contributors are:"
    ]
    for item in contributors:
        summary.append(f"- {item['label']}: {item['value']}")
    summary.append(
        "Transport T04 is delayed by 8 days and carries Generator Filter GF14. "
        "Bharati's projected spare inventory may fall below minimum reserve before the shipment arrives. "
        "Generator G07 supports Mission M12."
    )
    return " ".join(summary)
