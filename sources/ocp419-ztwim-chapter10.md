# OCP 4.19 Security and compliance - Chapter 10: Zero Trust Workload Identity Manager

> Source: local PDF OpenShift_Container_Platform-4.19-Security_and_compliance-en-US.pdf, chapter 10 (text extracted with pdftotext, 2026-11-20). Page headers/footers stripped.

```text

10.1. ZERO TRUST WORKLOAD IDENTITY MANAGER OVERVIEW
The Zero Trust Workload Identity Manager is a OpenShift Container Platform Operator that manages
the lifecycle of SPIFFE Runtime Environment (SPIRE) components. It enables workload identity
management based on the Secure Production Identity Framework for Everyone (SPIFFE) standard,
providing cryptographically verifiable identities (SVIDs) to workloads running in OpenShift Container
Platform clusters.

SPIFFE can work across diverse infrastructures including on-premise, cloud, and hybrid environments.
SPIFFE identities are cryptographically enabled providing a basis for auditing and compliance.

The following are components of the Zero Trust Workload Identity Manager architecture:

10.1.1. SPIFFE
Establish trust between software workloads in distributed systems with Secure Production Identity
Framework for Everyone (SPIFFE). SPIFFE assigns unique IDs to workloads, allowing them to verify
identities and communicate securely. This ensures secure authentication across dynamic environments.

The SPIFFE IDs are contained in the SPIFFE Verifiable Identity Document (SVID). SVIDs are used by
workloads to verify their identity to other workloads so that the workloads can communicate with each
other. The two main SVID formats are:

        X.509-SVIDs: X.509 certificates where the SPIFFE ID is embedded in the Subject Alternative
        Name (SAN) field.

        JWT-SVIDs: JSON Web Tokens (JWTs) where the SPIFFE ID is included as the sub claim.

For more information, see SPIFFE Overview.

10.1.2. SPIRE Server
Manage and issue SPIFFE identities within a trust domain using the SPIRE Server. By storing registration
entries and signing keys, you can control identity issuance and perform node attestation with the SPIRE
Agent. For more information, see About the SPIRE Server.

10.1.3. SPIRE Agent
The SPIRE Agent performs workload attestation to ensure that workloads receive a verified identity
when requesting authentication through the SPIFFE Workload API. The agent uses configured workload
attestor plugins to verify these identities. The plugins are used to verify the identity of the node on
which the agent is running. For more information, see About the SPIRE Agent.

10.1.4. Attestation
Attestation verifies the identity of nodes and workloads before issuing SPIFFE IDs. By comparing
attributes against defined selectors, this process ensures that only legitimate entities within the trust
domain receive cryptographic credentials.

The two main types of attestation in SPIFFE/SPIRE are:

        Node attestation: verifies the identity of a machine or a node on a system, before a SPIRE

          Node attestation: verifies the identity of a machine or a node on a system, before a SPIRE
          Agent running on that node can be trusted to request identities for workloads.

          Workload attestation: verifies the identity of an application or service running on an attested
          node before the SPIRE Agent on that node can provide it with a SPIFFE ID and SVID.

  For more information, see Attestation.

  10.2. ZERO TRUST WORKLOAD IDENTITY MANAGER COMPONENTS
  Review the components available in the initial release of Zero Trust Workload Identity Manager to
  understand the architecture. These components provide the foundation for identifying and securing
  your workloads.

  10.2.1. SPIFFE CSI Driver
  The SPIFFE Container Storage Interface (CSI) driver helps pods securely obtain their SPIFFE Verifiable
  Identity Document (SVID) by delivering the Workload API socket. By using Kubernetes ephemeral inline
  volumes, the driver simplifies how applications request temporary storage for identity management.

  When the pod starts, the Kubelet calls the SPIFFE CSI driver to provision and mount a volume into the
  pod’s containers. The SPIFFE CSI driver mounts a directory that contains the SPIFFE Workload API into
  the pod. Applications in the pod then communicate with the Workload API to obtain their SVIDs. The
  driver guarantees that each SVID is unique.

  10.2.2. SPIRE OpenID Connect Discovery Provider
  Use the SPIRE OpenID Connect (OIDC) Discovery Provider to integrate SPIRE workload identities with
  OIDC-compliant systems. This component exposes endpoints for token verification. It helps ensure
  compatibility between SPIRE-issued credentials and external APIs requiring standard OIDC tokens.

  While SPIRE primarily issues identities for workloads, additional workload-related claims can be
  embedded into JWT-SVIDs through the configuration of SPIRE, which these claims to be included in the
  token and verified by OIDC-compliant clients.

  10.2.3. SPIRE Controller Manager
  Use the SPIRE Controller Manager to automate workload registration with custom resource definitions
  (CRDs). The manager monitors pods and CRDs to create, update, or delete entries on the SPIRE Server.
  This process helps ensure that your SPIRE entries accurately reflect your active resources.

  The SPIRE Controller Manager is designed to be deployed on the same pod as the SPIRE Server. The
  manager communicates with the SPIRE Server API using a private UNIX Domain Socket within a shared
  volume.

  10.2.4. SPIRE Server and Agent telemetry
  Use the SPIRE Controller Manager to register workloads by using custom resource definitions (CRDs).
  The manager monitors pods and CRDs for changes and triggers a reconciliation process. This process
  creates, updates, or deletes SPIRE Server entries to help ensure they match your configuration.

  10.2.5. About the Zero Trust Workload Identity Manager workflow

  The following is a high-level workflow of the Zero Trust Workload Identity Manager within the Red Hat

The following is a high-level workflow of the Zero Trust Workload Identity Manager within the Red Hat
OpenShift cluster.

     1. The SPIRE, SPIRE Agent, SPIFFE CSI Driver, and the SPIRE OIDC Discovery Provider operands
        are deployed and managed by Zero Trust Workload Identity Manager via associated customer
        resource definitions (CRDs).

     2. Watches are then registered for relevant Kubernetes resources and the necessary SPIRE CRDs
        are applied to the cluster.

     3. The CR for the ZeroTrustWorkloadIdentityManager resource named cluster is deployed and
        managed by a controller.

    4. To deploy the SPIRE Server, SPIRE Agent, SPIFFE CSI Driver, and SPIRE OIDC Discovery
       Provider, you need to create a custom resource of a each certain type and name it cluster. The
       custom resource types are as follows:

            SPIRE Server - SpireServer

            SPIRE Agent - SpireAgent

            SPIFFE CSI Driver - SpiffeCSIDriver

            SPIRE OIDC discovery provider - SpireOIDCDiscoveryProvider

     5. When a node starts, the SPIRE Agent initializes, and connects to the SPIRE Server.

    6. The SPIRE Agent begins the node attestation process. The agent collects information on the
       node’s identity such as label name and namespace. The agent securely provides the information
       it gathered through the attestation to the SPIRE Server.

     7. The SPIRE Server then evaluates this information against its configured attestation policies and
        registration entries. If successful, the server generates an agent SVID and the Trust Bundle (CA
        Certificate) and securely sends this back to the SPIRE Agent.

    8. A workload starts on the node and needs a secure identity. The workload connects to the
       agent’s Workload API and requests a SVID.

    9. The SPIRE Agent receives the request and begins a workload attestation to gather information
       about the workload.

    10. After the SPIRE Agent gathers the information, the information is sent to the SPIRE Server and
        the server checks its configured registration entries.

    11. The SPIRE Agent receives the workload SVID and Trust Bundle and passes it on to the workload.
        The workload can now present their SVIDs to other SPIFFE-aware devices to communicate with
        them.

Additional resources

        Registering workloads

        SPIFFE Concepts

        SPIRE Use Cases

  10.3. ZERO TRUST WORKLOAD IDENTITY MANAGER RELEASE NOTES
  The Zero Trust Workload Identity Manager leverages Secure Production Identity Framework for
  Everyone (SPIFFE) and the SPIFFE Runtime Environment (SPIRE) to provide a comprehensive identity
  management solution for distributed systems.

  These release notes track the development of Zero Trust Workload Identity Manager.

  10.3.1. Zero Trust Workload Identity Manager 1.0.4
  Issued: 29 October 2026

  Some Common Vulnerabilities and Exposures (CVEs) and advisories are available for the Zero Trust
  Workload Identity Manager 1.0.4.

  The following advisories are available for this release:

          RHBA-2026:92267

          RHBA-2026:92269

          RHBA-2026:92270

          RHBA-2026:92271

          RHBA-2026:92273

          RHBA-2026:92274

  10.3.1.1. Fixed issues

  The following bug fix is available for this release:

          Before this update, the CreateOnlyMode condition remained True after you removed the
          CREATE_ONLY_MODE environment variable from the Operator subscription or set the
          variable to false. As a consequence, custom resource status continued to report that create-
          only mode was enabled. With this release, Zero Trust Workload Identity Manager sets the
          CreateOnlyMode condition to False with reason CreateOnlyModeDisabled when
          CREATE_ONLY_MODE is removed or set to false. (SPIRE-683)

  10.3.1.2. CVEs

  The following CVEs are available for this release:

          CVE-2026-111943

          CVE-2026-33818

  10.3.2. Zero Trust Workload Identity Manager 1.0.2
  Issued: 3 September 2026

  This release fixes some Common Vulnerabilities and Exposures (CVEs).

  The following advisories are available for the Zero Trust Workload Identity Manager:

        RHBA-2026:62762

        RHBA-2026:62764

        RHBA-2026:62766

        RHBA-2026:62768

        RHBA-2026:62769

        RHBA-2026:62770

        RHBA-2026:63118

10.3.2.1. CVEs

        CVE-2026-32283

        CVE-2026-33811

        CVE-2026-39829

        CVE-2026-39831

        CVE-2026-42502

        CVE-2026-46597

        CVE-2026-68121

        CVE-2026-71235

10.3.3. Zero Trust Workload Identity Manager 1.0.1
Issued: 17 May 2026

This release fixes some Common Vulnerabilities and Exposures (CVEs).

The following advisories are available for the Zero Trust Workload Identity Manager:

        RHBA-2026:17483

        RHSA-2026:17463

        RHSA-2026:17462

        RHSA-2026:17461

        RHSA-2026:17460

        RHSA-2026:17457

        RHSA-2026:17456

10.3.3.1. CVEs

        CVE-2026-21441

          CVE-2025-61726

          CVE-2025-61729

          CVE-2025-68121

  10.3.4. Zero Trust Workload Identity Manager 1.0.0 (General Availability)
  Issued: 12 December 2025

  This release introduces capabilities for enterprise readiness, security, and operational flexibility. The
  release includes SPIRE federation for cross-cluster identity, PostgreSQL support for production
  persistence, and enhanced security through stricter constraints and API validation.

  The following advisories are available for the Zero Trust Workload Identity Manager:

          RHBA-2025:23438

          RHBA-2025:23439

          RHBA-2025:23440

          RHBA-2025:23441

          RHBA-2025:23442

          RHBA-2025:23443

          RHBA-2025:23446

  Zero Trust Workload Identity Manager supports the following components and versions:

    Component                                             Version

    SPIRE Server                                          1.13.3

    SPIRE Agent                                           1.13.3

    SPIRE Controller Manager                              0.6.3

    SPIRE OIDC Discovery Provider                         1.13.3

    SPIFFE CSI Driver                                     0.2.8

  10.3.4.1. New features and enhancements

  SPIRE federation support
      The Operator now includes support for SPIRE federation, enabling workloads across distinct trust
      domains to securely communicate and authenticate with each other.

              Key capabilities:

                   Configuration of bundle endpoints using https_spiffe (TLS) or https_web (Web PKI)

               Configuration of bundle endpoints using https_spiffe (TLS) or https_web (Web PKI)
               profiles.

               Automatic certificate management via the ACME protocol. For example, Let’s Encrypt.

               Automatic OpenShift Container Platform route creation for federation endpoints.

               Ability to configure relationships with multiple federated trust domains.

           Customer action required:

               Review the federation configuration within the SpireServer custom resource (CR).

               Ensure proper DNS resolution and network connectivity to federated trust domains.

PostgreSQL database support
   SPIRE Server now supports PostgreSQL as an external database backend, accommodating
   production deployments that necessitate enterprise-grade data persistence and high availability.

           Supported Types: sqlite3 (default), postgres, mysql.

           Customer action required:

               For production, evaluation of migration from SQLite to PostgreSQL is recommended.

               Creation and configuration of Kubernetes Secrets for database TLS certificates and
               credentials are required.

Configurable agent socket path and Container Storage Interface (CSI) plugin name
   The SPIRE Agent socket path and the SPIFFE CSI Driver plugin name are now configurable,
   providing operational flexibility for environments with specific directory requirements or co-
   existence with multiple SPIFFE deployments.

           Key configuration points:

               SpireAgent.spec.socketPath

               SpiffeCSIDriver.spec.agentSocketPath

               SpiffeCSIDriver.spec.pluginName

           Customer action required:

               Ensure consistency between socketPath in the SpireAgent CR and agentSocketPath
               in the SpiffeCSIDriver CR.

Workload attestors verification API
   A new API has been introduced to configure kubelet certificate verification for workload attestation,
   enhancing security and supporting various OpenShift Container Platform configurations.

           Verification types:

               auto (default): Verification utilizes OpenShift Container Platform defaults
               (/etc/kubernetes/kubelet-ca.crt).

               hostCert: Uses a custom CA certificate path.

                  skip: Skips TLS verification (not recommended for production use).

  Configurable Certificate Authority and JSON Web Token key types
      Administrators can now configure the cryptographic key types used for the SPIRE Server Certificate
      Authority (CA) and JSON Web Token (JWT) signing, ensuring compliance with organizational
      security policies.

              Supported Key Types: rsa-2048 (default), rsa-4096, ec-p256, ec-p384.

              Customer action required:

                  Review organizational security policies to determine required key types.

  Custom namespace deployment

              The Operator and all associated operands can now be deployed within a custom namespace,
              providing flexibility for organizations with specific namespace governance requirements.

  Proxy-aware Operator and operands

              The Operator and all managed operands are now proxy-aware and automatically inherit
              cluster-wide proxy settings when configured.

  Enhanced Security Context Constraints

              SPIRE Agent and SPIFFE CSI Driver now run with Security Context Constraints (SCC) that
              prevent root user execution, though privileged container mode remains enabled for
              necessary host-level operations.

              The Operator and all operand containers are configured with the ReadOnlyRootFilesystem
              set to true.

  Enhanced API validation
      Comprehensive Common Expression Language (CEL) validation has been integrated into all custom
      resource definitions (CRDs) to prevent configuration errors during admission control.

              Key validations:

                  All Operator CRDs are enforced as singletons (must be named cluster).

                  Immutable Fields: Fields including trustDomain, clusterName, bundleConfigMap,
                  federation, bundleEndpoint profile, and all Persistence settings (size, accessMode,
                  and storageClass) are now immutable after initial creation.

              Customer action required:

                  Review existing CR configurations to ensure compliance with the new validation rules.

  Common configuration consolidation

              Standard configuration options (labels, resources, affinity, tolerations, nodeSelector) are
              now standardized across all operand CRs via a shared CommonConfig structure.

  Configuring log level and log format for the operands

      This release introduces flexible logging controls to improve observability and debugging across the

   This release introduces flexible logging controls to improve observability and debugging across the
   platform:

           SPIRE Components: Users can now configure the logLevel (debug, info, warn, error) and
           logFormat (text, JSON) independently for SpireServer, SpireAgent, and
           SpireOIDCDiscoveryProvider directly within their CR specifications. The defaults are set to
           "info" for the logLevel and "text" for the logFormat.

           Operator: The Operator’s log verbosity is now configurable via the
           OPERATOR_LOG_LEVEL environment variable using klog’s textlogger.

Refactor for create-only mode
   By setting the CREATE_ONLY_MODE environment variable, users can prevent the Operator from
   reconciling updates. This allows for manual resource modification without interference. If this mode
   is disabled, the Operator resumes enforcing the state and overwrites any manual changes.

10.3.4.2. Status and observability improvements

Enhanced status reporting

           The main CR now aggregates status information from all operand CRs.

           New status conditions include Upgradeable (indicating a safe upgrade path) and
           Progressing (detailing deployment progress).

Operator metrics

           Operator metrics are now exposed and secured with appropriate RBAC configuration.

           Integration is supported with the OpenShift Container Platform monitoring stack.

10.3.4.3. Fixed issues

Enhanced Security Context Constraints for SPIRE Agent

           Before this update, the SPIRE Agent and SPIFFE CSI Driver containers were running as root
           user, leading to potential security violations. With this release, Security Context Constraints
           (SCC) have been configured to ensure these components no longer run as root. While
           privileged container mode is still required for necessary capabilities, this change reduces
           potential security risks for the user.
           (SPIRE-60)

SpireServer updates now propagate without Operator restart

           Before this update, the Operator failed to trigger reconciliation after updating the operand
           CR spec. As a consequence, user updates to SpireServer CR resources were not
           propagated to the StatefulSet, causing reconciliation to fail and changes to be ignored,
           leading to inconsistent resource allocation. With this release, the race condition between the
           manager and reconciler’s cache to trigger reconciliation after CR updates has been fixed. As
           a result, post installation patch operations on SpireServer CRs reliably trigger reconciliation,
           ensuring updated values are applied to the StatefulSet without manual Operator restart.
           (SPIRE-68)

Removed unnecessary security context constraint for OpenID Connect discovery provider

             Before this update, the system unnecessarily created a custom security context constraint
             (SCC) for the OpenID Connect (OIDC) discovery provider, which increased the security
             footprint and configuration complexity even though the deployment did not require it. With
             this release, the custom SCC creation logic has been removed, resulting in a configuration
             where the OIDC discovery provider operates successfully without the extra security
             constraints.
             (SPIRE-190)

  Fixed ConfigMap Reconciliation for SPIRE Controller Manager

             Before this update, Spire-controller manager ConfigMap reconciliation failed due to an
             unhandled edge case in the previous implementation. As a consequence, users experienced
             configuration inconsistencies. With this release, the Spire-controller manager ConfigMap
             reconciliation issue has been resolved. As a result, end users now experience seamless Spire-
             controller manager configuration.
             (SPIRE-195)

  OIDC discovery provider now restarts automatically on configuration changes

             Before this update, the SPIRE OIDC discovery provider failed to automatically restart
             following configmap changes, leading to persistent authentication failures. With this release,
             updates to the CR now trigger an automatic pod restart, ensuring that configmap changes
             are applied immediately.
             (SPIRE-225)

  Corrected update rollback for DaemonSets, Deployments, and StatefulSets

             Before this update, daemonset, deployment, and statefulsets were not properly reverted
             to their original form in all valid scenarios due to an oversight in the update logic. As a
             consequence, user data loss or inconsistency occurred in valid scenarios. With this release,
             the update logic has been corrected, ensuring all valid scenarios revert to their original form.
             (SPIRE-248)

             Other bug fixes included:

                 Fixed issues related to continuous reconciliation and unnecessary updates.

                 Eliminated requeue logic for user input validation errors.

  10.3.5. Zero Trust Workload Identity Manager 0.2.0 (General Availability)
  Issued: 09 August 2025

  The following advisories are available for the Zero Trust Workload Identity Manager:

          RHBA-2025:15425

          RHBA-2025:15426

          RHBA-2025:15427

          RHBA-2025:15428

  10.3.5.1. New features and enhancements

Support for the managed OIDC Discovery Provider Route

          The Operator exposes the SPIREOIDCDiscoveryProvider spec through OpenShift
          Container Platform Routes under the domain *.apps.<cluster_domain> for the selected
          default installation.

          The managedRoute and externalSecretRef fields have been added to the
          spireOidcDiscoveryProvider spec.

          The managedRoute field is boolean and is set to true by default. If set to false, the
          Operator stops managing the route and the existing route will not be deleted automatically.
          If set back to true, the Operator resumes managing the route. If a route does not exist, the
          Operator creates a new one. If a route already exists, the Operator will override the user
          configuration if a conflict exists.

          The externalSecretRef references an externally managed Secret that has the TLS
          certificate for the oidc-discovery-provider Route host. When provided, this populates the
          route’s .Spec.TLS.ExternalCertificate field. For more information, see Creating a route with
          externally managed certificate

Enabling the custom Certificate Authority Time-To-Live for the SPIRE bundle

          The following Time-To-Live (TTL) fields have been added to the SpireServer custom
          resource definition (CRD) API for SPIRE Server certificate management:

              CAValidity (default: 24h)

              DefaultX509Validity (default: 1h)

              DefaultJWTValidity (default: 5m)

          The default values can be replaced in the server configuration with user-configurable
          options that give users the flexibility to customize certificate and SPIFFE Verifiable Identity
          Document (SVID) lifetimes based on their security requirements.

Enabling Manual User Configurations

          The Operator controller switches to create-only mode once the ztwim.openshift.io/create-
          only=true annotation is present on the Operator’s APIs. This allows resource creation while
          skipping the updates. A user can update the resources manually to test their configuration.
          This annotation supports APIs such as SpireServer, SpireAgents, SpiffeCSIDriver,
          SpireOIDCDiscoveryProvider, and ZeroTrustWorkloadIdentityManager.

          When the annotation is applied, all derived resources including resources created and
          managed by the Operator are created but not updated.

          After the annotation is removed and the pod restarts, the Operator tries to come back to the
          required state. The annotation is applied only once during start or a restart.

10.3.5.2. Fixed issues

JSON Web Token Issuer field now requires a valid URL

          Before this update, the JwtIssuer field for both the SpireServer and the
          SpireOidcDiscoveryProvider custom resources did not require the input to be a URL,

             frequently causing configuration errors. With this release, the validation has been updated,
             and users must now manually enter a valid issuer URL in the JwtIssuer field for both custom
             resources. As a result, misconfigurations caused by a malformed issuer values are prevented,
             ensuring a stable and reliable setup.
             (SPIRE-117)

  10.3.6. Zero Trust Workload Identity Manager 0.1.0 (General Availability)
  Issued: 16 June 2025

  The following advisories are available for the Zero Trust Workload Identity Manager:

          RHBA-2025:9088

          RHBA-2025:9085

          RHBA-2025:9090

          RHBA-2025:9084

          RHBA-2025:9089

          RHBA-2025:9087

          RHBA-2025:9101

          RHBA-2025:9104

  10.4. INSTALLING THE ZERO TRUST WORKLOAD IDENTITY MANAGER
  Install Zero Trust Workload Identity Manager to help ensure secure communication between your
  workloads. You can install the Zero Trust Workload Identity Manager by using either the web console or
  CLI.

  If you install the Operator into a custom namespace (for example, my-custom-namespace), all
  managed operand resources are deployed within that same namespace. All secrets and ConfigMaps
  referenced by the custom resources (CRs) must also exist in that custom namespace.

                IMPORTANT

                The Operator installation is not supported in the openshift-* namespaces and the
                default namespace.

  10.4.1. Installing the Zero Trust Workload Identity Manager by using the web console
  Use the OperatorHub in the OpenShift Container Platform web console to install the Zero Trust
  Workload Identity Manager. This process streamlines deployment and helps ensure the Operator is
  installed in the correct namespace with the appropriate installation mode.

                NOTE

                A minimum of 1Gi persistent volume is required to install the SPIRE Server.

Prerequisites

       You have access to the cluster with cluster-admin privileges.

       You have access to the OpenShift Container Platform web console.

Procedure

     1. Log in to the OpenShift Container Platform web console.

    2. Go to Ecosystem → Software Catalog.

    3. Search for Zero Trust Workload Identity Manager.

    4. On the Install Operator page:

        a. Update the Update channel, if necessary. The channel defaults to stable-v1, which installs
           the latest stable-v1 release of the Zero Trust Workload Identity Manager.

        b. Choose the Installed Namespace for the Operator. The default Operator namespace is
           zero-trust-workload-identity-manager.
           If the zero-trust-workload-identity-manager namespace does not exist, it is created for
           you.

                           NOTE

                           The Operator and operands are deployed in the same namespace.

        c. Select an Update Approval strategy

                The Automatic strategy allows Operator Lifecycle Manager (OLM) to automatically
                update the Operator when a new version is available.

                The Manual strategy requires a user with appropriate credentials to approve the
                Operator update.

    5. Click Install.

Verification

     1. Navigate to Ecosystem → Installed Operators.

        a. Verify that Zero Trust Workload Identity Manager is listed with a Status of Succeeded in
           the zero-trust-workload-identity-manager namespace.

        b. Verify that Zero Trust Workload Identity Manager controller manager deployment is ready
           and available by running the following command:

                $ oc get deployment -l name=zero-trust-workload-identity-manager -n zero-trust-
                workload-identity-manager

            Example output

                NAME                                   READY UP-TO-DATE AVAILABLE AGE
                zero-trust-workload-identity-manager-controller-manager 1/1 1 1    3h36m

       2. To check the Operator logs, run the following command:

              $ oc logs -f deployment/zero-trust-workload-identity-manager-controller-manager -n zero-
              trust-workload-identity-manager

  10.4.2. Installing the Zero Trust Workload Identity Manager by using the CLI

  Prerequisites

          You have access to the cluster with cluster-admin privileges.

                  NOTE

                  A minimum of 1Gi persistent volume is required to install the SPIRE Server.

  Procedure

       1. Create a new project named zero-trust-workload-identity-manager by running the following
          command:

              $ oc new-project zero-trust-workload-identity-manager

       2. Create an OperatorGroup object:

           a. Create a YAML file, for example, operatorGroup.yaml, with the following content:

              Example operatorGroup.yaml

                  apiVersion: operators.coreos.com/v1
                  kind: OperatorGroup
                  metadata:
                   name: openshift-zero-trust-workload-identity-manager
                   namespace: zero-trust-workload-identity-manager
                  spec:
                   upgradeStrategy: Default

           b. Create the OperatorGroup object by running the following command:

                  $ oc create -f operatorGroup.yaml

       3. Create a Subscription object:

           a. Create a YAML file, for example, subscription.yaml, that defines the Subscription object:

              Example subscription.yaml

                  apiVersion: operators.coreos.com/v1alpha1
                  kind: Subscription
                  metadata:
                   name: openshift-zero-trust-workload-identity-manager
                   namespace: zero-trust-workload-identity-manager
                  spec:

                channel: stable-v1
                name: openshift-zero-trust-workload-identity-manager
                source: redhat-operators
                sourceNamespace: openshift-marketplace
                installPlanApproval: Automatic

         b. Create the Subscription object by running the following command:

               $ oc create -f subscription.yaml

Verification

        Verify that the OLM subscription is created by running the following command:

           $ oc get subscription -n zero-trust-workload-identity-manager

        Example output

           NAME                               PACKAGE                      SOURCE
           CHANNEL
           openshift-zero-trust-workload-identity-manager zero-trust-workload-identity-manager
           redhat-operators stable-v1

        Verify whether the Operator is successfully installed by running the following command:

           $ oc get csv -n zero-trust-workload-identity-manager

        Example output

           NAME                            DISPLAY                    VERSION PHASE
           zero-trust-workload-identity-manager.v1.0.0 Zero Trust Workload Identity Manager 1.0.0
           Succeeded

        Verify that the Zero Trust Workload Identity Manager controller manager is ready by running the
        following command:

           $ oc get deployment -l name=zero-trust-workload-identity-manager -n zero-trust-workload-
           identity-manager

        Example output

           NAME                                   READY UP-TO-DATE AVAILABLE AGE
           zero-trust-workload-identity-manager-controller-manager 1/1 1 1    43m

10.5. DEPLOYING ZERO TRUST WORKLOAD IDENTITY MANAGER
OPERANDS
Deploy the Zero Trust Workload Identity Manager operands by creating their custom resources in a
specific order. Adhering to the sequence helps ensure the successful installation of components, such as
the SPIRE Server, SPIRE Agent, and SPIFFE CSI driver.

  You must deploy the operands in the following sequence to ensure successful installation:

           ZeroTrustWorkloadIdentityManager CR

           SPIRE Server

           SPIRE Agent

           SPIFFE CSI driver

           SPIRE OIDC discovery provider

  10.5.1. About the ZeroTrustWorkloadIdentityManager custom resource
  The ZeroTrustWorkloadIdentityManager is the primary custom resource that initializes the SPIRE
  deployments. This primary resource defines the trust domain and cluster name to help ensure secure
  workload identity management.

  Reference the complete YAML specification to correctly structure the
  ZeroTrustWorkloadIdentityManager CR. This example helps you identify required fields and
  immutable parameters for your configuration.

      apiVersion: operator.openshift.io/v1alpha1
      kind: ZeroTrustWorkloadIdentityManager
      metadata:
       name: cluster
       labels:
         app.kubernetes.io/name: zero-trust-workload-identity-manager
         app.kubernetes.io/managed-by: zero-trust-workload-identity-manager
      spec:
        trustDomain: "example.com"
        clusterName: "production-cluster"
        bundleConfigMap: "spire-bundle"

  where:

  spec.trustDomain
      Specifies the trust domain to be used for the SPIFFE identifiers. Must be a valid SPIFFE trust domain
      (lowercase alphanumeric, hyphens, and dots). Maximum length is 255 characters. After setting a
      value for the field, the field is immutable. Red Hat highly recommends to set this value to match your
      the base application URL (for example, apps.mycluster.example.com) of your OpenShift Container
      Platform cluster. Using a different value might cause automatically generated OpenShift Routes or
      federation endpoints to be created with incorrect or mismatched hostnames later in the
      configuration process.
  spec.clusterName
      Specifies the name that identifies this cluster within the trust domain. Must be a valid DNS-1123
      subdomain with a maximum length of 63 characters. Once set, this field is immutable.
  spec.bundleConfigMap
      Specifies the name of the ConfigMap that stores the SPIRE trust bundle. This ConfigMap contains
      the root certificates for the trust domain and is created and maintained by the Operator. Must be a
      valid Kubernetes name with a maximum length of 253 characters. This field is optional (defaults to
      spire-bundle) and once set, is immutable.

10.5.2. Deploying the SPIRE Server
Deploy the SPIRE Server by configuring the SpireServer custom resource (CR). This establishes a
central authority that manages and issues identities to the workloads in your cluster.

Prerequisites

       You have access to the cluster as a user with the cluster-admin role.

       You have installed Zero Trust Workload Identity Manager in the cluster.

Procedure

     1. Create the SpireServer CR:

        a. Create a YAML file that defines the SpireServer CR, for example, SpireServer.yaml:

            Example SpireServer.yaml

                apiVersion: operator.openshift.io/v1alpha1
                kind: SpireServer
                metadata:
                 name: cluster
                spec:
                 logLevel: "info"
                 logFormat: "text"
                 jwtIssuer: "https://oidc-discovery.apps.cluster.example.com"
                 caValidity: "24h"
                 defaultX509Validity: "1h"
                 defaultJWTValidity: "5m"
                 jwtKeyType: "rsa-2048"
                 caSubject:
                   country: "US"
                   organization: "Example Corporation"
                   commonName: "SPIRE Server CA"
                 persistence:
                   size: "5Gi"
                   accessMode: "ReadWriteOnce"
                   storageClass: "gp3-csi"
                 datastore:
                   databaseType: "sqlite3"
                   connectionString: "/run/spire/data/datastore.sqlite3"
                   tlsSecretName: ""
                   maxOpenConns: 100
                   maxIdleConns: 10
                   connMaxLifetime: 0
                   disableMigration: "false"

            where:

            metadata.name
                Specifies that the value must be cluster.
            spec.logLevel

                Specifies the logging level for the SPIRE Server. The valid options are debug, info, warn,

                 Specifies the logging level for the SPIRE Server. The valid options are debug, info, warn,
                 and error.
              spec.logFormat
                 Specifies the logging format for the SPIRE Server. The valid options are text and json.
              spec.jwtIssuer
                 Specifies the JWT issuer URL. Must be a valid HTTPS or HTTP URL with a maximum
                 length of 512 characters.
              spec.caValidity
                 Specifies the validity period (Time to Live (TTL)) for the SPIRE Server’s CA certificate.
                 This determines how long the server’s root or intermediate certificate is valid. The
                 format is a duration string (for example, 24h, 168h).
              spec.defaultX509Validity
                 Specifies the default validity period (TTL) for X.509 SVIDs issued to workloads. This
                 value is used if a specific TTL is not configured for a registration entry.
              spec.defaultJWTValidity
                 Specifies thedefault validity period (TTL) for JWT SVIDs issued to workloads. This value
                 is used if a specific TTL is not configured for a registration entry.
              spec.jwtKeyType
                 Specifies the key type used for JWT signing. The valid options are rsa-2048, rsa-4096,
                 ec-p256, and ec-p384. This field is optional.
              spec.caSubject.country
                 Specifies the country for the SPIRE Server certificate authority (CA). Must be an ISO
                 3166-1 alpha-2 country code (2 characters).
              spec.caSubject.organization
                 Specifies the organization for the SPIRE Server CA. Maximum length is 64 characters.
              spec.caSubject.commonName
                 Specifies the common name for the SPIRE Server CA. Maximum length is 255
                 characters.
              spec.persistence.size
                 Specifies the size of the persistent volume (for example, 1Gi, 5Gi). Once set, this field is
                 immutable.
              spec.persistence.accessMode
                 Specifies the access mode for the persistent volume. The valid options are
                 ReadWriteOnce, ReadWriteOncePod, and ReadWriteMany. Once set, this field is
                 immutable.
              spec.persistence.storageClass
                 Specifies the storage class to be used for the PVC. Once set, this field is immutable.
              spec.datastore.databaseType
                 Specifies the type of database to use for the datastore. The valid options are sql,
                 sqlite3, postgres, mysql, aws_postgresql, and aws_mysql.
              spec.datastore.connectionString
                 Specifies the connection string for the database. For PostgreSQL with SSL, include
                 sslmode and certificate paths (for example, dbname=spire user=spire
                 host=postgres.example.com sslmode=verify-full).

           spec.datastore.tlsSecretName
               Specifies the name of a Kubernetes Secret containing TLS certificates for database
               connections. The Secret will be mounted at /run/spire/db/certs. This field is optional.
           spec.datastore.maxOpenConns
               Specifies the maximum number of open database connections. Must be between 1 and
               10000.
           spec.datastore.maxIdleConns
               Specifies the maximum number of idle database connections in the pool. Must be
               between 0 and 10000.
           spec.datastore.connMaxLifetime
               Specifies the maximum lifetime of a database connection in seconds. A value of 0 means
               connections are not closed due to age.
           spec.datastore.disableMigration
               Specifies whether to disable automatic database migration. The valid options are true
               and false.

        b. Apply the configuration by running the following command:

               $ oc apply -f SpireServer.yaml

Verification

       Verify that the stateful set of SPIRE Server is ready and available by running the following
       command:

           $ oc get statefulset -l app.kubernetes.io/name=spire-server -n zero-trust-workload-identity-
           manager

       Example output

           NAME         READY AGE
           spire-server 1/1 65s

       Verify that the status of the SPIRE Server pod is Running by running the following command:

           $ oc get po -l app.kubernetes.io/name=spire-server -n zero-trust-workload-identity-manager

       Example output

           NAME           READY STATUS RESTARTS         AGE
           spire-server-0 2/2 Running 1 (108s ago) 111s

       Verify that the persistent volume claim (PVC) is bound, by running the following command:

           $ oc get pvc -l app.kubernetes.io/name=spire-server -n zero-trust-workload-identity-manager

       Example output

           NAME                  STATUS     VOLUME                            CAPACITY ACCESS

              MODES STORAGECLASS VOLUMEATTRIBUTECLASS AGE
              spire-data-spire-server-0 Bound pvc-27a36535-18a1-4fde-ab6d-e7ee7d3c2744 5Gi
              RW0         gp3-csi     <unset>     22m

  10.5.3. Deploying the SPIRE Agent
  Use the SpireAgent custom resource to configure the SPIRE Agent DaemonSet on your nodes. This
  defines how the agent verifies workloads and manages identity attestation across your OpenShift
  Container Platform cluster.

  Prerequisites

          You have access to the cluster as a user with the cluster-admin role.

          You have installed Zero Trust Workload Identity Manager in the cluster.

  Procedure

       1. Create the SpireAgent CR:

           a. Create a YAML file that defines the SpireAgent CR, for example, SpireAgent.yaml:

              Example SpireAgent.yaml

                  apiVersion: operator.openshift.io/v1alpha1
                  kind: SpireAgent
                  metadata:
                   name: cluster
                  spec:
                   socketPath: "/run/spire/agent-sockets"
                   logLevel: "info"
                   logFormat: "text"
                   nodeAttestor:
                     k8sPSATEnabled: "true"
                   workloadAttestors:
                     k8sEnabled: "true"
                     workloadAttestorsVerification:
                      type: "auto"
                      hostCertBasePath: "/etc/kubernetes"
                      hostCertFileName: "kubelet-ca.crt"
                     disableContainerSelectors: "false"
                     useNewContainerLocator: "true"

              where:

              metadata.name
                  Specifies that the value must be cluster.
              spec.socketPath
                  Specifies the directory on the host where the SPIRE agent socket is created. This
                  directory is shared with the SPIFFE CSI driver via the hostPath volume. Must match the
                  SpiffeCSIDriver.spec.agentSocketPath for workloads to access the socket. Must be an
                  absolute path with a maximum length of 256 characters.
              spec.logLevel
                  Specifies the logging level for the SPIRE Server. The valid options are debug, info, warn,

               Specifies the logging level for the SPIRE Server. The valid options are debug, info, warn,
               and error.
           spec.logFormat
               Specifies the logging format for the SPIRE Server. The valid options are text and json.
           spec.nodeAttestor.k8sPSATEnabled
               Specifies whether Kubernetes Projected Service Account Token (PSAT) node
               attestation is enabled. When enabled, the SPIRE agent uses K8s PSATs to prove its
               identity to the SPIRE server during node attestation. The valid options are true and
               false.
           spec.workloadAttestors.k8sEnabled
               Specifies whether the Kubernetes workload attestor is enabled. When enabled, the
               SPIRE agent can verify workload identities using Kubernetes pod information and service
               account tokens. The valid options are true and false.
           spec.workloadAttestors.workloadAttestorsVerification.type
               Specifies the kubelet certificate verification mode. The valid options are auto, hostCert,
               and skip.
           spec.workloadAttestors.workloadAttestorsVerification.hostCertBasePath
               Specifies the directory containing the kubelet CA certificate. Required when type is
               hostCert. Optional when type is auto (defaults to /etc/kubernetes if not specified).
           spec.workloadAttestors.workloadAttestorsVerification.hostCertFileName
               Specifies the file name for the kubelet’s CA certificate. When combined with
               hostCertBasePath, forms the full path. Required when type is hostCert. Optional when
               type is auto. Defaults to kubelet-ca.crt if not specified.
           spec.workloadAttestors.disableContainerSelectors
               Specifies whether to disable container selectors in the Kubernetes workload attestor.
               Set to true if using holdApplicationUntilProxyStarts in Istio. The valid options are true
               and false.
           spec.workloadAttestors.useNewContainerLocator
               Specifies enabling the new container locator algorithm that has support for cgroups v2.
               The valid options are true and false.

        b. Apply the configuration by running the following command:

               $ oc apply -f SpireAgent.yaml

Verification

       Verify that the daemon set of the SPIRE Agent is ready and available by running the following
       command:

           $ oc get daemonset -l app.kubernetes.io/name=spire-agent -n zero-trust-workload-identity-
           manager

       Example output

           NAME        DESIRED CURRENT READY UP-TO-DATE AVAILABLE NODE
           SELECTOR AGE
           spire-agent 3    3   3   3    3    <none>    10m

          Verify that the status of SPIRE Agent pods is Running by running the following command:

              $ oc get po -l app.kubernetes.io/name=spire-agent -n zero-trust-workload-identity-manager

          Example output

              NAME             READY STATUS RESTARTS AGE
              spire-agent-dp4jb 1/1 Running 0   12m
              spire-agent-nvwjm 1/1 Running 0    12m
              spire-agent-vtvlk 1/1 Running 0  12m

  10.5.4. Deploying the SPIFFE Container Storage Interface driver
  Configure the Container Storage Interface (CSI) driver using the SpiffeCSIDriver CR. This
  configuration mounts SPIFFE sockets directly into workload pods, which allows your applications to
  access the SPIFFE Workload API securely.

  Prerequisites

          You have access to the cluster as a user with the cluster-admin role.

          You have installed Zero Trust Workload Identity Manager in the cluster.

  Procedure

       1. Create the SpiffeCSIDriver CR:

           a. Create a YAML file that defines the SpiffeCSIDriver CR object, for example,
              SpiffeCSIDriver.yaml:

              Example SpiffeCSIDriver.yaml

                  apiVersion: operator.openshift.io/v1alpha1
                  kind: SpiffeCSIDriver
                  metadata:
                   name: cluster
                  spec:
                   agentSocketPath: "/run/spire/agent-sockets"
                   pluginName: "csi.spiffe.io"

              where:

              metadata.name
                  Specifies that the name must be cluster.
              spec.agentSocketPath
                  Specifies the path to the directory containing the SPIRE agent’s Workload API socket.
                  This directory is bind-mounted into workload containers by the CSI driver. The directory
                  is shared between the SPIRE agent and CSI driver via a hostPath volume. Must be an
                  absolute path with a maximum length of 256 characters. This value must match
                  SpireAgent.spec.socketPath for workloads to access the socket.

            spec.pluginName
                Specifies the name of the CSI plugin. This sets the CSI driver name that is deployed to
                the cluster and used in VolumeMount configurations. Must match the driver name
                referenced in the workload pods. Must be a valid domain name format (for example,
                csi.spiffe.io) with a maximum length of 127 characters.

        b. Apply the configuration by running the following command:

                $ oc apply -f SpiffeCSIDriver.yaml

Verification

       Verify that the daemon set of the SPIFFE CSI driver is ready and available by running the
       following command:

            $ oc get daemonset -l app.kubernetes.io/name=spiffe-csi-driver -n zero-trust-workload-
            identity-manager

       Example output

            NAME                  DESIRED CURRENT READY UP-TO-DATE AVAILABLE NODE
            SELECTOR AGE
            spire-spiffe-csi-driver 3    3   3  3     3    <none>    114s

       Verify that the status of SPIFFE Container Storage Interface (CSI) Driver pods is Running by
       running the following command:

            $ oc get po -l app.kubernetes.io/name=spiffe-csi-driver -n zero-trust-workload-identity-
            manager

       Example output

            NAME                       READY STATUS RESTARTS AGE
            spire-spiffe-csi-driver-gpwcp 2/2 Running 0   2m37s
            spire-spiffe-csi-driver-rrbrd 2/2 Running 0  2m37s
            spire-spiffe-csi-driver-w6s6q 2/2 Running 0   2m37s

10.5.5. Deploying the SPIRE OpenID Connect Discovery Provider
Deploy the SPIRE OpenID Connect (OIDC) Discovery Provider by configuring the
SpireOIDCDiscoveryProvider CR. This allows you to define the trust domain and JSON web token
(JWT) issuer for your cluster.

Prerequisites

       You have access to the cluster as a user with the cluster-admin role.

       You have installed Zero Trust Workload Identity Manager in the cluster.

Procedure

     1. Create the SpireOIDCDiscoveryProvider CR:

           a. Create a YAML file that defines the SpireOIDCDiscoveryProvider CR, for example,
              SpireOIDCDiscoveryProvider.yaml:

              Example SpireOIDCDiscoveryProvider.yaml

                 apiVersion: operator.openshift.io/v1alpha1
                 kind: SpireOIDCDiscoveryProvider
                 metadata:
                  name: cluster
                 spec:
                  logLevel: "info"
                  logFormat: "text"
                  csiDriverName: "csi.spiffe.io"
                  jwtIssuer: "https://oidc-discovery.apps.cluster.example.com"
                  replicaCount: 1
                  managedRoute: "true"
                  externalSecretRef: ""

              where:

              metadata.name
                 Specifies that the value must be cluster.
              spec.logLevel
                 Specifies the logging level for the SPIRE Server. The valid options are debug, info, warn,
                 and error.
              spec.logFormat
                 Specifies the logging format for the SPIRE Server. The valid options are text and json.
              spec.csiDriverName
                 Specifies the name of the CSI driver to use for mounting the Workload API socket. This
                 must match the SpiffeCSIDriver.spec.pluginName value for the OIDC provider to
                 access SPIFFE identities. Must be a valid DNS subdomain format (for example,
                 csi.spiffe.io) with a maximum length of 127 characters.
              spec.jwtIssuer
                 Specifies the JWT issuer URL. Must be a valid HTTPS or HTTP URL with a maximum
                 length of 512 characters. This value must match the SpireServer.spec.jwtIssuer value.
              spec.replicaCount
                 Specifies the number of replicas for the OIDC Discovery Provider deployment. Must be
                 between 1 and 5.
              spec.managedRoute
                 Specifies whether the Operator automatically creates an OpenShift route for the OIDC
                 Discovery Provider endpoints. Set to true to have the Operator automatically create and
                 maintain an OpenShift route for OIDC discovery endpoints (*.apps.). Set to false for
                 administrators to manually configure routes or ingress.
              spec.ternalSecretRef
                 Specifies a reference to an externally managed secret that contains the TLS certificate
                 for the OIDC Discovery Provider route host. Must be a valid Kubernetes secret reference
                 name with a maximum length of 253 characters. This field is optional.

           b. Apply the configuration by running the following command:

                $ oc apply -f SpireOIDCDiscoveryProvider.yaml

Verification

     1. Verify that the deployment of OIDC Discovery Provider is ready and available by running the
        following command:

           $ oc get deployment -l app.kubernetes.io/name=spiffe-oidc-discovery-provider -n zero-trust-
           workload-identity-manager

        Example output

           NAME                          READY UP-TO-DATE AVAILABLE AGE
           spire-spiffe-oidc-discovery-provider 1/1 1    1    2m58s

     2. Verify that the status of OIDC Discovery Provider pods is Running by running the following
        command:

           $ oc get po -l app.kubernetes.io/name=spiffe-oidc-discovery-provider -n zero-trust-workload-
           identity-manager

        Example output

           NAME                                    READY STATUS RESTARTS AGE
           spire-spiffe-oidc-discovery-provider-64586d599f-lcc94 2/2 Running 0 7m15s

10.6. CONFIGURING THE EGRESS PROXY FOR THE ZERO TRUST
WORKLOAD IDENTITY MANAGER
Operator Lifecycle Manager (OLM) automatically configures managed Operators with proxy settings
when you use a cluster-wide egress proxy. To support proxying HTTPS connections, you can inject
certificate authority (CA) certificates into the Zero Trust Workload Identity Manager.

10.6.1. Injecting a custom CA certificate for the Zero Trust Workload Identity
Manager
Inject certificate authority (CA) certificates into the Zero Trust Workload Identity Manager to support
proxying HTTPS connections. This configuration helps ensure that the Identity Manager can
communicate securely when you enable a cluster-wide proxy.

Prerequisites

        You have access to the cluster as a user with the cluster-admin role.

        You have enabled the cluster-wide proxy for OpenShift Container Platform.

        You have installed Zero Trust Workload Identity Manager 1.0.0 or later.

        You have deployed the SPIRE Server, SPIRE Agent, SPIFFEE CSI Driver, and the SPIRE OIDC
        Discovery Provider operands in the cluster.

  Procedure

       1. Create a config map in the zero-trust-workload-identity-manager namespace by running the
          following command:

              $ oc create configmap trusted-ca -n zero-trust-workload-identity-manager

       2. Inject the CA bundle that is trusted by OpenShift Container Platform into the config map by
          running the following command:

              $ oc label cm trusted-ca config.openshift.io/inject-trusted-cabundle=true -n zero-trust-
              workload-identity-manager

       3. Update the subscription for the Zero Trust Workload Identity Manager to use the config map by
          running the following command:

              $ oc -n zero-trust-workload-identity-manager patch subscription openshift-zero-trust-
              workload-identity-manager --type='merge' -p '{"spec":{"config":{"env":
              [{"name":"TRUSTED_CA_BUNDLE_CONFIGMAP","value":"trusted-ca"}]}}}'

  Verification

       1. Verify that the operands have finished rolling out by running the following command:

              $ oc rollout status deployment/zero-trust-workload-identity-manager-controller-manager -n
              zero-trust-workload-identity-manager && \
              $ oc rollout status statefulset/spireserver -n zero-trust-workload-identity-manager && \
              $ oc rollout status daemonset/spire-agent -n zero-trust-workload-identity-manager && \
              $ oc rollout status deployment/spire-spiffe-oidc-discovery-provider -n zero-trust-workload-
              identity-manager

          Example output

              deployment "zero-trust-workload-identity-manager-controller-manager" successfully rolled out
              statefulset "spire-server" successfully rolled out
              daemonset "spire-agent" successfully rolled out
              deployment "spire-spiffe-oidc-discovery-provider" successfully rolled out

       2. Verify that the CA bundle was mounted as a volume by running the following command:

              $ oc get deployment zero-trust-workload-identity-manager -n zero-trust-workload-identity-
              manager -o=jsonpath={.spec.template.spec.'containers[0].volumeMounts'}

              $ oc get statefulset spire-server -n zero-trust-workload-identity-manager -o
              jsonpath='{.spec.template.spec.containers[*].volumeMounts[?(@.name=="trusted-ca-
              bundle")]}'

              $ oc get daemonset spire-agent -n zero-trust-workload-identity-manager -o
              jsonpath='{.spec.template.spec.containers[*].volumeMounts[?(@.name=="trusted-ca-
              bundle")]}'

           $ oc get daemonset spire-spiffe-csi-driver -n zero-trust-workload-identity-manager -o
           jsonpath='{.spec.template.spec.containers[*].volumeMounts[?(@.name=="trusted-ca-
           bundle")]}'

        Example output

           [{{"mountPath":"/etc/pki/ca-trust/extracted/pem","name":"trusted-ca-bundle","readOnly":true}}]

     3. Verify that the source of the CA bundle is the trusted-ca config map by running the following
        command:

           $ oc get deployment zero-trust-workload-identity-manager -n zero-trust-workload-identity-
           manager -o=jsonpath={.spec.template.spec.volumes}

           $ oc get statefulset spire-server -n zero-trust-workload-identity-manager -
           o=jsonpath='{.spec.template.spec.volumes}' | jq '.[] | select(.name=="trusted-ca-bundle")'

           $ oc get daemonset spire-agent -n zero-trust-workload-identity-manager -
           o=jsonpath='{.spec.template.spec.volumes}' | jq '.[] | select(.name=="trusted-ca-bundle")'

           $ oc get deployment spire-spiffe-oidc-discovery-provider -n zero-trust-workload-identity-
           manager -o=jsonpath='{.spec.template.spec.volumes}' | jq '.[] | select(.name=="trusted-ca-
           bundle")'

        Example output

           {
               "configMap": {
                 "defaultMode": 420,
                 "items": [
                    {
                      "key": "ca-bundle.crt",
                      "path": "tls-ca-bundle.pem"
                    }
                 ],
                 "name": "trusted-ca"
               },
               "name": "trusted-ca-bundle"
           }

10.6.2. Additional resources
        Configuring proxy support in Operator Lifecycle Manager

10.7. ZERO TRUST WORKLOAD IDENTITY MANAGER OIDC
FEDERATION
Configure Zero Trust Workload Identity Manager to act as an OpenID Connect (OIDC) provider through
the SPIRE server. This integration allows workloads to receive verifiable JSON Web Tokens (JWT-
SVIDs) and allows external systems, such as cloud providers, to retrieve public keys from the discovery
endpoint.

  The following providers are verified to work with SPIRE OIDC federation:

          Azure Entra ID

          Vault

  10.7.1. About the Entra ID OpenID Connect
  Integrate Entra ID OpenID Connect (OIDC) with SPIRE to provide workloads with automatic, short-lived
  cryptographic identities. This configuration allows you to securely authenticate services without
  maintaining static secrets.

  Integrating Entra ID OpenID Connect (OIDC) with SPIRE provides workloads with automatic, short-lived
  cryptographic identities. The SPIRE-issued identities are sent to Entra ID to securely authenticate the
  service without any static secrets.

  10.7.1.1. Configuring the external certificate for the managed OIDC discovery provider route

  Configure the managed OIDC discovery provider route to use an externally managed TLS certificate. By
  referencing a TLS secret, you can secure the OIDC endpoint with your own certificate credentials.

  Prerequisites

          You have installed Zero Trust Workload Identity Manager 0.2.0 or later.

          You have deployed the SPIRE Server, SPIRE Agent, SPIFFEE CSI Driver, and the SPIRE OIDC
          Discovery Provider operands in the cluster.

          You have installed the cert-manager Operator for Red Hat OpenShift. For more information,
          Installing the cert-manager Operator for Red Hat OpenShift .

          You have created a ClusterIssuer or Issuer configured with a publicly trusted CA service. For
          example, an Automated Certificate Management Environment (ACME) type Issuer with the
          "Let’s Encrypt ACME" service. For more information, see Configuring an ACME issuer

  Procedure

       1. Create a Role to provide the router service account permissions to read the referenced secret
          by running the following command:

              $ oc create role secret-reader \
               --verb=get,list,watch \
               --resource=secrets \
               --resource-name=$TLS_SECRET_NAME \
               -n zero-trust-workload-identity-manager

       2. Create a RoleBinding resource to bind the router service account with the newly created Role
          resource by running the following command:

              $ oc create rolebinding secret-reader-binding \
               --role=secret-reader \
               --serviceaccount=openshift-ingress:router \
               -n zero-trust-workload-identity-manager

       3. Configure the SpireOIDCDIscoveryProvider Custom Resource (CR) object to reference the

     3. Configure the SpireOIDCDIscoveryProvider Custom Resource (CR) object to reference the
        Secret generated in the earlier step by running the following command:

            $ oc patch SpireOIDCDiscoveryProvider cluster --type=merge -p='
            spec:
              externalSecretRef: ${TLS_SECRET_NAME}
            '

Verification

     1. In the SpireOIDCDiscoveryProvider CR, check if the ManageRouteReady condition is set to
        True by running the following command:

            $ oc wait --for=jsonpath='{.status.conditions[?
            (@.type=="ManagedRouteReady")].status}'=True SpireOIDCDiscoveryProvider/cluster --
            timeout=120s

     2. Verify that the OIDC endpoint can be accessed securely through HTTPS by running the
        following command:

            $ curl https://$JWT_ISSUER_ENDPOINT/.well-known/openid-configuration

            {
             "issuer": "https://$JWT_ISSUER_ENDPOINT",
             "jwks_uri": "https://$JWT_ISSUER_ENDPOINT/keys",
             "authorization_endpoint": "",
             "response_types_supported": [
                "id_token"
             ],
             "subject_types_supported": [],
             "id_token_signing_alg_values_supported": [
                "RS256",
                "ES256",
                "ES384"
             ]
            }%

10.7.1.2. Disabling a managed route

If you want to fully control the behavior of exposing the OIDC Discovery Provider service, you can
disable the managed Route based on your requirements.

Procedure

        To manually configure the OIDC Discovery Provider, set managedRoute to false by running
        the following command:

            $ oc patch SpireOIDCDiscoveryProvider cluster --type=merge -p='
            spec:
             managedRoute: "false"

10.7.1.3. Using Entra ID with Microsoft Azure

Configure your Microsoft Azure environment to enable Entra ID integration with Azure. By defining

  Configure your Microsoft Azure environment to enable Entra ID integration with Azure. By defining
  variables and creating a resource group, you establish the infrastructure needed to securely manage
  workload identities.

  Prerequisites

          You have configured the SPIRE OIDC Discovery Provider Route to serve the TLS certificates
          from a publicly trusted CA.

  Procedure

       1. Log in to Azure by running the following command:

              $ az login

       2. Configure variables for your Azure subscription and tenant by running the following commands:

              $ export SUBSCRIPTION_ID=$(az account list --query "[?isDefault].id" -o tsv)

              $ export TENANT_ID=$(az account list --query "[?isDefault].tenantId" -o tsv)

              $ export LOCATION=centralus

              Replace the SUBSCRIPTION_ID variable with your unique subscription identifier.

              Replace the TENANT_ID variable with the ID for your Azure Active Directory instance.

              Replace the LOCATION variable with the Azure region where your resource is created.

       3. Define resource variable names by running the following commands:

              $ export NAME=ztwim

              $ export RESOURCE_GROUP="${NAME}-rg"

              $ export STORAGE_ACCOUNT="${NAME}storage"

              $ export STORAGE_CONTAINER="${NAME}storagecontainer"

              $ export USER_ASSIGNED_IDENTITY_NAME="${NAME}-identity"

              Replace the NAME variable with the base name for all resources.

              Replace the RESOURCE_GROUP variable with the name of the resource group.

              Replace the STORAGE_ACCOUNT variable with the name for the storage account.

              Replace the STORAGE_CONTAINER variable with the name for the storage container.

              Replace the USEDR_ASSIGNED_IDENTITY_NAME variable with the name for a managed
              identity.

    4. Create the resource group by running the following command:

            $ az group create \
             --name "${RESOURCE_GROUP}" \
             --location "${LOCATION}"

10.7.1.4. Configuring Azure blob storage

Create a new Microsoft Azure storage account and container to provide a dedicated location for your
content. Configuring this storage ensures that the Zero Trust Workload Identity Manager can
successfully store and retrieve blobs for your environment.

Procedure

     1. Create a new storage account that is used to store content by running the following command:

            $ az storage account create \
             --name ${STORAGE_ACCOUNT} \
             --resource-group ${RESOURCE_GROUP} \
             --location ${LOCATION} \
             --encryption-services blob

     2. Obtain the storage ID for the newly created storage account by running the following command:

            $ export STORAGE_ACCOUNT_ID=$(az storage account show -n
            ${STORAGE_ACCOUNT} -g ${RESOURCE_GROUP} --query id --out tsv)

     3. Create a storage container inside the newly created storage account to provide a location to
        support the storage of blobs by running the following command:

            $ az storage container create \
             --account-name ${STORAGE_ACCOUNT} \
             --name ${STORAGE_CONTAINER} \
             --auth-mode login

10.7.1.5. Configuring an Azure user managed identity

Create a user-assigned managed identity in Azure to manage access control for your resources. You
must also obtain the Client ID to associate roles with the service principal.

Procedure

     1. Create a new User Managed Identity and then obtain the Client ID of the related Service
        Principal associated with the User Managed Identity by running the following command:

            $ az identity create \
             --name ${USER_ASSIGNED_IDENTITY_NAME} \
             --resource-group ${RESOURCE_GROUP}

            $ export IDENTITY_CLIENT_ID=$(az identity show --resource-group
            "${RESOURCE_GROUP}" --name "${USER_ASSIGNED_IDENTITY_NAME}" --query
            'clientId' -otsv)

       2. Retrieve the CLIENT_ID of an Azure user-assigned managed identity and save it as an
          environment variable by running the following command:

             $ export IDENTITY_CLIENT_ID=$(az identity show --resource-group
             "${RESOURCE_GROUP}" --name "${USER_ASSIGNED_IDENTITY_NAME}" --query
             'clientId' -otsv)

       3. Associate a role with the Service Principal associated with the User Managed Identity by running
          the following command:

             $ az role assignment create \
              --role "Storage Blob Data Contributor" \
              --assignee "${IDENTITY_CLIENT_ID}" \
              --scope ${STORAGE_ACCOUNT_ID}

  10.7.1.6. Creating the demonstration application

  Create the demonstration application to verify that the entire system functions correctly. This process
  validates the configuration of your application secrets and namespaces.

  Procedure
  To create the demonstration application, complete the following steps:

       1. Set the application name and namespace by running the following commands:

             $ export APP_NAME=workload-app

             $ export APP_NAMESPACE=demo

       2. Create the namespace by running the following command:

             $ oc create namespace $APP_NAMESPACE

       3. Create the application Secret by running the following command:

             $ oc apply -f - << EOF
             apiVersion: v1
             kind: Secret
             metadata:
              name: $APP_NAME
              namespace: $APP_NAMESPACE
             stringData:
              AAD_AUTHORITY: https://login.microsoftonline.com/
              AZURE_AUDIENCE: "api://AzureADTokenExchange"
              AZURE_TENANT_ID: "${TENANT_ID}"
              AZURE_CLIENT_ID: "${IDENTITY_CLIENT_ID}"
              BLOB_STORE_ACCOUNT: "${STORAGE_ACCOUNT}"
              BLOB_STORE_CONTAINER: "${STORAGE_CONTAINER}"
             EOF

  10.7.1.7. Deploying the workload application

  Deploy the workload application to your cluster to validate the Zero Trust Workload Identity Manager

Deploy the workload application to your cluster to validate the Zero Trust Workload Identity Manager
environment. This application confirms that the SPIFFE Workload API is functioning and can successfully
retrieve JWT tokens.

Prerequisites

        The demonstration application has been created and deployed.

Procedure

     1. To deploy the application, copy the entire command block provided and paste it directly into
        your terminal. Press Enter.

            $ oc apply -f - << EOF
            apiVersion: v1
            kind: ServiceAccount
            metadata:
              name: $APP_NAME
              namespace: $APP_NAMESPACE
            ---
            kind: Deployment
            apiVersion: apps/v1
            metadata:
              name: $APP_NAME
              namespace: $APP_NAMESPACE
            spec:
              selector:
                matchLabels:
                 app: $APP_NAME
              template:
                metadata:
                 labels:
                   app: $APP_NAME
                   deployment: $APP_NAME
                spec:
                 serviceAccountName: $APP_NAME
                 containers:
                   - name: $APP_NAME
                     image: "registry.redhat.io/ubi9/python-311:latest"
                     command:
                      - /bin/bash
                      - "-c"
                      -|
                        #!/bin/bash
                        pip install spiffe azure-cli

                     cat << EOF > /opt/app-root/src/get-spiffe-token.py
                     #!/opt/app-root/bin/python
                     from spiffe import JwtSource
                     import argparse
                     parser = argparse.ArgumentParser(description='Retrieve SPIFFE Token.')
                     parser.add_argument("-a", "--audience", help="The audience to include in the
            token", required=True)
                     args = parser.parse_args()
                     with JwtSource() as source:
                       jwt_svid = source.fetch_svid(audience={args.audience})

                       print(jwt_svid.token)
                      EOF

                       chmod +x /opt/app-root/src/get-spiffe-token.py
                       while true; do sleep 10; done
                   envFrom:
                   - secretRef:
                       name: $APP_NAME
                   env:
                     - name: SPIFFE_ENDPOINT_SOCKET
                       value: unix:///run/spire/sockets/spire-agent.sock
                   securityContext:
                     allowPrivilegeEscalation: false
                     capabilities:
                       drop:
                         - ALL
                     readOnlyRootFilesystem: false
                     runAsNonRoot: true
                     seccompProfile:
                       type: RuntimeDefault
                   ports:
                     - containerPort: 8080
                       protocol: TCP
                   volumeMounts:
                     - name: spiffe-workload-api
                       mountPath: /run/spire/sockets
                       readOnly: true
               volumes:
                 - name: spiffe-workload-api
                   csi:
                     driver: csi.spiffe.io
                     readOnly: true
             EOF

  Verification

       1. Ensure that the workload-app pod is running successfully by running the following command:

             $ oc get pods -n $APP_NAMESPACE

          Example output

             NAME                  READY          STATUS   RESTARTS        AGE
             workload-app-5f8b9d685b-abcde        1/1  Running 0           60s

       2. Retrieve the SPIFFE JWT Token (SVID-JWT):

           a. Get the pod name dynamically by running the following command:

                 $ POD_NAME=$(oc get pods -n $APP_NAMESPACE -l app=$APP_NAME -o
                 jsonpath='{.items[0].metadata.name}')

           b. Run the script inside the pod by running the following command:

                $ oc exec -it $POD_NAME -n $APP_NAMESPACE -- \
                 /opt/app-root/src/get-spiffe-token.py -a "api://AzureADTokenExchange"

10.7.1.8. Configuring Azure with the SPIFFE identity federation

Configure Microsoft Azure with SPIFFE identity federation to enable password-free, automated
authentication for the demonstration application. This federates the User Managed Identity with the
SPIFFE identity associated with your workload application.

Procedure

        Federate the identities between the User Managed Identity and the SPIFFE identity associated
        with the workload application by running the following command:

            $ az identity federated-credential create \
             --name ${NAME} \
             --identity-name ${USER_ASSIGNED_IDENTITY_NAME} \
             --resource-group ${RESOURCE_GROUP} \
             --issuer https://$JWT_ISSUER_ENDPOINT \
             --subject spiffe://$APP_DOMAIN/ns/$APP_NAMESPACE/sa/$APP_NAME \
             --audience api://AzureADTokenExchange

10.7.1.9. Verifying that the application workload can access the content in the Azure Blob
Storage

Verify that your application workload can connect to the Azure Blob Storage. By uploading a test file,
you validate the authentication token and ensure that the workload has the correct permissions.

Prerequisites

        An Azure Blob Storage has been created.

Procedure

     1. Retrieve a JWT token from the SPIFFE Workload API by running the following command:

            $ oc rsh -n $APP_NAMESPACE deployment/$APP_NAME

     2. Create and export an environment variable named TOKEN by running the following command:

            $ export TOKEN=$(/opt/app-root/src/get-spiffe-token.py --audience=$AZURE_AUDIENCE)

     3. Log in to Azure CLI included within the pod by running the following command:

            $ az login --service-principal \
             -t ${AZURE_TENANT_ID} \
             -u ${AZURE_CLIENT_ID} \
             --federated-token ${TOKEN}

    4. Create a new file with the application workload pod and upload the file to the Blob Storage by
       running the following command:

              $ echo “Hello from OpenShift” > openshift-spire-federated-identities.txt

       5. Upload a file to the Azure Blog Storage by running the following command:

              $ az storage blob upload \
               --account-name ${BLOB_STORE_ACCOUNT} \
               --container-name ${BLOB_STORE_CONTAINER} \
               --name openshift-spire-federated-identities.txt \
               --file openshift-spire-federated-identities.txt \
               --auth-mode login

  Verification

          Confirm the file uploaded successfully by listing the files contained by running the following
          command:

              $ az storage blob list \
               --account-name ${BLOB_STORE_ACCOUNT} \
               --container-name ${BLOB_STORE_CONTAINER} \
               --auth-mode login \
               -o table

  10.7.2. About Vault OpenID Connect
  Use Vault OpenID Connect (OIDC) with SPIRE to securely authenticate workloads. Vault uses SPIRE as
  a trusted OIDC provider to validate workload identities. This configuration enables workloads to receive
  short-lived tokens to access secrets and perform actions within Vault.

  10.7.2.1. Installing Vault

  Install HashiCorp Vault to serve as an OpenID Connect (OIDC) provider. This establishes the necessary
  infrastructure to manage workload identities securely in your Zero Trust Workload Identity Manager
  environment.

  Prerequisites

          Configure a route. For more information, see Route configuration

          Helm is installed.

          A command-line JSON processor for easily reading the output from the Vault API.

          A HashiCorp Helm repository is added.

  Procedure

       1. Create the vault-helm-value.yaml file.

              global:
                enabled: true
                openshift: true 1
                tlsDisable: true 2
              injector:

            enabled: false
           server:
            ui:
             enabled: true
            image:
             repository: docker.io/hashicorp/vault
             tag: "1.19.0"
            dataStorage:
             enabled: true 3
             size: 1Gi
            standalone:
             enabled: true 4
             config: |
                listener "tcp" {
                  tls_disable = 1 5
                  address = "[::]:8200"
                  cluster_address = "[::]:8201"
                }
                storage "file" {
                  path = "/vault/data"
                }
            extraEnvironmentVars: {}

           The openshift field optimizes the deployment for OpenShift-specific security contexts.

           The tlsDisable field disables TLS for Kubernetes objects created by the chart.

           The datastorage.enabled field creates a 1Gi persistent volume to store Vault data.

           The standalone.enabled field deploys a single Vault pod.

           The tls_disabled field tells the Vault server to not use TLS.

    2. Run the helm install command:

           $ helm install vault hashicorp/vault \
            --create-namespace -n vault \
            --values ./vault-helm-value.yaml

    3. Expose the Vault service by running the following command:

           $ oc expose service vault -n vault

    4. Set the VAULT_ADDR environment variable to retrieve the hostname from the new route and
       then export it by running the following command:

           $ export VAULT_ADDR="http://$(oc get route vault -n vault -o jsonpath='{.spec.host}')"

                       NOTE

                       http:// is prepended because TLS is disabled.

Verification

          To ensure your Vault instance is running, run the following command:

              $ curl -s $VAULT_ADDR/v1/sys/health | jq

          Example output

              {
                  "initialized": true,
                  "sealed": true,
                  "standby": true,
                  "performance_standby": false,
                  "replication_performance_mode": "disabled",
                  "replication_dr_mode": "disabled",
                  "server_time_utc": 1663786574,
                  "version": "1.19.0",
                  "cluster_name": "vault-cluster-a1b2c3d4",
                  "cluster_id": "5e6f7a8b-9c0d-1e2f-3a4b-5c6d7e8f9a0b"
              }

  10.7.2.2. Initializing and unsealing Vault

  A newly installed Vault is sealed. This means that the primary encryption key, which protects all other
  encryption keys, is not loaded into the server memory upon startup. You need to initialize Vault to unseal
  it.

  The steps to initialize a Vault server are:

        1. Initialize and unseal Vault

       2. Enable the key-value (KV) secrets engine and store a test secret

       3. Configure JSON Web Token (JWT) authentication with SPIRE

       4. Deploy a demonstration application

       5. Authenticate and retrieve the secret

  Prerequisites

          Ensure that Vault is running.

          Ensure that Vault is not initialized. You can only initialize a Vault server once.

  Procedure

        1. Open a remote shell into the vault pod by running the following command:

              $ oc rsh -n vault statefulset/vault

       2. Initialize Vault to get your unseal key and root token by running the following command:

              $ vault operator init -key-shares=1 -key-threshold=1 -format=json

       3. Export the unseal key and root token you received from the earlier command by running the

     3. Export the unseal key and root token you received from the earlier command by running the
        following commands:

            $ export UNSEAL_KEY=<Your-Unseal-Key>

            $ export ROOT_TOKEN=<Your-Root-Token>

    4. Unseal Vault using your unseal key by running the following command:

            $ vault operator unseal -format=json $UNSEAL_KEY

     5. Exit the pod by entering exit.

Verification

        To verify that the Vault pod is ready, run the following command:

            $ oc get pod -n vault

        Example output

            NAME        READY    STATUS            RESTARTS     AGE
            vault-0   1/1    Running 0               65d

10.7.2.3. Enabling the key-value secrets engine and store a test secret

Enable the key-value secrets engine to create a secure, centralized location for managing credentials.
You can also store a test secret to verify that the engine is working.

Prerequisites

        Make sure that Vault is initialized and unsealed.

Procedure

     1. Open another shell session in the Vault pod by running the following command:

            $ oc rsh -n vault statefulset/vault

     2. Export your root token again within this new session and log in by running the following
        command:

            $ export ROOT_TOKEN=<Your-Root-Token>

            $ vault login "${ROOT_TOKEN}"

     3. Enable the KV secrets engine at the secret/ path and create a test secret by running the
        following commands:

            $ export NAME=ztwim

              $ vault secrets enable -path=secret kv

              $ vault kv put secret/$NAME version=v0.1.0

  Verification

          To verify that the secret is stored correctly, run the following command:

              $ vault kv get secret/$NAME

  10.7.2.4. Configuring JSON Web Token authentication with SPIRE

  To help your applications securely log in to Vault using SPIFFE identities, configure JSON Web Token
  (JWT) authentication.

  Prerequisites

          Make sure that Vault is initialized and unsealed.

          Ensure that a test secret is stored in the key-value secrets engine.

  Procedure

       1. On your local machine, retrieve the SPIRE Certificate Authority (CA) bundle and save it to a file
          by running the following command:

              $ oc get cm -n zero-trust-workload-identity-manager spire-bundle -o jsonpath='{
              .data.bundle\.crt }' > oidc_provider_ca.pem

       2. Back in the Vault pod shell, create a temporary file and paste the contents of
          oidc_provider_ca.pem into it by running the following command:

              $ cat << EOF > /tmp/oidc_provider_ca.pem
              -----BEGIN CERTIFICATE-----
              <Paste-Your-Certificate-Content-Here>
              -----END CERTIFICATE-----
              EOF>

       3. Set up the necessary environment variables for the JWT configuration by running the following
          commands:

              $ export APP_DOMAIN=<Your-App-Domain>

              $ export JWT_ISSUER_ENDPOINT="oidc-discovery.$APP_DOMAIN"

              $ export OIDC_URL="https://$JWT_ISSUER_ENDPOINT"

              $ export OIDC_CA_PEM="$(cat /tmp/oidc_provider_ca.pem)"

       4. Crate a new environment variable by running the following command:

          $ export ROLE="${NAME}-role"

    5. Enable the JWT authentication method by running the following command:

          $ vault auth enable jwt

    6. Configure you ODIC authentication method by running the following command:

          $ vault write auth/jwt/config \
           oidc_discovery_url=$OIDC_URL \
           oidc_discovery_ca_pem="$OIDC_CA_PEM" \
           default_role=$ROLE

    7. Create a policy named ztwim-policy by running the following command:

          $ export POLICY="${NAME}-policy"

    8. Grant read access to the secret you created earlier by running the following command:

          $ vault policy write $POLICY -<<EOF
          path "secret/$NAME" {
             capabilities = ["read"]
          }
          EOF>>

    9. Create the following environment variables by running the following commands:

          $ export APP_NAME=client

          $ export APP_NAMESPACE=demo

          $ export AUDIENCE=$APP_NAME

   10. Create a JWT role that binds the policy to workload with a specific SPIFFE ID by running the
       following command:

          $ vault write auth/jwt/role/$ROLE -<<EOF
          {
            "role_type": "jwt",
            "user_claim": "sub",
            "bound_audiences": "$AUDIENCE",
            "bound_claims_type": "glob",
            "bound_claims": {
              "sub": "spiffe://$APP_DOMAIN/ns/$APP_NAMESPACE/sa/$APP_NAME"
            },
            "token_ttl": "24h",
            "token_policies": "$POLICY"
          }
          EOF

10.7.2.5. Deploying a demonstration application

  Deploy a demonstration application to create a simple client that uses its SPIFFE identity to
  authenticate with Vault. By doing this you can verify that the client can successfully authenticate using
  the configured identity.

  Procedure

       1. On your local machine, set the environment variables for your application by running the
          following commands:

              $ export APP_NAME=client

              $ export APP_NAMESPACE=demo

              $ export AUDIENCE=$APP_NAME

       2. Apply the Kubernetes manifest to create the namespace, service account, and deployment for
          the demo app by running the following command. This deployment mounts the SPIFFE CSI
          driver socket.

              $ oc apply -f - <<EOF
              # ... (paste the full YAML from your provided code here) ...
              EOF>>

  Verification

          Verify that the client deployment is ready by running the following command:

              $ oc get deploy -n $APP_NAMESPACE

          Example output

              NAME         READY            UP-TO-DATE      AVAILABLE        AGE
              frontend-app 2/2          2         2         120d
              backend-api   3/3         3          3        120d

  10.7.2.6. Authenticating and retrieving the secret

  Use the demonstration application to fetch a JWT token from the SPIFFE Workload API. This token
  allows you to authenticate with Vault to securely retrieve the secret and verify the workflow.

  Procedure

       1. Fetch a JWT-SVID by running the following command inside the running client pod:

              $ oc -n $APP_NAMESPACE exec -it $(oc get pod -o=jsonpath='{.items[*].metadata.name}' -l
              app=$APP_NAME -n $APP_NAMESPACE) \
               -- /opt/spire/bin/spire-agent api fetch jwt \
               -socketPath /run/spire/sockets/spire-agent.sock \
               -audience $AUDIENCE

       2. Copy the token from the output and export it as an environment variable on your local machine
          by running the following command:

           $ export IDENTITY_TOKEN=<Your-JWT-Token>

     3. Crate a new environment variable by running the following command:

           $ export ROLE="${NAME}-role"

     4. Use curl to send the JWT token to the Vault login endpoint to get a Vault client token by
        running the following command:

           $ VAULT_TOKEN=$(curl -s --request POST --data '{ "jwt": "'"${IDENTITY_TOKEN}"'", "role":
           "'"${ROLE}"'"}' "${VAULT_ADDR}"/v1/auth/jwt/login | jq -r '.auth.client_token')

Verification

        Use the newly acquired Vault token to read the secret from the KV store by running the
        following command:

           $ curl -s -H "X-Vault-Token: $VAULT_TOKEN" $VAULT_ADDR/v1/secret/$NAME | jq

        You should see the contents of the secret ("version": "v0.1.0") in the output, confirming the
        entire workflow is successful.

10.8. ZERO TRUST WORKLOAD IDENTITY MANAGER SPIRE
FEDERATION
Configure SPIRE federation to enable workloads in different trust domains to securely authenticate
each other across clusters, cloud providers, and organizational boundaries. By establishing trust
relationships between separate SPIRE deployments, you can build a zero-trust architecture that spans
multiple environments without compromising security or sharing secrets.

Federation works by securely sharing trust bundles between SPIRE servers through dedicated
federation endpoints. Each SPIRE deployment maintains its own trust domain and cryptographic
identity, while being able to verify identities from federated trust domains. This approach enables cross-
cluster communication, multi-cloud deployments, and secure integration with external partners.

Setting up SPIRE federation involves the following high-level steps:

     1. Choose an authentication profile: Select either https_spiffe or https_web.

     2. Configure the bundle endpoints: Each cluster exposes its trust bundle through a federation
        endpoint secured by the chosen authentication profile.

     3. Bootstrap the initial trust: Manually fetch and configure the initial trust bundle from each
        remote cluster.

     4. Establish federation relationships: Create ClusterFederatedTrustDomain resources to define
        which clusters trust each other.

     5. Configure automatic synchronization: The SPIRE Controller Manager automatically keeps trust
        bundles synchronized after initial setup.

10.8.1. Understanding bundle endpoint profiles

The bundle endpoint profile determines how your cluster exposes its trust bundle to other SPIRE

  The bundle endpoint profile determines how your cluster exposes its trust bundle to other SPIRE
  deployments and how it authenticates remote clusters accessing the bundle. Choose the profile that
  best matches your security requirements and infrastructure.

  The Zero Trust Workload Identity Manager supports two authentication profiles for federation:

  https_spiffe
      Uses SPIFFE-based TLS authentication. The SPIRE server presents its own SVID (SPIFFE Verifiable
      Identity Document) to authenticate itself to remote SPIRE servers. This profile provides strong
      cryptographic identity verification and is ideal for federation between SPIRE deployments.
  https_web
      Uses standard Web PKI (X.509 certificates from public or private certificate Authorities). This profile
      supports both automatic certificate management via ACME (Let’s Encrypt) and manual certificate
      management using tools like cert-manager.

  The following table summarizes the key differences between the two profiles:

    Criteria                     https_spiffe                           https_web

    Authentication method        SPIFFE SVID (TLS)                      X.509 certificate from CA

    Certificate management       Automatic (SPIRE-managed)              ACME (automatic) or manual

    Trust model                  SPIFFE trust domain                    Web PKI / CA trust

    Best for                     Internal SPIRE-to-SPIRE federation     External federation, public endpoints

    Security level               Very high (cryptographic identity)     High (CA-based trust)

    Setup complexity             Medium (requires SPIFFE IDs)           Low (ACME) to Medium (manual
                                                                        certs)

                     IMPORTANT

                     After enablement, federation cannot be disabled. The bundle endpoint profile is
                     immutable once configured. Changing the profile or disabling federation requires
                     reinstallation of the system. However, peer configurations (federatesWith) remain
                     dynamic and can be added or removed at any time. Plan your profile selection carefully
                     based on your long-term federation requirements.

  10.8.2. Federation configuration examples
  The following examples demonstrate different SPIRE federation configurations. Use these as templates
  when setting up federation between your clusters.

  Example 1: Using ACME for automatic certificate management
      The following example shows how to configure federation using Let’s Encrypt for automatic
      certificate provisioning and renewal:

         apiVersion: operator.openshift.io/v1alpha1
         kind: SpireServer

     metadata:
      name: cluster
     spec:
      trustDomain: cluster1.example.com
      federation:
        bundleEndpoint:
         profile: https_web
         refreshHint: 300
         httpsWeb:
           acme:
             directoryUrl: https://acme-v02.api.letsencrypt.org/directory
             domainName: federation.apps.cluster1.example.com
             email: admin@example.com
             tosAccepted: "true"
        federatesWith:
         - trustDomain: cluster2.example.com
           bundleEndpointUrl: https://federation.apps.cluster2.example.com
           bundleEndpointProfile: https_web
         - trustDomain: cluster3.example.com
           bundleEndpointUrl: https://federation.apps.cluster3.example.com
           bundleEndpointProfile: https_web
        managedRoute: "true"

          The profile field uses https_web profile for Web PKI certificate-based authentication.

          The directoryURL field is used for the production directory. For testing, use staging URL
          https://acme-staging-v02.api.letsencrypt.org/directory

Example 2: Using manual certificate management with cert-manager
  The following example shows how to configure federation using externally managed certificates:

     apiVersion: operator.openshift.io/v1alpha1
     kind: SpireServer
     metadata:
      name: cluster
     spec:
      trustDomain: cluster1.example.com
      federation:
        bundleEndpoint:
         profile: https_web
         refreshHint: 300
         httpsWeb:
           servingCert:
             fileSyncInterval: 86400
             externalSecretRef: spire-server-federation-tls
        federatesWith:
         - trustDomain: cluster2.example.com
           bundleEndpointUrl: https://federation.apps.cluster2.example.com
           bundleEndpointProfile: https_web
         - trustDomain: cluster3.example.com
           bundleEndpointUrl: https://federation.apps.cluster3.example.com
           bundleEndpointProfile: https_web
        managedRoute: "true"

          The fileSyncInterval field checks for certificate updates every 24 hours.

              The externalSecretRef field is the name of the Kubernetes Secret containing tls.crt and
              tls.key

  Example 3: Using https_spiffe profile for SPIRE-to-SPIRE federation
      The following example shows how to configure federation using SPIFFE-based TLS authentication:

         apiVersion: operator.openshift.io/v1alpha1
         kind: SpireServer
         metadata:
          name: cluster
         spec:
          trustDomain: cluster1.example.com
          federation:
            bundleEndpoint:
             profile: https_spiffe
             refreshHint: 300
            federatesWith:
             - trustDomain: cluster2.example.com
               bundleEndpointUrl: https://federation.apps.cluster2.example.com
               bundleEndpointProfile: https_spiffe
               endpointSpiffeId: spiffe://cluster2.example.com/spire/server
             - trustDomain: cluster3.example.com
               bundleEndpointUrl: https://federation.apps.cluster3.example.com
               bundleEndpointProfile: https_spiffe
               endpointSpiffeId: spiffe://cluster3.example.com/spire/server
            managedRoute: "true"

              The profile field uses https_spiffe profile for SPIFFE-based TLS authentication.

              The endpointSiffeId field contains the SPIFFE ID of the remote SPIRE server, required for
              identity validation.

  Example 4: Mixed federation with multiple authentication profiles
      The following example shows a cluster federating with multiple remote clusters using different
      authentication profiles:

         apiVersion: operator.openshift.io/v1alpha1
         kind: SpireServer
         metadata:
          name: cluster
         spec:
          trustDomain: internal-cluster.example.com
          federation:
            bundleEndpoint:
             profile: https_spiffe
             refreshHint: 300
            federatesWith:
             # Internal cluster using SPIFFE TLS
             - trustDomain: dev-cluster.example.com
               bundleEndpointUrl: https://federation.apps.dev-cluster.example.com
               bundleEndpointProfile: https_spiffe
               endpointSpiffeId: spiffe://dev-cluster.example.com/spire/server
             # External partner using Web PKI
             - trustDomain: partner.example.com

           bundleEndpointUrl: https://federation.partner.example.com
           bundleEndpointProfile: https_web
         # Another external partner using Web PKI
         - trustDomain: vendor.example.com
           bundleEndpointUrl: https://spire-federation.vendor.example.com
           bundleEndpointProfile: https_web
        managedRoute: "true"

            The profile field cluster exposes its bundle using https_spiffe profile.

            The bundleEndpointProfile field cluster exposes its bundle using https_spiffe profile.

10.8.3. Configuring SPIRE federation with the https_spiffe profile
The Zero Trust Workload Identity Manager includes SPIRE Federation support, allowing multiple
independent SPIRE deployments to establish trust relationships. This procedure demonstrates how to
configure federation using the https_spiffe profile, which uses SPIFFE-based TLS authentication
between SPIRE servers.

Prerequisites

       You have installed the OpenShift CLI (oc).

       You have installed the Zero Trust Workload Identity Manager on all clusters that will participate
       in the federation.

       You have cluster-admin privileges on all participating clusters.

       You have network connectivity between the clusters you intend to federate.

Procedure

     1. Configure the SpireServer custom resource on each cluster to enable federation with the
        https_spiffe profile. The https_spiffe profile uses SPIFFE-based TLS authentication, where
        SPIRE servers authenticate to each other using their own SPIFFE Verifiable Identity Documents
        (SVIDs).

            apiVersion: operator.openshift.io/v1alpha1
            kind: SpireServer
            metadata:
             name: cluster
            spec:
             trustDomain: cluster1.example.com
             federation:
               bundleEndpoint:
                profile: https_spiffe
                refreshHint: 300
               managedRoute: "true"

            The spec.trustDomain field sets a unique trust domain for each cluster.

            The spec.federation.bundleEnpoint.profile field uses the https_spiffe profile for SPIFFE-
            based TLS authentication.

                 The spec.federation.bundleEndpoint.refreshHint field suggests intervals (in seconds) for
                 remote servers to refresh the trust bundle. Range: 60-3600 seconds.

                 The spec.federation.managedRoute field enables automatic route creation by the
                 Operator.

       2. Apply the configuration changes by running the following command:

             $ oc apply -f spire-server.yaml

       3. Check the status of the SPIRE Server by entering the following command. Wait for the Ready
          status to be returned.

             $ oc get spireserver cluster -w

       4. Verify that the federation route has been created:

             $ oc get route -n zero-trust-workload-identity-manager | grep federation

          Example output

             NAME                 HOST/PORT                        PATH SERVICES      PORT
             TERMINATION
             spire-server-federation federation.apps.cluster1.example.com     spire-server 8443
             passthrough

       5. Fetch the trust bundle from each remote cluster’s federation endpoint:

             $ curl -k https://federation.apps.cluster2.example.com > cluster2-bundle.json

                            NOTE

                            For https_spiffe profile, you might need to use the -k flag if the certificate is not
                            trusted by your system’s CA bundle:

          The response contains the trust bundle in JSON Web Key Set (JWKS) format:

          Example trust bundle

             {
                 "keys": [
                    {
                      "use": "x509-svid",
                      "kty": "RSA",
                      "n": "...",
                      "e": "AQAB",
                      "x5c": ["..."]
                    }
                 ],
                 "spiffe_sequence": 1,
                 "refresh_hint": 300
             }

6. Create ClusterFederatedTrustDomain resources for each remote trust domain.

    a. On Cluster 1, create a resource to federate with Cluster 2:

          apiVersion: spire.spiffe.io/v1alpha1
          kind: ClusterFederatedTrustDomain
          metadata:
           name: federation-to-cluster2
          spec:
           trustDomain: <CLUSTER2_APPS_DOMAIN>
           bundleEndpointURL: https://federation.<CLUSTER2_APPS_DOMAIN>
           bundleEndpointProfile:
             type: https_spiffe
             endpointSPIFFEID: spiffe://<CLUSTER2_APPS_DOMAIN>/spire/server
           className: zero-trust-workload-identity-manager-spire
           trustDomainBundle: |
             {
               "keys": [
                  {
                    "use": "x509-svid",
                    "kty": "RSA",
                    "n": "...",
                    "e": "AQAB",
                    "x5c": ["..."]
                  }
               ],
               "spiffe_sequence": 1
             }

       where

       <CLUSTER2_APPS_DOMAIN>
          Specifies the trust domain of the external cluster you are federating with.
       spec.bundleEndpointProfile.endpointSPIFFEID
          Specifies the SPIFFE ID of the remote SPIRE server. Required for https_spiffe profile to
          validate the remote server’s identity.
       spec.trustDomainBundle
          Specifies the complete trust bundle JSON that you fetched in the previous step.
       spec.className
          Specifies the name of a class to watch CRs for. Spire-controller-manager watches the
          resource only if spec.className is set to zero-trust-workload-identity-manager-
          spire.

7. Apply the ClusterFederatedTrustDomain resource by running the following command:

      $ oc apply -f clusterfederatedtrustdomain.yaml

8. Repeat steps 5-7 on each cluster for every remote cluster it should federate with. For
   bidirectional federation, each cluster needs a ClusterFederatedTrustDomain resource for
   every other cluster.

9. Update the SpireServer resource on each cluster to add the federatesWith configuration:

             apiVersion: operator.openshift.io/v1alpha1
             kind: SpireServer
             metadata:
              name: cluster
             spec:
              trustDomain: cluster1.example.com
              federation:
                bundleEndpoint:
                 profile: https_spiffe
                 refreshHint: 300
                federatesWith:
                 - trustDomain: cluster2.example.com
                   bundleEndpointUrl: https://federation.apps.cluster2.example.com
                   bundleEndpointProfile: https_spiffe
                   endpointSpiffeId: spiffe://cluster2.example.com/spire/server
                 - trustDomain: cluster3.example.com
                   bundleEndpointUrl: https://federation.apps.cluster3.example.com
                   bundleEndpointProfile: https_spiffe
                   endpointSpiffeId: spiffe://cluster3.example.com/spire/server
                managedRoute: "true"

              The spec.federation.federatesWith field lists all remote trust domains this cluster should
              federate with.

      10. Apply the updated configuration by running the following command:

             $ oc apply -f spireserver.yaml

  Verification

       1. Verify that the ClusterFederatedTrustDomain resources have been created by running the
          following command:

             $ oc get clusterfederatedtrustdomains

          Example output

             NAME              TRUST DOMAIN          ENDPOINT URL                           AGE
             cluster2-federation cluster2.example.com https://federation.apps.cluster2.example.com
             5m
             cluster3-federation cluster3.example.com https://federation.apps.cluster3.example.com
             5m

       2. Check the status of a ClusterFederatedTrustDomain to ensure bundle synchronization is
          working by running the following command:

             $ oc describe clusterfederatedtrustdomain cluster2-federation

          Look for successful status conditions indicating that the trust bundle has been synchronized.

       3. Verify that the federation endpoint is accessible by running the following command:

             $ curl https://federation.apps.cluster1.example.com

        You should receive a JSON response containing the trust bundle.

    4. Check the SPIRE Server logs to confirm federation is active by running the following command:

            $ oc logs -n zero-trust-workload-identity-manager \
              statefulset/spire-server -c spire-server --tail=50

        Look for log messages indicating successful bundle synchronization with federated trust
        domains.

10.8.4. Using SPIRE federation with Automatic Certificate Management
Environment protocol
Using SPIRE federation with Automatic Certificate Management Environment (ACME) protocol
provides automatic certificate provisioning from Let’s Encrypt. ACME also enables automatic certificate
renewal before expiration, eliminating manual certificate management overhead.

Prerequisites

        You have installed the Zero Trust Workload Identity Manager on all clusters that will participate
        in the federation.

        You have installed the OpenShift CLI (oc).

        You have cluster-admin privileges on all participating clusters.

        Your federation endpoints must be publicly accessible for Let’s Encrypt HTTP-01 challenge
        validation.

        You have network connectivity between all federated clusters.

Procedure

     1. Configure the SpireServer custom resource on each cluster to enable federation with ACME
        certificate management.
        Create or update your SpireServer resource with the federation configuration:

            apiVersion: operator.openshift.io/v1alpha1
            kind: SpireServer
            metadata:
             name: cluster
            spec:
             trustDomain: cluster1.example.com
             federation:
               bundleEndpoint:
                profile: https_web
                refreshHint: 300
                httpsWeb:
                 acme:
                   directoryUrl: https://acme-v02.api.letsencrypt.org/directory
                   domainName: federation.apps.cluster1.example.com
                   email: admin@example.com
                   tosAccepted: "true"
               managedRoute: "true"

              The spec.trustDomain field sets a unique trust domain for each cluster (for example,
              cluster1.example.com, cluster2.example.com).

              The spec.federation.bundleEndpoint.profile field uses the https_web profile for ACME-
              based certificate management.

              The spec.federation.bundleEndpoint.httpsWeb.acme.directoryUrl field contains the
              Let’s Encrypt production directory URL. For testing, use: https://acme-staging-
              v02.api.letsencrypt.org/directory.

              The spec.federation.bundleEndpoint.httpsWeb.acme.domainName field is the domain
              name where your federation endpoint is accessible. This automatically sets to federation.
              <cluster-apps-domain> if managedRoute is set to "true".

              The spec.federation.bundleEndpoint.httpsWeb.acme.email field is your email address
              for ACME account registration and certificate expiration notifications.

              The spec.federation.bundleEndpoint.httpsWeb.acme.tosAccepted field accepts the
              Let’s Encrypt Terms of Service.

              The spec.federation.managedRoute field enables an automatic route creation by the
              Operator for the federation bundle endpoint.

       2. Apply the configuration to each cluster by running the following command:

             $ oc apply -f spireserver.yaml

       3. Check the status of the SPIRE Server by entering the following command. Wait for the Ready
          status to be returned before proceeding to the next step.

             $ oc get spireserver cluster -w

          Example output

             NAME     STATUS AGE
             cluster Ready 5m

       4. Verify that the federation route has been created by running the following command:

             $ oc get route -n zero-trust-workload-identity-manager | grep federation

          Example output

             NAME                 HOST/PORT                            PATH SERVICES      PORT
             TERMINATION
             spire-server-federation federation.apps.cluster1.example.com         spire-server
             8443 passthrough

       5. On each cluster, fetch the trust bundle from the federation endpoint by running the following
          command:

             $ curl https://federation.apps.cluster1.example.com > cluster1-bundle.json

   The response contains the trust bundle in JSON Web Key Set (JWKS) format:

   Example trust bundle

      {
          "keys": [
             {
               "use": "x509-svid",
               "kty": "RSA",
               "n": "...",
               "e": "AQAB",
               "x5c": ["..."]
             }
          ],
          "spiffe_sequence": 1,
          "refresh_hint": 300
      }

6. Create ClusterFederatedTrustDomain resources to establish federation relationships.

    a. On Cluster 1, create resources to federate with Cluster 2 and Cluster 3:

             apiVersion: spire.spiffe.io/v1alpha1
             kind: ClusterFederatedTrustDomain
             metadata:
               name: cluster2-federation
             spec:
               trustDomain: cluster2.example.com
               bundleEndpointURL: https://federation.apps.cluster2.example.com
               bundleEndpointProfile:
                 type: https_web
               className: zero-trust-workload-identity-manager-spire
               trustDomainBundle: |
                 {
                   "keys": [...],
                   "spiffe_sequence": 1
                 }
             ---
             apiVersion: spire.spiffe.io/v1alpha1
             kind: ClusterFederatedTrustDomain
             metadata:
               name: cluster3-federation
             spec:
               trustDomain: cluster3.example.com
               bundleEndpointURL: https://federation.apps.cluster3.example.com
               bundleEndpointProfile:
                 type: https_web
               className: zero-trust-workload-identity-manager-spire
               trustDomainBundle: |
                 {
                   "keys": [...],
                   "spiffe_sequence": 1
                 }

              The spec.trustDomainBundle field contains the complete trust bundle JSON that you

                  The spec.trustDomainBundle field contains the complete trust bundle JSON that you
                  fetched using curl in step 5.

                  The spec.className field contains the name of a class to watch CRs for. Spire-
                  controller-manager watches the resource only if spec.className is set to zero-trust-
                  workload-identity-manager-spire.

       7. Apply the ClusterFederatedTrustDomain resources by running the following command:

             $ oc apply -f cluster-federated-trust-domains.yaml

       8. Repeat steps 6 and 7 on each cluster to establish bidirectional federation. Each cluster needs
          ClusterFederatedTrustDomain resources for every other cluster it federates with.

       9. Update the SpireServer resource on each cluster to add the federatesWith configuration:

             apiVersion: operator.openshift.io/v1alpha1
             kind: SpireServer
             metadata:
              name: cluster
             spec:
              # ... existing configuration ...
              federation:
                bundleEndpoint:
                 # ... existing bundleEndpoint configuration ...
                federatesWith:
                 - trustDomain: cluster2.example.com
                   bundleEndpointUrl: https://federation.apps.cluster2.example.com
                   bundleEndpointProfile: https_web
                 - trustDomain: cluster3.example.com
                   bundleEndpointUrl: https://federation.apps.cluster3.example.com
                   bundleEndpointProfile: https_web
                managedRoute: "true"

              The spec.federation.federatesWith field lists all remote trust domains this cluster should
              federate with.

      10. Apply the updated configuration by running the following command:

             $ oc apply -f spireserver.yaml

  Verification

       1. Verify that the ClusterFederatedTrustDomain resources have been created by running the
          following command:

             $ oc get clusterfederatedtrustdomains

          Example output

             NAME              TRUST DOMAIN         ENDPOINT URL                           AGE
             cluster2-federation cluster2.example.com https://federation.apps.cluster2.example.com
             5m

            cluster3-federation cluster3.example.com https://federation.apps.cluster3.example.com
            5m

     2. Check the status of a ClusterFederatedTrustDomain to ensure bundle synchronization is
        working by running the following command:

            $ oc describe clusterfederatedtrustdomain cluster2-federation

        Look for Successful status conditions indicating that the trust bundle has been synchronized.

     3. Verify that the federation endpoint is accessible and serving the trust bundle by running the
        following command:

            $ curl https://federation.apps.cluster1.example.com

        You should receive a JSON response containing the trust bundle.

     4. Check the SPIRE Server logs to confirm federation is active by running the following command:

            $ oc logs -n zero-trust-workload-identity-manager deployment/spire-server -c spire-server --
            tail=50

        Look for log messages indicating successful bundle synchronization with federated trust
        domains.

     5. Verify that all SPIRE components are running by running the following command:

            $ oc get pods -n zero-trust-workload-identity-manager

        Example output

            NAME              READY STATUS RESTARTS AGE
            spire-agent-abcde    1/1 Running 0   10m
            spire-server-0     2/2 Running 0   10m

     6. Optional: Test cross-cluster workload authentication by deploying workloads with SPIFFE
        identities on different clusters and verifying they can authenticate to each other using the
        federated trust.

10.8.5. Using SPIRE federation with manual certificate management
You can use SPIRE federation with custom certificate management using cert-manager or other
certificate providers. This approach provides flexibility for organizations that require control over
certificate issuance, support for internal certificate authorities (CAs), or integration with existing
certificate management infrastructure.

Prerequisites

        You have installed the Zero Trust Workload Identity Manager on all clusters that will participate
        in the federation.

        You have installed the OpenShift CLI (oc).

        You have cluster-admin privileges on all participating clusters.

          You have installed the cert-manager Operator for Red Hat OpenShift. For more information,
          see cert-manager Operator for Red Hat OpenShift .

          Your federation endpoints must be publicly accessible for certificate validation.

          You have network connectivity between all federated clusters.

  Procedure

       1. Install the cert-manager Operator on the cluster where you want to use externally managed
          certificates.
          Create a namespace and install the operator:

              apiVersion: v1
              kind: Namespace
              metadata:
                name: cert-manager-operator
              ---
              apiVersion: operators.coreos.com/v1
              kind: OperatorGroup
              metadata:
                name: openshift-cert-manager-operator
                namespace: cert-manager-operator
              spec:
                upgradeStrategy: Default
              ---
              apiVersion: operators.coreos.com/stable-v1
              kind: Subscription
              metadata:
                name: openshift-cert-manager-operator
                namespace: cert-manager-operator
              spec:
                source: redhat-operators
                sourceNamespace: openshift-marketplace
                name: openshift-cert-manager-operator
                channel: stable-v1

       2. Apply the cert-manager installation by running the following command:

              $ oc apply -f cert-manager-install.yaml

       3. Check the status of the cert-manager Operator by entering the following command:

              $ oc get pods -n cert-manager

          All cert-manager pods should be in Running status.

       4. Create an Issuer for certificate provisioning.
          For Let’s Encrypt with HTTP-01 challenge:

              apiVersion: cert-manager.io/v1
              kind: Issuer
              metadata:
               name: letsencrypt-http01

       namespace: zero-trust-workload-identity-manager
      spec:
       acme:
        server: https://acme-v02.api.letsencrypt.org/directory
        privateKeySecretRef:
         name: letsencrypt-account-key
        solvers:
         - http01:
            ingress:
              ingressClassName: openshift-default

   Alternatively, for an internal CA:

      apiVersion: cert-manager.io/v1
      kind: Issuer
      metadata:
       name: internal-ca
       namespace: zero-trust-workload-identity-manager
      spec:
       ca:
         secretName: internal-ca-key-pair

5. Apply the Issuer by running the following command:

      $ oc apply -f issuer.yaml

6. Determine the federation endpoint domain name.
   The federation route follows a predictable naming pattern if managedRoute is set to true. Get
   your cluster’s application domain by running the following command:

      $ CLUSTER_DOMAIN=$(oc get ingresses.config/cluster -o jsonpath='{.spec.domain}')
      $ FEDERATION_DOMAIN="federation.${CLUSTER_DOMAIN}"
      $ echo "Federation domain will be: $FEDERATION_DOMAIN"

   Example output

      Federation domain will be: federation.apps.cluster1.example.com

                  NOTE

                  The federation route is created automatically if managedRoute is set to true
                  when you apply the SpireServer configuration in a later step. The route name is
                  spire-server-federation and the hostname is federation.<cluster-apps-
                  domain>.

7. Create a Certificate resource to request a TLS certificate.
   Use the federation domain determined in the previous step:

      apiVersion: cert-manager.io/v1
      kind: Certificate
      metadata:
       name: spire-server-federation-tls

              namespace: zero-trust-workload-identity-manager
             spec:
              secretName: spire-server-federation-tls
              duration: 2160h
              renewBefore: 360h
              commonName: federation.apps.cluster1.example.com
              dnsNames:
                - federation.apps.cluster1.example.com
              usages:
                - server auth
                - digital signature
                - key encipherment
              issuerRef:
                kind: Issuer
                name: letsencrypt-http01

              The secretName field must match the externalSecretRef value in SpireServer.

              The duration field shows how long a certificate is valid. Certificates are valid for 90 days.

              The renewBefore field shows how many days a certificate must be renewed before it
              expires. Renew a certificate 15 days before expiration.

              The commonName field must be replaced with your actual federation domain from the
              previous step.

              The dnsNames field must match the commonName and the actual route hostname that
              was created.

              The name field must reference the Issuer that was created earlier.

       8. Apply the Certificate resource by running the following command:

             $ oc apply -f certificate.yaml

       9. Monitor the certificate issuance by running the following command:

             $ oc get certificate spire-server-federation-tls \
               -n zero-trust-workload-identity-manager -w

          Example output when ready

             NAME                     READY SECRET                    AGE
             spire-server-federation-tls True spire-server-federation-tls 2m

      10. Create RBAC permissions for the OpenShift Ingress Router to access the certificate secret.
          Create a Role by running the following command:

             $ oc create role secret-reader \
               --verb=get,list,watch \
               --resource=secrets \
               --resource-name=spire-server-federation-tls \
               -n zero-trust-workload-identity-manager

   Create a RoleBinding by running the following command:

       $ oc create rolebinding secret-reader-binding \
         --role=secret-reader \
         --serviceaccount=openshift-ingress:router \
         -n zero-trust-workload-identity-manager

11. Configure the SpireServer custom resource to use manual certificate management.
    Now that the certificate is ready, configure the SpireServer to reference it:

       apiVersion: operator.openshift.io/v1alpha1
       kind: SpireServer
       metadata:
        name: cluster
       spec:
        trustDomain: cluster1.example.com
        federation:
          bundleEndpoint:
           profile: https_web
           refreshHint: 300
           httpsWeb:
            servingCert:
              fileSyncInterval: 86400
              externalSecretRef: spire-server-federation-tls
          managedRoute: "true"

       The profile field must use https_web profile for certificate-based authentication.

       The fileSyncInterval field checks for certificate updates every 24 hours (86400 seconds).
       Range: 3600-7776000 seconds.

       The externalSecretRef field is the name of the secret containing the TLS certificate and
       private key. Must match the certificate secret created in the previous steps.

12. Apply the configuration by running the following command:

       $ oc apply -f spireserver.yaml

13. Wait for the SPIRE Server to be ready:

       $ oc get spireserver cluster -n zero-trust-workload-identity-manager -w

   Wait until the status shows Ready.

14. Verify that the federation route was created by running the following command:

       $ oc get route spire-server-federation -n zero-trust-workload-identity-manager

   Example output

       NAME                 HOST/PORT                       PATH SERVICES      PORT
       TERMINATION
       spire-server-federation federation.apps.cluster1.example.com    spire-server 8443
       reencrypt

          Verify that the route hostname matches the domain name used in your certificate.

      15. Verify that the federation endpoint is accessible by running the following command:

             $ curl https://$(oc get route spire-server-federation \
                -n zero-trust-workload-identity-manager \
                -o jsonpath='{.spec.host}')

          You should receive a JSON response containing the trust bundle.

      16. Fetch the trust bundle from each federation endpoint that you want to federate with.
          For each remote cluster, fetch its trust bundle by running the following commands:

             $ curl https://federation.apps.cluster1.example.com > cluster1-bundle.json
             $ curl https://federation.apps.cluster2.example.com > cluster2-bundle.json

          The trust bundle is in JSON Web Key Set (JWKS) format:

          Example trust bundle

             {
                 "keys": [
                    {
                      "use": "x509-svid",
                      "kty": "RSA",
                      "n": "xGOzB...",
                      "e": "AQAB",
                      "x5c": ["MIIC..."]
                    }
                 ],
                 "spiffe_sequence": 1,
                 "refresh_hint": 300
             }

      17. Create ClusterFederatedTrustDomain resources for each remote trust domain you want to
          federate with:

             apiVersion: spire.spiffe.io/v1alpha1
             kind: ClusterFederatedTrustDomain
             metadata:
              name: cluster1-federation
             spec:
              trustDomain: cluster1.example.com
              bundleEndpointURL: https://federation.apps.cluster1.example.com
              bundleEndpointProfile:
                type: https_web
              className: zero-trust-workload-identity-manager-spire
              trustDomainBundle: |
                {
                  "keys": [
                   {
                     "use": "x509-svid",
                     "kty": "RSA",
                     "n": "xGOzB...",

            "e": "AQAB",
            "x5c": ["MIIC..."]
             }
          ],
          "spiffe_sequence": 1
          }
      ---
      apiVersion: spire.spiffe.io/v1alpha1
      kind: ClusterFederatedTrustDomain
      metadata:
        name: cluster2-federation
      spec:
        trustDomain: cluster2.example.com
        bundleEndpointURL: https://federation.apps.cluster2.example.com
        bundleEndpointProfile:
          type: https_web
        className: zero-trust-workload-identity-manager-spire
        trustDomainBundle: |
          {
            "keys": [...],
            "spiffe_sequence": 1
          }

       The trustDomainBundle field contains the complete trust bundle JSON that you fetched
       in the previous step.

       The spec.className field contains the name of a class to watch CRs for. Spire-controller-
       manager watches the resource only if spec.className is set to zero-trust-workload-
       identity-manager-spire.

18. Apply the ClusterFederatedTrustDomain resources by running the following command:

      $ oc apply -f clusterfederatedtrustdomains.yaml

19. Update the SpireServer resource to add the federatesWith configuration:

      apiVersion: operator.openshift.io/v1alpha1
      kind: SpireServer
      metadata:
       name: cluster
      spec:
       trustDomain: cluster3.example.com
       federation:
         bundleEndpoint:
          profile: https_web
          refreshHint: 300
          httpsWeb:
            servingCert:
              fileSyncInterval: 86400
              externalSecretRef: spire-server-federation-tls
         federatesWith:
          - trustDomain: cluster1.example.com
            bundleEndpointUrl: https://federation.apps.cluster1.example.com
            bundleEndpointProfile: https_web

                  - trustDomain: cluster2.example.com
                    bundleEndpointUrl: https://federation.apps.cluster2.example.com
                    bundleEndpointProfile: https_web
                 managedRoute: "true"

              The federatesWith field lists all remote trust domains this cluster should federate with.

      20. Apply the updated configuration by running the following command:

             $ oc apply -f spireserver.yaml

      21. Repeat steps 1-15 on each cluster that participates in the federation, ensuring that:

              Each cluster has cert-manager installed and configured

              Each cluster has its own certificate created and ready before applying the SpireServer
              configuration

              Each cluster has the RBAC for the ingress router configured

              Each cluster has ClusterFederatedTrustDomain resources for every other cluster it
              federates with

              Each cluster’s SpireServer has the complete federatesWith list

  Verification

       1. Verify that the certificate has been issued successfully by running the following command:

             $ oc get certificate spire-server-federation-tls \
               -n zero-trust-workload-identity-manager

          Example output

             NAME                     READY SECRET                    AGE
             spire-server-federation-tls True spire-server-federation-tls 5m

       2. Check the certificate details and expiration by running the following command:

             $ oc get secret spire-server-federation-tls \
               -n zero-trust-workload-identity-manager \
               -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -noout -dates

          Example output

             notBefore=Dec 16 10:00:00 2025 GMT
             notAfter=Mar 16 10:00:00 2026 GMT

       3. Verify that the RBAC permissions are configured correctly by running the following command:

             $ oc get role,rolebinding -n zero-trust-workload-identity-manager \
               | grep secret-reader

   Example output

      role.rbac.authorization.k8s.io/secret-reader
      rolebinding.rbac.authorization.k8s.io/secret-reader-binding

   Verify the RoleBinding references the correct ServiceAccount by running the following
   command:

      $ oc describe rolebinding secret-reader-binding \
        -n zero-trust-workload-identity-manager

   Example output

      Name:       secret-reader-binding
      Namespace: zero-trust-workload-identity-manager
      Role:
       Kind: Role
       Name: secret-reader
      Subjects:
       Kind        Name Namespace
       ----      ---- ---------
       ServiceAccount router openshift-ingress

4. Verify that the ClusterFederatedTrustDomain resources have been created by running the
   following command:

      $ oc get clusterfederatedtrustdomains

   Example output

      NAME              TRUST DOMAIN          ENDPOINT URL                           AGE
      cluster1-federation cluster1.example.com https://federation.apps.cluster1.example.com
      5m
      cluster2-federation cluster2.example.com https://federation.apps.cluster2.example.com
      5m

5. Check the status of a ClusterFederatedTrustDomain to ensure bundle synchronization is
   working by running the following command:

      $ oc describe clusterfederatedtrustdomain cluster1-federation

   Look for successful status conditions indicating that the trust bundle has been synchronized.

6. Verify that the federation endpoint is accessible and using the correct certificate by running the
   following command:

      $ curl -v https://$(oc get route spire-server-federation \
         -n zero-trust-workload-identity-manager \
         -o jsonpath='{.spec.host}')

   In the output, verify that the certificate presented is issued by your configured CA (Let’s
   Encrypt or internal CA).

       7. Check the SPIRE Server logs to confirm that by running the following command:

               Federation is active with remote trust domains

               Trust bundles are being synchronized

               The bundle endpoint is serving correctly

                  $ oc logs -n zero-trust-workload-identity-manager \
                    statefulset/spire-server -c spire-server --tail=100

               Look for log messages indicating successful federation bundle synchronization.

       8. Verify that all SPIRE components are running by running the following command:

              $ oc get pods -n zero-trust-workload-identity-manager

            Example output

              NAME                            READY STATUS RESTARTS AGE
              spire-agent-abc123                  1/1 Running 0   10m
              spire-server-0                   2/2 Running 0    10m

       9. Optional: Test cross-cluster workload authentication by deploying workloads with SPIFFE
          identities on different clusters and verifying they can authenticate to each other using the
          federated trust.

  10.8.6. Federation configuration field reference
  This reference provides detailed information about all configuration fields available for SPIRE federation
  in the SpireServer custom resource. Use this reference when customizing your federation setup.

  Top-level federation fields

    Field                  Type         Require     Default               Description
                                        d

    federation.bundle      object       Yes         N/A                   Configuration for this cluster’s
    Endpoint                                                              federation endpoint that exposes
                                                                          the trust bundle to remote
                                                                          clusters.

    federation.federat     array        No          []                    List of remote trust domains to
    esWith                                                                federate with.

    federation.manag       string       No          "true"                Enable or disable automatic
    edRoute                                                               OpenShift Route creation. Set to
                                                                          "true" for operator-managed
                                                                          routes or "false" for manual
                                                                          route management.

  bundleEndpoint configuration fields

 Field                Type       Require     Default           Description
                                 d

 federation.bundle     string    Yes         https_spiffe      Authentication profile for the
 Endpoint.profile      (enum)                                  bundle endpoint. Valid values:
                                                               https_spiffe or https_web.
                                                               This value is immutable after
                                                               initial configuration.

 federation.bundle     integer   No          300               Suggested interval (in seconds)
 Endpoint.refreshH                                             for remote servers to refresh the
 int                                                           trust bundle. Valid range: 60-
                                                               3600.

 federation.bundle     object    Conditio    N/A               Required when profile is
 Endpoint.httpsWe                nal                           https_web. Contains certificate
 b                                                             configuration.

httpsWeb configuration fields

 Field                Type       Require     Default           Description
                                 d

 federation.bundle     object    Conditio    N/A               ACME configuration for
 Endpoint.httpsWe                nal                           automatic certificate
 b.acme                                                        management. Mutually exclusive
                                                               with servingCert.

 federation.bundle     object    Conditio    N/A               Manual certificate configuration.
 Endpoint.httpsWe                nal                           Mutually exclusive with acme.
 b.servingCert

ACME configuration fields

 Field                Type       Require     Default           Description
                                 d

 federation.bundle     string    Yes         N/A               ACME directory URL. For Let’s
 Endpoint.httpsWe                                              Encrypt production:
 b.acme.directoryU                                             https://acme-
 rl                                                            v02.api.letsencrypt.org/direc
                                                               tory. For staging: https://acme-
                                                               staging-
                                                               v02.api.letsencrypt.org/direc
                                                               tory

    Field                 Type         Require    Default   Description
                                       d

    federation.bundle      string      Yes        N/A       Fully qualified domain name for
    Endpoint.httpsWe                                        the certificate. Typically the
    b.acme.domainNa                                         federation endpoint hostname.
    me

    federation.bundle      string      Yes        N/A       Email address for ACME account
    Endpoint.httpsWe                                        registration and certificate
    b.acme.email                                            expiration notifications.

    federation.bundle      string      No         "false"   Accept the ACME provider’s
    Endpoint.httpsWe                                        Terms of Service. Must be "true"
    b.acme.tosAccept                                        to obtain certificates.
    ed

  servingCert configuration fields

    Field                 Type         Require    Default   Description
                                       d

    federation.bundle      integer     No         86400     Interval (in seconds) to check for
    Endpoint.httpsWe                                        certificate updates. Valid range:
    b.servingCert.file                                      3600-7776000 (1 hour to 90
    SyncInterval                                            days).

    federation.bundle      string      Yes        N/A       Name of the Kubernetes Secret
    Endpoint.httpsWe                                        containing the TLS certificate
    b.servingCert.exte                                      (tls.crt) and private key (tls.key)
    rnalSecretRef                                           for the federation route.

  federatesWith configuration fields

    Field                 Type         Require    Default   Description
                                       d

    federation.federat     string      Yes        N/A       Trust domain name of the remote
    esWith[].trustDom                                       SPIRE deployment (for example,
    ain                                                     cluster2.example.com).

    federation.federat     string      Yes        N/A       HTTPS URL of the remote
    esWith[].bundleEn                                       federation endpoint (for example,
    dpointUrl                                               https://federation.apps.clust
                                                            er2.example.com).

 Field                   Type       Require     Default               Description
                                    d

 federation.federat      string     Yes         N/A                    Authentication profile of the
 esWith[].bundleEn       (enum)                                        remote endpoint. Valid values:
 dpointProfile                                                         https_spiffe or https_web.

 federation.federat      string     Conditio    N/A                    SPIFFE ID of the remote SPIRE
 esWith[].endpoint                  nal                                server (for example,
 SpiffeId                                                              spiffe://cluster2.example.co
                                                                       m/spire/server). Required when
                                                                       bundleEndpointProfile is
                                                                       https_spiffe.

Field validation rules
   The following validation rules are enforced by the Operator:

           Profile immutability: The bundleEndpoint.profile field cannot be changed after initial
           configuration. Changing it requires deleting and recreating the SpireServer resource (re-
           installation of the system).

           Mutual exclusivity: Within httpsWeb, only one of acme or servingCert can be specified.

           Conditional requirements: When profile is https_web, the httpsWeb object must be present
           with either acme or servingCert configured.

           SPIFFE ID requirement: When bundleEndpointProfile is https_spiffe in the federatesWith
           list, the endpointSpiffeId field is required.

           Array limits: The federatesWith array supports a maximum of 50 entries.

           Numeric ranges:

               refreshHint: 60-3600 seconds

               fileSyncInterval: 3600-7776000 seconds

10.9. ENABLING CREATE-ONLY MODE FOR THE ZERO TRUST
WORKLOAD IDENTITY MANAGER
To pause Operator reconciliation, enable create-only mode by setting an environment variable in the
subscription object. By setting this value, you can perform manual configurations or debug the Operator
without the controller overwriting your changes.

The following scenarios are examples of when the create-only mode might be of use:

Manual Customization Required: You need to customize operator-managed resources (ConfigMaps,
Deployments, DaemonSets, etc.) with specific configurations that differ from the operator’s defaults

Day 2 Operations: After initial deployment, you want to prevent the operator from overwriting their
manual changes during subsequent reconciliation cycles

  Configuration Drift Prevention: You want to maintain control over certain resource configurations
  while still benefiting from the operator’s lifecycle management

  10.9.1. Pausing Operator reconciliation
  Pause reconciliation of the operands by enabling create-only mode. This setting prevents the Operator
  from automatically reverting your manual changes to the desired state. You can enable this mode by
  updating the Operator’s subscription object.

                  IMPORTANT

                  When create-only mode is disabled, the Operator overwrites the resources if any
                  conflicts exist.

  Prerequisites

          You have installed Zero Trust Workload Identity Manager on your machine.

          You have installed the SPIRE Servers, Agents, SPIFFE Container Storage Interface (CSI), and an
          OpenID Connect (OIDC) Discovery Provider and are in running status.

  Procedure

          To pause reconciling the operands resources managed by the Operator, add the environment
          variable CREATE_ONLY_MODE: true in the subscription object by running the following
          command:

              $ oc -n $OPERATOR_NAMESPACE patch subscription openshift-zero-trust-workload-
              identity-manager --type='merge' -p '{"spec":{"config":{"env":
              [{"name":"CREATE_ONLY_MODE","value":"true"}]}}}'

  Verification

          Check the status of the SpireServer resource to confirm that the create-only mode is active.
          The status must be true and the reason must be CreateOnlyModeEnabled.

              $ oc get SpireServer cluster -o yaml

  The following is an example that confirms that the 'create-only' mode is active.

      status:
       conditions:
       - lastTransitionTime: "2025-12-23T11:36:58Z"
         message: All components are ready
         reason: Ready
         status: "True"
         type: Ready
       - lastTransitionTime: "2025-12-23T11:36:58Z"
         message: All operand CRs are ready
         reason: Ready
         status: "True"
         type: OperandsAvailable
       - lastTransitionTime: "2025-12-23T11:36:58Z"

     message: create-only mode enabled
     reason: CreateOnlyModeEnabled
     status: "True"
     type: CreateOnlyMode

                IMPORTANT

                The Operator updates the upgradeable condition to false in the operatorCondition
                resource. You might not be able to upgrade the Operator when in create-only mode.

10.9.2. Resuming Operator reconciliation by annotation
To resume Operator reconciliation after manual configuration or debugging, disable the create-only
mode. This allows the controller to resume managing resources and applying the desired state. You can
disable this mode by setting the environment variable in the subscription object.

Prerequisites

        You have enabled create-only mode on the Zero Trust Workload Identity Manager.

        You have completed your manual configuration or debugging tasks.

Procedure

        To restart reconciling the Operator-managed resources, add the environment variable
        CREATE_ONLY_MODE: false in the subscription object by running the following command:

            $ oc -n $OPERATOR_NAMESPACE patch subscription openshift-zero-trust-workload-
            identity-manager --type='merge' -p '{"spec":{"config":{"env":
            [{"name":"CREATE_ONLY_MODE","value":"false"}]}}}'

Verification

        Check the status of the SpireServer resource to confirm that create-only mode is disabled by
        running the following command:

            $ oc get SpireServer cluster -o yaml

        Example output

            status:
             conditions:
             - lastTransitionTime: "2025-12-23T11:40:00Z"
               message: create-only mode disabled
               reason: CreateOnlyModeDisabled
               status: "False"
               type: CreateOnlyMode

10.10. MONITORING ZERO TRUST WORKLOAD IDENTITY MANAGER

You can configure OpenShift Monitoring to collect these metrics by using the Prometheus Operator

  You can configure OpenShift Monitoring to collect these metrics by using the Prometheus Operator
  format. By default, the SPIRE Server and SPIRE Agent components of the Zero Trust Workload Identity
  Manager emit metrics.

  10.10.1. Enabling user workload monitoring
  Enable user workload monitoring to track metrics for your user-defined projects. Configuring this
  feature allows you to observe application performance and helps you maintain the health of your
  services.

  Prerequisites

          You have access to the cluster as a user with the cluster-admin cluster role.

  Procedure

       1. Create the cluster-monitoring-config.yaml file to define and configure the ConfigMap:

              apiVersion: v1
              kind: ConfigMap
              metadata:
               name: cluster-monitoring-config
               namespace: openshift-monitoring
              data:
               config.yaml: |
                 enableUserWorkload: true

       2. Apply the ConfigMap by running the following command:

              $ oc apply -f cluster-monitoring-config.yaml

  Verification

          Verify that the monitoring components for user workloads are running in the openshift-user-
          workload-monitoring namespace:

              $ oc -n openshift-user-workload-monitoring get pod

          Example output

              NAME                        READY STATUS RESTARTS AGE
              prometheus-operator-6cb6bd9588-dtzxq 2/2 Running 0     50s
              prometheus-user-workload-0        6/6 Running 0    48s
              prometheus-user-workload-1        6/6 Running 0    48s
              thanos-ruler-user-workload-0     4/4 Running 0    42s
              thanos-ruler-user-workload-1     4/4 Running 0    42s

  The status of the pods such as prometheus-operator, prometheus-user-workload, and thanos-ruler-
  user-workload must be Running.

  Additional resources

          Setting up metrics collection for user-defined projects

10.10.2. Configuring metrics collection for SPIRE Server by using a ServiceMonitor
To collect custom metrics from the SPIRE Server, create a ServiceMonitor custom resource (CR). This
configuration enables the Prometheus Operator to scrape metrics from the default endpoint, which
helps you monitor your SPIRE deployment.

The SPIRE Server operand exposes metrics by default on port 9402 at the /metrics endpoint. You can
configure metrics collection for the SPIRE Server by creating a ServiceMonitor custom resource (CR)
that enables the Prometheus Operator to collect custom metrics.

Prerequisites

       You have access to the cluster as a user with the cluster-admin cluster role.

       You have installed the Zero Trust Workload Identity Manager.

       You have deployed the SPIRE Server operand in the cluster.

       You have enabled the user workload monitoring.

Procedure

     1. Create the ServiceMonitor CR:

        a. Create the YAML file that defines the ServiceMonitor CR:

            Example servicemonitor-spire-server file

                apiVersion: monitoring.coreos.com/v1
                kind: ServiceMonitor
                metadata:
                labels:
                  app.kubernetes.io/name: server
                  app.kubernetes.io/instance: spire
                name: spire-server-metrics
                namespace: zero-trust-workload-identity-manager
                spec:
                endpoints:
                - port: metrics
                  interval: 30s
                  path: /metrics
                selector:
                  matchLabels:
                    app.kubernetes.io/name: server
                    app.kubernetes.io/instance: spire
                namespaceSelector:
                  matchNames:
                  - zero-trust-workload-identity-manager

        b. Create the ServiceMonitor CR by running the following command:

                $ oc create -f servicemonitor-spire-server.yaml

            After the ServiceMonitor CR is created, the user workload Prometheus instance begins

              After the ServiceMonitor CR is created, the user workload Prometheus instance begins
              metrics collection from the SPIRE Server. The collected metrics are labeled with
              job="spire-server".

  Verification

       1. In the OpenShift Container Platform web console, navigate to Observe → Targets.

       2. In the Label filter field, enter the following label to filter the metrics targets:

              $ service=zero-trust-workload-identity-manager-metrics-service

       3. Confirm that the Status column shows Up for the spire-server-metrics entry.

  Additional resources

          Configuring user workload monitoring

  10.10.3. Configuring metrics collection for SPIRE Agent by using a Service Monitor
  Configure metrics collection for the SPIRE Agent by creating a ServiceMonitor custom resource (CR).
  This enables the Prometheus Operator to collect custom metrics that the SPIRE Agent exposes on the
  default port.

  Prerequisites

          You have access to the cluster as a user with the cluster-admin cluster role.

          You have installed the Zero Trust Workload Identity Manager.

          You have deployed the SPIRE Agent operand in the cluster.

          You have enabled the user workload monitoring.

  Procedure

       1. Create the ServiceMonitor CR:

           a. Create the YAML file that defines the ServiceMonitor CR:

              Example servicemonitor-spire-agent.yaml file

                  apiVersion: monitoring.coreos.com/v1
                  kind: ServiceMonitor
                  metadata:
                   labels:
                     app.kubernetes.io/name: agent
                     app.kubernetes.io/instance: spire
                   name: spire-agent-metrics
                   namespace: zero-trust-workload-identity-manager
                  spec:
                   endpoints:
                   - port: metrics
                     interval: 30s

                  path: /metrics
                 selector:
                  matchLabels:
                    app.kubernetes.io/name: agent
                    app.kubernetes.io/instance: spire
                 namespaceSelector:
                  matchNames:
                  - zero-trust-workload-identity-manager

         b. Create the ServiceMonitor CR by running the following command:

                $ oc create -f servicemonitor-spire-agent.yaml

            After the ServiceMonitor CR is created, the user workload Prometheus instance begins
            metrics collection from the SPIRE Agent. The collected metrics are labeled with job="spire-
            agent".

Verification

     1. In the OpenShift Container Platform web console, navigate to Observe → Targets.

     2. In the Label filter field, enter the following label to filter the metrics targets:

            $ service=spire-agent

     3. Confirm that the Status column shows Up for the spire-agent-metrics entry.

10.10.4. Configuring metrics collection for the Operator by using a ServiceMonitor
The Zero Trust Workload Identity Manager exposes metrics by default on port 8443 at the /metrics
service endpoint. You can configure metrics collection for the Operator by creating a ServiceMonitor
custom resource (CR) that enables the Prometheus Operator to collect custom metrics. For more
information, see "Configuring user workload monitoring".

The SPIRE Server operand exposes metrics by default on port 9402 at the /metrics endpoint. You can
configure metrics collection for the SPIRE Server by creating a ServiceMonitor custom resource (CR)
that enables the Prometheus Operator to collect custom metrics.

Prerequisites

        You have access to the cluster as a user with the cluster-admin cluster role.

        You have installed the Zero Trust Workload Identity Manager.

        You have enabled the user workload monitoring.

Procedure

     1. Configure the Operator to use HTTP or HTTPS protocols for the metrics server.

         a. Update the subscription object for Zero Trust Workload Identity Manager to configure the
            HTTP protocol by running the following command:

                $ oc -n zero-trust-workload-identity-manager patch subscription zero-trust-workload-

                 identity-manager-subscription --type='merge' -p '{"spec":{"config":{"env":
                 [{"name":"METRICS_BIND_ADDRESS","value":":8080"}, {"name":
                 "METRICS_SECURE", "value": "false"}]}}}'

           b. Verify the Zero Trust Workload Identity Manager pod is redeployed and that the configured
              values for METRICS_BIND_ADDRESS and METRICS_SECURE is updated by running the
              following command:

                 $ oc set env --list deployment/zero-trust-workload-identity-manager-controller-manager -
                 n zero-trust-workload-identity-manager | grep -e METRICS_BIND_ADDRESS -e
                 METRICS_SECURE -e container

              Example output

                 deployments/zero-trust-workload-identity-manager-controller-manager, container
                 manager
                 METRICS_BIND_ADDRESS=:8080
                 METRICS_SECURE=false

       2. Create the Secret resource with kubernetes.io/service-account.name annotation to inject the
          token required for authenticating with the metrics server.

           a. Create the secret-zero-trust-workload-identity-manager.yaml YAML file:

                 apiVersion: v1
                 kind: Secret
                 metadata:
                  labels:
                    name: zero-trust-workload-identity-manager
                  name: zero-trust-workload-identity-manager-metrics-auth
                  namespace: zero-trust-workload-identity-manager
                  annotations:
                    kubernetes.io/service-account.name: zero-trust-workload-identity-manager-controller-
                 manager
                 type: kubernetes.io/service-account-token

           b. Create the Secret resource by running the following command:

                 $ oc apply -f secret-zero-trust-workload-identity-manager.yaml

       3. Create the ClusterRoleBinding resource required for granting permissions to access the
          metrics.

           a. Create the clusterrolebinding-zero-trust-workload-identity-manager.yaml YAML file:

                 apiVersion: rbac.authorization.k8s.io/v1
                 kind: ClusterRoleBinding
                 metadata:
                  labels:
                    name: zero-trust-workload-identity-manager
                  name: zero-trust-workload-identity-manager-allow-metrics-access
                 roleRef:
                  apiGroup: rbac.authorization.k8s.io
                  kind: ClusterRole

           name: zero-trust-workload-identity-manager-metrics-reader
          subjects:
          - kind: ServiceAccount
            name: zero-trust-workload-identity-manager-controller-manager
            namespace: zero-trust-workload-identity-manager

    b. Create the ClusterRoleBinding resource by running the following command:

          $ oc apply -f clusterrolebinding-zero-trust-workload-identity-manager.yaml

4. Create the following ServiceMonitor CR if the metrics server is configured to use http.

    a. Create the servicemonitor-zero-trust-workload-identity-manager-http.yaml YAML file:

          apiVersion: monitoring.coreos.com/v1
          kind: ServiceMonitor
          metadata:
           labels:
             name: zero-trust-workload-identity-manager
           name: zero-trust-workload-identity-manager-metrics-monitor
           namespace: zero-trust-workload-identity-manager
          spec:
           endpoints:
             - authorization:
                 credentials:
                   name: zero-trust-workload-identity-manager-metrics-auth
                   key: token
                 type: Bearer
               interval: 60s
               path: /metrics
               port: metrics-http
               scheme: http
               scrapeTimeout: 30s
           namespaceSelector:
             matchNames:
               - zero-trust-workload-identity-manager
           selector:
             matchLabels:
               name: zero-trust-workload-identity-manager

    b. Create the ServiceMonitor CR by running the following command:

          $ oc apply -f servicemonitor-zero-trust-workload-identity-manager-http.yaml

5. Create the following ServiceMonitor CR if the metrics server is configured to use https.

    a. Create the servicemonitor-zero-trust-workload-identity-manager-https.yaml YAML file:

          apiVersion: monitoring.coreos.com/v1
          kind: ServiceMonitor
          metadata:
           labels:
             name: zero-trust-workload-identity-manager
           name: zero-trust-workload-identity-manager-metrics-monitor
           namespace: zero-trust-workload-identity-manager

                  spec:
                   endpoints:
                    - authorization:
                        credentials:
                          name: zero-trust-workload-identity-manager-metrics-auth
                          key: token
                        type: Bearer
                      interval: 60s
                      path: /metrics
                      port: metrics-https
                      scheme: https
                      scrapeTimeout: 30s
                      tlsConfig:
                        ca:
                          configMap:
                           name: openshift-service-ca.crt
                           key: service-ca.crt
                        serverName: zero-trust-workload-identity-manager-metrics-service.zero-trust-
                  workload-identity-manager.svc.cluster.local
                   namespaceSelector:
                    matchNames:
                      - zero-trust-workload-identity-manager
                   selector:
                    matchLabels:
                      name: zero-trust-workload-identity-manager

           b. Create the ServiceMonitor CR by running the following command:

                  $ oc apply -f servicemonitor-zero-trust-workload-identity-manager-https.yaml

              After the ServiceMonitor CR is created, the user workload Prometheus instance begins
              metrics collection from the SPIRE Server. The collected metrics are labeled with job="zero-
              trust-workload-identity-manager-metrics-service".

  Verification

       1. In the OpenShift Container Platform web console, navigate to Observe → Targets.

       2. In the Label filter field, enter the following label to filter the metrics targets:

             $ service=zero-trust-workload-identity-manager-metrics-service

       3. Confirm that the Status column shows Up for the zero-trust-workload-identity-manager
          entry.

  Additional resources

          Configuring user workload monitoring

  10.10.5. Querying metrics for the Zero Trust Workload Identity Manager
  As a cluster administrator, or as a user with view access to all namespaces, you can query SPIRE Agent
  and SPIRE Server metrics by using the OpenShift Container Platform web console or the command line.
  The query retrieves all the metrics collected from the SPIRE components that match the specified job

labels.

Prerequisites

          You have access to the cluster as a user with the cluster-admin role.

          You have installed the Zero Trust Workload Identity Manager.

          You have deployed the SPIRE Server and SPIRE Agent operands in the cluster.

          You have enabled monitoring and metrics collection by creating ServiceMonitor objects.

Procedure

      1. In the OpenShift Container Platform web console, navigate to Observe → Metrics.

     2. In the query field, enter the following PromQL expression to query SPIRE Server metrics:

             {job="spire-server"}

     3. In the query field, enter the following PromQL expression to query SPIRE Agent metrics.

             {job="spire-agent"}

Additional resources

          Accessing metrics

10.10.6. Zero Trust Workload Identity Manager monitoring available metrics
Monitor the health and performance of Zero Trust Workload Identity Manager components by reviewing
exposed metrics. This reference describes controller, certificate, and runtime metrics that help you
maintain system health and troubleshoot errors.

The Zero Trust Workload Identity Manager exposes the following metrics:

Controller runtime metrics

             controller_runtime_active_workers: Number of currently used workers per controller

             controller_runtime_max_concurrent_reconciles: Maximum number of concurrent
             reconciles per controller

             controller_runtime_reconcile_errors_total: Total number of reconciliation errors per
             controller

             controller_runtime_reconcile_time_seconds: Length of time per reconciliation per
             controller

             controller_runtime_reconcile_total: Total number of reconciliations per controller

Certificate watcher metrics

             certwatcher_read_certificate_errors_total: Total number of certificate read errors

              certwatcher_read_certificate_total: Total number of certificates read

  Go runtime metrics
      Standard Go runtime metrics including:

              go_gc_duration_seconds: Garbage collection duration

              go_goroutines: Number of goroutines

              go_memstats_*: Memory statistics

              process_*: Process statistics

  Custom Operator metrics
      The Operator also exposes custom metrics related to:

              SPIRE Server status and health

              SPIRE Agent deployment status

              SPIFFE CSI Driver status

              OIDC Discovery Provider status

              Workload identity management operations

  10.11. UNINSTALLING THE ZERO TRUST WORKLOAD IDENTITY
  MANAGER
  To remove the Zero Trust Workload Identity Manager from OpenShift Container Platform, uninstall the
  Operator and delete its related resources. This process removes the component from your cluster.

  10.11.1. Uninstalling the Zero Trust Workload Identity Manager
  To remove the Zero Trust Workload Identity Manager from your cluster, uninstall the Operator using the
  web console. This helps you clean up resources and delete the service from your environment.

  Prerequisites

          You have access to the cluster with cluster-admin privileges.

          You have access to the OpenShift Container Platform web console.

          The Zero Trust Workload Identity Manager is installed.

  Procedure

        1. Log in to the OpenShift Container Platform web console.

       2. Uninstall the Zero Trust Workload Identity Manager.

           a. Go to Ecosystem → Installed Operators.

           b. Click the Options menu next to the Zero Trust Workload Identity Manager entry, and

        b. Click the Options menu next to the Zero Trust Workload Identity Manager entry, and
           then click Uninstall Operator.

        c. In the confirmation dialog, click Uninstall.

10.11.2. Uninstalling Zero Trust Workload Identity Manager resources by using the
CLI
Remove Zero Trust Workload Identity Manager resources from your cluster using the CLI. This deletes
the remaining operands and definitions to help ensure a clean environment after you uninstall the
product.

Prerequisites

       You have access to the cluster with cluster-admin privileges.

Procedure

     1. Uninstall the operands by running each of the following commands:

        a. Delete the SpireOIDCDiscoveryProvider cluster by running the following command:

                $ oc delete SpireOIDCDiscoveryProvider cluster

        b. Delete the SpiffeCSIDriver cluster by running the following command:

                $ oc delete SpiffeCSIDriver cluster -l=app.kubernetes.io/name=zero-trust-workload-
                identity-manager

        c. Delete the SpireAgent cluster by running the following command:

                $ oc delete SpireAgent cluster

        d. Delete the SpireServer cluster by running the following command:

                $ oc delete SpireServer cluster

        e. Delete the ZeroTrustWorkloadIdentityManager cluster by running the following
           command:

                $ oc delete ZeroTrustWorkloadIdentityManager cluster

         f. Delete the persistent volume claim (PVC) by running the following command:

                $ oc delete pvc -l=app.kubernetes.io/name=spire-server

        g. Delete the service by running the following command:

                $ oc delete service -l=app.kubernetes.io/name=zero-trust-workload-identity-manager -n
                zero-trust-workload-identity-manager

        h. Delete the namespace by running the following command:

                 $ oc delete ns zero-trust-workload-identity-manager

            i. Delete the cluster role by running the following command:

                 $ oc delete clusterrole -l=app.kubernetes.io/name=zero-trust-workload-identity-manager

            j. Delete the admission wehhook configuration by running the following command:

                 $ oc delete validatingwebhookconfigurations -l=app.kubernetes.io/name=zero-trust-
                 workload-identity-manager

       2. Delete the custom resource definitions (CRDs) by running each of the following commands:

           a. Delete the SPIRE Server CRD by running the following command:

                 $ oc delete crd spireservers.operator.openshift.io

           b. Delete the SPIRE Agent CRD by running the following command:

                 $ oc delete crd spireagents.operator.openshift.io

           c. Delete the SPIFFEE CSI Drivers CRD by running the following command:

                 $ oc delete crd spiffecsidrivers.operator.openshift.io

           d. Delete the SPIRE OIDC Discovery Provider CRD by running the following command:

                 $ oc delete crd spireoidcdiscoveryproviders.operator.openshift.io

           e. Delete the SPIRE and SPIFFE cluster federated trust domains CRD by running the
              following command:

                 $ oc delete crd clusterfederatedtrustdomains.spire.spiffe.io

           f. Delete the cluster SPIFFE IDs CRD by running the following command:

                 $ oc delete crd clusterspiffeids.spire.spiffe.io

           g. Delete the SPIRE and SPIFFE cluster static entries CRD by running the following command:

                 $ oc delete crd clusterstaticentries.spire.spiffe.io

           h. Delete the Zero Trust Workload Identity Manager CRD by running the following command:

                 $ oc delete crd zerotrustworkloadidentitymanagers.operator.openshift.io

  Verification
  To verify that the resources have been deleted, replace each oc delete command with oc get, and then
  run the command. If no resources are returned, the deletion was successful.

```
