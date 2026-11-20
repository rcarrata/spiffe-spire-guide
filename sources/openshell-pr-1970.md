Source: https://github.com/NVIDIA/OpenShell/pull/1970
Retrieved: 2026-11-20 (via `gh api`, read-only)

# NVIDIA/OpenShell PR #1970 - feat(provider): support for SPIFFE backed token exchange

| Field | Value |
|---|---|
| State | closed, **merged** |
| Merged at | 2026-08-24T05:56:57Z (merge commit `40d1b4866691be03b5617089739c7f2325487479`) |
| Author | grs |
| Created | 2026-06-22 |
| Base / head | `main` / `token-exchange` |
| Labels | `test:e2e`, `gator:approval-needed` |
| Milestone | none |
| Size | 84 files, +10154 / -1814 |
| Fixes | #1987 "feat: support user-subject dynamic token grants for sandbox agents" (closed) |
| First release containing it | **v0.0.113** (2026-08-25). Checked with compare API: merge commit is 9 commits ahead of v0.0.111 and included in v0.0.113. |

## Summary (my notes)

- Before this PR OpenShell already had `token_grant` with `client_credentials`: the sandbox supervisor gets a JWT-SVID from the SPIFFE Workload API and sends it as `client_assertion` to a token endpoint (Keycloak etc.). The Helm value `server.providerTokenGrants.spiffe` already existed (sandbox socket only).
- This PR adds **`grant_type: token_exchange`** (RFC 8693). Two-stage flow:
  1. Supervisor fetches its JWT-SVID and calls the new gateway gRPC **`ExchangeProviderSubjectToken`** (auth_mode `sandbox`). The gateway verifies the supervisor SVID with JWT bundles from **its own** Workload API socket, fetches its **own gateway JWT-SVID**, and exchanges the stored user subject token (provider credential) at `token_endpoint` with `audience = <supervisor SPIFFE ID>`.
  2. Supervisor exchanges that intermediate token again, using its own JWT-SVID as `client_assertion`, and gets the final token: `sub` = user, `azp` = sandbox SPIFFE ID.
- The subject token (user OIDC token) is **gateway-only**, never given to the sandbox. New CLI flag `openshell provider create|update --from-oidc-token`.
- Gateway socket config is an **env var** in this PR: `OPENSHELL_GATEWAY_SPIFFE_WORKLOAD_API_SOCKET` (set by Helm when `server.providerTokenGrants.spiffe.enabled=true`). There is **no** `[openshell.gateway.spiffe*]` TOML section in #1970.
- Sandbox supervisor socket env: `OPENSHELL_PROVIDER_SPIFFE_WORKLOAD_API_SOCKET` (`openshell_core::sandbox_env::PROVIDER_SPIFFE_WORKLOAD_API_SOCKET`), default path `/spiffe-workload-api/spire-agent.sock` (mount dir constant `PROVIDER_SPIFFE_WORKLOAD_API_SOCKET_MOUNT_DIR = "/spiffe-workload-api"`). Podman driver gets new config `provider_spiffe_workload_api_socket` (host path).
- `client_assertion_type` default is `urn:ietf:params:oauth:client-assertion-type:jwt-bearer`; set `urn:ietf:params:oauth:client-assertion-type:jwt-spiffe` when the IdP expects it (the example profiles use jwt-spiffe).

> Note on the "SPIFFE broker API" and `[openshell.gateway.spiffe_broker]`: these are **not** from #1970. They come from the later PR **#4732 "feat(gateway): broker stable sandbox SPIFFE provider tokens"** (merged 2026-11-18, not yet in a release; v0.1.9 from 2026-11-17 does not include it). See the section at the end.

---

## Full description (PR body)

### Summary
This PR adds the ability to specify token_exchange instead of a simple token_grant in a provider profile, with the goal of automatically obtaining a token that combines the agents identity with that of the user on whose behalf it is acting.

As with the existing token grants, the token exchange is initiated by the supervisor proxy. In the case of an exchange however it requires a subject token that has the supervisor clients id in the audience. To get this, a two stage exchange is required.

The supervisor first requests a token from the gateway. The gateway does the first exchange, using the identified credential in a provider as the subject and requesting the audience needed for the supervisor (which is based on the supervisors SPIFFE ID). The token from that exchange is then returned to the supervisor which uses it as the subject for a further exchange. The resulting token than has the subject of the original provider credential but the sandbox (as identified by its SPIFFE ID) as the authorized party.

An option was also added to the CLI for provider create|update, allowing the current OIDC token to be stored.

### Related Issue
Fixes #1987

### Changes
- Added token_exchange as a provider token grant mode alongside client_credentials.
- Extended provider profiles/protobuf with subject-token metadata, requested token type, and SPIFFE JWT-SVID settings.
- Added gateway-side subject-token exchange support for sandbox-scoped dynamic credentials.
- Added shared SPIFFE/JWT-SVID helpers and gateway SPIFFE Workload API Helm wiring.
- Updated CLI option to store current OIDC token.

### Testing
- [x] `mise run pre-commit` passes
- [x] Unit tests added/updated
- [x] E2E tests added/updated (if applicable)
- [x] Manual tests of token exchange, including with updated token, as well as of the original simple token grant.

### Checklist
- [x] Follows Conventional Commits
- [x] Commits are signed off (DCO)
- [x] Architecture docs updated (if applicable)

---

## Changed files (84)

```
.agents/skills/debug-openshell-cluster/SKILL.md            modified +9-3
Cargo.lock                                                 modified +232-45
Cargo.toml                                                 modified +1-1
architecture/sandbox.md                                    modified +23-6
crates/openshell-cli/src/main.rs                           modified +47-27
crates/openshell-cli/src/oidc_auth.rs                      modified +16-6
crates/openshell-cli/src/run.rs                            modified +255-46
crates/openshell-cli/tests/ensure_providers_integration.rs modified +9-1
crates/openshell-cli/tests/mtls_integration.rs             modified +12-4
crates/openshell-cli/tests/provider_commands_integration.rs modified +55-49
crates/openshell-cli/tests/sandbox_create_lifecycle_integration.rs modified +9-1
crates/openshell-cli/tests/sandbox_name_fallback_integration.rs modified +9-1
crates/openshell-core/Cargo.toml                           modified +3-1
crates/openshell-core/src/driver_utils.rs                  modified +3-0
crates/openshell-core/src/grpc_client.rs                   modified +61-6
crates/openshell-core/src/lib.rs                           modified +3-0
crates/openshell-core/src/oauth.rs                         added    +766-0
crates/openshell-core/src/spiffe.rs                        added    +177-0
crates/openshell-driver-podman/src/config.rs               modified +8-0
crates/openshell-driver-podman/src/container.rs            modified +74-0
crates/openshell-providers/src/profiles.rs                 modified +454-2
crates/openshell-sdk/tests/client_mock.rs                  modified +7-0
crates/openshell-server/Cargo.toml                         modified +2-1
crates/openshell-server/src/auth/oidc.rs                   modified +6-0
crates/openshell-server/src/auth/sandbox_jwt.rs            modified +8-0
crates/openshell-server/src/auth/sandbox_methods.rs        modified +3-0
crates/openshell-server/src/grpc/mod.rs                    modified +9-1
crates/openshell-server/src/grpc/policy.rs                 modified +122-0
crates/openshell-server/src/grpc/provider.rs               modified +663-15
crates/openshell-server/src/lib.rs                         modified +4-0
crates/openshell-server/src/provider_refresh.rs            modified +2-0
crates/openshell-server/tests/common/mod.rs                modified +10-2
crates/openshell-server/tests/supervisor_relay_integration.rs modified +6-0
crates/openshell-supervisor-network/Cargo.toml             modified +1-1
crates/openshell-supervisor-network/src/l7/relay.rs        modified +302-0
crates/openshell-supervisor-network/src/l7/token_grant_injection.rs modified +138-10
crates/openshell-supervisor-network/src/lib.rs             modified +0-1
crates/openshell-supervisor-network/src/proxy.rs           modified +141-18
crates/openshell-supervisor-network/src/spiffe_endpoint.rs removed  +0-17
crates/openshell-supervisor-network/src/token_grant.rs     modified +254-448
crates/openshell-supervisor-process/src/process.rs         modified +126-91
crates/openshell-supervisor-process/src/run.rs             modified +10-2
crates/openshell-supervisor-process/src/ssh.rs             modified +12-38
deploy/helm/openshell/README.md                            modified +12-7
deploy/helm/openshell/README.md.gotmpl                     modified +10-5
deploy/helm/openshell/templates/_gateway-workload.tpl      modified +17-1
deploy/helm/openshell/tests/gateway_config_test.yaml       modified +32-4
deploy/helm/openshell/values.yaml                          modified +6-6
docs/kubernetes/access-control.mdx                         modified +6-2
docs/reference/gateway-config.mdx                          modified +8-0
docs/sandboxes/manage-providers.mdx                        modified +29-0
docs/sandboxes/providers-v2.mdx                            modified +47-10
e2e/rust/Cargo.lock                                        modified +555-16
e2e/rust/Cargo.toml                                        modified +10-0
e2e/rust/e2e-podman.sh                                     modified +7-0
e2e/rust/tests/provider_token_exchange.rs                  added    +907-0
e2e/with-podman-gateway.sh                                 modified +13-0
examples/spiffe-token-exchange-demo/README.md              added    +232-0
examples/spiffe-token-exchange-demo/demo.sh                added    +229-0
examples/spiffe-token-exchange-demo/k8s/kustomization.yaml added    +20-0
examples/spiffe-token-exchange-demo/k8s/protected-service.js added  +120-0
examples/spiffe-token-exchange-demo/k8s/spiffe-helper.conf added    +8-0
examples/spiffe-token-exchange-demo/k8s/token-issuer.js    added    +342-0
examples/spiffe-token-exchange-demo/k8s/workloads.yaml     added    +230-0
examples/spiffe-token-exchange-demo/podman/README.md       added    +316-0
examples/spiffe-token-exchange-demo/podman/demo.sh         added    +675-0
examples/spiffe-token-exchange-demo/podman/provider-profile.yaml added +58-0
examples/spiffe-token-exchange-demo/podman/spire/agent.conf added   +37-0
examples/spiffe-token-exchange-demo/podman/spire/common.sh added    +157-0
examples/spiffe-token-exchange-demo/podman/spire/oidc-discovery-provider.conf added +19-0
examples/spiffe-token-exchange-demo/podman/spire/register-gateway.sh added +40-0
examples/spiffe-token-exchange-demo/podman/spire/register-sandbox.sh added +43-0
examples/spiffe-token-exchange-demo/podman/spire/server.conf added  +39-0
examples/spiffe-token-exchange-demo/podman/spire/start-agent.sh added +78-0
examples/spiffe-token-exchange-demo/podman/spire/start-server-oidc.sh added +80-0
examples/spiffe-token-exchange-demo/podman/start-gateway.sh added   +233-0
examples/spiffe-token-exchange-demo/provider-profile.yaml  added    +53-0
proto/openshell.proto                                      modified +60-0
sdk/go/openshell/v1/internal/converter/coverage_test.go    modified +3-0
sdk/go/openshell/v1/internal/converter/profile.go          modified +52-0
sdk/go/openshell/v1/internal/converter/profile_test.go     modified +26-0
sdk/go/openshell/v1/types/profile.go                       modified +19-0
sdk/go/proto/openshellv1/openshell.pb.go                   modified +1232-919
sdk/go/proto/openshellv1/openshell_grpc.pb.go              modified +42-0
```

---

## Key excerpts

### 1. Helm values (`deploy/helm/openshell/values.yaml`)

```diff
-  # Dynamic provider token grants. When SPIFFE is enabled here, sandbox
-  # supervisors mount the SPIFFE Workload API socket so provider profiles can
-  # exchange JWT-SVIDs for upstream access tokens. Supervisor-to-gateway
-  # authentication still uses gateway-minted sandbox JWTs.
+  # Dynamic provider token grants. When SPIFFE is enabled here, both the
+  # gateway and sandbox supervisors mount the SPIFFE Workload API socket so
+  # token-exchange profiles can use gateway- and sandbox-scoped JWT-SVIDs.
+  # Supervisor-to-gateway authentication still uses gateway-minted sandbox JWTs.
   providerTokenGrants:
     spiffe:
-      # -- Mount the SPIFFE Workload API socket into sandbox pods for dynamic provider token grants.
+      # -- Mount the SPIFFE Workload API socket into gateway and sandbox pods for dynamic provider token grants.
       enabled: false
-      # -- Path to the SPIFFE Workload API socket mounted into sandbox pods.
+      # -- Path to the SPIFFE Workload API socket mounted into gateway and sandbox pods.
       workloadApiSocketPath: /spiffe-workload-api/spire-agent.sock
```

So: `server.providerTokenGrants.spiffe.enabled` (default `false`) and `server.providerTokenGrants.spiffe.workloadApiSocketPath` (default `/spiffe-workload-api/spire-agent.sock`). Note: on current `main` the Helm README now says to set `gatewayConfig.openshell.drivers.kubernetes.provider_spiffe_workload_api_socket_path` for sandbox supervisors (changed after #1970).

### 2. Gateway pod wiring (`templates/_gateway-workload.tpl`)

```diff
+        {{- if .Values.server.providerTokenGrants.spiffe.enabled }}
+        - name: OPENSHELL_GATEWAY_SPIFFE_WORKLOAD_API_SOCKET
+          value: {{ .Values.server.providerTokenGrants.spiffe.workloadApiSocketPath | quote }}
+        {{- end }}
...
+        {{- if .Values.server.providerTokenGrants.spiffe.enabled }}
+        - name: spiffe-workload-api
+          mountPath: {{ dir .Values.server.providerTokenGrants.spiffe.workloadApiSocketPath | quote }}
+          readOnly: true
+        {{- end }}
...
+    {{- if .Values.server.providerTokenGrants.spiffe.enabled }}
+    - name: spiffe-workload-api
+      csi:
+        driver: csi.spiffe.io
+        readOnly: true
+    {{- end }}
```

Uses the SPIFFE CSI driver `csi.spiffe.io`.

Gateway config docs (`docs/reference/gateway-config.mdx`):

> For token-exchange provider profiles, the gateway also needs access to its own SPIFFE Workload API socket. In Helm deployments, set `server.providerTokenGrants.spiffe.enabled=true`; the chart mounts the socket into the gateway pod and sets `OPENSHELL_GATEWAY_SPIFFE_WORKLOAD_API_SOCKET`. The gateway verifies supervisor JWT-SVIDs with JWT bundles fetched from the SPIFFE Workload API, so this validation path does not require gateway access to the SPIRE OIDC discovery endpoint or its TLS CA.

### 3. How the sandbox supervisor gets an SVID

`crates/openshell-supervisor-network/src/token_grant.rs` - `fetch_jwt_svid_for_token_grant` reads the socket from `OPENSHELL_PROVIDER_SPIFFE_WORKLOAD_API_SOCKET` and connects with the `spiffe` crate (`WorkloadApiClient`):

```diff
 async fn fetch_jwt_svid_for_token_grant(audience: &str) -> Result<String> {
     let socket_path = provider_spiffe_workload_api_socket_from_env()?;
 
     let endpoint =
-        crate::spiffe_endpoint::workload_api_endpoint(std::path::Path::new(&socket_path));
+        openshell_core::spiffe::workload_api_endpoint(std::path::Path::new(&socket_path));
 
     // Connect to SPIRE agent
     let client = WorkloadApiClient::connect_to(&endpoint)
```

`crates/openshell-core/src/spiffe.rs` (new, shared helper; moved from supervisor-network):

```rust
/// If the path already has a scheme (`unix:` or `tcp:`), use it as-is.
/// Otherwise, assume it is a Unix socket path and prepend `unix:`.
pub fn workload_api_endpoint(path: &Path) -> String { ... }

pub fn trust_domain(subject: &str) -> Option<&str> {
    let rest = subject.strip_prefix("spiffe://")?;
    ...
}
```

Defined constants:

```rust
// crates/openshell-core/src/sandbox_env.rs (already present)
pub const PROVIDER_SPIFFE_WORKLOAD_API_SOCKET: &str =
    "OPENSHELL_PROVIDER_SPIFFE_WORKLOAD_API_SOCKET";
// crates/openshell-core/src/driver_utils.rs (added)
pub const PROVIDER_SPIFFE_WORKLOAD_API_SOCKET_MOUNT_DIR: &str = "/spiffe-workload-api";
```

The supervisor hides the identity socket from sandbox child processes with a separate mount namespace (`supervisor-process/src/run.rs`):

```diff
+    // Provider token grants may mount supervisor-only identity sockets such as
+    // the SPIFFE Workload API. Prepare the child mount namespace that hides
+    // those mounts before supervisor seccomp hardening removes the needed
+    // namespace syscalls.
+    #[cfg(target_os = "linux")]
+    crate::process::prepare_supervisor_identity_mount_namespace_from_env()?;
```

Podman driver (`driver-podman/src/config.rs`):

```diff
+    /// Host path to a SPIFFE Workload API Unix socket exposed to sandbox
+    /// supervisors for provider token exchange client assertions.
+    pub provider_spiffe_workload_api_socket: Option<PathBuf>,
```

Example SPIFFE ID used in tests and demo: `spiffe://openshell.local/openshell/sandbox/<sandbox-uuid>`. The K8s setup uses a `ClusterSPIFFEID` that assigns sandbox IDs from the pod annotation `openshell.io/sandbox-id`.

### 4. New gateway gRPC (`proto/openshell.proto`)

```proto
  // Exchange a stored provider subject token for an intermediate token scoped
  // to the calling supervisor's SPIFFE identity.
  rpc ExchangeProviderSubjectToken(ExchangeProviderSubjectTokenRequest)
      returns (ExchangeProviderSubjectTokenResponse) {
    option (openshell.options.v1.authorization) = {
      auth_mode: "sandbox"
    };
  }

enum ProviderCredentialTokenGrantType {
  PROVIDER_CREDENTIAL_TOKEN_GRANT_TYPE_UNSPECIFIED = 0;
  PROVIDER_CREDENTIAL_TOKEN_GRANT_TYPE_CLIENT_CREDENTIALS = 1;
  PROVIDER_CREDENTIAL_TOKEN_GRANT_TYPE_TOKEN_EXCHANGE = 2;
}

message ProviderCredentialTokenGrantSubjectToken {
  string source = 1;              // phase one: "provider_credential"
  string credential = 2;
  string subject_token_type = 3;  // default urn:ietf:params:oauth:token-type:access_token
}

// added to ProviderCredentialTokenGrant:
  ProviderCredentialTokenGrantType grant_type = 8;
  ProviderCredentialTokenGrantSubjectToken subject_token = 9;
  string requested_token_type = 10;

message ExchangeProviderSubjectTokenRequest {
  string sandbox_id = 1;
  string provider = 2;
  string credential_key = 3;
  // Supervisor JWT-SVID. The gateway verifies this and uses its `sub` claim
  // as the requested audience for the intermediate token.
  string supervisor_jwt_svid = 4 [(openshell.options.v1.secret) = true];
}

message ExchangeProviderSubjectTokenResponse {
  string access_token = 1 [(openshell.options.v1.secret) = true];
  int64 expires_in = 2;
  string token_type = 3;
}
```

### 5. Gateway side broker (`crates/openshell-server/src/grpc/provider.rs`)

```rust
const GATEWAY_SPIFFE_WORKLOAD_API_SOCKET: &str = "OPENSHELL_GATEWAY_SPIFFE_WORKLOAD_API_SOCKET";

pub(super) async fn handle_exchange_provider_subject_token(...) {
    let principal = crate::auth::guard::enforce_sandbox_scope(&request, &req.sandbox_id)?;
    ...
    if !spec.providers.iter().any(|provider| provider == &req.provider) {
        return Err(Status::permission_denied("provider is not attached to this sandbox"));
    }
    ...
    let gateway_jwt_svid = fetch_gateway_jwt_svid(&jwt_svid_audience).await?;
    let gateway_claims = parse_unverified_spiffe_claims(&gateway_jwt_svid)?;
    validate_gateway_jwt_svid_claims(&gateway_claims, &jwt_svid_audience)?;
    let supervisor_claims = validate_supervisor_jwt_svid(
        &req.supervisor_jwt_svid, &gateway_claims, &jwt_svid_audience).await?;
    ...
    let token_response = perform_intermediate_token_exchange(
        &token_grant.token_endpoint,
        &gateway_jwt_svid,                 // client_assertion = gateway SVID
        &token_grant.client_assertion_type,
        &stored_subject_token,             // user OIDC token from provider
        &subject_token.subject_token_type,
        &supervisor_claims.sub,            // audience = supervisor SPIFFE ID
        &token_grant.requested_token_type,
    )
```

Supervisor SVID validation (issuer and trust domain must match the gateway SVID, signature checked with Workload API JWT bundles):

```rust
    if unverified.iss != gateway_claims.iss {
        return Err(Status::permission_denied(
            "supervisor SVID issuer does not match gateway SVID issuer"));
    }
    ...
    if supervisor_trust_domain != gateway_trust_domain {
        return Err(Status::permission_denied(
            "supervisor SVID trust domain does not match gateway SVID trust domain"));
    }
    ...
    let bundles = client.fetch_jwt_bundles().await ...;
    spiffe::JwtSvid::parse_and_validate(token, &bundles, &[expected_audience])
        .map_err(|e| Status::permission_denied(format!("invalid supervisor JWT-SVID: {e}")))?;
```

Intermediate tokens are cached by provider resource version, supervisor SPIFFE subject and gateway SPIFFE subject (`INTERMEDIATE_TOKEN_CACHE`).

### 6. Supervisor two-stage flow (`token_grant.rs`)

```rust
            match grant_type {
                ProviderCredentialTokenGrantType::ClientCredentials
                | ProviderCredentialTokenGrantType::Unspecified => {
                    perform_token_grant(request.token_endpoint, &jwt_svid,
                        request.client_assertion_type, request.audience, request.scopes).await
                }
                ProviderCredentialTokenGrantType::TokenExchange => {
                    ...
                    let intermediate =
                        openshell_core::grpc_client::exchange_provider_subject_token(
                            &endpoint, &sandbox_id, provider, credential_key, &jwt_svid,
                        ).await ...;
                    validate_access_token(&intermediate.access_token)?;
                    perform_token_exchange(
                        request.token_endpoint,
                        &TokenExchangeParams {
                            client_assertion: &jwt_svid,
                            client_assertion_type: request.client_assertion_type,
                            subject_token: &intermediate.access_token,
                            subject_token_type: ACCESS_TOKEN_TYPE,
                            audience: request.audience,
                            scopes: request.scopes,
                            requested_token_type: request.requested_token_type,
                        },
                    ).await
                }
            }
```

### 7. OAuth form (`crates/openshell-core/src/oauth.rs`, new)

```rust
pub const DEFAULT_CLIENT_ASSERTION_TYPE: &str =
    "urn:ietf:params:oauth:client-assertion-type:jwt-bearer";
pub const ACCESS_TOKEN_TYPE: &str = "urn:ietf:params:oauth:token-type:access_token";
const TOKEN_EXCHANGE_GRANT_TYPE: &str = "urn:ietf:params:oauth:grant-type:token-exchange";

// client_credentials (RFC 7523):
        ("grant_type", "client_credentials"),
        ("client_assertion_type", client_assertion_type),
        ("client_assertion", params.client_assertion),

// token exchange (RFC 8693):
    let form_params = vec![
        ("grant_type", TOKEN_EXCHANGE_GRANT_TYPE),
        ("client_assertion_type", client_assertion_type),
        ("client_assertion", params.client_assertion),
        ("subject_token", params.subject_token),
        ("subject_token_type", subject_token_type),
        ("requested_token_type", requested_token_type),
    ];
// + optional "audience" and "scope"
```

No `client_id` is sent; the client is identified by the `sub` of the JWT-SVID. Unit test asserts `client_assertion_type = urn:ietf:params:oauth:client-assertion-type:jwt-spiffe` round trips into the form.

### 8. Provider profile (`examples/spiffe-token-exchange-demo/provider-profile.yaml`)

```yaml
id: spiffe-token-exchange-demo
credentials:
  - name: subject_token
    description: Demo user subject token stored for gateway-side token exchange only
    required: true
  - name: access_token
    description: Access token obtained via RFC 8693 token exchange
    required: false
    auth_style: bearer
    header_name: Authorization
    token_grant:
      grant_type: token_exchange
      token_endpoint: http://token-exchange-issuer.default.svc.cluster.local/token
      audience: demo-default
      jwt_svid_audience: http://token-exchange-issuer.default.svc.cluster.local
      client_assertion_type: urn:ietf:params:oauth:client-assertion-type:jwt-spiffe
      scopes: [demo]
      cache_ttl_seconds: 60
      subject_token:
        source: provider_credential
        credential: subject_token
        subject_token_type: urn:ietf:params:oauth:token-type:access_token
      audience_overrides:
        - host: alpha-exchange.default.svc.cluster.local
          port: 80
          audience: alpha
          scopes: [alpha]
```

Docs (`docs/sandboxes/providers-v2.mdx`) Keycloak-style example: `token_endpoint: https://login.example.com/realms/custom/protocol/openid-connect/token`, `jwt_svid_audience: https://login.example.com/realms/custom` (realm issuer = Keycloak `aud` requirement). "When omitted, OpenShell derives an issuer-style audience from Keycloak token endpoint paths or falls back to the full token endpoint URL."

Token grant fields added: `grant_type` (`client_credentials` default | `token_exchange`), `requested_token_type`, `subject_token` (`source`, `credential`, `subject_token_type`). Doc row:

> | `client_assertion_type` | No | OAuth2 `client_assertion_type` form value. Defaults to RFC 7523 `urn:ietf:params:oauth:client-assertion-type:jwt-bearer`. Set `urn:ietf:params:oauth:client-assertion-type:jwt-spiffe` when the token issuer expects the SPIFFE assertion type. |

CLI:

```shell
openshell provider create --name custom-api --type custom-api --from-oidc-token
openshell provider update custom-api --from-oidc-token
```

> The CLI copies the current OIDC access token and its expiry into the provider ... OpenShell does not store the OIDC refresh token in the provider. When the stored subject-token credential expires, the gateway rejects intermediate token exchange until the provider is updated with a fresh token.

### 9. Architecture doc (`architecture/sandbox.md`, extract)

> `client_credentials` grants use the supervisor SPIFFE JWT-SVID directly as the client assertion. `token_exchange` grants ask the gateway to broker an intermediate token using a stored provider subject credential and the gateway's own SPIFFE JWT-SVID; the supervisor then exchanges that intermediate token for the final upstream token using its own JWT-SVID. ... The gateway verifies the supervisor JWT-SVID signature with JWT bundles fetched from its SPIFFE Workload API.

---

## Review comments (relevant)

- **rhuss (2026-07-30, inline, sandbox_env.rs)**: `GATEWAY_SPIFFE_WORKLOAD_API_SOCKET` does not belong in `sandbox_env` (no driver sets it). **grs**: moved to a private server-local constant in `crates/openshell-server/src/grpc/provider.rs`.
- **rhuss (inline, proto)**: `supervisor_jwt_svid` and `access_token` missing `[(openshell.options.v1.secret) = true]`. **grs**: fixed.
- **rhuss (inline, token_grant.rs)**: unknown `grant_type` silently falls back to `ClientCredentials`; suggest warning/error. **grs**: fixed.
- **rhuss / coderabbit (inline)**: stage-2 `subject_token_type` was derived from `requested_token_type`; should be access token type. **grs**: fixed (renamed constant).
- **rhuss review (2026-07-30)**: "The two-stage exchange design is solid, and the security model (subject token never leaves gateway, audience-scoped intermediates, full SVID verification via SPIRE JWT bundles) is well thought through." Suggested splitting out the demo and a shared exchange helper. Also: "If a provider profile doesn't declare `token_exchange`, or SPIFFE infrastructure isn't present, the feature is completely inert."
- **afourniernv (2026-07-21)** asked if Okta client-secret OBO exchange (#1681) is covered. **grs**: "At present it does indeed require the IdP to accept SPIFFE JWT-SVIDs" - this path is meant for a platform-provided credential scoped to the sandbox.
- **akram (2026-08-10), OpenShift + ZTWIM test**: demo passes on k3d (upstream SPIRE) and OpenShift ROSA HCP 4.21 with Zero Trust Workload Identity Manager operator v1.1.0. ZTWIM adaptations: `ClusterSPIFFEID` needs `className: zero-trust-workload-identity-manager-spire`; OIDC discovery service is in the `zero-trust-workload-identity-manager` namespace; `SPIRE_ISSUER` must match `jwtIssuer` in the SpireServer CR (not the service name); self-signed OIDC cert (dev workaround `NODE_TLS_REJECT_UNAUTHORIZED=0`). Token refresh verified after 6 min (5 min JWT-SVID TTL). Result token: `sub: demo-user`, `aud: alpha, account`, `azp: spiffe://openshell.local/openshell/sandbox/<uuid>`. Released CLI v0.0.45 did not support `token_exchange` at that time.
- **franciscojavierarceo (2026-08-14)**: macOS build broken by `Path` import under `cfg(linux)` in Podman helpers (fixed later, "portability delta").
- **johntmyers / gator-agent (2026-08-21)**: blocking finding `GATOR-e577e093-01` - subject credential (raw user OIDC token) was reachable through the sandbox static-credential placeholder surface. Resolved same day: "The subject credential is withheld from sandbox environment material, static bindings, expiry metadata, and workload placeholder ownership; profile validation rejects workload-injectable broker subjects".
- grs (2026-07-14): "verified that this works with both currently supported supervisor topologies."

---

## Later development: PR #4732 (SPIFFE Broker API, `[openshell.gateway.spiffe_broker]`)

Source: https://github.com/NVIDIA/OpenShell/pull/4732 - "feat(gateway): broker stable sandbox SPIFFE provider tokens", by drew, **merged 2026-11-18**, closes #4731. Not in v0.1.9 (latest release, 2026-11-17).

From the body: "Enable shared-supervisor Kubernetes sandboxes to obtain provider access tokens using stable sandbox SPIFFE identities. The gateway obtains sandbox JWT-SVIDs through SPIRE's experimental SPIFFE Broker API and performs provider-token exchanges. Supervisors authenticate with each sandbox generation's credentials and receive only final provider access tokens; workloads receive no SPIFFE socket or credentials."

- New RPC `GetSandboxProviderAccessToken`.
- Sandbox SPIFFE ID: `<prefix>/gateway/<gateway-id>/sandbox/<sandbox-id>`, requested by the Sandbox CR Kubernetes UID.
- Gateway authenticates to the Broker over mTLS with its X.509-SVID from the CSI Workload API; gateway does RFC 7523 or both RFC 8693 stages itself.
- New crates `openshell-spiffe` and `openshell-spire` (`crates/openshell-spire/src/broker.rs`); `crates/openshell-server/src/spiffe_broker.rs`; `openshell-core/src/spiffe.rs` from #1970 removed (moved).
- Config `SpiffeBrokerConfig` fields: `spiffe_id_prefix`, `endpoint`, `node_local_port`, `server_spiffe_id`, `server_spiffe_id_prefix`, `workload_api_socket_path`. Requires `gateway_jwt` with positive `ttl_secs`. SPIRE side needs the Broker endpoint enabled, gateway SPIFFE ID authorized (`impersonate-via-spire`), and K8s workload attestor `access_policy: enforced`.

Helm example (`deploy/helm/openshell/ci/values-supervisor-spiffe.yaml`):

```yaml
gatewayConfig:
  openshell.drivers.kubernetes:
    supervisor_topology: gateway
  openshell.gateway.spiffe_broker:
    spiffe_id_prefix: spiffe://openshell.local/openshell
    endpoint: https://spire-broker.spire.svc:8443
    server_spiffe_id_prefix: spiffe://openshell.local/spire/agent/k8s_psat/openshell-e2e
    workload_api_socket_path: /spiffe-workload-api/spire-agent.sock
```

Node-local variant uses `node_local_port: 8443` instead of `endpoint` (chart injects node address from `status.hostIP`). Helm README: "For `supervisor_topology: gateway`, configure `gatewayConfig.openshell.gateway.spiffe_broker` instead. Only the gateway mounts the CSI Workload API socket and obtains stable sandbox identities through the Broker API; shared supervisors receive final access tokens."
