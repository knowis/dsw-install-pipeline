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

runtask:
    oc apply -f tekton/task-install-keycloak.yaml
    oc apply -f tekton/taskrun-keycloak-install.yaml
