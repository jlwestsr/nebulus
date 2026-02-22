# Nebulus Prime Security Audit Report

**Date**: 2026-02-10
**Auditor**: Agent 2 (Claude Code)
**Scope**: nebulus-prime (Linux deployment)
**Context**: Security parity audit following Mac Mini (nebulus-edge) assessment

---

## Executive Summary

This security audit of nebulus-prime identified **11 security findings** across 4 severity levels. The findings parallel the Mac Mini audit with platform-specific variations. Two **P0 (Critical)** issues require immediate remediation: plaintext API keys in `.env` and unauthenticated service endpoints exposed to 0.0.0.0.

**Key Risk Areas**:

- Plaintext secrets in environment files (P0)
- Unauthenticated services exposed to all network interfaces (P0)
- Docker socket exposure via Dozzle container (P1)
- Missing at-rest encryption for sensitive databases (P1)
- No authentication on API endpoints (P1)

**Compliance Impact**:

- **SOC 2**: Fails CC6.1 (logical access controls), CC6.6 (encryption)
- **HIPAA**: Fails 164.312(a)(1) (access controls), 164.312(a)(2)(iv) (encryption)
- **GDPR/CCPA**: Risk of unauthorized data access
- **NIST 800-53**: Gaps in AC-2, AC-3, SC-8, SC-28

---

## Findings

| ID | Severity | Category | Description | File/Location |
|----|----------|----------|-------------|---------------|
| NPRIME-01 | P0 | Secrets | Google API key in plaintext | `.env:12` |
| NPRIME-02 | P0 | Network | Services bound to 0.0.0.0 expose internal APIs to network | `docker-compose.yml` (all services) |
| NPRIME-03 | P0 | Network | TabbyAPI has authentication disabled | `config/tabby/config.yml:7` |
| NPRIME-04 | P1 | Infrastructure | Docker socket mounted in Dozzle container | `docker-compose.yml:39` |
| NPRIME-05 | P1 | Encryption | No at-rest encryption for SQLite databases | `data/gantry.db`, `src/mcp_server/scheduler.db` |
| NPRIME-06 | P1 | Authentication | MCP server API endpoints lack authentication | `src/mcp_server/server.py` |
| NPRIME-07 | P1 | Authentication | ChromaDB HTTP endpoint has no authentication | `docker-compose.yml:57-78` |
| NPRIME-08 | P2 | Input Validation | Cron schedule parsing without strict validation | `src/mcp_server/scheduler.py:32-37` |
| NPRIME-09 | P2 | Email Security | SMTP credentials passed via environment variables | `docker-compose.yml:92-96` |
| NPRIME-10 | P3 | Code Quality | Subprocess calls without explicit allowlist validation | `src/cli.py`, `nebulus_prime/adapter.py` |
| NPRIME-11 | P3 | Logging | Sensitive data may be logged in scheduler execution | `src/mcp_server/scheduler.py:110-124` |

---

## Detailed Findings

### NPRIME-01: Plaintext Google API Key (P0 - Critical)

**File**: `.env:12`
**Finding**: Google API key stored in plaintext:

```bash
GOOGLE_API_KEY=[REVOKED-KEY-EXPIRED]
GOOGLE_CSE_ID=939a33d3800f94239
```

**Risk**: Full compromise of Google Cloud services if file is exposed. This key is also committed to git history if `.env` was ever tracked.

**Remediation**:

1. **Immediate**: Revoke the exposed API key at Google Cloud Console
2. Generate new key and store in secrets manager (e.g., Docker secrets, HashiCorp Vault)
3. Update `.gitignore` to ensure `.env` is never committed
4. Implement runtime secret injection via Docker secrets or external KMS
5. Add pre-commit hook to scan for API key patterns

**Compliance Impact**: Violates SOC 2 CC6.1, HIPAA 164.312(a)(2)(i)

---

### NPRIME-02: Services Bound to 0.0.0.0 (P0 - Critical)

**File**: `docker-compose.yml` (lines 19, 41, 66, 88, 112)
**Finding**: All services expose ports to `0.0.0.0:PORT` instead of `127.0.0.1:PORT`:

```yaml
ports:
  - "5000:5000"      # TabbyAPI - should be 127.0.0.1:5000:5000
  - "8888:8080"      # Dozzle - should be 127.0.0.1:8888:8080
  - "8001:8000"      # ChromaDB - should be 127.0.0.1:8001:8000
  - "8002:8000"      # MCP Server - should be 127.0.0.1:8002:8000
  - "3000:8080"      # Open WebUI - should be 127.0.0.1:3000:8080
```

**Risk**: Services are accessible from ANY network interface (including external networks if firewall is misconfigured). Attackers on the same network can directly access internal APIs.

**Remediation**:

1. Bind all internal services to `127.0.0.1:PORT:CONTAINER_PORT`
2. Only Open WebUI frontend should be exposed if needed for LAN access
3. Use reverse proxy (nginx/Caddy) with authentication for remote access
4. Add firewall rules to restrict access to trusted IPs only

**Example fix**:

```yaml
ports:
  - "127.0.0.1:5000:5000"    # TabbyAPI - localhost only
  - "127.0.0.1:8001:8000"    # ChromaDB - localhost only
```

**Compliance Impact**: Violates SOC 2 CC6.1, NIST 800-53 AC-3

---

### NPRIME-03: TabbyAPI Authentication Disabled (P0 - Critical)

**File**: `config/tabby/config.yml:7`
**Finding**:

```yaml
disable_auth: true
```

**Risk**: Anyone with network access can make LLM inference requests, potentially exhausting GPU resources or exfiltrating model outputs.

**Remediation**:

1. Enable TabbyAPI authentication: `disable_auth: false`
2. Configure API key authentication in TabbyAPI
3. Store API keys in secrets manager
4. Update clients to pass authentication headers

**Compliance Impact**: Violates SOC 2 CC6.1, NIST 800-53 AC-2

---

### NPRIME-04: Docker Socket Exposure (P1 - High)

**File**: `docker-compose.yml:39`
**Finding**: Dozzle container has full Docker socket access:

```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
```

**Risk**: Compromised Dozzle container = root access to host. Attacker can:

- Start/stop containers
- Execute commands in any container
- Mount host filesystem
- Escalate to root on host

**Remediation**:

1. Use Docker socket proxy with read-only access (tecnativa/docker-socket-proxy)
2. Configure proxy to only allow log reading
3. Run Dozzle with minimal permissions
4. Consider alternative log aggregation (Grafana Loki, Promtail)

**Example**:

```yaml
docker-socket-proxy:
  image: tecnativa/docker-socket-proxy
  environment:
    CONTAINERS: 1
    LOGS: 1
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock:ro

dozzle:
  environment:
    - DOCKER_HOST=tcp://docker-socket-proxy:2375
```

**Compliance Impact**: Violates SOC 2 CC6.6, NIST 800-53 AC-6

---

### NPRIME-05: No At-Rest Encryption (P1 - High)

**Files**:

- `data/gantry.db` (Gantry application database)
- `src/mcp_server/scheduler.db` (Scheduler job store)
- `test.db` (test database)

**Finding**: SQLite databases stored unencrypted on disk. Databases may contain:

- User data (conversations, preferences)
- Scheduled task prompts (may contain PII)
- Configuration data

**Risk**: Physical access or backup exposure leaks all data. Fails compliance encryption requirements.

**Remediation**:

1. Enable SQLite encryption extension (SQLCipher)
2. Use LUKS full-disk encryption for data directories
3. Implement database-level encryption for sensitive columns
4. Add encryption key rotation policy
5. Document encryption key storage/recovery procedures

**Example SQLCipher usage**:

```python
import sqlcipher3
conn = sqlcipher3.connect('scheduler.db')
conn.execute("PRAGMA key='encryption_key_from_secrets_manager'")
```

**Compliance Impact**: Violates HIPAA 164.312(a)(2)(iv), SOC 2 CC6.6, NIST 800-53 SC-28

---

### NPRIME-06: MCP Server API Lacks Authentication (P1 - High)

**File**: `src/mcp_server/server.py`
**Finding**: All API endpoints (lines 103-148, 156-263) have no authentication:

- Task management: `/api/tasks` (GET/POST/DELETE)
- Conversation management: `/api/conversations` (CRUD)
- User preferences: `/api/users/{user_id}/preferences`

**Risk**: Any network client can:

- Create/delete scheduled tasks
- Access all conversation history
- Modify user preferences
- Trigger manual task execution

**Remediation**:

1. Implement API key authentication middleware
2. Add JWT-based authentication for user-specific endpoints
3. Use FastAPI dependency injection for auth
4. Add rate limiting
5. Log all API access attempts

**Example FastAPI auth**:

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("MCP_API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

@app.get("/api/tasks", dependencies=[Depends(verify_api_key)])
async def get_tasks_api(request: Request):
    ...
```

**Compliance Impact**: Violates SOC 2 CC6.1, NIST 800-53 AC-2, AC-3

---

### NPRIME-07: ChromaDB No Authentication (P1 - High)

**File**: `docker-compose.yml:57-78`
**Finding**: ChromaDB runs with no authentication enabled. Default ChromaDB HTTP mode has no auth.

**Risk**:

- Anyone can read/write/delete vector collections
- Exposed LTM (long-term memory) data
- Potential data poisoning attacks

**Remediation**:

1. Enable ChromaDB authentication (requires ChromaDB 0.4+)
2. Configure token-based auth or use Chroma Cloud with SSO
3. Implement network isolation (Docker internal network only)
4. Add nginx reverse proxy with basic auth for internal tools

**Example ChromaDB auth** (requires newer version):

```yaml
environment:
  - CHROMA_SERVER_AUTH_PROVIDER=token
  - CHROMA_SERVER_AUTH_CREDENTIALS=file:/app/credentials.txt
volumes:
  - ./chroma_credentials.txt:/app/credentials.txt:ro
```

**Compliance Impact**: Violates SOC 2 CC6.1, NIST 800-53 AC-3

---

### NPRIME-08: Cron Schedule Validation (P2 - Medium)

**File**: `src/mcp_server/scheduler.py:32-37`
**Finding**: Cron parsing splits on spaces without strict validation:

```python
parts = schedule_cron.split()
if len(parts) != 5:
    return "Error: Schedule must be in standard 5-part cron format"
```

**Risk**:

- Injection of unexpected cron expressions
- Resource exhaustion from invalid schedules
- No validation of ranges (e.g., hour > 23)

**Remediation**:

1. Use `croniter` library for strict validation before parsing
2. Add range validation for each cron field
3. Allowlist cron patterns (e.g., no `* * * * *` - every minute)
4. Add max task frequency policy

**Example**:

```python
from croniter import croniter

def validate_cron(schedule_cron: str) -> bool:
    try:
        croniter(schedule_cron)
        # Add business logic: e.g., min interval is 5 minutes
        return True
    except Exception:
        return False
```

**Compliance Impact**: Minor - defense in depth

---

### NPRIME-09: SMTP Credentials in Environment (P2 - Medium)

**File**: `docker-compose.yml:92-96`
**Finding**: SMTP credentials passed as environment variables:

```yaml
environment:
  - SMTP_USER=${SMTP_USER}
  - SMTP_PASS=${SMTP_PASS}
```

**Risk**:

- Environment variables visible in `docker inspect`
- Logged in container orchestration tools
- Exposed via `/proc/<pid>/environ` if attacker gets shell

**Remediation**:

1. Use Docker secrets for credentials
2. Rotate SMTP credentials regularly
3. Use OAuth2 for email sending (Gmail API) instead of SMTP
4. Store credentials in secrets manager (Vault, AWS Secrets Manager)

**Example Docker secrets**:

```yaml
services:
  mcp-server:
    secrets:
      - smtp_user
      - smtp_pass
    environment:
      - SMTP_USER_FILE=/run/secrets/smtp_user
      - SMTP_PASS_FILE=/run/secrets/smtp_pass

secrets:
  smtp_user:
    file: ./secrets/smtp_user.txt
  smtp_pass:
    file: ./secrets/smtp_pass.txt
```

**Compliance Impact**: Violates SOC 2 CC6.1

---

### NPRIME-10: Subprocess Call Validation (P3 - Low)

**Files**:

- `src/cli.py:24-51` (run_command, run_interactive)
- `nebulus_prime/adapter.py:82-116` (start_services, stop_services, restart_services, get_logs)

**Finding**: Subprocess calls accept list arguments but no allowlist validation. While not using `shell=True`, there's no explicit command allowlist.

**Risk**:

- If user input ever flows to these functions, command injection possible
- Currently low risk as all calls are hardcoded

**Remediation**:

1. Create command allowlist: `ALLOWED_COMMANDS = ["docker", "docker-compose"]`
2. Validate `command[0]` against allowlist before execution
3. Add explicit type checking for arguments
4. Log all subprocess executions

**Example**:

```python
ALLOWED_COMMANDS = ["docker", "docker-compose", "python3"]

def run_command(command: List[str], capture_output: bool = False):
    if command[0] not in ALLOWED_COMMANDS:
        raise ValueError(f"Command not allowed: {command[0]}")
    logger.info(f"Executing: {' '.join(command)}")
    return subprocess.run(command, check=True, text=True, capture_output=capture_output)
```

**Compliance Impact**: Minor - defense in depth

---

### NPRIME-11: Sensitive Data in Logs (P3 - Low)

**File**: `src/mcp_server/scheduler.py:110-124`
**Finding**: Task execution logs may include prompts that contain PII:

```python
logger.info(f"Executing job: {title}")
```

**Risk**:

- PII/PHI leakage in log files
- Logs aggregated to external systems may expose sensitive data

**Remediation**:

1. Implement PII detection/redaction for logs
2. Use structured logging with field-level control
3. Add log retention policy (delete after 30 days)
4. Encrypt log files at rest
5. Review what gets logged (avoid logging prompt content)

**Example**:

```python
import logging
from nebulus_core.intelligence.pii import redact_pii

logger.info(f"Executing job: {redact_pii(title)}")
```

**Compliance Impact**: Violates HIPAA 164.308(a)(5)(ii)(C) (log review), GDPR Art. 32

---

## Infrastructure Security Assessment

### Docker Compose Configuration

**Findings**:

- **Network isolation**: `ai-network` bridge mode provides basic isolation but all services can communicate freely
- **Resource limits**: Only Dozzle and Open WebUI have CPU/memory limits; other services unbounded
- **Restart policy**: `unless-stopped` appropriate for dev/lab environment
- **Volume mounts**: Root workspace mounted into MCP server (`- .:/workspace`) - overly permissive

**Recommendations**:

1. Implement network segmentation (separate networks for frontend/backend/data)
2. Add resource limits to all services
3. Use named volumes instead of bind mounts where possible
4. Implement least-privilege volume mounts (read-only where possible)

### Network Exposure Summary

| Service | Container Port | Host Port | Binding | Risk |
|---------|---------------|-----------|---------|------|
| TabbyAPI | 5000 | 5000 | 0.0.0.0 | P0 - LLM inference exposed, no auth |
| ChromaDB | 8000 | 8001 | 0.0.0.0 | P1 - Vector DB exposed, no auth |
| MCP Server | 8000 | 8002 | 0.0.0.0 | P1 - Admin API exposed, no auth |
| Open WebUI | 8080 | 3000 | 0.0.0.0 | P2 - Frontend, relies on app auth |
| Dozzle | 8080 | 8888 | 0.0.0.0 | P1 - Log viewer + Docker socket access |

**Recommendation**: Bind ALL services to `127.0.0.1` except Open WebUI (if LAN access needed).

---

## Comparison with Mac Mini (nebulus-edge) Audit

| Finding Category | nebulus-prime | nebulus-edge | Notes |
|-----------------|---------------|--------------|-------|
| Plaintext secrets | P0 (Google API key in .env) | P0 (Multiple keys) | Similar risk |
| At-rest encryption | P1 (SQLite DBs unencrypted) | P0 (Model files, ChromaDB) | Prime: lower risk (smaller data footprint) |
| Network exposure | P0 (All services 0.0.0.0) | P1 (MLX server localhost only) | Prime: worse than Edge |
| Docker socket exposure | P1 (Dozzle has full access) | N/A (no Docker on Edge) | Prime-specific risk |
| Authentication | P1 (No auth on APIs) | P1 (No auth on MLX) | Similar risk |
| SMTP credentials | P2 (env vars) | N/A | Prime-specific |
| Subprocess validation | P3 | P3 | Similar risk |
| Logging sensitivity | P3 | P3 | Similar risk |

**Key Differences**:

1. **Prime has MORE attack surface** due to Docker Compose multi-service architecture
2. **Edge has HIGHER data risk** due to larger model files and embedded ChromaDB
3. **Prime has Docker-specific risks** (socket exposure) that don't exist on Edge
4. **Both fail authentication/encryption requirements** for SOC 2 / HIPAA compliance

---

## Remediation Priority Matrix

### Immediate (This Week)

| ID | Action | Effort | Impact |
|----|--------|--------|--------|
| NPRIME-01 | Revoke Google API key, implement secrets manager | 4h | P0 |
| NPRIME-02 | Bind services to 127.0.0.1 | 1h | P0 |
| NPRIME-03 | Enable TabbyAPI authentication | 2h | P0 |

### Short-Term (This Month)

| ID | Action | Effort | Impact |
|----|--------|--------|--------|
| NPRIME-04 | Implement Docker socket proxy | 3h | P1 |
| NPRIME-05 | Enable SQLite encryption (SQLCipher) | 6h | P1 |
| NPRIME-06 | Add MCP server API authentication | 4h | P1 |
| NPRIME-07 | Enable ChromaDB authentication | 3h | P1 |

### Medium-Term (This Quarter)

| ID | Action | Effort | Impact |
|----|--------|--------|--------|
| NPRIME-08 | Improve cron validation | 2h | P2 |
| NPRIME-09 | Move SMTP creds to Docker secrets | 2h | P2 |
| NPRIME-10 | Add subprocess allowlist | 2h | P3 |
| NPRIME-11 | Implement log redaction | 4h | P3 |

**Total Remediation Effort**: ~33 hours (approx 1 week of focused work)

---

## Compliance Gaps

### SOC 2 Type II

| Control | Status | Findings |
|---------|--------|----------|
| CC6.1 - Logical Access Controls | FAIL | NPRIME-01, 02, 03, 06, 07, 09 |
| CC6.6 - Encryption | FAIL | NPRIME-05 |
| CC6.7 - System Boundaries | PARTIAL | NPRIME-02, 04 |
| CC7.2 - Change Management | PASS | Git workflow enforced |

### HIPAA (if handling PHI)

| Requirement | Status | Findings |
|-------------|--------|----------|
| 164.312(a)(1) - Access Control | FAIL | NPRIME-02, 03, 06, 07 |
| 164.312(a)(2)(iv) - Encryption | FAIL | NPRIME-05 |
| 164.308(a)(5)(ii)(C) - Log Review | PARTIAL | NPRIME-11 |
| 164.312(d) - Data Integrity | PARTIAL | No tamper detection |

### GDPR/CCPA

| Requirement | Status | Findings |
|-------------|--------|----------|
| Art. 32 - Security Measures | FAIL | NPRIME-01, 02, 05, 06, 07 |
| Art. 25 - Data Protection by Design | PARTIAL | No default encryption |
| CCPA 1798.150 - Data Breach Liability | AT RISK | High breach probability |

### NIST 800-53

| Control | Status | Findings |
|---------|--------|----------|
| AC-2 - Account Management | FAIL | NPRIME-03, 06 |
| AC-3 - Access Enforcement | FAIL | NPRIME-02, 06, 07 |
| AC-6 - Least Privilege | FAIL | NPRIME-04 |
| SC-8 - Transmission Confidentiality | PARTIAL | No TLS enforced |
| SC-28 - Protection of Data at Rest | FAIL | NPRIME-05 |

---

## Recommendations

### Architecture Changes

1. **Implement Defense in Depth**:
   - Add nginx reverse proxy with authentication
   - Use Docker secrets for all credentials
   - Implement network segmentation (frontend/backend/data networks)
   - Add intrusion detection (OSSEC, Fail2ban)

2. **Zero Trust Model**:
   - Authenticate all inter-service communication
   - Implement mTLS between containers
   - Add service mesh (Istio/Linkerd) for advanced deployments

3. **Secrets Management**:
   - Deploy HashiCorp Vault or AWS Secrets Manager
   - Rotate all secrets immediately
   - Implement automatic secret rotation

### Operational Changes

1. **Monitoring & Alerting**:
   - Deploy Prometheus + Grafana for metrics
   - Add security event logging (auditd)
   - Implement anomaly detection

2. **Incident Response**:
   - Document breach response procedures
   - Implement automated backup encryption
   - Test disaster recovery procedures

3. **Access Control**:
   - Implement RBAC for all APIs
   - Add API rate limiting
   - Enable audit logging for all access

### Development Process

1. **Security Testing**:
   - Add SAST (Bandit, Safety) to CI/CD
   - Implement dependency vulnerability scanning
   - Add pre-commit hooks for secret detection

2. **Code Review**:
   - Require security review for auth/crypto changes
   - Document security assumptions
   - Maintain threat model

---

## Conclusion

Nebulus-prime has **11 security findings**, with 3 critical (P0) issues requiring immediate remediation. The platform has a **larger attack surface** than nebulus-edge due to its multi-service Docker architecture but handles less sensitive data.

**Primary Concerns**:

1. **All services exposed to network** with no authentication (P0)
2. **Plaintext API keys** in environment files (P0)
3. **Docker socket exposure** creates privilege escalation risk (P1)
4. **No encryption at rest** for databases (P1)

**Compliance Status**: Currently FAILS SOC 2, HIPAA, GDPR/CCPA, and NIST 800-53 requirements. Estimated **33 hours of remediation work** to achieve basic compliance posture.

**Next Steps**:

1. Execute immediate remediation (bind to localhost, revoke API keys)
2. Implement authentication on all APIs
3. Enable encryption at rest
4. Deploy secrets management solution
5. Re-audit after remediation

---

**Report Generated**: 2026-02-10
**Agent**: Claude Code Agent 2
**Classification**: INTERNAL - West AI Labs LLC Proprietary
