# Pipeline - Flow of tasks

## Intro
The DSW install pipeline focuses on installing the design-time parts of DSW first with as little user interaction as possible. Its aim is to start the pipeline and then after 30 minutes be able to login to Solution Designer with some test user credentials and create projects, draw diagrams etc.

## Flow

- establish some pipeline global facts like cluster url (script) ✔️
- install keycloak (script & helm) ✔️
- install schema registry Apicurio (helm?)
- create mandatory configuration secrets (script)
- install dsw (script & helm)
- install gitea/forgejo
- Create user, configure user and provide output about how and where to login in the pipeline
