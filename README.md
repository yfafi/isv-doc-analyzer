# ISV Doc Analyzer

Outil d'analyse automatique de documentation éditeur (ISV) pour la qualification de progiciels sur OpenShift.

## Problème

Dans le cadre du programme MoveToCloud2027, chaque progiciel éditeur doit être qualifié avant déploiement sur OpenShift. Aujourd'hui, cette qualification commence par une étape manuelle : un consultant lit la documentation éditeur (souvent 100+ pages, pensée pour un déploiement VM) et en extrait les prérequis techniques qu'il mappe ensuite vers les concepts OpenShift (SCC, RBAC, PVC, NetworkPolicies, etc.).

Ce travail prend **1 à 2 jours par progiciel**, est répétitif, et constitue le principal bottleneck de l'onboarding applicatif.

Les outils déterministes du pipeline existant (Conftest/OPA, kube-linter, kubeconform) interviennent **après** — ils valident un Helm chart ou un manifest YAML une fois qu'il existe. Mais personne n'automatise la première étape : lire la doc éditeur et en extraire les spécifications OpenShift.

**Lightspeed** (Ansible, OpenShift) ne couvre pas non plus ce besoin : il assiste dans la console ou dans Ansible, pas en amont sur de la documentation externe.

## Solution

ISV Doc Analyzer prend un document éditeur (PDF, Markdown, texte) en entrée et produit un **rapport de qualification structuré** :

```
Doc éditeur (PDF) → [ISV Doc Analyzer] → Rapport de qualification OpenShift
                                               │
                                               ├── Prérequis réseau → Services, Routes, NetworkPolicies
                                               ├── Prérequis stockage → PVC, StorageClass (RWO/RWX)
                                               ├── Prérequis sécurité → SCC, RBAC, ServiceAccount
                                               ├── Dépendances externes → Operators, services externes
                                               ├── Ressources compute → Requests/Limits, HPA
                                               ├── Alertes d'incompatibilité → 🔴 🟡 🟢 classées
                                               └── Checklist OK/KO → Verdict par critère
```

Le rapport alimente directement le pipeline de qualification existant, en remplaçant 1-2 jours de lecture manuelle par ~2 heures de revue assistée.

## Utilisation

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-..."

python src/analyzer.py document_editeur.pdf
python src/analyzer.py document_editeur.pdf --model claude-sonnet-5
```

Sortie : un fichier `*_qualification_report.md` dans le même répertoire.

## Exemple

Voir le dossier `examples/` :
- `uipath_orchestrator_install_guide.md` — documentation simulée d'un éditeur RPA
- `uipath_orchestrator_qualification_report.md` — rapport de qualification généré

## Roadmap

| Phase | Objectif | Quarter |
|-------|----------|---------|
| **1 — MVP** | Script fonctionnel + prompt structuré + exemple UiPath | Q actuel |
| **2 — Intégration pipeline** | Sortie JSON compatible Conftest, intégration CI/CD | Q+1 |
| **3 — Multi-sources** | Support Word/HTML, enrichissement par base de connaissances des qualifs passées | Q+2 |
| **4 — Interface** | CLI enrichie ou interface web, feedback loop consultants | Q+3 |
