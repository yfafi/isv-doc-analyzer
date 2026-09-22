# Rapport de Qualification OpenShift — UiPath Orchestrator v2024.10

> Généré automatiquement par ISV Doc Analyzer

---

## 1. Résumé

| | |
|---|---|
| **Éditeur** | UiPath |
| **Produit** | Orchestrator |
| **Version** | 2024.10 |
| **Description** | Plateforme de gestion centralisée pour robots RPA — déploiement, monitoring, planification et audit des processus automatisés |
| **Architecture** | 3 composants : Web App (ASP.NET Core), Background Jobs Service, Webhook Service. Déployables ensemble ou séparément |

---

## 2. Prérequis réseau

| Port | Protocole | Direction | Usage | Mapping OpenShift |
|------|-----------|-----------|-------|-------------------|
| 443 | HTTPS | Entrant | Interface web + API REST | **Route** (edge TLS) + **Service** ClusterIP |
| 8080 | HTTP | Interne | Communication inter-services | **Service** ClusterIP (interne uniquement) |
| 9200 | TCP | Sortant | Elasticsearch | **NetworkPolicy** egress vers namespace/service Elasticsearch |
| 9300 | TCP | Sortant | Elasticsearch transport | **NetworkPolicy** egress (si Elasticsearch in-cluster) |
| 1433 | TCP | Sortant | SQL Server | **NetworkPolicy** egress — probablement externe au cluster |
| 6379 | TCP | Sortant | Redis | **NetworkPolicy** egress vers Redis (Operator ou externe) |
| 5672 | TCP | Sortant | RabbitMQ (AMQP) | **NetworkPolicy** egress vers RabbitMQ (optionnel) |
| 10000 | TCP | Entrant | Métriques Prometheus | **Service** ClusterIP + **ServiceMonitor** pour scraping |
| 636 | TCP | Sortant | LDAPS (authentification) | **NetworkPolicy** egress vers serveur LDAP externe |

**Actions requises :**
- Créer une **Route** TLS pour le port 443 (avec certificat via cert-manager ou fourni)
- Définir des **NetworkPolicies** restrictives : seuls les flux documentés ci-dessus doivent être autorisés
- Le port 10000 (métriques) doit être accessible par le Prometheus du cluster uniquement

---

## 3. Prérequis stockage

| Volume | Taille min | Mode d'accès | Contenu | Mapping OpenShift |
|--------|-----------|--------------|---------|-------------------|
| `/opt/uipath/orchestrator/packages/` | 50 Go | **RWX** | Packages NuGet (.nupkg) | PVC avec StorageClass **NFS ou CephFS** |
| `/opt/uipath/orchestrator/media/` | 100 Go | **RWX** | Captures d'écran, pièces jointes | PVC avec StorageClass **NFS ou CephFS** |
| `/var/log/uipath/` | 10 Go | RWO | Logs applicatifs | PVC standard (ou redirection stdout) |

**Points critiques :**
- Les volumes `packages` et `media` **doivent** être en RWX (ReadWriteMany) car partagés entre instances en mode HA → vérifier que le cluster dispose d'un StorageClass compatible (NFS, CephFS, Azure Files)
- Le volume `logs` peut être évité si on redirige les logs vers stdout/stderr (voir section Alertes)

---

## 4. Prérequis sécurité

### User et SCC

| Critère | Valeur documentée | Impact OpenShift |
|---------|-------------------|------------------|
| User runtime | `orchestrator` (UID 1000) | UID fixe → incompatible avec `restricted-v2` (UID aléatoire) |
| Root requis | Oui, pour installation et gestion des certificats | Pas nécessaire au runtime si les certs sont montés via Secret |
| Capabilities | `CAP_NET_BIND_SERVICE` (bind port 443) | Nécessite SCC custom ou passage au port > 1024 |

**SCC recommandé : `nonroot-v2` avec ajustements**
- Monter les certificats TLS via **Secret** Kubernetes au lieu du keystore système → supprime le besoin de root
- Utiliser un port > 1024 en interne (ex: 8443) et laisser la **Route** OpenShift gérer le TLS sur le port 443 → supprime le besoin de `CAP_NET_BIND_SERVICE`
- Fixer le `runAsUser: 1000` dans le SecurityContext du pod

### RBAC

| ServiceAccount | Rôle | Scope |
|----------------|------|-------|
| `uipath-orchestrator` | Accès aux Secrets (TLS, DB credentials) | Namespace applicatif |
| `uipath-orchestrator` | Accès aux ConfigMaps | Namespace applicatif |

### Certificats TLS
- Recommandation : utiliser **cert-manager** Operator pour la gestion automatique
- Alternative : créer un Secret TLS manuellement et le monter dans le pod

---

## 5. Dépendances externes

| Composant | Version | Obligatoire | Déploiement OpenShift recommandé |
|-----------|---------|-------------|----------------------------------|
| SQL Server | 2019+ | ✅ Oui | **Externe au cluster** — SQL Server n'a pas d'Operator mature pour OpenShift. Utiliser le SQL Server existant du client |
| Elasticsearch | 7.17.x / 8.x | ✅ Oui | **OpenShift Logging Operator** (basé sur OpenSearch) ou **ECK Operator** si licence Elastic |
| Redis | 6.x+ | ✅ Oui (si HA) | **Redis Operator** (via OperatorHub) — mode Sentinel |
| RabbitMQ | 3.11+ | ⚠️ Optionnel | **RabbitMQ Cluster Operator** (via OperatorHub) — uniquement si multi-nœuds |
| LDAP/AD | - | ⚠️ Si auth AD | **Externe** — connexion sortante LDAPS depuis le cluster |

---

## 6. Ressources compute

| Composant | CPU request | CPU limit | RAM request | RAM limit | Réplicas (prod) |
|-----------|------------|-----------|-------------|-----------|-----------------|
| Web App | 2 | 4 | 4 Gi | 8 Gi | 2 minimum |
| Background Jobs | 1 | 2 | 2 Gi | 4 Gi | 1 |
| Webhook Service | 500m | 1 | 1 Gi | 2 Gi | 1 |
| **Total minimum prod** | **5.5** | **11** | **11 Gi** | **22 Gi** | **4 pods** |

**Considérations HPA :**
- Web App éligible au HPA sur CPU (seuil 70%)
- Background Jobs : pas de scaling horizontal (traitement séquentiel)

---

## 7. Alertes d'incompatibilité

### 🔴 BLOQUANT

1. **`CAP_NET_BIND_SERVICE` requis pour port 443**
   L'application cherche à binder directement sur le port 443. Sur OpenShift, les pods non-privilegiés ne peuvent pas utiliser les ports < 1024.
   **Workaround :** configurer l'application sur un port > 1024 (ex: 8443) et utiliser une Route OpenShift pour exposer sur 443. Vérifier que la variable de configuration `ORCHESTRATOR_PORT` est disponible.

2. **Stockage RWX obligatoire en mode HA**
   Les volumes `packages` et `media` doivent être partagés entre instances. Si le cluster ne dispose pas de StorageClass RWX (NFS, CephFS), le mode HA est impossible.
   **Action :** vérifier la disponibilité d'un StorageClass RWX auprès de l'équipe plateforme.

### 🟡 ATTENTION

3. **UID fixe (1000) — incompatible avec `restricted-v2` par défaut**
   Le SCC `restricted-v2` d'OpenShift attribue des UID aléatoires. L'application attend UID 1000.
   **Workaround :** utiliser le SCC `nonroot-v2` et fixer `runAsUser: 1000` dans le Deployment. Nécessite validation par l'équipe sécurité.

4. **Logs écrits sur disque, pas stdout**
   Les logs sont écrits dans `/var/log/uipath/` en fichiers rotatifs. Cela empêche la collecte par le stack de logging OpenShift (Fluentd/Vector).
   **Workaround :** vérifier si UiPath supporte une option de redirection stdout, ou déployer un sidecar de collecte de logs.

5. **Accès au keystore système pour certificats TLS**
   L'application s'attend à lire les certificats depuis `/etc/ssl/certs/`. Sur OpenShift, on monte les certificats via des Secrets.
   **Workaround :** monter un Secret TLS sur le chemin attendu, ou configurer le chemin du certificat via variable d'environnement.

6. **Sticky sessions requises**
   Le mode HA nécessite l'affinité de session sur le load balancer. Sur OpenShift, cela se configure via une annotation sur la Route.
   **Action :** ajouter `haproxy.router.openshift.io/disable_cookies: "false"` sur la Route.

### 🟢 OK

7. **Health check endpoint disponible** — `GET /api/status` (HTTP 200) → utilisable comme `livenessProbe` et `readinessProbe`
8. **Endpoint Prometheus natif** — port 10000 `/metrics` → intégration directe avec le monitoring OpenShift
9. **Format de logs JSON** — compatible avec parsing structuré si redirigé vers stdout

---

## 8. Checklist de qualification

| Critère | Verdict | Commentaire |
|---------|---------|-------------|
| SCC compatible (restricted-v2) | ❌ KO | UID fixe 1000 + `CAP_NET_BIND_SERVICE` → nécessite `nonroot-v2` + config port |
| RBAC minimal défini | ✅ OK | Accès Secrets + ConfigMaps uniquement |
| Stockage compatible | ⚠️ Conditionnel | Dépend de la disponibilité RWX sur le cluster |
| Réseau documenté | ✅ OK | Tous les ports et flux sont documentés |
| Images depuis registry approuvé | ❓ À vérifier | Non documenté — demander à UiPath le registry et la politique de pull |
| Resource requests/limits | ✅ OK | Valeurs documentées, cohérentes |
| Health checks documentés | ✅ OK | `/api/status` disponible |
| Helm chart / Operator | ❓ À vérifier | Non mentionné dans la doc — demander à UiPath |
| Stratégie de backup | ❓ À vérifier | Backup SQL documenté, mais pas le stockage fichiers |
| Logs stdout/stderr | ❌ KO | Logs sur filesystem — sidecar ou reconfiguration nécessaire |

**Verdict global : 🟡 DÉPLOYABLE AVEC ADAPTATIONS**

4 points requièrent une action avant déploiement (port binding, SCC, stockage RWX, logs).
3 points nécessitent une clarification auprès de l'éditeur (registry, Helm chart, backup fichiers).
