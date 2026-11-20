Source: https://github.com/keycloak/keycloak/issues/41907
Retrieved: 2026-11-20 (via `gh api`, read-only)

# keycloak/keycloak #41907 - Support authenticating clients with SPIFFE/SPIRE

| Field | Value |
|---|---|
| State | closed (state_reason: **duplicate**), closed 2025-09-16 |
| Author | stianst |
| Created | 2025-08-15 |
| Labels | `kind/feature` |
| Milestone | none |
| Superseded by | [#42634 Federated client authentication](https://github.com/keycloak/keycloak/issues/42634) (closed/completed 2026-03-17, milestone 26.6.0) |

## Current status (summary as of 2026-11-20)

- The work moved to the epic **#42634 "Federated client authentication"**. SPIFFE was implemented as an **identity provider type `spiffe`** plus a generic **client authenticator `federated-jwt`** ("Signed JWT - Federated"), not as a separate SPIFFE client authenticator. This is the "milestone 2" approach from this issue.
- **Merged**: experimental code landed in main in Sept 2025 (PR #42229 federated client auth, PR #42314 SPIFFE identity provider). Both became **preview** in **Keycloak 26.4.0** (PR #42753).
- **Keycloak 26.6.0** (PR #47184, merged 2026-03-17): `CLIENT_AUTH_FEDERATED` and `KUBERNETES_SERVICE_ACCOUNTS` went to **supported (default)**. **`SPIFFE` stays PREVIEW** because the IETF OAuth SPIFFE client auth draft is still a draft.
- Follow-up to make SPIFFE supported: **#46977 "Supported SPIFFE client authentication"** - still **open**, now on "27.0 Development Milestone" (it was set provisionally to 26.7 first).
- Latest Keycloak release at time of writing: 26.8.2 (2026-11-05). SPIFFE is still preview there (the `Profile.java` on main still has `SPIFFE(..., Type.PREVIEW)`).
- Other open SPIFFE work: #49833 "Client authentication with SPIFFE X509 SVID" (open), PR #54746 "feat: support SPIFFE federation bundle maps" (open, opened 2026-11-06).

### How to use it (from code and docs on main)

- Feature flags: `spiffe` (preview, must be enabled) and `client-auth-federated` (default since 26.6). From 26.5 you can enable a single feature with `--feature-spiffe=enabled` (release notes 26.5.0: "`feature-<name>` option (like `feature-spiffe=enabled`)"). Before 26.6, `client-auth-federated` was also needed (preview).
- Identity provider: type / provider id **`spiffe`** (`SpiffeIdentityProviderFactory.PROVIDER_ID = "spiffe"`, display name "SPIFFE"). Config keys (`SpiffeIdentityProviderConfig`):
  - `trustDomain` - "SPIFFE Trust Domain", must match `spiffe://[a-z0-9.\-_]*` (e.g. `spiffe://my-trust-domain`). In 26.5 this replaced the old `issuer` key (upgrade note "SPIFFE Identity Provider configuration changed").
  - `bundleEndpoint` - "SPIFFE Bundle Endpoint", `https` URL of the SPIFFE bundle endpoint **or** an OIDC JWKS endpoint (OIDC JWKS support added by PR #43651/#43656, Oct 2025).
  - Also `allowedClockSkew`. A `spiffe_refresh_hint` support was added for bundle refresh (PR #43242, merged 2025-10-07).
- Client authenticator: id **`federated-jwt`** (`FederatedJWTClientAuthenticator.PROVIDER_ID`), display "Signed JWT - Federated", help "Validates client based on signed JWT issued and signed by an external identity provider". Per-client attributes:
  - `jwt.credential.issuer` - alias of the identity provider ("Identity provider")
  - `jwt.credential.sub` - "Federated subject", the external client id = `sub` of the assertion (for SPIFFE the SPIFFE ID, e.g. `spiffe://example.org/myclient`)
- Assertion type: `SpiffeConstants.CLIENT_ASSERTION_TYPE = "urn:ietf:params:oauth:client-assertion-type:jwt-spiffe"` (from draft-schwenkschuster-oauth-spiffe-client-auth). For other IdPs the standard `...:jwt-bearer` is used.
- Rules (from #42634): JWS signed by IdP keys; `iss` must match the IdP, unless `sub` is a URI like `spiffe://trust-domain/workload-id` and `iss` is missing (scheme + authority used as `iss`); `aud` single value = realm issuer URL; `exp` required; `jti` required unless the IdP allows re-use (SPIFFE JWT-SVIDs can be re-used). SPIFFE docs: "Each client must have a unique subject identifier (SPIFFE ID) for each realm." For SPIFFE the audience can not be customised ("left out SPIFFE as it requires the realm issuer URI").
- Since 26.5 the Keycloak client id does not need to equal the `sub` (the "Federated subject" field is used); `client_id` param can be left out (comment by ahus1, 2026-01-20). PR #48026 (merged 2026-05-26) made the `client_id` parameter validation for federated assertions configurable.
- Docs: Server Admin guide `_identity_broker_spiffe` ("SPIFFE identity providers", tech preview) and "Signed JWT issued by an Identity Provider" in confidential client credentials.

Example token request (shape, from comments; for SPIFFE use the jwt-spiffe type):

```
POST /realms/<realm>/protocol/openid-connect/token
grant_type=client_credentials
client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-spiffe
client_assertion=<JWT-SVID with aud = https://<kc>/realms/<realm>>
```

### Linked / related PRs (all keycloak/keycloak)

| PR | Title | Merged |
|---|---|---|
| #42038 | Draft experimental SPIFFE authenticator (milestone 1 approach) | not merged (dropped, "milestone 1 is a dead-end") |
| #42229 | Experimental federated client authentication | 2025-09-02 |
| #42314 | Experimental SPIFFE identity provider | 2025-09-04 |
| #42472 | Refactor JWTValidator for self-signed and federated client assertions | 2025-09-10 |
| #42581 | Client Authenticator configurable per client | 2025-09-16 |
| #42732 | Documentation for federated client authentication | 2025-09-19 |
| #42753 | Promote CLIENT_AUTH_FEDERATED and SPIFFE features to preview (26.4.0) | 2025-09-19 |
| #43242 | Add support for spiffe_refresh_hint to Spiffe Identity Provider | 2025-10-07 |
| #43428 / #43441 | Fix SPIFFE client authentication when iss claim is included (+ backport) | 2025-10-14 |
| #43651 / #43656 | SPIFFE should support OIDC JWK endpoint (+ backport) | 2025-10-22 / 2025-10-23 |
| #46629 | Max allowed expiration of federated client assertion in IdP settings | 2026-02-27 |
| #46670 / #46810 | SPIFFE client assertion NPE if no client found (+ 26.5 backport) | 2026-03-03 / 2026-03-06 |
| #47184 | Promote federated client authentication, including OIDC and Kube to fully supported (26.6.0) | 2026-03-17 |
| #48026 | Configurable `client_id` parameter validation for federated client assertions | 2026-05-26 |
| #54746 | feat: support SPIFFE federation bundle maps | open |

Key files of the merged implementation:

- PR #42229: `services/.../authentication/authenticators/client/FederatedJWTClientAuthenticator.java` (+209), `server-spi-private/.../broker/provider/ClientAssertionContext.java`, `ClientAssertionIdentityProvider.java`, `OIDCIdentityProvider.java` / `OIDCIdentityProviderConfig.java` (client assertion support), `Profile.java`, admin UI `AdvancedSettings.tsx`, `DefaultAuthenticationFlows.java`.
- PR #42314: new package `services/src/main/java/org/keycloak/broker/spiffe/` with `SpiffeIdentityProvider.java` (+190), `SpiffeIdentityProviderConfig.java`, `SpiffeIdentityProviderFactory.java`, `SpiffeBundleEndpointLoader.java`, `SpiffeConstants.java`; JWK/KeyUse changes in `core` for SPIFFE bundle keys (`use: jwt-svid`).
- PR #47184 `Profile.java` diff:

```diff
-        CLIENT_AUTH_FEDERATED("Authenticates client based on assertions issued by identity provider", Type.PREVIEW),
+        CLIENT_AUTH_FEDERATED("Authenticates client based on assertions issued by identity provider", Type.DEFAULT),
 
         SPIFFE("SPIFFE trust relationship provider", Type.PREVIEW),
 
-        KUBERNETES_SERVICE_ACCOUNTS("Kubernetes service accounts trust relationship provider", Type.PREVIEW),
+        KUBERNETES_SERVICE_ACCOUNTS("Kubernetes service accounts trust relationship provider", Type.DEFAULT),
```

Release notes 26.6.0 (added by #47184):

> Federated client authentication is now promoted to supported, including support for client assertions issued by external OpenID Connect identity providers and Kubernetes Service Accounts.
> Since the OAuth SPIFFE Client Authentication specification is still in a draft status this feature remains a preview feature in Keycloak.

Release notes 26.4.0 (added by #42753):

> Identity providers are now able to federate client authentication. This allows clients to authenticate with SPIFFE JWT SVIDs, Kubernetes service accounts, or tokens issued by a OpenID Connect identity provider. This feature is currently preview, and expected to become supported in 26.5.

### Design references

- IETF draft: https://datatracker.ietf.org/doc/draft-schwenkschuster-oauth-spiffe-client-auth/ (defines `jwt-spiffe` assertion type)
- POC/demo by stianst: https://github.com/stianst/playground/tree/main/demos/spiffe and branch https://github.com/stianst/keycloak/tree/spiffe-jwt-svids-with-idp
- Community extensions mentioned: https://github.com/CarrettiPro/keycloak-spiffe, https://github.com/christian-posta/keycloak-agent-identity, blog https://blog.christianposta.com/authenticating-mcp-oauth-clients-with-spiffe/
- Related: #37600 (Kubernetes service accounts), #38146 (Federated identity auth for Entra/AWS), spiffe/spiffe#349 (add `jti` to JWT-SVIDs)

---

## Issue body (original)

### Description

`SPIFFE and SPIRE provide strongly attested, cryptographic identities to workloads across a wide variety of platforms`

Workloads can leverage either X.509 SVID or JWT SVID when authenticating. In Keycloak clients can authenticate via mTLS, but using mTLS is a more complicated setup for SPIFFE/SPIRE and a simpler integration would be via JWT SVID.

Supporting SPIFFE/SPIRE can be broken down into the following milestones:

#### Milestone 1 - Support configuring a client to authenticate via JWT SVID

Ability to leverage SPIFFE JWT IDs to authenticate one or more clients within Keycloak.

Keycloak already supports [JSON Web Token (JWT) Profile for OAuth 2.0 Client Authentication and Authorization Grants](https://datatracker.ietf.org/doc/html/rfc7523) that provides the basic capabilities required for this. However, there are a few issues that prevents this from working currently:

* Keycloak requires the `jti` claim, which is not issued by SPIFFE/SPIRE. This [claim is optional](https://datatracker.ietf.org/doc/html/rfc7523#section-3) in JSON Web Token (JWT) Profile for OAuth 2.0 Client Authentication and Authorization Grants
* Keycloak requires the token issuer to be identical to the client id. For JWT SVID the issuer will be SPIFFE/SPIRE and not the client
* Keycloak requires the subject to be the client id. A workaround would be to use something like `spiffe://example.org/myclient` for the client id, but we may want some form of mapping between the clients SPIFFE ID and the ID within Keycloak

#### Milestone 2 - Introduce a central trusted token issuer

In milestone 1 each individual client will need to be configured with the SPIFFE/SPIRE as the token issuer, and the relevant keys.

With a central trusted token issuer concept (think identity providers) the SPIFFE/SPIRE server can be configured once within a realm and a client can be linked to the token issuer instead of duplicating.

We can extend on the concept of identity providers for this purpose, and introduce identity providers that are not used for delegated authentication of users only, but also for delegated authentication of clients.

This can in the future also help with things like allowing mapping of the tokens issued by SPIFFE/SPIRE through protocol mappers.

#### Milestone 3 - Support dynamic client registration with SPIFFE/SPIRE

In the previous milestones the client has to be created first, but once we have the concept of a trust relationship with SPIFFE/SPIRE we can also allow clients to dynamically register themselves using their JWT SVID.

---

## Comments (on #41907)

**stianst - 2025-08-15**
[Authenticating MCP OAuth Clients With SPIFFE and SPIRE](https://blog.christianposta.com/authenticating-mcp-oauth-clients-with-spiffe/) touches on the issued identified for milestone 1 and works around this by introducing a custom client authenticator. There's quite a few folks around that have done similar things.
We could introduce a different authenticator, but honestly I think it would be better to have the `jti` claim optional (perhaps with a configuration option to enforce it for a given client) and have the ability to configure a different `issuer` value than the client id directly.

**stianst - 2025-08-15**
This is related to https://github.com/keycloak/keycloak/issues/37600, which is a very similar use-case, but for Kubernetes service accounts.

**arndt-s - 2025-08-15**
Thank you for this initiative! I want to point everyones attention to https://datatracker.ietf.org/doc/draft-schwenkschuster-oauth-spiffe-client-auth/. An IETF draft document in the OAuth working group that standardizes OAuth 2.0 Client Authentication with SPIFFE. It's work in progress and an implementation in Keycloak would help us get early feedback for it!

**stianst - 2025-08-15**
Links: https://github.com/CarrettiPro/keycloak-spiffe and https://github.com/christian-posta/keycloak-agent-identity

**stianst - 2025-08-15**
For milestone 3 not sure if we want to support automatic client registration like we do for users, or just allow clients to self-register themselves. Automatic client registration is a bit more tricky as we are not likely to get proper config. Another thing to think about is automatic registration of service accounts, what access if any should they get automatically, etc.

**arndt-s - 2025-08-15**
+1 this is exactly the reason why the standards are split into different documents. We've foreseen that dynamic client registration or trust on first use will be much more difficult to implement. Thus, the client registration is in a dedicated draft to not "gate" it behind other, more innovative, ideas. It is also useful for a lot of other deployments which are totally ok with manual registration.

**stianst - 2025-08-15**
One of the first things to figure out is if we want to extend the `Signed Jwt` authenticator to support JWT SVIDs, or introduce a new authenticator.
In the end I think it's best to introduce a new authenticator. Main reasons for this is lack of `iss` in the JWT-SVID specification (even though it can be configured at least in SPIRE) and we would also have an alternative mechanism for looking up the client. Essentially we can split `spiffe://example.org/myclient` into `example.org` and `myclient`.
A SPIFFE authenticator can also support the `urn:ietf:params:oauth:client-assertion-type:jwt-spiffe` assertion type from https://datatracker.ietf.org/doc/draft-schwenkschuster-oauth-spiffe-client-auth/

**slaskawi - 2025-08-18**
In https://github.com/keycloak/keycloak/pull/39210, I'm experimenting with adding Kubernetes-specific JWT URLs to the Signed JWT Authenticator and I noticed the implementation is spread all over the place. The configuration is also divided into two tabs (Keys and the Authenticator), which makes it a bit harder to tackle from the code. Personally, I would lean towards a new Authenticator that provides everything in a generic screen and do not require a specific UI implementation in the Admin Panel. If we decided to implement it this way, I could probably retrofit the Kubernetes Signed JWT to build a foundation for it.

**VinodAnandan - 2025-08-20**
Suggests Milestone 1 relates to OAuth 2.0 Attestation-Based Client Authentication (https://datatracker.ietf.org/doc/draft-ietf-oauth-attestation-based-client-auth/), and raises the risk of a stolen client attestation JWT; the spec addresses this with a Client Attestation Proof of Possession (PoP) JWT. References discussion #40413 and a PoC by thomasdarimont (https://github.com/thomasdarimont/keycloak/tree/poc/client-attestation).

**stianst - 2025-08-21**
JWT SVIDs are delivered securely from the SPIFFE provider to the workload with a single audience targeting Keycloak; and again over TLS from the workload to Keycloak. I don't really see how `oauth-attestation-based-client-auth` is relevant to this use-case.

**stianst - 2025-08-21**
If anyone wants to take a look at I've sent a draft PR for an experimental SPIFFE authenticator: https://github.com/keycloak/keycloak/pull/42038
To try it out with SPIRE I've added https://github.com/stianst/playground/tree/main/demos/spiffe. There's scripts to install and setup SPIRE as well as steps to configure Keycloak.

**VinodAnandan - 2025-08-22**
TLS on its own does not address all the threats associated with JWTs (e.g. replay). Asks what alternative mechanisms protect against compromised externally attested JWTs if JTI and proof of possession are not required. Argues SVID JWT, Kubernetes SA JWT, and Client Attestation JWT are all forms of external attestation.

**stianst - 2025-08-27**
I think I've reached the conclusion that milestone 1 is a dead-end; and we should move straight to milestone 2. The challenge is keys. The keys used for the JWT is a third-party and should not be the keys associated with the client itself. We could introduce a way to configure that separately for the authenticator, but digging into the code it would require a lot of changes to now use the clients own keys.
It'll most likely be simpler to just go straight for milestone 2, and have an identity provider verify the token in the first place.

**stianst - 2025-08-28**
Played around with milestone 2 and it's a lot nicer and simpler approach. POC here: https://github.com/stianst/keycloak/tree/spiffe-jwt-svids-with-idp
The demo has been updated to use this approach instead: https://github.com/stianst/playground/tree/main/demos/spiffe

**stianst - 2025-09-16**
Initially the aim was to focus on SPIFFE JWT SVIDs, but this extended into support also external client assertions issued by other identity providers (OIDC, Kubernetes Service Accounts, etc.). I'm closing this issue in favour of #42634.

## Timeline (cross-references on #41907)

- 2025-08-15 referenced from spiffe/spiffe#349 "Add `jti` claim to JWT-SVIDs" (closed)
- 2025-08-27 referenced from keycloak#38146 "Support Federated Identity Authentication for Clients like Microsoft Entra and AWS" (open)
- 2025-09-16 closed as duplicate of #42634

---

## Successor epic #42634 "Federated client authentication" (relevant extract)

State: closed/completed 2026-03-17. Labels: `kind/feature`, `team/core-clients`, `release/26.6.0`. Milestone: 26.6.0.

Goals: support client assertions (RFC 7521) issued by 3rd party providers for OIDC clients; support SPIFFE JWT SVIDs (draft-schwenkschuster-oauth-spiffe-client-auth); support Kubernetes Service Accounts. Non-goals: X.509 auth (SPIFFE X.509 SVIDs etc.); auto/dynamic registration of clients (later follow-up).

Notes from the body: "Instead of adding a different concept of 3rd party trust in a realm this should be based on identity providers." Requirements for client assertions: JWS signed with IdP keys; `iss` must match IdP issuer (required unless `sub` is a URI including the issuer); `sub` must match the external subject configured for the client, and for a URI like `spiffe://trust-domain/workload-id` with no `iss`, scheme + authority is used as `iss`; `aud` single value equal to realm issuer URL; `exp` required; `nbf` optional; `iat` optional, max 300s in past; `jti` required and unique unless re-use permitted by IdP.

Relevant comments (abridged):

- **chr-fritz - 2025-11-02**: tried preview in 26.4.1 with Kubernetes SA tokens, could not get it to work; noted the `iat` 300s limit is too restrictive for K8s projected tokens (min 600s).
- **stianst - 2025-11-04/05**: needed flags `SUPPORTS_CLIENT_ASSERTIONS`, `SUPPORTS_CLIENT_ASSERTION_REUSE`, `VALIDATE_SIGNATURE`; fixed by PR #43967.
- **J0F3 / thomasdarimont (Nov 2025 - Feb 2026)**: Entra ID / GCP need a custom `aud`. stianst: "The token really should have Keycloak as its sole audience". Result: OIDC IdP option "Allows Client ID as audience for assertions", and #45178 for cases where the issuer URL can not be the audience.
- **ahus1 - 2026-01-20**: "in 26.5 ... passing in the client_id is no longer necessary, and the client ID doesn't need to match the subject any more, although you can still only have one client per Kubernetes service account" - uses "Federated Subject" field.
- **thomasdarimont - 2026-02-26**: two PRs: max client assertion expiration for IdPs (OIDC, SPIFFE, Kubernetes) #46629; expected client assertion audience for OIDC/Kubernetes - "left out SPIFFE as it requires the realm issuer URI".

Cross-references on #42634: #46662 (expected assertion audience, closed not merged), **#46977 Supported SPIFFE client authentication (open)**, **#47184 promote to supported (merged 2026-03-17)**, #49833 Client authentication with SPIFFE X509 SVID (open), rossoctl/cortex#82 "Use SPIRE JWT to authenticate with Keycloak (use Federated Client Auth)".

### #46977 "Supported SPIFFE client authentication" (open)

> Preview support for SPIFFE client authentication was introduced in #42634. However, since the specification is still in draft SPIFFE authentication didn't graduate to supported.
> Goals: Review specification and reflect any required changes; Make SPIFFE client authentication fully supported

stianst (2026-03-09): "Provisionally set to 26.7, we aim to make this supported as soon as possible when the specification is finalised." Current milestone: "27.0 Development Milestone".
