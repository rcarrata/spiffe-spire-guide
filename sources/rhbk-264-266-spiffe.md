> Source: https://docs.redhat.com/en/documentation/red_hat_build_of_keycloak/26.4/html/release_notes/newfeatures (Ch. 18) and https://docs.redhat.com/en/documentation/red_hat_build_of_keycloak/26.4/html/release_notes/techpreview (Ch. 19)
> Retrieved: 2026-11-23 (via Red Hat docs search/fetch, read-only)
> Notes: Only the SPIFFE / federated client authentication statements are kept. RHBK 26.6 release notes checked too: https://docs.redhat.com/en/documentation/red_hat_build_of_keycloak/26.6/html/release_notes/newfeatures and .../techpreview

# Red Hat build of Keycloak release notes: SPIFFE / federated client authentication

## RHBK 26.4 (release notes apply to 26.4.17)

Ch. 18, New features and enhancements, highlights list:

> Federated Client Authentication to use SPIFFE or Kubernetes service account tokens for client authentication.

Ch. 19, Technology preview features:

> 19.1. Federated client authentication and SPIFFE trust relationship provider
>
> Identity providers are now able to federate client authentication. This allows clients to authenticate with SPIFFE JWT SVIDs, Kubernetes service accounts, or tokens issued by a OpenID Connect identity provider.

So the upstream 26.4.0 preview code (`spiffe` IdP + `federated-jwt` authenticator, PRs #42229/#42314/#42753) is in the Red Hat build, and Red Hat declares it Technology Preview. As with upstream, it needs the preview features enabled at server start; the docs do not spell out the flags, but upstream 26.4 requires both `spiffe` and `client-auth-federated`.

## RHBK 26.6

Ch. 9, New features and enhancements:

> Federated client authentication, eliminating the need to manage individual client secrets in Red Hat build of Keycloak

> 9.1.2. Federated client authentication … This feature includes support for client assertions issued by external OpenID Connect identity providers and Kubernetes Service Accounts.

The supported list names OIDC IdPs and Kubernetes service accounts only - **SPIFFE is not named**, matching upstream 26.6.0 where `SPIFFE` stays `Type.PREVIEW` because the IETF OAuth SPIFFE client auth draft is not final. The RHBK 26.6 technology preview chapter does not mention SPIFFE either.

Ch. 9.3.3 confirms the single-option flag reaches the Red Hat build in 26.6:

> You can now enable or disable individual features using the feature- option such as feature-spiffe=enabled.

## What this confirms for us

- RHBK 26.4.18 (our version) ships the SPIFFE JWT-SVID client auth code, as Technology Preview. No guess from upstream mapping needed any more: it is in the Red Hat release notes.
- An RHBK 26.6 stream exists and makes federated client authentication supported *for OIDC IdPs and Kubernetes service accounts*, but SPIFFE JWT-SVIDs stay preview there too. So "ask RHDP for an RHBK 26.6+ stream" (option 1 in module 05) does not by itself make SPIFFE supported - it only buys the `--feature-spiffe=enabled` single flag and the newer `trustDomain` IdP shape.
- X.509-SVID client auth is absent from all RHBK release notes checked (upstream #49833 still open).
