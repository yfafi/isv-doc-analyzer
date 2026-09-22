# UiPath Orchestrator — Guide d'installation v2024.10

## 1. Présentation

UiPath Orchestrator est la plateforme de gestion centralisée pour les robots RPA UiPath. Elle permet le déploiement, le monitoring, la planification et l'audit de l'ensemble des processus automatisés de l'entreprise.

## 2. Architecture

Orchestrator repose sur une architecture multi-composants :

- **Web Application** : interface utilisateur et API REST (ASP.NET Core)
- **Background Jobs Service** : traitement asynchrone des tâches planifiées
- **Webhook Service** : gestion des notifications et callbacks externes

Les trois composants peuvent tourner sur le même serveur ou être déployés séparément pour la haute disponibilité.

## 3. Prérequis système

### 3.1 Système d'exploitation
- Windows Server 2019/2022 ou Linux (RHEL 8+, Ubuntu 20.04+)
- Pour Linux : le service tourne sous le user `orchestrator` (UID 1000) mais nécessite un accès root pour l'installation initiale et la gestion des certificats système

### 3.2 Ressources matérielles

| Composant | CPU | RAM | Disque |
|-----------|-----|-----|--------|
| Web App (par instance) | 4 vCPU | 8 Go | 20 Go |
| Background Jobs | 2 vCPU | 4 Go | 10 Go |
| Webhook Service | 1 vCPU | 2 Go | 5 Go |

En production, il est recommandé de déployer au minimum 2 instances du Web App derrière un load balancer.

### 3.3 Ports réseau

| Port | Protocole | Direction | Usage |
|------|-----------|-----------|-------|
| 443 | HTTPS | Entrant | Interface web et API REST |
| 8080 | HTTP | Interne | Communication inter-services (Web ↔ Background Jobs) |
| 9200 | TCP | Sortant | Connexion vers Elasticsearch |
| 9300 | TCP | Sortant | Cluster Elasticsearch (transport) |
| 1433 | TCP | Sortant | Connexion SQL Server |
| 6379 | TCP | Sortant | Connexion Redis |
| 5672 | TCP | Sortant | Connexion RabbitMQ (AMQP) |
| 10000 | TCP | Entrant | Endpoint de métriques Prometheus |

### 3.4 Certificats
- Un certificat TLS valide est requis pour le endpoint HTTPS (port 443)
- Le certificat doit être stocké dans le keystore système (`/etc/ssl/certs/` sur Linux)
- Les communications inter-services utilisent mTLS en mode production

## 4. Dépendances

### 4.1 Base de données — SQL Server
- **Version** : SQL Server 2019 ou supérieur, ou Azure SQL
- **Taille initiale** : 50 Go minimum, prévoir 200 Go pour un an d'exploitation
- Le compte de service SQL nécessite les rôles `db_owner` sur la base Orchestrator
- Collation requise : `SQL_Latin1_General_CP1_CI_AS`

### 4.2 Elasticsearch
- **Version** : 7.17.x ou 8.x
- Utilisé pour l'indexation et la recherche des logs des robots
- Stockage recommandé : 100 Go minimum (dépend du volume de logs)
- 3 nœuds minimum en production

### 4.3 Redis
- **Version** : 6.x ou supérieur
- Utilisé comme cache distribué et pour la gestion des sessions en mode multi-instance
- Mode Sentinel recommandé en production pour la haute disponibilité

### 4.4 RabbitMQ (optionnel)
- **Version** : 3.11+
- Nécessaire uniquement pour les déploiements multi-nœuds
- Utilisé pour la communication asynchrone entre Web App et Background Jobs
- Peut être remplacé par le mode "in-process" pour les déploiements single-node

## 5. Stockage

### 5.1 Stockage des packages NuGet
Les packages RPA (.nupkg) sont stockés sur le filesystem local par défaut :
- Chemin : `/opt/uipath/orchestrator/packages/`
- Taille : dépend du nombre de processus, prévoir 50 Go minimum
- **Important** : en mode multi-instance, ce répertoire doit être partagé entre toutes les instances (NFS ou stockage partagé)

### 5.2 Stockage des médias
Les captures d'écran et pièces jointes des exécutions sont stockées dans :
- Chemin : `/opt/uipath/orchestrator/media/`
- Taille : prévoir 100 Go minimum
- Ce répertoire doit également être partagé en mode multi-instance

### 5.3 Logs applicatifs
- Chemin : `/var/log/uipath/`
- Les logs sont écrits en fichiers rotatifs (100 Mo max par fichier, 10 fichiers)
- Format : JSON structuré

## 6. Sécurité

### 6.1 Compte de service
L'application tourne sous un compte de service dédié (`orchestrator`). Ce compte nécessite :
- Accès en lecture/écriture aux répertoires de stockage
- Accès au keystore système pour les certificats TLS
- Capacité à binder sur les ports < 1024 (port 443) → nécessite `CAP_NET_BIND_SERVICE`

### 6.2 Authentification
- Authentification SAML 2.0 / OpenID Connect supportée
- Intégration Active Directory / LDAP
- L'application doit pouvoir effectuer des requêtes LDAP sortantes (port 636, LDAPS)

### 6.3 Chiffrement
- Toutes les données sensibles (credentials des robots, API keys) sont chiffrées en base avec AES-256
- La clé de chiffrement est stockée dans un fichier de configuration protégé

## 7. Haute disponibilité

En mode HA, Orchestrator nécessite :
- Minimum 2 instances Web App derrière un load balancer
- Session affinity (sticky sessions) activée sur le load balancer
- Redis obligatoire pour le partage de sessions
- Stockage partagé NFS pour les packages et médias
- Health check endpoint : `GET /api/status` (retourne HTTP 200)

## 8. Monitoring

- Endpoint Prometheus : `http://localhost:10000/metrics`
- Métriques exposées : nombre de jobs, temps d'exécution, files d'attente, erreurs
- Dashboard Grafana fourni dans le package d'installation
