#!/usr/bin/env python3
"""Generate the .excalidraw diagrams for the SPIFFE/SPIRE learning pack.

Usage: python3 -I scripts/gen_excalidraw.py <out_dir>
"""
import json
import random
import sys
from pathlib import Path

# palette (Excalidraw-ish)
C = {
    "spire": ("#1971c2", "#d0ebff"),   # blue - SPIRE / identity plane
    "k8s": ("#495057", "#f1f3f5"),     # grey - OpenShift / k8s
    "kc": ("#9c36b5", "#f3d9fa"),      # purple - Keycloak
    "os": ("#2f9e44", "#d3f9d8"),      # green - OpenShell
    "gw": ("#e8590c", "#ffe8cc"),      # orange - MCP Gateway / Authorino
    "bad": ("#c92a2a", "#ffe3e3"),     # red - blocked / today
    "note": ("#5c5f66", "#fff9db"),    # yellow sticky
    "plain": ("#1e1e1e", "transparent"),
}


class Doc:
    def __init__(self):
        self.els = []
        self.rng = random.Random(42)

    def _base(self, kind, x, y, w, h, stroke, bg, **kw):
        e = {
            "id": f"{kind[:2]}{len(self.els)}", "type": kind, "x": x, "y": y,
            "width": w, "height": h, "angle": 0, "strokeColor": stroke,
            "backgroundColor": bg, "fillStyle": "solid", "strokeWidth": 2,
            "strokeStyle": "solid", "roughness": 1, "opacity": 100,
            "groupIds": [], "frameId": None, "roundness": None,
            "seed": self.rng.randint(1, 2**31), "version": 1,
            "versionNonce": self.rng.randint(1, 2**31), "isDeleted": False,
            "boundElements": [], "updated": 1, "link": None, "locked": False,
        }
        e.update(kw)
        self.els.append(e)
        return e

    def text(self, x, y, s, size=16, color="#1e1e1e", align="left", w=None):
        lines = s.split("\n")
        width = w or max(len(l) for l in lines) * size * 0.55
        h = len(lines) * size * 1.25
        return self._base("text", x, y, width, h, color, "transparent",
                          text=s, originalText=s, fontSize=size, fontFamily=1,
                          textAlign=align, verticalAlign="top", containerId=None,
                          lineHeight=1.25, baseline=size)

    def box(self, x, y, w, h, label, kind="plain", size=16, shape="rectangle",
            dashed=False, sub=None):
        stroke, bg = C[kind]
        r = self._base(shape, x, y, w, h, stroke, bg,
                       roundness={"type": 3} if shape == "rectangle" else {"type": 2},
                       strokeStyle="dashed" if dashed else "solid")
        lines = label.split("\n")
        th = len(lines) * size * 1.25
        sub_h = 0
        if sub:
            sub_h = len(sub.split("\n")) * 13 * 1.25 + 4
        ty = y + (h - th - sub_h) / 2
        self.text(x + 6, ty, label, size, stroke if kind != "note" else "#1e1e1e",
                  "center", w - 12)
        if sub:
            self.text(x + 6, ty + th + 4, sub, 13, "#5c5f66", "center", w - 12)
        return r

    def frame(self, x, y, w, h, title, kind="k8s"):
        stroke, bg = C[kind]
        self._base("rectangle", x, y, w, h, stroke, "transparent",
                   strokeStyle="dashed", roundness={"type": 3}, strokeWidth=1)
        self.text(x + 12, y + 8, title, 18, stroke)

    def arrow(self, x1, y1, x2, y2, label=None, color="#1e1e1e", dashed=False,
              both=False, lx=None, ly=None, size=14):
        self._base("arrow", x1, y1, abs(x2 - x1), abs(y2 - y1), color, "transparent",
                   points=[[0, 0], [x2 - x1, y2 - y1]], lastCommittedPoint=None,
                   startBinding=None, endBinding=None,
                   startArrowhead="arrow" if both else None, endArrowhead="arrow",
                   strokeStyle="dashed" if dashed else "solid",
                   roundness={"type": 2})
        if label:
            tx = lx if lx is not None else (x1 + x2) / 2 + 6
            ty = ly if ly is not None else (y1 + y2) / 2 - 10
            self.text(tx, ty, label, size, color)

    def save(self, path):
        data = {"type": "excalidraw", "version": 2,
                "source": "https://excalidraw.com", "elements": self.els,
                "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None},
                "files": {}}
        Path(path).write_text(json.dumps(data, indent=1))


def a_big_picture():
    d = Doc()
    d.text(40, 10, "SPIRE big picture: one passport office, a consulate per node", 26)
    d.frame(20, 60, 1180, 620, "Trust domain: spiffe://apps.cluster.example.com", "spire")
    d.box(470, 110, 280, 110, "SPIRE Server", "spire", 22,
          sub="CA + signing keys\nregistration entries")
    d.box(820, 110, 330, 110, "Controller Manager", "spire", 18,
          sub="watches ClusterSPIFFEID + pods\n-> creates entries")
    d.arrow(820, 165, 752, 165, both=True, color=C["spire"][0])
    d.box(60, 110, 330, 110, "OIDC Discovery Provider", "spire", 18,
          sub="/.well-known/openid-configuration\n/keys (JWKS)")
    d.arrow(470, 165, 392, 165, "public keys", C["spire"][0], lx=400, ly=135)
    for i, nx in enumerate([60, 450, 840]):
        d.frame(nx, 290, 320, 370, f"Node {i+1}", "k8s")
        d.box(nx + 40, 340, 240, 80, "SPIRE Agent", "spire", 20, sub="DaemonSet pod")
        d.arrow(nx + 160, 340, 610, 222, "node attestation\n(k8s PSAT)" if i == 0 else None,
                C["spire"][0], dashed=True, lx=nx + 170, ly=250)
        d.box(nx + 40, 445, 240, 40, "Workload API socket (CSI)", "k8s", 14)
        d.arrow(nx + 160, 445, nx + 160, 422, color=C["k8s"][0])
        d.box(nx + 20, 530, 130, 100, "pod A", "os", 16, sub="sa: hermes")
        d.box(nx + 170, 530, 130, 100, "pod B", "k8s", 16, sub="sa: other")
        d.arrow(nx + 85, 530, nx + 120, 487, color=C["os"][0])
        d.arrow(nx + 235, 530, nx + 200, 487, color=C["k8s"][0])
    d.box(1220, 300, 260, 230, "Passport analogy\n\nServer = passport office\nAgent = consulate\nSVID = passport\nSPIFFE ID = your name\nBundle = stamps guards trust",
          "note", 15)
    return d


def b_attestation():
    d = Doc()
    d.text(40, 10, "Attestation: the workload sends NOTHING to prove itself", 26)
    cols = [("Workload\n(pod)", "os", 80), ("SPIRE Agent\n(node)", "spire", 380),
            ("kubelet /\nkernel", "k8s", 680), ("SPIRE Server", "spire", 980),
            ("K8s API\nTokenReview", "k8s", 1280)]
    for name, k, x in cols:
        d.box(x, 60, 200, 70, name, k, 18)
        d._base("line", x + 100, 130, 0, 820, "#adb5bd", "transparent",
                points=[[0, 0], [0, 820]], strokeStyle="dashed", strokeWidth=1,
                lastCommittedPoint=None, startBinding=None, endBinding=None,
                startArrowhead=None, endArrowhead=None)
    X = {n.split("\n")[0]: x + 100 for n, _, x in cols}
    W, A, K, S, T = X["Workload"], X["SPIRE Agent"], X["kubelet /"], X["SPIRE Server"], X["K8s API"]
    d.text(60, 150, "NODE ATTESTATION (once per node)", 16, C["spire"][0])
    steps = [
        (A, S, "1. here is my projected SA token (PSAT)", 190),
        (S, T, "2. is this token real?", 240),
        (T, S, "3. yes: node X, sa spire-agent", 290),
        (S, A, "4. agent SVID + trust bundle + my entries", 340),
    ]
    d.text(60, 400, "WORKLOAD ATTESTATION (every request)", 16, C["os"][0])
    steps += [
        (W, A, "5. FetchJWTSVID(aud=keycloak) on the socket", 440),
        (A, K, "6. who is PID 4242? (SO_PEERCRED)", 500),
        (K, A, "7. pod hermes-plain, ns user1-hermes,\n    sa hermes-agent, image ...", 560),
        (A, A, "", 0),
        (A, W, "9. JWT-SVID sub=spiffe://.../ns/user1-hermes/sa/hermes-agent", 720),
    ]
    for a, b, lbl, y in steps:
        if a == b:
            continue
        d.arrow(a, y, b, y, None, "#1e1e1e")
        d.text(min(a, b) + 10, y - 22, lbl, 14)
    d.box(A - 90, 610, 380, 70, "8. match selectors against\nregistration entries (ClusterSPIFFEID)", "spire", 14)
    d.box(60, 800, 600, 110, "Why you can't fake it: the agent asks the KERNEL\nwho is on the socket and the KUBELET what that pod is.\nNothing the container says is trusted.", "note", 16)
    return d


def c_ztwim():
    d = Doc()
    d.text(40, 10, "ZTWIM on OpenShift: CRs you write -> what the operator runs", 26)
    d.frame(20, 60, 380, 640, "You write (all name: cluster)", "plain")
    crs = [("ZeroTrustWorkloadIdentityManager", "trustDomain, clusterName"),
           ("SpireServer", "jwtIssuer, TTLs, datastore"),
           ("SpireAgent", "k8sPSAT, socketPath"),
           ("SpiffeCSIDriver", "csi.spiffe.io"),
           ("SpireOIDCDiscoveryProvider", "jwtIssuer, managedRoute"),
           ("ClusterSPIFFEID", "which pods = which ID"),
           ("ClusterFederatedTrustDomain", "trust other domains")]
    for i, (n, s) in enumerate(crs):
        d.box(40, 100 + i * 82, 340, 66, f"{i+1 if i < 5 else '+'} {n}", "k8s", 15, sub=s)
    d.box(470, 60, 260, 70, "ZTWIM operator", "spire", 20)
    d.arrow(400, 95, 468, 95, "reconciles", C["spire"][0], lx=405, ly=70)
    d.frame(450, 160, 760, 540, "ns: zero-trust-workload-identity-manager", "spire")
    d.box(480, 210, 330, 120, "StatefulSet spire-server", "spire", 17,
          sub="container: spire-server\ncontainer: controller-manager\nPVC (sqlite3)")
    d.box(850, 210, 330, 120, "Deployment\nspire-spiffe-oidc-discovery-provider", "spire", 15,
          sub="+ Route oidc-discovery.<apps>")
    d.box(480, 380, 330, 90, "DaemonSet spire-agent", "spire", 17, sub="1 per node")
    d.box(850, 380, 330, 90, "DaemonSet spire-spiffe-csi-driver", "spire", 15,
          sub="mounts the agent socket")
    d.box(480, 520, 330, 80, "ConfigMap spire-bundle", "spire", 16, sub="trust bundle (CA certs)")
    d.arrow(645, 380, 645, 332, both=True, color=C["spire"][0])
    d.arrow(812, 425, 848, 425, both=True, color=C["spire"][0])
    d.arrow(645, 330, 645, 518, color=C["spire"][0], dashed=True)
    d.box(850, 520, 330, 140, "Must match!\nagent.socketPath = csi.agentSocketPath\ncsi.pluginName = oidc.csiDriverName\nserver.jwtIssuer = oidc.jwtIssuer", "note", 14)
    d.arrow(380, 590, 478, 260, "entries", C["spire"][0], dashed=True, lx=390, ly=430)
    d.box(1260, 200, 260, 140, "Your pod", "os", 18,
          sub="volume: csi.spiffe.io\nSPIFFE_ENDPOINT_SOCKET=\nunix:///run/spire/sockets/\nspire-agent.sock")
    d.arrow(1182, 425, 1300, 342, "socket", C["os"][0], lx=1220, ly=400)
    d.box(1260, 420, 260, 120, "Keycloak / Vault /\nAuthorino / Entra", "kc", 16,
          sub="trust the issuer,\nfetch JWKS")
    d.arrow(1182, 270, 1258, 470, "JWKS", C["kc"][0], lx=1200, ly=330)
    return d


def d_jwt_card():
    d = Doc()
    d.text(40, 10, "Anatomy of a JWT-SVID", 26)
    d.box(40, 70, 1100, 60, "eyJhbGciOiJSUzI1NiIsImtpZCI6Ii4uLiJ9 . eyJzdWIiOiJzcGlmZmU6Ly8uLi4ifQ . c2lnbmF0dXJl",
          "plain", 15)
    d.box(40, 170, 300, 220, "HEADER\n\nalg: RS256\nkid: fKhJk0u...\ntyp: JWT", "gw", 17)
    d.box(380, 170, 460, 220, "PAYLOAD\n\nsub: spiffe://apps.../ns/user1-hermes/sa/hermes-agent\naud: [keycloak realm URL]\nexp: iat + 5m\niat: 1795600000\niss: https://oidc-discovery.apps...", "spire", 15)
    d.box(880, 170, 260, 220, "SIGNATURE\n\nSPIRE Server\nJWT key\n(public half in JWKS)", "kc", 16)
    notes = [(40, "kid -> pick key\nin the JWKS"), (380, "sub = WHO (picked by SPIRE)\naud = FOR WHOM (picked by the caller)\nexp = 5 minutes, then useless"),
             (880, "verify with\n/.well-known -> jwks_uri")]
    for x, t in notes:
        d.box(x, 430, 300 if x != 380 else 460, 100, t, "note", 15)
    d.box(40, 570, 1100, 90, "NOT inside: roles, scopes, username, azp, jti. A JWT-SVID says WHICH SOFTWARE this is,\nnot what it may do. Permissions come from Keycloak / Authorino.", "bad", 16)
    return d


def e_end_to_end():
    d = Doc()
    d.text(40, 10, "OpenShell sandbox -> supervisor -> gateway -> Keycloak -> MCP Gateway (target, OpenShell >= v0.0.113)", 24)
    d.frame(20, 70, 520, 560, "Sandbox pod (OpenShell)", "os")
    d.box(50, 120, 220, 110, "Agent (Hermie)", "os", 18, sub="sees only a\nplaceholder")
    d.box(300, 120, 210, 110, "Supervisor\n+ egress proxy", "os", 16, sub="swaps placeholder\nfor real token")
    d.box(300, 300, 210, 80, "Workload API\nsocket (CSI)", "spire", 15)
    d.arrow(405, 300, 405, 232, "1. FetchJWTSVID", C["spire"][0], lx=410, ly=250)
    d.box(50, 300, 220, 80, "SPIRE Agent\n(node)", "spire", 16)
    d.arrow(272, 340, 298, 340, both=True, color=C["spire"][0])
    d.box(50, 450, 460, 150, "Sandbox never holds: the JWT-SVID,\nthe Keycloak token, any secret.\nIt only sees an opaque placeholder\n(same trick as --provider maas in Module 2).", "note", 15)
    d.box(640, 120, 260, 110, "OpenShell Gateway", "os", 18, sub="SPIFFE broker API\nhas its own SVID")
    d.arrow(512, 175, 638, 175, "2. SVID + grant request", C["os"][0], lx=520, ly=145)
    d.box(1020, 120, 300, 130, "Keycloak (realm)", "kc", 20,
          sub="token endpoint\nRFC 8693 token exchange\nclient auth = jwt-spiffe")
    d.arrow(902, 160, 1018, 160, "3. token-exchange\nclient_assertion=SVID", C["kc"][0], lx=905, ly=110)
    d.arrow(1018, 210, 902, 210, "4. access token\nsub=user azp=sandbox SPIFFE ID", C["kc"][0], lx=905, ly=215)
    d.box(1020, 330, 300, 90, "SPIRE OIDC provider", "spire", 16, sub="JWKS")
    d.arrow(1170, 330, 1170, 252, "verify SVID\nsignature", C["spire"][0], lx=1178, ly=270)
    d.arrow(638, 215, 512, 215, "5. token (to supervisor only)", C["os"][0], lx=515, ly=222)
    d.box(640, 470, 300, 130, "MCP Gateway", "gw", 20, sub="Authorino AuthPolicy\n1. JWT from realm\n2. tool:X in roles\n3. azp = agent (new CEL)")
    d.arrow(512, 228, 700, 468, "6. tools/call + Bearer\n(injected at egress)", C["gw"][0], lx=620, ly=320)
    d.box(1020, 490, 300, 90, "MCP servers -> plant-api", "k8s", 16)
    d.arrow(942, 535, 1018, 535, "7. allowed", C["gw"][0], lx=945, ly=505)
    d.arrow(1170, 422, 942, 500, "JWKS (realm)", C["kc"][0], dashed=True, lx=1000, ly=440)
    return d


def f_trust_map():
    d = Doc()
    d.text(40, 10, "Trust map: who verifies whom, with which key", 26)
    d.box(520, 70, 300, 100, "SPIRE Server", "spire", 22, sub="root of workload trust")
    d.box(80, 260, 280, 100, "SPIRE Agent", "spire", 20, sub="trusts server bundle")
    d.box(520, 260, 300, 100, "OIDC Discovery Provider", "spire", 17, sub="re-publishes JWT keys")
    d.box(960, 260, 300, 100, "Kubernetes API", "k8s", 20, sub="TokenReview")
    d.box(80, 460, 280, 100, "Sandbox / OpenShell\nsupervisor + gateway", "os", 16)
    d.box(520, 460, 300, 100, "Keycloak realm", "kc", 22, sub="own signing keys")
    d.box(960, 460, 300, 100, "MCP Gateway\n(Authorino)", "gw", 18)
    d.arrow(300, 258, 560, 172, "agent SVID (signed by server)", C["spire"][0], lx=250, ly=190)
    d.arrow(820, 120, 1100, 258, "server checks agent PSAT", C["k8s"][0], lx=900, ly=160)
    d.arrow(670, 172, 670, 258, "JWT keys", C["spire"][0], lx=680, ly=200)
    d.arrow(220, 362, 220, 458, "workload SVID", C["spire"][0], lx=230, ly=395)
    d.arrow(362, 510, 518, 510, "JWT-SVID as client auth", C["kc"][0], lx=365, ly=480)
    d.arrow(670, 458, 670, 362, "Keycloak fetches JWKS\nto verify the SVID", C["spire"][0], lx=680, ly=390)
    d.arrow(822, 510, 958, 510, "Authorino fetches\nrealm JWKS", C["kc"][0], lx=830, ly=525)
    d.arrow(220, 562, 1110, 600, None, C["gw"][0])
    d.text(500, 600, "Bearer = Keycloak token (NOT the SVID)", 15, C["gw"][0])
    d.arrow(820, 300, 958, 400, "option: verify JWT-SVID\ndirectly (customHeader)", C["spire"][0], dashed=True, lx=880, ly=375)
    d.box(80, 660, 1180, 80, "Two independent roots: SPIRE signs WORKLOAD identity. Keycloak signs USER identity + permissions.\nKeycloak bridges them: it accepts a SPIRE-signed SVID and mints its own token that names both.", "note", 15)
    return d


def g_today_vs_target():
    d = Doc()
    d.text(40, 10, "Our lab: today vs target (from repo + Robert's design note)", 26)
    d.frame(20, 60, 640, 640, "TODAY (main branch)", "bad")
    d.box(50, 110, 580, 90, "mcp-token-refresh.py (sidecar / in sandbox)", "bad", 16,
          sub="grant_type=password as realm user 'operator'\nMCP_USERNAME / MCP_PASSWORD env vars (bridge.yaml:487-489)")
    d.box(50, 240, 580, 80, "Keycloak public client 'mcp-gateway'", "kc", 16,
          sub="token: azp=mcp-gateway, NO sub, NO aud, 18 tool roles")
    d.box(50, 360, 580, 70, "gateway.json -> Hermie reads it", "os", 16)
    d.box(50, 470, 580, 100, "MCP Gateway AuthPolicy (mcp-gateway-policy.yaml)", "gw", 15,
          sub="mcp: jwt issuerUrl realm   |   mcps: tool:X in resource_access\nasks: does OPERATOR hold tool:X? (no agent in the question)")
    d.box(50, 600, 580, 70, "OpenShell chart 0.0.92 / CLI 0.1: static credentials only,\nno token_grant / jwt-spiffe", "bad", 14)
    for y1, y2 in [(200, 238), (320, 358), (430, 468)]:
        d.arrow(340, y1, 340, y2, color=C["bad"][0])
    d.frame(700, 60, 780, 640, "TARGET", "os")
    d.box(730, 110, 340, 90, "ZTWIM installed", "spire", 17, sub="v1.1.3, ClusterSPIFFEID per tenant\nOIDC provider publishes JWKS")
    d.box(1110, 110, 340, 90, "Path A: hermes-plain", "os", 17, sub="broker sidecar + csi.spiffe.io\nworks without OpenShell upgrade")
    d.box(730, 240, 720, 90, "Broker: password grant (operator) -> RFC 8693 exchange", "kc", 16,
          sub="client auth = JWT-SVID (private_key_jwt / federated) or X509-SVID (tls_client_auth)\nresult: sub=operator, azp=hermes-agent")
    d.box(730, 370, 720, 100, "AuthPolicy adds one CEL predicate (AND-ed in patternMatching)", "gw", 16,
          sub="has(auth.identity.azp) && auth.identity.azp == 'hermes-agent'\noperator-only token -> 403, exchanged token + role -> allow")
    d.box(730, 500, 720, 70, "jti -> Authorino log, plant-api audit, raised_by_verified, MLflow tags", "spire", 15)
    d.box(730, 600, 720, 70, "Path B: sandbox via OpenShell token_grant (needs 0.0.92 -> >= v0.0.113 upgrade)", "bad", 15, dashed=True)
    for y1, y2 in [(200, 238), (330, 368), (470, 498)]:
        d.arrow(1090, y1, 1090, y2, color=C["os"][0])
    return d


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in [("a-spire-big-picture", a_big_picture), ("b-attestation-sequence", b_attestation),
                     ("c-ztwim-crds", c_ztwim), ("d-jwt-svid-card", d_jwt_card),
                     ("e-sandbox-to-mcp-end-to-end", e_end_to_end), ("f-trust-map", f_trust_map),
                     ("g-our-lab-today-vs-target", g_today_vs_target)]:
        fn().save(out / f"{name}.excalidraw")
        print("wrote", name)
