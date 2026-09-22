# How AI Agents Are Transforming Our Daily Work in the Field

## 1. Introduction 

We hear about AI everywhere, but what does it actually change for us in the field? Between marketing announcements and the reality of our missions, there's a gap. However, one technology is starting to have a real impact on our daily work: **AI agents**.

The difference with traditional chatbots? An AI agent doesn't just answer a question. It can **act**: query APIs, analyze logs, generate code, cross-reference multiple sources of information. In short, execute tasks that we do manually today.

The goal of this article: understand what an AI agent technically is, why it's becoming viable now, and identify concrete use cases for our job.

---

## 2. What Is an AI Agent? 

Before talking about AI agents, let's clarify the difference with what we already know.

**A chatbot** (ChatGPT, Copilot in simple mode): you ask a question, it answers. It's text generation, period. Useful, but passive.

**An AI agent**: you give it a goal, and it breaks down the problem, uses tools, analyzes results, and adjusts its approach. It's **autonomous execution**.

### The 4 characteristics of an AI agent

1. **Understands a global objective**  
   Not just "answer this question," but "diagnose why this pod keeps crashing."

2. **Breaks down into subtasks**  
   It will identify that it needs to: check logs, analyze Kubernetes events, look at resource limits, cross-reference with the deployment config.

3. **Uses tools**  
   It can execute `kubectl`, query Prometheus, read documentation, call APIs. It's not limited to generating text.

4. **Adapts based on results**  
   If logs show an OOMKilled error, it will dig into memory limits. If it's a network error, it will check NetworkPolicies. It adjusts its reasoning.

### Concrete example

You ask an agent: *"Why is my application not responding on OpenShift?"*

- It queries the pods → detects a CrashLoopBackOff
- It reads the logs → sees a database connection error
- It checks the database service → detects it's not in the same namespace
- It analyzes the NetworkPolicies → identifies the blocking issue
- It proposes a correction with the YAML manifest

All of this in a few seconds, where we would spend 15-30 minutes investigating manually.

---

## 3. Why the Hype Now?

AI agents are not a new concept. But three elements have recently converged to make them finally **usable in production**.

### 1. LLMs have become powerful enough

Current language models (Claude, Llama 3...) understand technical context. They can read Kubernetes logs, analyze YAML, understand system errors. Before 2023, models hallucinated too much or didn't handle complexity. Today, it's workable.

### 2. The tool ecosystem is mature

Kubernetes, Ansible, Terraform, cloud providers... all expose structured APIs. An agent can easily interact with these systems. The tools we use daily have become "agent-friendly."

### 3. The need for intelligent automation

Classic scripts (bash, Python) have their limits: they do exactly what you tell them, nothing more. As soon as there's variability (different log formats, non-standard configurations), they break. AI agents bring **adaptability** without rewriting the script for each edge case.

### The available technical ecosystem

On the Red Hat stack side, several building blocks are stabilizing:

- **OpenShift AI**: operator to deploy and manage models (LLMs, classic ML). Based on Kubeflow.
- **RHEL AI**: LLM models packaged for RHEL, with InstructLab for local fine-tuning.
- **Lightspeed**: agents integrated into Ansible Automation Platform and OpenShift Console. Generate YAML code, playbooks, assist with troubleshooting.

What changes compared to public cloud solutions: everything runs on-premise, data doesn't leave the datacenter. Critical for regulated sectors (banking, healthcare, defense).

Technically, these tools expose the same primitives as general-purpose agents (access to Kubernetes APIs, Ansible, registries), but with models trained on Red Hat documentation and code.

### Why it concerns us

Some tasks we repeat (reading docs, troubleshooting, code generation) can be accelerated.

---

## 4. Concrete Use Cases for Red Hat Consultants

Concretely, where can an AI agent save us time on missions? Here are a few use cases based on tasks a consultant might do regularly.

### a) Accelerating technical documentation

**The problem:**  
You get an editor's documentation to deploy their application on OpenShift. 200 pages of poorly structured PDF, with prerequisites buried in multiple chapters. You need to extract: network ports, dependencies (database, cache), required volumes, security constraints.

**The AI agent:**  
You give it the PDF, it automatically extracts the essentials: network flow table, list of dependencies, sizing. It even identifies potential incompatibilities with OpenShift (e.g., the application wants to run as root).

**The gain:**  
Going from 1-2 days of reading/note-taking to 2 hours of assisted review. You keep control, but eliminate the grunt work.

---

### b) Intelligent troubleshooting

**The problem:**  
OpenShift cluster in production, an application is degrading. Client pressure. You need to correlate: application logs, Kubernetes events, Prometheus metrics, pod configuration. Each lead takes 10-15 minutes to investigate.

**The AI agent:**  
You give it the objective: "Diagnose why app XYZ has been slow for the past hour." It automatically queries logs, events, metrics, cross-references with the app documentation, and gives you 2-3 hypotheses ranked by probability with evidence.

**The gain:**  
Diagnosis in 5 minutes instead of 30-45 minutes. In production, every minute counts.

---

### c) Assisted migration (VM to containers)

**The problem:**  
Migrate 50 applications running on VMs to OpenShift. Each app has its specificities: system dependencies, network configuration, volume mounts. Doing this manually means weeks of repetitive work.

**The AI agent:**  
It analyzes the current config of each VM (installed packages, active services, open ports), proposes a Dockerfile + adapted Kubernetes manifests, and detects incompatibilities (e.g., the app uses an unsupported NFS filesystem).

**The gain:**  
Industrialization of standard cases. The consultant focuses on the 10 complex apps, the agent handles the other 40. In the end, the consultant still keeps control to validate or verify.

---

### d) Infrastructure code generation

**The problem:**  
Create Ansible playbooks, CI/CD pipelines, Kubernetes NetworkPolicies. It's repetitive, prone to syntax errors, and must respect the client's security standards.

**The AI agent:**  
From functional specs ("deploy this app with access only from the ingress"), it generates compliant manifests, with best practices (resource limits, security context, network policies).

**The gain:**  
Zero syntax errors, automatic compliance with standards, time saved on "plumbing" tasks.

---

### e) Monitoring and continuous learning

**The problem:**  
New OpenShift versions every 3-4 months, CVEs, breaking changes. Reading all the release notes, identifying what impacts our client projects is time-consuming.

**The AI agent:**  
It summarizes release notes, identifies changes that impact your ongoing projects (e.g., "this API is deprecated, used in 3 of your clusters"), proposes corrective actions.

**The gain:**  
Staying up to date without spending 5 hours/week monitoring. The agent does the first pass, you validate.

---

## 5. What It Changes for the Consultant Role

Let's be clear: an AI agent won't replace a consultant. But it will **redefine** where we spend our time. It acts as their assistant.

### What the AI Agent Does NOT Do

❌ **Understand political/organizational context**  
An agent doesn't detect unspoken issues in meetings, power dynamics between teams, or implicit budget constraints.

❌ **Make strategic architecture decisions**  
Choosing between a multi-cluster deployment or federation, balancing performance vs. cost, adapting a solution to business constraints... that remains the job of consultants or architects.

❌ **Support change management**  
Training teams, reassuring during migration, managing resistance... humans remain essential.

### What the AI Agent DOES

✅ **Eliminates repetitive and low-value tasks**  
Reading docs, extracting requirements, generating boilerplate code, debugging syntax errors.

✅ **Accelerates the understanding phase**  
Analyzing an existing cluster, understanding legacy architecture, identifying dependencies between components.

✅ **Frees up time for support**  
Less time on operational tasks = more time with the client, understanding their real needs and co-building the solution.

The consultant:

- Remains the expert in architecture and strategic decisions
- Also becomes an orchestrator of AI agents for operational tasks
- Spends more time client-side (added value) and less on repetitive technical tasks
- Can manage more projects in parallel thanks to the acceleration of "mechanical" phases

**AI doesn't replace the consultant, it allows them to rise to a higher level.** To spend less time in the weeds and more time on strategy and support.

---

## 6. Where to Start?

Concretely, how to get started without drowning in the ambient noise around AI?

### 1. Experiment on your own tasks

The best way to understand is to test. A few leads:

- **Test existing tools**: GitHub Copilot for code, Claude with tool access, Red Hat's Lightspeed assistants (if available in your context).
- **Identify 1-2 repetitive tasks** in your daily mission work. For example: "I always spend 2 hours extracting info from an editor's docs" or "I often debug the same type of Kubernetes error."
- **Measure the gain**: no need for complex metrics, just note how much time you actually save.

The goal is not to automate everything at once, but to **validate usefulness on a concrete case**.

### 2. Understand the limits

AI agents are not magic. You need to know their weaknesses:

- **Hallucinations**: they can invent commands, APIs, or configs that don't exist. Always verify.
- **Data security**: be careful what you send to public APIs (OpenAI, etc.). Prefer on-premise or Red Hat solutions for sensitive data.
- **Limited context**: an agent can't analyze 50 log files of 1GB each. You need to prepare the ground.

Understanding these limits allows you to use agents **where they're effective**, not everywhere.

### 3. Share with the community

AI applied to infrastructure is still being built. Sharing experiences (what works, what doesn't) allows:

- Learning collectively
- Identifying real use cases vs. trends
- Feeding back concrete needs to Red Hat

Whether internally or externally (blogs, meetups), field feedback has value.

---

## 7. Conclusion

AI agents are not a passing trend. They represent an evolution of work tools, just as Kubernetes did for application deployment.

As consultants, understanding and mastering these technologies now can be really useful because:
- Clients may ask the question (trending topic)
- Productivity gains (troubleshooting, code generation, doc analysis)
- Identify use cases that work in daily practice

AI doesn't replace the consultant, it eliminates repetitive tasks. It's up to us to define how it can be useful.
