# ISV Doc Analyzer

Automated analysis of vendor (ISV) documentation for OpenShift deployment qualification.

## Problem

Before deploying any third-party software on OpenShift, a consultant must first read the vendor's installation documentation — often 100+ pages written for traditional VM deployments, not Kubernetes. The critical information is scattered: network ports in chapter 4, storage requirements in an appendix, security constraints buried in system prerequisites.

The consultant spends **1 to 2 days per application** extracting technical prerequisites and mentally mapping them to OpenShift concepts (SCC, RBAC, PVC, NetworkPolicies, etc.). For migration programs involving 30-50 applications, this adds up to weeks of repetitive work before a single line of YAML is written.

Existing deterministic tools in the qualification pipeline (Conftest/OPA, kube-linter, kubeconform) operate **downstream** — they validate a Helm chart or manifest once it exists. But no one automates the **upstream** step: reading vendor documentation and extracting OpenShift specifications.

**Red Hat Lightspeed** doesn't cover this either — it assists inside the OpenShift console or Ansible, not upstream on external vendor documentation.

## Solution

ISV Doc Analyzer takes a vendor document (PDF, Markdown, text) as input and produces a **structured qualification report**:

```
Vendor doc (PDF) → [ISV Doc Analyzer] → OpenShift Qualification Report
                                               │
                                               ├── Networking     → Services, Routes, NetworkPolicies
                                               ├── Storage        → PVC, StorageClass (RWO/RWX)
                                               ├── Security       → SCC, RBAC, ServiceAccount
                                               ├── Dependencies   → Operators, external services
                                               ├── Compute        → Requests/Limits, HPA
                                               ├── Compatibility  → 🔴 🟡 🟢 rated alerts
                                               └── Checklist      → Pass/Fail per criterion
```

The report feeds directly into the existing qualification pipeline, replacing 1-2 days of manual reading with ~2 hours of assisted review.

## Usage

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-..."

python src/analyzer.py vendor_doc.pdf
python src/analyzer.py vendor_doc.pdf --model claude-sonnet-5
```

Output: a `*_qualification_report.md` file in the same directory.

## Example

See the `examples/` folder:
- `uipath_orchestrator_install_guide.md` — simulated vendor documentation for a RPA platform
- `uipath_orchestrator_qualification_report.md` — generated qualification report

## Roadmap

| Phase | Goal | Timeline |
|-------|------|----------|
| **1 — MVP** | Working script + structured prompt + UiPath example | Current quarter |
| **2 — Pipeline integration** | JSON output compatible with Conftest, CI/CD integration | Q+1 |
| **3 — Multi-source** | Word/HTML support, knowledge base from past qualifications | Q+2 |
| **4 — Interface** | CLI improvements or web UI, consultant feedback loop | Q+3 |

## Context

The `docs/` folder contains research articles on AI agents for Red Hat consultants that led to this project.
