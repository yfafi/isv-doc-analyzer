#!/usr/bin/env python3
"""
ISV Doc Analyzer — Analyze vendor documentation for OpenShift deployment qualification.
Takes a PDF or text file as input, produces a structured qualification report.
"""

import anthropic
import base64
import sys
from pathlib import Path

SYSTEM_PROMPT = """You are a Red Hat OpenShift expert responsible for qualifying third-party software (ISV) for deployment on a production OpenShift cluster.

You are given the installation documentation from a software vendor. Your mission:
1. Extract ALL technical prerequisites (including implicit ones)
2. Map them to the corresponding OpenShift concepts
3. Identify incompatibilities and friction points

Be exhaustive: missing or ambiguous information is just as important as what is explicitly documented. Flag what the vendor does NOT say but a consultant must verify.

Produce a structured Markdown report with the following sections:

## 1. Summary
- Name, version, vendor
- Functional description (2-3 lines)
- Application architecture (monolithic, microservices, components)

## 2. Networking requirements
Table: Port | Protocol | Usage | OpenShift mapping (Service, Route, NetworkPolicy)

## 3. Storage requirements
Table: Volume | Min size | Access mode (RWO/RWX) | OpenShift mapping (PVC, StorageClass)

## 4. Security requirements
- Required user (root / non-root / specific UID)
- Required Linux capabilities
- Recommended OpenShift SCC (restricted-v2, nonroot-v2, anyuid, privileged)
- Required ServiceAccount and RBAC roles
- TLS certificates required

## 5. External dependencies
Table: Component | Version | Required/Optional | Recommended OpenShift deployment (Operator, Helm, external)

## 6. Compute resources
- CPU and memory per component (recommended requests / limits)
- Recommended replica count (dev / prod)
- HPA considerations

## 7. Compatibility alerts
Classified by severity:
- 🔴 BLOCKER: prevents deployment without exception or workaround
- 🟡 WARNING: requires specific OpenShift configuration
- 🟢 OK: compatible with OpenShift defaults

## 8. Qualification checklist
Verdict per criterion:
- SCC compatible (restricted-v2 by default)
- Minimal RBAC defined
- Storage compatible with cluster
- Networking documented (ports, flows)
- Images from approved registry
- Resource requests/limits defined
- Health checks (liveness/readiness) documented
- Helm chart or Operator available
- Backup strategy documented
- Logs to stdout/stderr (compatible with centralized collection)
"""


def analyze_pdf(pdf_path: str, model: str) -> str:
    client = anthropic.Anthropic()

    pdf_data = Path(pdf_path).read_bytes()
    pdf_base64 = base64.standard_b64encode(pdf_data).decode("utf-8")

    message = client.messages.create(
        model=model,
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_base64,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Analyze this vendor documentation and produce the full OpenShift qualification report.",
                    },
                ],
            }
        ],
    )

    return message.content[0].text


def analyze_text(text_path: str, model: str) -> str:
    client = anthropic.Anthropic()

    content = Path(text_path).read_text()

    message = client.messages.create(
        model=model,
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    "Analyze this vendor documentation and produce the full "
                    "OpenShift qualification report.\n\n---\n\n" + content
                ),
            }
        ],
    )

    return message.content[0].text


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyzer.py <doc_path> [--model MODEL]")
        print("Supported formats: .pdf, .md, .txt")
        print("Default model: claude-sonnet-5")
        sys.exit(1)

    doc_path = sys.argv[1]
    model = "claude-sonnet-5"

    if "--model" in sys.argv:
        idx = sys.argv.index("--model")
        if idx + 1 < len(sys.argv):
            model = sys.argv[idx + 1]

    if not Path(doc_path).exists():
        print(f"File not found: {doc_path}")
        sys.exit(1)

    ext = Path(doc_path).suffix.lower()

    print(f"Analyzing: {doc_path}")
    print(f"Model: {model}")
    print("---")

    if ext == ".pdf":
        report = analyze_pdf(doc_path, model)
    elif ext in (".md", ".txt"):
        report = analyze_text(doc_path, model)
    else:
        print(f"Unsupported format: {ext}")
        sys.exit(1)

    output_name = Path(doc_path).stem + "_qualification_report.md"
    output_path = Path(doc_path).parent / output_name
    output_path.write_text(report)

    print(report)
    print(f"\n--- Report saved: {output_path}")


if __name__ == "__main__":
    main()
