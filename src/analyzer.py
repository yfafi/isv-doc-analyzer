#!/usr/bin/env python3
"""
ISV Doc Analyzer — Qualification de documentation éditeur pour déploiement OpenShift.
Prend un PDF ou fichier texte éditeur en entrée, produit un rapport de qualification structuré.
"""

import anthropic
import base64
import sys
from pathlib import Path

SYSTEM_PROMPT = """Tu es un expert Red Hat OpenShift chargé de qualifier des progiciels tiers (ISV) pour déploiement sur un cluster OpenShift de production.

On te fournit la documentation d'un éditeur logiciel. Ta mission :
1. Extraire TOUS les prérequis techniques (même implicites)
2. Les mapper vers les concepts OpenShift correspondants
3. Identifier les incompatibilités et points de friction

Sois exhaustif : les informations manquantes ou ambiguës sont aussi importantes que celles explicitement documentées. Signale ce que l'éditeur ne dit PAS mais qu'un consultant doit vérifier.

Produis un rapport structuré en Markdown avec les sections suivantes :

## 1. Résumé
- Nom, version, éditeur
- Description fonctionnelle (2-3 lignes)
- Architecture applicative (monolithique, microservices, composants)

## 2. Prérequis réseau
Tableau : Port | Protocole | Usage | Mapping OpenShift (Service, Route, NetworkPolicy)

## 3. Prérequis stockage
Tableau : Volume | Taille min | Mode d'accès (RWO/RWX) | Mapping OpenShift (PVC, StorageClass)

## 4. Prérequis sécurité
- User requis (root / non-root / UID spécifique)
- Capabilities Linux nécessaires
- SCC OpenShift recommandé (restricted-v2, nonroot-v2, anyuid, privileged)
- ServiceAccount et rôles RBAC nécessaires
- Certificats TLS requis

## 5. Dépendances externes
Tableau : Composant | Version | Obligatoire/Optionnel | Déploiement OpenShift recommandé (Operator, Helm, externe)

## 6. Ressources compute
- CPU et mémoire par composant (requests / limits recommandés)
- Nombre de réplicas recommandé (dev / prod)
- Considérations HPA

## 7. Alertes d'incompatibilité
Classées par sévérité :
- 🔴 BLOQUANT : empêche le déploiement sans dérogation ou workaround
- 🟡 ATTENTION : nécessite une configuration spécifique OpenShift
- 🟢 OK : compatible par défaut avec OpenShift

## 8. Checklist de qualification
Verdict par critère :
- SCC compatible (restricted-v2 par défaut)
- RBAC minimal défini
- Stockage compatible avec le cluster
- Réseau documenté (ports, flux)
- Images depuis registry approuvé
- Resource requests/limits définis
- Health checks (liveness/readiness) documentés
- Helm chart ou Operator disponible
- Stratégie de backup documentée
- Logs en stdout/stderr (compatible collecte centralisée)
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
                        "text": "Analyse cette documentation éditeur et produis le rapport de qualification OpenShift complet.",
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
                    "Analyse cette documentation éditeur et produis le rapport "
                    "de qualification OpenShift complet.\n\n---\n\n" + content
                ),
            }
        ],
    )

    return message.content[0].text


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyzer.py <chemin_doc> [--model MODEL]")
        print("Formats supportés : .pdf, .md, .txt")
        print("Modèle par défaut : claude-sonnet-5")
        sys.exit(1)

    doc_path = sys.argv[1]
    model = "claude-sonnet-5"

    if "--model" in sys.argv:
        idx = sys.argv.index("--model")
        if idx + 1 < len(sys.argv):
            model = sys.argv[idx + 1]

    if not Path(doc_path).exists():
        print(f"Fichier introuvable : {doc_path}")
        sys.exit(1)

    ext = Path(doc_path).suffix.lower()

    print(f"Analyse en cours : {doc_path}")
    print(f"Modèle : {model}")
    print("---")

    if ext == ".pdf":
        report = analyze_pdf(doc_path, model)
    elif ext in (".md", ".txt"):
        report = analyze_text(doc_path, model)
    else:
        print(f"Format non supporté : {ext}")
        sys.exit(1)

    output_name = Path(doc_path).stem + "_qualification_report.md"
    output_path = Path(doc_path).parent / output_name
    output_path.write_text(report)

    print(report)
    print(f"\n--- Rapport sauvegardé : {output_path}")


if __name__ == "__main__":
    main()
