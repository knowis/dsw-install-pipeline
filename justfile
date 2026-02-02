#set shell := ["zsh", "-cu"]


default:
    just --list

cleanup:
    #!/usr/bin/env sh
    # delete tekton resources
    oc delete task,pipeline,pipelinerun,taskrun --all

    # delete all helm releases
    helm uninstall $(helm list -q)

    oc delete persistentvolumeclaim,route --all
    oc delete secret --field-selector type=Opaque

runtask:
    oc apply -f tekton/02-task-install-keycloak.yaml
    oc apply -f tekton/02-task-run-keycloak-install.yaml

run-pipeline:
    oc apply -f tekton/02-task-install-keycloak.yaml
    oc apply -f tekton/04-task-create-mandatory-config.yaml
    oc apply -f tekton/05-task-install-dsw.yaml
    oc apply -f tekton/00-pipeline-ibm-devops-solution-workbench-install.yaml
    oc create -f tekton/00-pipeline-run-ibm-devops-solution-workbench-install.yaml
