#set shell := ["zsh", "-cu"]


default:
    just --list

cleanup:
    #!/usr/bin/env sh
    # delete tekton resources
    oc delete task,pipeline,pipelinerun,taskrun --all

    # delete all helm releases
    helm uninstall $(helm list -q -n techzone-dsw-support) -n techzone-dsw-support
    helm uninstall $(helm list -q -n techzone-dsw-tools) -n techzone-dsw-tools

    oc delete persistentvolumeclaim,route --all -n techzone-dsw-tools
    oc delete persistentvolumeclaim,route --all -n techzone-dsw-support
    oc delete secret --field-selector type=Opaque -n techzone-dsw-tools
    oc delete secret --field-selector type=Opaque -n techzone-dsw-support

    oc delete namespace -l app.kubernetes.io/created-by=dsw-techzone-tekton-installer

run-pipeline:
    oc apply -f tekton/ibm-cloud-secrets-manager-get.yaml
    oc apply -f tekton/00-pipeline-ibm-devops-solution-workbench-install.yaml
    oc create -f tekton/00-pipeline-run-ibm-devops-solution-workbench-install.yaml
