import os
from dotenv import load_dotenv
from google import genai
import json

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


def generate_response(prompt):
    if not prompt or not prompt.strip():
        raise ValueError("prompt cannot be empty")

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    response_json = json.loads(response.text)

    # Extract individual parameters
    response_language = response_json.get("response_language")
    direct_answer = response_json.get("direct_answer", {})
    key_findings = response_json.get("key_findings", [])
    evidence_ids = response_json.get("evidence_ids", [])

    # Print individual parameters//temp print 
    print("\n========== LLM RESPONSE ==========")

    print("\nResponse Language:")
    print(response_language)

    print("\nDirect Answer:")
    print(direct_answer.get("text"))

    print("\nKey Findings:")
    for index, finding in enumerate(key_findings, start=1):
        print(f"\nFinding {index}:")
        print(finding.get("text"))
        print("Evidence IDs:", finding.get("evidence_ids", []))

    print("\nFinal Evidence IDs:")
    print(evidence_ids)

    print("\n==================================")

    return response_json
