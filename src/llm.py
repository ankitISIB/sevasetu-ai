import os
from google import genai


def investigate_area(area_data):
    """
    Send structured welfare evidence to Gemini
    and return an administrative assessment.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return "Gemini API key not found."

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are SevaSetu AI, an AI assistant supporting government
welfare officers.

Analyze the following welfare-service evidence.

IMPORTANT RULES:
- Use ONLY the information provided.
- Do not invent facts.
- Do not accuse anyone of fraud or wrongdoing.
- An anomaly is NOT proof of fraud.
- Do not make eligibility, rejection, or government decisions.
- Provide recommendations for an officer to review.
- Keep the assessment concise and action-oriented.

WELFARE AREA DATA:

Area: {area_data.get("area", "Unknown")}
District: {area_data.get("district", "Unknown")}
Block: {area_data.get("block", "Unknown")}

Eligible beneficiaries: {area_data.get("eligible", 0)}
Received benefits: {area_data.get("received", 0)}
Coverage: {area_data.get("coverage", 0):.1f}%
Coverage gap: {area_data.get("coverage_gap", 0):.1f}%

Applications: {area_data.get("applications", 0)}
Pending cases: {area_data.get("pending", 0)}
Pending rate: {area_data.get("pending_rate", 0):.1f}%

Rejected cases: {area_data.get("rejected", 0)}
Rejection rate: {area_data.get("rejection_rate", 0):.1f}%

Average processing time: {area_data.get("processing_days", 0):.1f} days

Priority score: {area_data.get("priority_score", 0):.1f}/100
Risk level: {area_data.get("risk_level", "UNKNOWN")}
Anomaly status: {area_data.get("anomaly_status", "Unknown")}

Provide:

1. Situation summary
2. Key evidence
3. Possible administrative explanation
4. Recommended officer actions
5. Whether citizen outreach may be worth reviewing

Clearly state that the final decision belongs to the officer.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt
        )

        return response.text

    except Exception as e:
        return f"Gemini error: {str(e)}"
