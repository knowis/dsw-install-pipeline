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

run-pipeline:
    oc apply -f tekton/00-pipeline-ibm-devops-solution-workbench-install.yaml
    oc create -f tekton/00-pipeline-run-ibm-devops-solution-workbench-install.yaml
