# Article Update Guide — Step by Step

Follow these 5 steps in order. Each step tells you exactly what to find and what to replace/add in your Google Doc.

---

## Step 1 — Update the title

**Find:**
> How AI Agents Are Transforming Our Daily Work in the Field

**Replace with:**
> How AI Agents Are Transforming Our Daily Work in the Field — From Reflection to a Working POC

---

## Step 2 — Update the Introduction (Section 1)

**Find the last paragraph of Section 1:**
> The goal of this article: understand what an AI agent technically is, why it's becoming viable now, and identify concrete use cases for our job.

**Replace with:**
> The goal of this article: understand what an AI agent technically is, why it's becoming viable now, and identify concrete use cases for our job. Beyond theory, this article also presents a **proof of concept built from a real field need** — automating the analysis of vendor documentation for OpenShift deployment qualification.

---

## Step 3 — Strengthen Section 4a (Documentation analysis)

**Find the entire section 4a:**
> ### a) Accelerating technical documentation
>
> **The problem:**
> You get an editor's documentation to deploy their application on OpenShift. 200 pages of poorly structured PDF, with prerequisites buried in multiple chapters. You need to extract: network ports, dependencies (database, cache), required volumes, security constraints.
>
> **The AI agent:**
> You give it the PDF, it automatically extracts the essentials: network flow table, list of dependencies, sizing. It even identifies potential incompatibilities with OpenShift (e.g., the application wants to run as root).
>
> **The gain:**
> Going from 1-2 days of reading/note-taking to 2 hours of assisted review. You keep control, but eliminate the grunt work.

**Replace with:**
> ### a) Accelerating vendor documentation analysis
>
> **The problem:**
> Before deploying any third-party software on OpenShift, a consultant must read the vendor's documentation — often 100+ pages written for traditional VM deployments, not Kubernetes. Network ports are in chapter 4, storage requirements in an appendix, security constraints buried in system prerequisites. The consultant spends 1-2 days extracting this information and mentally mapping it to OpenShift concepts: Does this app need a specific SCC? Will the storage require RWX? Does it try to bind to a privileged port?
>
> This is not a theoretical problem. On migration programs involving dozens of applications, this manual analysis is the **main bottleneck** of application onboarding. Deterministic tools in the pipeline (Conftest/OPA, kube-linter, kubeconform) validate manifests — but someone still has to read the vendor doc and translate it into OpenShift specs first.
>
> **The AI agent:**
> You give it the vendor PDF. It extracts all technical prerequisites — including implicit ones — and maps each to the corresponding OpenShift concept: Services, Routes, NetworkPolicies, PVCs, SCC, RBAC. It flags what the vendor does NOT say but that a consultant must verify. It produces a structured qualification report with a pass/fail checklist.
>
> **The gain:**
> 1-2 days of reading replaced by ~2 hours of assisted review. The consultant still validates everything, but the extraction and mapping work is done. On a program with 30-50 applications, this saves weeks.
>
> **This use case is the one I chose to turn into a working POC — see Section 7.**

---

## Step 4 — Add a NEW section before the Conclusion

**Find:**
> ## 7. Conclusion

**Add this entire section BEFORE the Conclusion (the Conclusion becomes Section 8):**

> ## 7. From Theory to Practice: ISV Doc Analyzer
>
> The use cases described above are not just ideas — one of them directly addresses a pain point I face on my current engagement. This led me to build a working proof of concept.
>
> ### The field problem
>
> On a large-scale migration program, each third-party application must be qualified before deployment on OpenShift. The qualification starts with reading the vendor's installation documentation and extracting all the technical prerequisites: networking, storage, security, dependencies, compute resources.
>
> This documentation is written for VM-based deployments. The consultant must read it end-to-end and mentally translate every requirement into OpenShift terms:
>
> - "The app listens on port 443" → Route with TLS termination + Service, but also: the app tries to bind to a privileged port → SCC issue
> - "Requires shared storage for packages" → PVC with RWX access mode → does the cluster have NFS or CephFS?
> - "Runs under user orchestrator (UID 1000)" → fixed UID, incompatible with restricted-v2 SCC default
> - "Logs written to /var/log/app/" → filesystem logs, not stdout → invisible to OpenShift logging stack
>
> This takes 1-2 days per application. Multiply by 30-50 apps on a migration program, and it becomes the main bottleneck.
>
> **Red Hat Lightspeed** doesn't address this. Lightspeed assists inside the OpenShift console or Ansible — it helps once you know what to do. **ISV Doc Analyzer helps you figure out what to do.**
>
> ### What the POC does
>
> ISV Doc Analyzer is a Python script that takes a vendor document (PDF, Markdown, text) as input and produces a structured OpenShift qualification report:
>
> ```
> Vendor doc (PDF) → [ISV Doc Analyzer] → OpenShift Qualification Report
>                                                │
>                                                ├── Networking     → Services, Routes, NetworkPolicies
>                                                ├── Storage        → PVC, StorageClass (RWO/RWX)
>                                                ├── Security       → SCC, RBAC, ServiceAccount
>                                                ├── Dependencies   → Operators, external services
>                                                ├── Compute        → Requests/Limits, HPA
>                                                ├── Compatibility  → 🔴 🟡 🟢 rated alerts
>                                                └── Checklist      → Pass/Fail per criterion
> ```
>
> ### Example: UiPath Orchestrator
>
> As a concrete test, I ran the analyzer against a simulated UiPath Orchestrator installation guide. Here's what it found:
>
> **Blockers identified:**
> - The app binds to port 443 directly → requires `CAP_NET_BIND_SERVICE` → incompatible with non-privileged pods on OpenShift. Workaround: configure internal port > 1024, let the Route handle TLS.
> - HA mode requires RWX shared storage for packages and media → cluster must have NFS or CephFS StorageClass.
>
> **Warnings:**
> - Fixed UID 1000 → incompatible with `restricted-v2` SCC (random UID). Workaround: use `nonroot-v2` SCC.
> - Logs written to filesystem, not stdout → invisible to cluster logging. Needs sidecar or app reconfiguration.
> - TLS certificates expected from system keystore → must be mounted via Kubernetes Secrets instead.
>
> **Checklist output:**
>
> | Criterion | Verdict |
> |-----------|---------|
> | SCC compatible (restricted-v2) | ❌ FAIL |
> | Minimal RBAC defined | ✅ PASS |
> | Storage compatible | ⚠️ Conditional |
> | Networking documented | ✅ PASS |
> | Images from approved registry | ❓ To verify |
> | Resource requests/limits | ✅ PASS |
> | Health checks documented | ✅ PASS |
> | Helm chart / Operator available | ❓ To verify |
> | Logs to stdout/stderr | ❌ FAIL |
>
> **Overall: 🟡 DEPLOYABLE WITH ADAPTATIONS** — 4 actions required, 3 clarifications needed from the vendor.
>
> This is exactly the kind of insight that a consultant discovers after a full day of reading. The agent surfaces it in minutes.
>
> ### Roadmap
>
> | Phase | Goal | Timeline |
> |-------|------|----------|
> | **1 — MVP** | Working script + structured prompt + UiPath example | Current quarter ✅ |
> | **2 — Pipeline integration** | JSON output compatible with Conftest, CI/CD integration | Q+1 |
> | **3 — Multi-source** | Word/HTML support, knowledge base from past qualifications | Q+2 |
> | **4 — Interface** | CLI improvements or web UI, consultant feedback loop | Q+3 |
>
> The source code is available on GitHub (internal access).

---

## Step 5 — Update the Conclusion (now Section 8)

**Find:**
> ## 7. Conclusion
>
> AI agents are not a passing trend. They represent an evolution of work tools, just as Kubernetes did for application deployment.
>
> As consultants, understanding and mastering these technologies now can be really useful because:
> - Clients may ask the question (trending topic)
> - Productivity gains (troubleshooting, code generation, doc analysis)
> - Identify use cases that work in daily practice
>
> AI doesn't replace the consultant, it eliminates repetitive tasks. It's up to us to define how it can be useful.

**Replace with:**
> ## 8. Conclusion
>
> AI agents are not a passing trend. They represent an evolution of work tools, just as Kubernetes did for application deployment.
>
> As consultants, understanding and mastering these technologies now can be really useful because:
> - Clients may ask the question (trending topic)
> - Productivity gains (troubleshooting, code generation, doc analysis)
> - Identifying use cases that work in daily practice — and building tools around them
>
> The ISV Doc Analyzer POC is a concrete example of this approach: a real field problem, a working solution, and a roadmap for continuous improvement. It doesn't replace Red Hat Lightspeed — it fills a gap that Lightspeed doesn't cover: the upstream analysis of vendor documentation before deployment work even begins.
>
> AI doesn't replace the consultant, it eliminates repetitive tasks. It's up to us to build the tools that make it useful.

---

## Summary of changes

| Step | Section | What changed |
|------|---------|-------------|
| 1 | Title | Added "From Reflection to a Working POC" |
| 2 | Introduction | Added one sentence about the POC |
| 3 | Section 4a | Rewritten with real field context + link to POC section |
| 4 | New Section 7 | Full POC presentation: problem, solution, UiPath example, roadmap |
| 5 | Conclusion (now 8) | Updated to reference the POC and Lightspeed positioning |

## Publishing checklist

1. ☐ Open Google Doc
2. ☐ Apply Steps 1-5 above (copy-paste)
3. ☐ Read through once to check flow
4. ☐ Copy from Google Doc to Red Hat internal blog
5. ☐ Add the UiPath checklist table as a screenshot if the blog doesn't support Markdown tables
6. ☐ Share the blog post link with your manager
