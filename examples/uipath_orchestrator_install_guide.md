# UiPath Orchestrator — Installation Guide v2024.10

## 1. Overview

UiPath Orchestrator is the centralized management platform for UiPath RPA robots. It handles deployment, monitoring, scheduling, and auditing of all automated processes across the enterprise.

## 2. Architecture

Orchestrator relies on a multi-component architecture:

- **Web Application**: user interface and REST API (ASP.NET Core)
- **Background Jobs Service**: asynchronous processing of scheduled tasks
- **Webhook Service**: notification management and external callbacks

All three components can run on the same server or be deployed separately for high availability.

## 3. System Prerequisites

### 3.1 Operating System
- Windows Server 2019/2022 or Linux (RHEL 8+, Ubuntu 20.04+)
- On Linux: the service runs under the `orchestrator` user (UID 1000) but requires root access for initial installation and system certificate management

### 3.2 Hardware Resources

| Component | CPU | RAM | Disk |
|-----------|-----|-----|------|
| Web App (per instance) | 4 vCPU | 8 GB | 20 GB |
| Background Jobs | 2 vCPU | 4 GB | 10 GB |
| Webhook Service | 1 vCPU | 2 GB | 5 GB |

In production, it is recommended to deploy at least 2 Web App instances behind a load balancer.

### 3.3 Network Ports

| Port | Protocol | Direction | Usage |
|------|----------|-----------|-------|
| 443 | HTTPS | Inbound | Web interface and REST API |
| 8080 | HTTP | Internal | Inter-service communication (Web ↔ Background Jobs) |
| 9200 | TCP | Outbound | Elasticsearch connection |
| 9300 | TCP | Outbound | Elasticsearch cluster (transport) |
| 1433 | TCP | Outbound | SQL Server connection |
| 6379 | TCP | Outbound | Redis connection |
| 5672 | TCP | Outbound | RabbitMQ connection (AMQP) |
| 10000 | TCP | Inbound | Prometheus metrics endpoint |

### 3.4 Certificates
- A valid TLS certificate is required for the HTTPS endpoint (port 443)
- The certificate must be stored in the system keystore (`/etc/ssl/certs/` on Linux)
- Inter-service communications use mTLS in production mode

## 4. Dependencies

### 4.1 Database — SQL Server
- **Version**: SQL Server 2019 or higher, or Azure SQL
- **Initial size**: 50 GB minimum, plan for 200 GB for one year of operation
- The SQL service account requires `db_owner` roles on the Orchestrator database
- Required collation: `SQL_Latin1_General_CP1_CI_AS`

### 4.2 Elasticsearch
- **Version**: 7.17.x or 8.x
- Used for indexing and searching robot logs
- Recommended storage: 100 GB minimum (depends on log volume)
- 3 nodes minimum in production

### 4.3 Redis
- **Version**: 6.x or higher
- Used as distributed cache and for session management in multi-instance mode
- Sentinel mode recommended in production for high availability

### 4.4 RabbitMQ (optional)
- **Version**: 3.11+
- Required only for multi-node deployments
- Used for asynchronous communication between Web App and Background Jobs
- Can be replaced by "in-process" mode for single-node deployments

## 5. Storage

### 5.1 NuGet Package Storage
RPA packages (.nupkg) are stored on the local filesystem by default:
- Path: `/opt/uipath/orchestrator/packages/`
- Size: depends on the number of processes, plan for 50 GB minimum
- **Important**: in multi-instance mode, this directory must be shared across all instances (NFS or shared storage)

### 5.2 Media Storage
Screenshots and execution attachments are stored in:
- Path: `/opt/uipath/orchestrator/media/`
- Size: plan for 100 GB minimum
- This directory must also be shared in multi-instance mode

### 5.3 Application Logs
- Path: `/var/log/uipath/`
- Logs are written as rotating files (100 MB max per file, 10 files)
- Format: structured JSON

## 6. Security

### 6.1 Service Account
The application runs under a dedicated service account (`orchestrator`). This account requires:
- Read/write access to storage directories
- Access to the system keystore for TLS certificates
- Ability to bind to ports < 1024 (port 443) → requires `CAP_NET_BIND_SERVICE`

### 6.2 Authentication
- SAML 2.0 / OpenID Connect authentication supported
- Active Directory / LDAP integration
- The application must be able to make outbound LDAP requests (port 636, LDAPS)

### 6.3 Encryption
- All sensitive data (robot credentials, API keys) is encrypted at rest with AES-256
- The encryption key is stored in a protected configuration file

## 7. High Availability

In HA mode, Orchestrator requires:
- Minimum 2 Web App instances behind a load balancer
- Session affinity (sticky sessions) enabled on the load balancer
- Redis mandatory for session sharing
- NFS shared storage for packages and media
- Health check endpoint: `GET /api/status` (returns HTTP 200)

## 8. Monitoring

- Prometheus endpoint: `http://localhost:10000/metrics`
- Exposed metrics: job count, execution time, queues, errors
- Grafana dashboard included in the installation package
