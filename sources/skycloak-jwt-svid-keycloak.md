> Source: https://skycloak.io/blog/workload-identity-federation-spiffe-jwt-svid-keycloak/
> Retrieved: 2026-11-20
> Author: Guilliano Molaire (Skycloak), published 2026-09-20, updated 2026-10-16
> Notes: Converted from the page HTML. Marketing CTA blocks, author bio, tags and related links removed. Technical text kept verbatim.

# Workload Identity Federation to Keycloak: SPIFFE JWT-SVID as Client Auth

Workload Identity Federation to Keycloak: SPIFFE JWT-SVID as Client Auth. An IETF draft lets workloads authenticate to an OAuth server with SPIFFE JWT-SVIDs, not client secrets. What it specifies and what Keycloak 26.x supports now.

*Last updated: September 2026*

**Workload identity federation means a service proves who it is with a short-lived credential its platform issued, rather than with a secret someone pasted into a config file. The OAuth working group has a draft that applies this to OAuth client authentication directly: a workload presents a SPIFFE JWT-SVID to the token endpoint instead of a `client_secret`. It is an Internet-Draft, not a shipped Keycloak feature, but one of its authors is a Keycloak co-founder, and the patterns it formalises are ones you can approximate on Keycloak 26.x today.**

If you arrived here from the cloud vendors’ version of this phrase, a quick orientation. Google Cloud and Microsoft Entra both use “workload identity federation” for a specific trade: your workload presents a token its own platform issued, and the cloud IAM service exchanges it for cloud credentials. AWS does the same thing under different names, through `AssumeRoleWithWebIdentity` and IAM Roles Anywhere. The SPIFFE work generalises that, with your own authorization server on the receiving end.

## What does the OAuth SPIFFE client authentication draft specify?

The draft, “OAuth SPIFFE Client Authentication,” defines how SPIFFE Verifiable Identity Documents serve as OAuth client credentials, removing the need for a registered client secret. Its authors are Arndt Schwenkschuster, Pieter Kasselman, Scott Rose, Stian Thorgersen and Nancy Cam-Winget, and the work is carried in the [oauth-wg/oauth-spiffe-client-authentication repository](https://github.com/oauth-wg/oauth-spiffe-client-authentication) on GitHub. Stian Thorgersen co-founded Keycloak and is its project lead, which is a reasonable signal about where this ends up.

Three credential shapes are covered:

| Credential | Mechanism | How it is presented |
|----|----|----|
| JWT-SVID | Client assertion | `urn:ietf:params:oauth:client-assertion-type:jwt-spiffe` |
| X.509-SVID | Mutual TLS, per RFC 8705 | Client certificate on the TLS connection |
| WIT-SVID | Attestation-based client auth | Per the attestation-based client auth draft |

For the JWT-SVID case, the assertion carries the SPIFFE ID in `sub`, for example `spiffe://example.org/my-oauth-client`, an `exp`, and an `aud` claim that the draft requires to contain only the authorization server’s issuer identifier as its sole value. That last constraint is audience binding: an SVID minted for one authorization server cannot be presented to another. It does not address replay against the same server within the token lifetime, which is what the short `exp` is for.

## How is this different from private_key_jwt?

Both send a signed JWT to the token endpoint, and that similarity hides the part that matters. With `private_key_jwt` under RFC 7523, you register a key per client, and the assertion’s `iss` and `sub` are the `client_id`. Trust flows from a key you enrolled by hand.

With a SPIFFE SVID, trust flows from the trust domain. The authorization server verifies the signature using keys retrieved from the SPIFFE Bundle Endpoint, not from a per-client JWKS you pasted in, and the identity in `sub` is a SPIFFE ID issued by an attestation process that checked what the workload actually is.

The `client_id` is still required, and the draft allows it to be the SPIFFE ID itself or a URL pointing to a Client ID Metadata Document. The binding requirement is explicit. The draft tells the authorization server to “Verify that the SPIFFE ID in the `sub` claim matches, or is associated with, the client identified by the `client_id` parameter of the request.” A valid SVID is not by itself permission to act as an arbitrary client.

Operationally, this is what removes the secret rotation problem rather than relocating it. SVIDs are short-lived and reissued automatically by the workload API. There is no long-lived material to rotate, expire or leak into a build log.

## What does the authorization server have to validate?

The draft lists five checks, and the order matters less than doing all of them.

1.  The JWT is well-formed and carries the required claims.
2.  `exp` has not passed.
3.  `aud` contains the authorization server’s issuer identifier, and only that.
4.  The signature verifies against trust domain keys retrieved from the SPIFFE Bundle Endpoint.
5.  The SPIFFE ID in `sub` matches, or is associated with, the presented `client_id`.

For X.509-SVIDs the equivalent is standard path validation against SPIFFE trust anchors, plus certificate constraints: exactly one URI SAN containing a valid SPIFFE ID, the `digitalSignature` key usage bit set, and Basic Constraints with CA set to FALSE.

Two security considerations from the draft are worth quoting to anyone about to implement this. On trust anchors: “Using the system trust store as trust anchor would allow ANY certificate authority in it to issue a trusted X509-SVID for ANY SPIFFE ID.” And on token confusion: “A token MUST NOT be accepted as a JWT-SVID or WIT-SVID solely because it is a JWT, its signature validates under keys discovered from iss, and its `sub` resembles a SPIFFE ID.”

The first is the failure mode we would expect to see most often, because reaching for the system trust store is the default in most TLS libraries, and doing so widens the set of issuers that can mint a trusted SPIFFE ID to every CA in that store.

## What can you actually run on Keycloak 26.x today?

No released Keycloak implements the draft as of 26.7.4, so the honest answer is that you build the same properties out of mechanisms Keycloak already supports, and keep the migration path in view.

**Signed JWT client authentication.** Keycloak supports client assertions under RFC 7523, where a confidential client authenticates with a JWT signed by its own key instead of a shared secret. In the admin console this is **Clients \> your client \> Credentials \> Client Authenticator**, set to *Signed JWT*. The request then carries the assertion rather than a secret:

```
curl -X POST \
  -d "grant_type=client_credentials" \
  -d "client_id=my-workload" \
  -d "client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer" \
  -d "client_assertion=$SIGNED_JWT" \
  "https://auth.example.com/realms/myrealm/protocol/openid-connect/token"
```

This is the closest production-ready analogue, and it gets you off `client_secret` today. The gap versus SPIFFE is that you enroll and manage the key per client rather than deriving trust from a workload attestation, and the assertion type is `jwt-bearer` rather than the draft’s `jwt-spiffe`.

**Mutual TLS client authentication.** Keycloak supports mTLS client authentication per RFC 8705, selected as the *X509 Certificate* client authenticator, with certificate-bound access tokens available as a separate advanced setting. If SPIRE already issues X.509-SVIDs to your workloads, you can terminate that trust at Keycloak by configuring the appropriate trust anchors, which is architecturally close to the X.509-SVID path in the draft. Getting the trust store right is the whole job here, per the warning above.

**Short lifetimes and no offline tokens for machine clients.** Whatever the client authentication method, service accounts should get short access token lifespans and no offline access. That is the piece of the SPIFFE posture that is purely configuration, and most realms have it wrong by default. We cover the baseline setup in [the Keycloak machine-to-machine authentication guide](/blog/keycloak-machine-to-machine-authentication/), and the wider set of habits in [API authentication best practices](/blog/api-authentication-best-practices/).

The node-level trust assumption underneath all of this deserves its own read. An SVID is only as good as the attestation that produced it, and a compromised node undermines everything downstream, which we went through in [the SPIFFE and SPIRE node compromise post](/blog/spiffe-spire-node-compromise-workload-identity/).

## How does this compare to cloud workload identity federation?

The cloud implementations solve a narrower problem: getting into that cloud’s IAM. Google Cloud, Entra and AWS each accept an external OIDC or SAML assertion and exchange it for their own credentials, which is why the phrase reads as a cloud-specific term to most engineers.

The SPIFFE approach points the other way. Your workloads get a platform-issued identity that is not tied to any one cloud, and your authorization server decides what to do with it. For teams running across more than one cloud, or across cloud and on-premises, that means one identity fabric to reason about instead of three separate federations that have to be kept in agreement.

Keycloak sits in this picture as the authorization server that issues application tokens once the workload has proved what it is. Token issuance and federation policy then live in one place you can audit, rather than in three separate cloud consoles. The delegation patterns that follow, where a workload acts for a user or another service, are the subject of [our cross-app access and ID-JAG post](/blog/cross-app-access-id-jag-ai-agents-keycloak/).

## Frequently asked questions

### What is a JWT-SVID?

A JWT-SVID is a SPIFFE Verifiable Identity Document in JWT form. It carries the workload’s SPIFFE ID in the `sub` claim, an audience, and a short expiry, and it is signed by the trust domain’s keys. Workloads fetch them from the SPIFFE Workload API rather than holding long-lived secrets.

### Does Keycloak support SPIFFE client authentication?

Not as specified in the draft. Keycloak 26.x supports signed JWT client assertions under RFC 7523 and mutual TLS client authentication under RFC 8705, which cover much of the same ground. The SPIFFE-specific assertion type is an Internet-Draft, and drafts change before they become RFCs.

### Can I use a JWT-SVID as a bearer token to my APIs?

You should not. In the client authentication draft the SVID authenticates the client to the authorization server, which then issues an access token for the API. Reusing the SVID as a bearer credential at every resource server spreads a credential far beyond the audience it was minted for.

### How is this different from an API key?

An API key is a long-lived shared secret that anyone holding it can replay indefinitely. An SVID is short-lived, issued after the platform attests what the workload is, scoped by its audience claim to one authorization server, and replaced automatically. We compare the broader options in [API key versus OAuth](/blog/api-key-vs-oauth-when-to-use/).

### Is workload identity federation only for Kubernetes?

No. SPIFFE and SPIRE are most commonly deployed in Kubernetes because attestation is straightforward there, but SPIRE supports node and workload attestors for virtual machines and bare metal as well. The OAuth draft does not assume any particular runtime.

## Sources

- Schwenkschuster, A., Kasselman, P., Rose, S., Thorgersen, S., Cam-Winget, N., “OAuth SPIFFE Client Authentication”, IETF OAuth Working Group Internet-Draft, 2026, retrieved 2026-09-20, <https://datatracker.ietf.org/doc/draft-ietf-oauth-spiffe-client-auth/>
- OAuth Working Group, “oauth-spiffe-client-authentication” draft repository, retrieved 2026-09-20, <https://github.com/oauth-wg/oauth-spiffe-client-authentication>
- Internet Engineering Task Force, RFC 7523, “JSON Web Token (JWT) Profile for OAuth 2.0 Client Authentication and Authorization Grants”, 2015, retrieved 2026-09-20, <https://datatracker.ietf.org/doc/html/rfc7523>
- Internet Engineering Task Force, RFC 8705, “OAuth 2.0 Mutual-TLS Client Authentication and Certificate-Bound Access Tokens”, 2020, retrieved 2026-09-20, <https://datatracker.ietf.org/doc/html/rfc8705>
- SPIFFE, “JWT-SVID” specification, retrieved 2026-09-20, <https://github.com/spiffe/spiffe/blob/main/standards/JWT-SVID.md>
- SPIFFE, “X509-SVID” specification, retrieved 2026-09-20, <https://github.com/spiffe/spiffe/blob/main/standards/X509-SVID.md>
- Keycloak, “Server Administration Guide”, client credentials, <https://www.keycloak.org/docs/latest/server_admin/index.html#_client-credentials>

