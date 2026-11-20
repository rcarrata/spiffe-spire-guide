> Source: https://docs.nvidia.com/openshell/dev/how-it-works/gateways/configuration
> Retrieved: 2026-11-20
> Version: OpenShell docs "dev" channel (unversioned path). Page title: Gateway Configuration.
> Notes: The full page is very long (~175k chars). This file keeps the "Sandbox identity through the SPIFFE Broker API" section VERBATIM, plus every SPIFFE / Workload API / token-grant related config key found elsewhere on the page (driver keys, gateway_jwt prerequisite, extension JWKS endpoints). Other sections are listed only as an outline at the end. Text and TOML are verbatim from the page unless marked "(note)".

# OpenShell Gateway Configuration - SPIFFE related parts

## Sandbox identity through the SPIFFE Broker API (verbatim)

(note) On the page this is a subsection of "Driver References > Kubernetes".

For shared-supervisor Kubernetes sandboxes, the gateway can obtain sandbox JWT-SVIDs through SPIRE’s experimental Broker API. This uses the gateway’s own X.509-SVID over mTLS.

```toml
[openshell.gateway.spiffe_broker]
spiffe_id_prefix = "spiffe://example.org/openshell"
node_local_port = 8443
server_spiffe_id_prefix = "spiffe://example.org/spire/agent/k8s_psat/cluster"
workload_api_socket_path = "/spiffe-workload-api/spire-agent.sock"
```

`node_local_port` connects directly to the SPIRE agent on the gateway Pod’s node. Helm injects `OPENSHELL_NODE_IP` from the Downward API’s `status.hostIP`; the gateway formats the IPv4 or IPv6 endpoint at startup without Kubernetes API calls or additional RBAC. A missing or invalid node IP prevents startup. The agent must expose its mTLS Broker listener on that node address through host networking or a host port. Broker traffic does not traverse a Kubernetes Service. The gateway does not fall back to a remote agent when its local agent is unavailable.

Configure exactly one transport: `node_local_port`, or an explicit HTTPS `endpoint` for a fixed address or Service. Outside Helm, node-local deployments must supply `OPENSHELL_NODE_IP` themselves. Both modes retain the same mTLS, SPIFFE peer verification, broker allowlist, and Kubernetes authorization checks.

Gateway session JWTs with a positive TTL are required. When enabling the broker on a gateway that omitted `gateway_jwt.ttl_secs`, set a positive value and restart existing sandboxes to issue expiring sessions; existing non-expiring sessions cannot request brokered tokens. The gateway fetches fresh X.509 credentials and trust bundles for each token acquisition, so Workload API rotation does not require a gateway restart. The same `workload_api_socket_path` supplies the gateway’s JWT-SVID for `token_exchange`; no separate socket environment variable is needed. Omit the driver’s `provider_spiffe_workload_api_socket_path` for shared supervisors.

The operator must enable SPIRE’s Broker endpoint, authorize the gateway SPIFFE ID for `KubernetesObjectReference` over TCP, and configure the Kubernetes attestor with `access_policy = "enforced"`. Give the agent permission to look up Sandbox resources and create SubjectAccessReviews. UID-only references require cluster-wide Sandbox `get`/`list` permission for the agents, even though SPIRE requests metadata-only responses. Grant the gateway’s SPIFFE ID the `impersonate-via-spire` verb on Sandbox resources only in its permitted namespaces.

Register each sandbox’s stable SPIFFE ID against its attested Sandbox resource UID. The gateway supplies the UID from its persisted compute-runtime identity; workload Pod replacement does not change it. Registrations must reach every eligible agent. In node-local mode this includes every node where a gateway replica may run, so gateway rescheduling does not require re-registration. Use a SPIRE node alias as the registration parent to cover agents attested with the intended cluster, namespace, and ServiceAccount selectors, including newly added nodes. The alias does not change the agents’ certificate identities.

Set exactly one peer policy. `server_spiffe_id_prefix` accepts descendants of the configured SPIFFE path in the same trust domain. The example accepts all node IDs in one attested cluster and rejects sibling cluster paths. For an endpoint serving one fixed identity, use `server_spiffe_id` instead. Certificate chain verification and the requirement for exactly one URI SAN apply to both modes. Do not use a trust-domain-wide peer policy. The installed SPIRE version and operator must support the experimental API; this configuration alone does not enable it.

If grants fail after rescheduling or adding nodes, check that the eligible agents match the peer prefix and node alias, and that Sandbox registrations have reached each agent. Identity or configuration rejections require fixing registration, trust, or authorization; connection failures can be retried. Provider-token requests use a separate instance of the configured gRPC rate budget. Authenticated work is also capped at four concurrent requests per sandbox and 64 per gateway, including when token caching is disabled.

## Gateway JWT prerequisite (`gateway_jwt.ttl_secs`)

(note) The broker section requires gateway session JWTs with a positive TTL. From the page's Authentication section and full example:

```toml
[openshell.gateway.gateway_jwt]
signing_key_path = "/etc/openshell/jwt/signing.pem"
public_key_path  = "/etc/openshell/jwt/public.pem"
kid_path         = "/etc/openshell/jwt/kid"
gateway_id       = "openshell"
# Optional; defaults to 900 seconds.
ttl_secs         = 3600
```

`[openshell.gateway.gateway_jwt] ttl_secs` controls generation-bound gateway-facing and Sandbox Protocol credentials minted for a sandbox session, plus typed extension JWTs. Omit it for non-expiring local sandbox session credentials: both session tokens carry `exp = 0`, supervisors skip periodic session-token renewal, and refresh responses omit their expiration timestamps. Typed extension JWTs retain a 900-second default when the field is omitted. Use omission only for local single-player Docker, Podman, or VM gateways. Explicit `0` is invalid. Kubernetes and other shared deployments should set a positive TTL; Helm renders `3600` seconds by default, and the gateway logs a warning when a Kubernetes gateway omits the field.

## Extension Token Verification Endpoints (verbatim)

When `gateway_jwt` is configured the gateway publishes two unauthenticated documents that extension services use to verify OpenShell callers:

| Path | Contents |
|----|----|
| `/.well-known/jwks.json` | Single-key JWKS holding the Ed25519 public key and its `kid`. |
| `/.well-known/openid-configuration` | OIDC-shaped discovery metadata: the exact expected `iss`, an absolute `jwks_uri`, and `EdDSA` as the only supported signing algorithm. |

The discovery document is OIDC-shaped rather than OIDC-compliant: `issuer` is the gateway identity (`openshell-gateway:<gateway_id>`), not the URL the document is served from. Verifiers compare `iss` against that value and must not infer trust from the document’s location; the serving TLS connection is what authenticates the gateway. Both endpoints return `404` when `gateway_jwt` is not configured.

## SPIFFE Workload API socket keys per compute driver (verbatim excerpts)

(note) These keys give the sandbox supervisor a SPIFFE Workload API socket, which dynamic provider token grants need (see openshell-dynamic-token-grants.md). Excerpts are the relevant lines from each driver's TOML example.

### Kubernetes driver - `[openshell.drivers.kubernetes]`

```toml
[openshell.drivers.kubernetes]
# ...
# Optional SPIFFE Workload API socket mounted into sandbox pods for dynamic
# provider token grants. Use an absolute path under a dedicated directory;
# shared roots such as /run, /var, /tmp, and /etc are rejected.
# Supervisor-to-gateway auth still uses gateway JWTs.
provider_spiffe_workload_api_socket_path = "/spiffe-workload-api/spire-agent.sock"
```

(note) The broker section says: "Omit the driver’s `provider_spiffe_workload_api_socket_path` for shared supervisors." Same Kubernetes example also sets `sa_token_ttl_secs = 3600` ("Kubelet clamps projected tokens below 600 seconds. The driver caps values at 86400.").

### Docker driver - `[openshell.drivers.docker]`

```toml
# Project a host Unix Workload API socket into the supervisor for provider
# token exchange. The socket parent must be a dedicated absolute directory.
provider_spiffe_workload_api_socket = "/run/spire/agent.sock"
```

### Podman driver - `[openshell.drivers.podman]`

```toml
# Project a host Workload API Unix socket into the supervisor, or use an
# explicit container-reachable TCP endpoint, for provider token exchange.
# provider_spiffe_workload_api_socket = "/run/spire/agent.sock"
# provider_spiffe_workload_api_socket = "tcp:169.254.1.2:8081"
```

### MicroVM driver - `[openshell.drivers.vm]`

```toml
# VM guests cannot mount a host Workload API Unix socket. Configure only a
# separately operated guest-reachable TCP listener and explicitly acknowledge
# the exposure; host-only sockets are never exposed automatically.
# provider_spiffe_workload_api_tcp_endpoint = "tcp:192.0.2.10:8081"
# provider_spiffe_allow_guest_tcp = true
```

## Summary of SPIFFE-related keys (note)

| Key | Table | Purpose |
|----|----|----|
| `spiffe_id_prefix` | `[openshell.gateway.spiffe_broker]` | SPIFFE ID prefix for sandbox identities (example `spiffe://example.org/openshell`) |
| `node_local_port` | `[openshell.gateway.spiffe_broker]` | Transport option 1: SPIRE agent Broker listener on the gateway Pod's node (uses `OPENSHELL_NODE_IP` from Downward API `status.hostIP`) |
| `endpoint` | `[openshell.gateway.spiffe_broker]` | Transport option 2: explicit HTTPS endpoint (fixed address or Service). Exactly one of `node_local_port` / `endpoint` |
| `server_spiffe_id_prefix` | `[openshell.gateway.spiffe_broker]` | Peer policy option 1: accept SPIRE agent IDs under this path (example `spiffe://example.org/spire/agent/k8s_psat/cluster`) |
| `server_spiffe_id` | `[openshell.gateway.spiffe_broker]` | Peer policy option 2: one fixed identity. Exactly one peer policy; trust-domain-wide not allowed |
| `workload_api_socket_path` | `[openshell.gateway.spiffe_broker]` | Gateway's own Workload API socket (X.509-SVID for broker mTLS, and JWT-SVID for `token_exchange`) |
| `ttl_secs` | `[openshell.gateway.gateway_jwt]` | Must be positive for broker use; Helm default 3600 |
| `provider_spiffe_workload_api_socket_path` | `[openshell.drivers.kubernetes]` | Workload API socket mounted into sandbox pods |
| `provider_spiffe_workload_api_socket` | `[openshell.drivers.docker]`, `[openshell.drivers.podman]` | Host Unix socket (or `tcp:` endpoint on Podman) projected into the supervisor |
| `provider_spiffe_workload_api_tcp_endpoint`, `provider_spiffe_allow_guest_tcp` | `[openshell.drivers.vm]` | Guest-reachable TCP Workload API for VMs, with explicit acknowledgement |

SPIRE-side requirements from the broker section: enable SPIRE's experimental Broker endpoint; authorize the gateway SPIFFE ID for `KubernetesObjectReference` over TCP; Kubernetes attestor `access_policy = "enforced"`; agents need Sandbox `get`/`list` and SubjectAccessReview create; gateway SPIFFE ID needs `impersonate-via-spire` verb on Sandbox resources in permitted namespaces; register each sandbox's SPIFFE ID against its Sandbox resource UID, using a SPIRE node alias as parent. Limits: 4 concurrent authenticated requests per sandbox, 64 per gateway.

No `trust_domain` key and no token-grant key is defined on this page; token grants live in provider profiles (see openshell-dynamic-token-grants.md).

## Outline of the rest of the page (not reproduced)

Source Precedence (CLI flag > `OPENSHELL_*` env > TOML > default; `--config`, `OPENSHELL_GATEWAY_CONFIG`, `OPENSHELL_DB_URL`); Package-Managed Locations; Layout (`[openshell] version = 2`, `compute_driver`); Slow sandbox startup; Request ID capacity; Additional Destination CAs (`[openshell.supervisor.network] additional_ca_bundle`); Migrate to schema version 2; Full Example; Gateway listener TLS; Metrics Listener TLS; Authentication (`[openshell.gateway.oidc]` with `issuer`, `audience`, `jwks_ttl_secs`, `roles_claim`, `admin_role`, `user_role`, `scopes_claim`; `[openshell.gateway.mtls_auth]`; `[openshell.gateway.auth] allow_unauthenticated_users`); Service Routing; Sandbox Updates; Workspace Secrets; Azure PostgreSQL workload identity (`database_auth = "azure-workload-identity"`); Database Pool; OCSF JSONL Output; Gateway Mutation Records; OTLP Export (`[openshell.gateway.otlp]` + `.traces`, `.metrics`, `.ocsf`, `.agent`); Supervisor Middleware Services (`[[openshell.supervisor.middleware]]`); Gateway Interceptors (`[[openshell.gateway.interceptors]]`, `binding_policy` dynamic/allowlist/exact, `provider_profile_sources`); Credential Drivers (`kubernetes-secrets`, `vault`); Gateway Peer Routing; Driver References (External Resource Admission, Kubernetes, MXC, Docker, Podman, MicroVM, Extension Driver); Preflight (`openshell-gateway config preflight`); Supervisor application listener.
