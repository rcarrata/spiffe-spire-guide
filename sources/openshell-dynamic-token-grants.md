> Source: https://docs.nvidia.com/openshell/v0.0.116/sandboxes/providers-v2
> Retrieved: 2026-11-20
> Version: OpenShell docs v0.0.116 (page banner says latest is v0.1.9; dev and v0.1.x indexes exist at https://docs.nvidia.com/openshell/<version>/llms.txt)
> Notes: Page title "Providers v2". This file keeps the "Dynamic Token Grants" section VERBATIM, the full profile schema YAML example VERBATIM (it contains the `token_grant` block with `grant_type: token_exchange`, `jwt-spiffe`, `subject_token`), and the refresh strategy tables (refresh is a separate, gateway-managed mechanism). Other sections are summarized at the end. Text marked "(note)" is added.

# OpenShell Providers v2 - Dynamic Token Grants

## Overview (verbatim)

Providers v2 turns providers from credential records into profile-backed access bundles. A provider profile describes the credentials, endpoints, binaries, policy rules, and refresh behavior for a provider type. A provider instance stores the concrete credential and config values for one gateway.

Provider profile policy composition is controlled by the gateway-level `providers_v2_enabled` setting. Enable it on the active gateway:

```shell
openshell settings set --global --key providers_v2_enabled --value true
```

The feature flag controls provider-derived policy layers. It does not disable endpoint binding for static credential placeholders. Provider profiles can also declare dynamic token grants that the sandbox proxy resolves on demand for matching HTTP endpoints.

Feature list item: "Dynamic token grants that use the sandbox’s SPIFFE JWT-SVID as an OAuth2 client assertion and inject short-lived tokens into supported headers for matching profile endpoints."

## Profile Schema example (verbatim)

Provider profile YAML and JSON use this shape. Treat this as a field map, not a profile to import verbatim.

```yaml
id: custom-api
# Present on exported custom profiles; preserve it when updating.
resource_version: 1
annotations:
  example.com/source: platform
display_name: Custom API
description: Custom API access for sandbox agents
category: data
inference_capable: false

credentials:
  - name: user_oidc_token
    description: User OIDC token stored for gateway-side token exchange only
    required: true

  - name: api_token
    description: API access token
    env_vars: [CUSTOM_API_TOKEN]
    required: true

    # Accepted values: basic, bearer, header, query, path.
    # These fields describe static credential placement.
    # Static runtime injection still uses env placeholder resolution.
    auth_style: bearer
    header_name: authorization
    query_param: api_key
    path_template: /v1/{credential}/resources

    refresh:
      # Accepted values:
      # static, external, oauth2_refresh_token,
      # oauth2_client_credentials, google_service_account_jwt.
      strategy: oauth2_client_credentials
      token_url: https://login.example.com/oauth2/token
      scopes: [api.read, api.write]
      refresh_before_seconds: 300
      max_lifetime_seconds: 3600
      material:
        - name: client_id
          description: OAuth client ID
          required: true
          secret: false
        - name: client_secret
          description: OAuth client secret
          required: true
          secret: true

    # Optional dynamic credential. The sandbox supervisor resolves this on
    # demand for matching endpoint traffic, caches the returned access token,
    # and injects it according to auth_style/header_name.
    token_grant:
      # Accepted values: client_credentials, token_exchange.
      grant_type: token_exchange
      token_endpoint: https://login.example.com/realms/custom/protocol/openid-connect/token
      audience: api://custom-api
      jwt_svid_audience: https://login.example.com/realms/custom
      client_assertion_type: urn:ietf:params:oauth:client-assertion-type:jwt-spiffe
      scopes: [api.read, api.write]
      cache_ttl_seconds: 300
      requested_token_type: urn:ietf:params:oauth:token-type:access_token
      subject_token:
        source: provider_credential
        credential: user_oidc_token
        subject_token_type: urn:ietf:params:oauth:token-type:access_token
      audience_overrides:
        - host: api.example.com
          port: 443
          path: /v1/projects/**
          audience: api://custom-projects
          scopes: [projects.read]

discovery:
  credentials: [api_token]

endpoints:
  - host: api.example.com
    port: 443
    path: /v1/**
    protocol: rest
    tls: ""
    enforcement: enforce
    allowed_ips: []
    ports: []
    allow_encoded_slash: false
    websocket_credential_rewrite: false
    request_body_credential_rewrite: false
    allow_uninspected_credentials: false
    persisted_queries: deny
    graphql_max_body_bytes: 65536
    rules:
      - allow:
          method: GET
          path: /v1/projects/**
          command: ""
          query:
            tag:
              any: ["prod-*", "staging-*"]
          operation_type: ""
          operation_name: ""
          fields: []
    deny_rules:
      - method: DELETE
        path: /v1/projects/**
        command: ""
        query: {}
        operation_type: ""
        operation_name: ""
        fields: []
    graphql_persisted_queries:
      # Key must match the request's persisted query hash or saved-query ID.
      9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08:
        operation_type: query
        operation_name: GetProject
        fields: [project]

binaries:
  - /usr/bin/curl
  - /usr/local/bin/custom-cli
```

## Dynamic Token Grants (verbatim)

`token_grant` belongs to one credential declaration. When a sandbox with the provider attached sends HTTP traffic to a matching profile endpoint, the supervisor resolves the dynamic credential, caches the returned access token, and injects it before forwarding the request upstream. Use `auth_style: bearer` to inject `Authorization: Bearer <token>`, or `auth_style: header` with `header_name` to inject the raw access token into a custom header. Token grants do not support `query` or `path` placement.

OpenShell supports two dynamic grant types:

| Grant type | Behavior |
|----|----|
| `client_credentials` | The supervisor requests a SPIFFE JWT-SVID from the local Workload API and sends it directly to `token_endpoint` as the OAuth2 client assertion. This is the default when `grant_type` is omitted. |
| `token_exchange` | The supervisor first asks the gateway for an intermediate token. The request includes the supervisor JWT-SVID; the gateway verifies it, uses the SVID subject as the intermediate token audience, and exchanges the stored subject credential at the same `token_endpoint` using the gateway’s own JWT-SVID as the client assertion. The supervisor then exchanges that intermediate token for the final upstream token using its own JWT-SVID as the client assertion. |

Create provider instances for token-grant-only profiles with `--runtime-credentials`. This records an empty provider instance and makes the runtime-resolved credential source explicit:

```shell
openshell provider create \
  --name spiffe-token-demo \
  --type spiffe-token-demo \
  --runtime-credentials
```

For `token_exchange` profiles, the provider also stores the user subject token referenced by `token_grant.subject_token.credential`. That credential is gateway-only: the sandbox does not receive it as environment material, static credential binding metadata, or workload placeholder ownership. Create or update that provider credential from the current gateway OIDC login with `--from-oidc-token`. This requires an active named gateway that was registered for OIDC. The CLI copies the current OIDC access token and its expiry into the provider. If the stored gateway access token is expired and a refresh token is available, the CLI refreshes it first. OpenShell does not store the OIDC refresh token in the provider. When the stored subject-token credential expires, the gateway rejects intermediate token exchange until the provider is updated with a fresh token.

```shell
openshell provider create \
  --name custom-api \
  --type custom-api \
  --from-oidc-token

openshell provider update custom-api \
  --from-oidc-token
```

OpenShell infers the destination credential when the provider profile has exactly one `token_grant.subject_token.credential`. If a profile declares more than one token-exchange subject credential, pass `--credential <key>` to choose one.

Token grant fields:

| Field | Required | Behavior |
|----|----|----|
| `grant_type` | No | `client_credentials` or `token_exchange`. Defaults to `client_credentials` for backward compatibility. |
| `token_endpoint` | Yes | OAuth2 token endpoint that accepts a SPIFFE JWT-SVID client assertion. Use `https://` unless the endpoint is loopback or a Kubernetes service DNS name such as `token-issuer.default.svc.cluster.local`. |
| `audience` | No | Resource audience requested from the token service. For `token_exchange`, this is the final exchange audience; the gateway intermediate exchange always uses the verified supervisor SVID subject as its audience. |
| `jwt_svid_audience` | No | Audience used when requesting the JWT-SVID. When omitted, OpenShell derives an issuer-style audience from Keycloak token endpoint paths or falls back to the full token endpoint URL. |
| `client_assertion_type` | No | OAuth2 `client_assertion_type` form value. Defaults to RFC 7523 `urn:ietf:params:oauth:client-assertion-type:jwt-bearer`. Set `urn:ietf:params:oauth:client-assertion-type:jwt-spiffe` when the token issuer expects the SPIFFE assertion type. |
| `scopes` | No | OAuth2 scopes sent as a space-separated `scope` parameter. |
| `cache_ttl_seconds` | No | Token cache TTL override. When omitted or `0`, OpenShell uses the token response `expires_in` with a 30-second safety margin and one-hour cap, or five minutes minus the margin if the response does not include an expiry. |
| `requested_token_type` | No | RFC 8693 `requested_token_type` sent during token exchange. Defaults to `urn:ietf:params:oauth:token-type:access_token`. |
| `subject_token` | Required for `token_exchange` | Subject-token source used for the gateway-brokered intermediate exchange. Phase one supports `source: provider_credential`, where `credential` names another credential declared in the same profile. That referenced credential is broker-only and cannot declare workload injection metadata such as env vars, static placement, refresh, or token grant metadata. |
| `subject_token.subject_token_type` | No | RFC 8693 `subject_token_type` for the stored subject token. Defaults to `urn:ietf:params:oauth:token-type:access_token`. |
| `audience_overrides` | No | Endpoint-specific final-exchange `audience` and `scopes` overrides selected by host, port, and path. These overrides do not affect the gateway intermediate exchange. |

Token grants require the sandbox supervisor to have access to a SPIFFE Workload API socket. `token_exchange` also requires the gateway to have its own Workload API socket so it can present a gateway JWT-SVID during the intermediate exchange. They apply to HTTP traffic that the proxy can inspect. Endpoints with `tls: skip` bypass TLS termination and cannot receive dynamic token grant injection for HTTPS traffic. The token service must return a token value that is safe for HTTP header placement; malformed values are rejected before caching or header injection.

The gateway only brokers an intermediate token for a sandbox principal, and only when the requested provider is attached to that sandbox. It verifies the supervisor JWT-SVID issuer, audience, signature, and SPIFFE trust domain against the gateway’s own JWT-SVID, then uses the verified supervisor SVID subject as the intermediate-token audience.

## Credential refresh (separate from token grants, verbatim)

Credential refresh metadata belongs to one credential declaration. The profile defines allowed defaults, such as token URL, scopes, refresh lead time, maximum lifetime, and required material keys. The provider instance stores the actual refresh material.

Profile YAML can declare these refresh strategies:

| Strategy | Behavior |
|----|----|
| `static` | Current credentials are updated through `openshell provider update`. The gateway does not mint a token. |
| `external` | An external process updates current credentials through `openshell provider update`. The gateway does not mint a token. |
| `oauth2_refresh_token` | The gateway exchanges a refresh token for a short-lived access token. |
| `oauth2_client_credentials` | The gateway mints a short-lived access token with OAuth2 client credentials. |
| `google_service_account_jwt` | The gateway signs a Google service account JWT and exchanges it for an access token. |
| `aws_sts_assume_role` | The gateway calls `sts:AssumeRole` and mints `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_SESSION_TOKEN` in one operation. Requires `providers_v2_enabled=true`. |

`openshell provider refresh configure` accepts only gateway-mintable strategies: `oauth2-refresh-token`, `oauth2-client-credentials`, `google-service-account-jwt`, and `aws-sts-assume-role`. Use `openshell provider update` for `static` and `external` refresh patterns.

Gateway-managed refresh strategies use these material keys:

| Strategy | Material keys |
|----|----|
| `oauth2_refresh_token` | `client_id`, `refresh_token`, optional `client_secret`. |
| `oauth2_client_credentials` | `client_id`, `client_secret`, optional `tenant_id` for Microsoft Entra token URLs. |
| `google_service_account_jwt` | `client_email`, `private_key`, optional `subject` or `sub`. |
| `aws_sts_assume_role` | `role_arn`, optional `session_name`, `external_id`, `aws_region`, and optional long-lived `aws_access_key_id` / `aws_secret_access_key` for gateways without ambient AWS credentials. |

OpenShell keeps token endpoints profile-owned. Refresh material cannot override `token_url` or `token_uri` during refresh configuration.

### Additional Outputs

### Additional Outputs

Most refresh strategies mint a single credential. `aws_sts_assume_role` mints three. A refresh declares the extra credentials it co-mints with `additional_outputs`, mapping each strategy-defined output id to a sibling credential whose `env_vars` receive the value:

```yaml
credentials:
  - name: access_key_id
    env_vars: [AWS_ACCESS_KEY_ID]
    required: true
    refresh:
      strategy: aws_sts_assume_role
      additional_outputs:
        - output: secret_access_key
          credential: secret_access_key
        - output: session_token
          credential: session_token
  - name: secret_access_key
    env_vars: [AWS_SECRET_ACCESS_KEY]
    required: true
  - name: session_token
    env_vars: [AWS_SESSION_TOKEN]
    required: true
```

The refresh attaches to the primary credential (`access_key_id`). Each referenced sibling must exist, declare exactly one env var, and not carry its own refresh. Because a refresh’s outputs are runtime-resolvable, a profile whose only credentials are STS-minted can be created with `--runtime-credentials`. The resolved output-to-env-key mapping is pinned when refresh is configured, so later profile edits do not silently redirect where minted values are written.

## Rest of the page (summary, note)

- Built-in profiles (v0.0.116): `claude-code`, `codex`, `copilot`, `cursor`, `deepinfra`, `github`, `google-vertex-ai`, `nvidia`, `pypi`. Categories: `other`, `inference`, `agent`, `source_control`, `messaging`, `data`, `knowledge`.
- Profile CLI: `openshell provider list-profiles`, `openshell provider profile export|import|update|lint|delete`. Updates need the current `resource_version`; updates that make dynamic token grants ambiguous for an attached sandbox are rejected.
- Provider instances: `openshell provider create --type <id>` with `--credential`, `--from-existing`, `--runtime-credentials`, `--from-oidc-token`; expiry via `--credential-expires-at`.
- Static credentials are env placeholders resolved by the proxy only at profile endpoints (host/port/path); mismatch returns HTTP 403 `credential_endpoint_mismatch`. `auth_style` accepts `basic`, `bearer`, `header`, `query`, `path`; token grants only support `bearer` and `header`.
- Sandbox lifecycle: `--provider` at create, `openshell sandbox provider list|attach|detach`. Attached sets with conflicting env keys or ambiguous dynamic token grants at equal host/path specificity are rejected.
- Policy composition: effective policy = base sandbox policy + `_provider_*` layers (not persisted; user policies cannot define `_provider_*`; a gateway global policy suppresses provider layers).
- Refresh CLI: `openshell provider refresh status|configure|rotate|delete`; OAuth failures report recovery actions such as `reauthorize` (for `invalid_grant`) and `fix_configuration`.
