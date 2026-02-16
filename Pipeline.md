# Pipeline - Flow of tasks

## Intro
The DSW install pipeline focuses on installing the design-time parts of DSW first with as little user interaction as possible. Its aim is to start the pipeline and then after 30 minutes be able to login to Solution Designer with some test user credentials and create projects, draw diagrams etc.

## IBM information and resources specific to TechZone installation automation

- The service account the pipeline runs under has cluster-admin privileges
- It is considered best practice to create new namespace(s) for the software to be installed in
- There are tokens to create pull-secrets in IBM Cloud Secrets Manager and there is a [predefined task](https://github.ibm.com/itz-content/deployer-tekton-tasks/blob/main/tasks/general-purpose/ibmcloud-secrets-manager-get.yaml) to obtain this token
- There are some predefined tekton tasks for various activities required by those TechZone tekton pipelines. See [GitHub public](https://github.com/itz-public/deployer-tekton-tasks) and [IBM GitHub](https://github.ibm.com/itz-content/deployer-tekton-tasks/tree/main). These should be present on the cluster a pipeline is run on.
- There are ways to provide parameters to a pipeline that can be configured in the TechZone catalog (details unclear yet)
- All pipeline sources should be hosted on IBM GitHub
- All tasks (apart from the tasks defined in the deployer-tekton-tasks repo) need to be inlined in the pipeline resource as only that resource is synced to the cluster


## Flow

- create namespace(s) ✔️
- establish some pipeline global facts like cluster url (script) ✔️
- create pull-secret(s) using IBM vault/key-manager 🚀 
- install keycloak (script & helm) ✔️
- install schema registry Apicurio (helm?)
- create mandatory configuration secrets (script) ✔️
- install dsw (script & helm) 🚀
- install gitea/forgejo/gitlab ✔️
- Create user, configure user and provide output about how and where to login in the pipeline 🚀
- Configure DSW: configure git provider, component repository(?), schema registry(?)
- fork, clone resources/assets needed for a user to get started easily
- Display / return information about what was created: user names and passwords, important http endpoints, version information
