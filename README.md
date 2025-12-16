# DSW Install Pipeline

This repository contains all required tekton resources needed to have tekton install a functional instance of DevOps Solution Workbench on an OpenShift Cluster (>= v4.18) that has tekton (tekton Pipeline >= v1.0.0) or OpenShift Pipelines (>=v1.19.0) installed.

## Task container image

The container-image folder contains dockerfiles to build container images that are suitable for usage in the pipeline steps.

### Image: k8tools

A dockerfile to build a container images with helm, oc and kukbectl installed. Build with `podman build -t mytag:0.0.1 -f container-images/k8stools .`. You can use p-podman.knowisag.local to run x86_64 arch builds. Versions of helm and oc binaries can be controlled by build-args used like this: `podman build -t mytag:0.0.1 -f container-images/k8stools --build-arg HELM_VERSION=3.19.2 --build-arg OPENSHIFT_VERSION=4.18.27  .`

## Pipelines and Tasks

The installation process should be as modular as possible so that during development individual steps can be tested in isolation. This means that each natural installation unit should be implemented using a task and then a main pipeline should be defined that orchestrates all the tasks in the correct order.

The high-level flow is this (See also [Mandatory Config](https://docs-devops-solution-workbench.knowis.net/5.1/docs/installing-upgrading/configuration/mandatory-config/) and [Installation Protocol](https://gitlab.knowis.net/tech-sales-enablement/tech-zone/techxchange102025/-/blob/main/install-protocol.md)) - lines marked with (?) are optional at the moment:
- Install MongoDB (might be superseded by embedded FerretDB soon)
- Install Keykloack
  - step 1: Install PostgreSQL instance
  - step 2: Install Keycloak operator
  - step 3: Install Keycloak resource
- Install kafka (?)
- Install schema registry apicurio (?)
  - step 1: Install PostgreSQL instance
  - step 2: Install apicurio operator
  - step 3: Install Apicurio resource
- Install ArgoCD (?)
- Create configuration secrets
  - mongodb / document-db binding secret
  - truststore secret with all relevant (private) CAs
  - iam secret
  - master key secret
  - schema registry secret (?)
  - argocd secret (?)
  - message service (kafka) secret (?)
- Install DSW using helm chart (once available)
- Create and configure a deployment target namespace
- Create at least one user
- Install GitLab (?)
  - Configure it with keycloak authentication
  - Give user Owner rights to one group
  - Create token for user and configure it in Solution Designer
- Configure Solution Designer with access to sample projects (?)
  - Create a workspace for user that groups those sample projects
