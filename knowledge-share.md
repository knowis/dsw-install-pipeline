# DSW Install Pipeline Knowledge Share Notes

## Motivation

IBM betreibt eine Abteilung namens TechZone. Aufgabe von TechZone ist es soweit ich das verstehe, IBM intern einen Kiosk zur Verfügung zu stellen, über den sich Mitarbeiter mit lauffähigen Installationen von allen (?) IBM Produkten versorgen können (zu Lern-, Demo- und Proof-of-Concept-Zwecken, nicht für den Produktiv Einsatz). Wir gehen davon aus, dass dies eine niedrigschwellige Möglichkeit bietet, sich mit einem IBM Produkt auseinaderzusetzen und ggf. die Bereitschaft von IBM Mitarbeitern (und Verkäufern) erhöht, unser Produkt mit Kunden ins Gespräch zu bringen. Ziel des dsw-install-pipeline Projekts ist es also eine automatisierte Installation von DSW zu entwicklen, die im Kontext des TechZone Kiosks dann einfach per Knopfdruck eine direkt nutzbare DSW Instanz bereitstellt.

Möglicher weiterer Nutzen des Projekts wäre eine beschleunigte Standard Installation von CSW/DSW Umgebungen (wie wir sie für Consors und Cajamar in der Vergangenheit von Hand installiert haben).

## Architektur & Implementierung

Laut unseren Ansprechpartnern bei IBM gibt es innerhalb von TechZone zwei unterstütze Wege für die Installation von Software über den TechZone Kiosk - Ansible und Tekton Pipelines. Wir haben uns für Tekton Pipelines entschieden, da wir einerseits erst spät von Ansible erfahren haben und andererseits Das DevOps Loop Team, zu dem DSW innerhalb der IBM gehört, ebenfalls Tekton Pipelines verwendet.

Der grobe Prozess für eine solche Kiosk Installation verläuft ungefähr so:

1. Der IBM  Mitarbeiter besucht den TechZone Kiosk, sucht nach dem Produkt welches ihn interessiert und klickt dann dort auf einen Button der sinngemäß mit "Neue Instanz von diesem Produkt für mich provisionieren" beschriftet ist.
2. Daraufhin wird über eine von TechZone erstellte und gepflegte Automation ein neuer OpenShift Cluster (auf VMs in der IBM Cloud (?)) erstellt
3. Sobald der Cluster lauffähig und online ist, werden auf dem Cluster einige TechZone spezifische Konfigurationen erstellt und der Tekton Pipeline Operator installiert
4. Als nächstes wird die für das gewählte Produkt passende Tekton Pipeline auf dem neuen Cluster "applied" und dadurch zur Ausführung gebracht.
5. Nach erfolgreicher Ausführung wird der bestellende Nutzer benachrichtigt und vermutlich (wie das funktioniert weiß ich noch nicht) in Kenntnis über wichtige Endpunkte, Zugangsdaten etc gesetzt.



## Tekton Basics

[Tekton](https://tekton.dev) ist eine Software, die ähnlich wie jenkins, GitHub Actions oder GitLab CI/CD dazu dient, eine Reihe von Schritten auszuführen, gewöhnlich um aus Software Quellcode eine ausführbare Datei und weitere Artefakte zu erstellen. Im Unterschied zu den geannten Alternativen, werden die Schritte allerdings direkt auf einem OpenShift/Kubernetes Cluster zur Ausführung gebracht.

Konzeptionell gibt es durchaus Ähnlichkeiten zwischen tekton und GitLab CI/CD pipelines. Beide sind nicht wirklich beschränkt auf das Builden von Software und bringen demnach auch keine fertigen Rezepte oder Bausteine dafür mit. Vielmehr dienen sie der Beschreibung eines Prozesses, der unterschiedliche Software Aktivitäten in einer definierten Folge orchestriert und es ermöglicht, dass die Produkte oder Artefakte dieser Aktivitäten von späteren Aktivitäten als Input genutzt werden können.
Eine weitere Ähnlichkeit (zumindest was die knowis interne Verwendung von GitLab Pipelines angeht) ist, dass beide Ansätze Container verwenden, um die einzelnen Aktivitäten durchzuführen. 

Während GitLab Pipelines über die Datei .gitlab-ci.yaml in einem GitLab Projekt definiert, werden Pipelines in tekton über kubernetes Resourcen definiert. Dazu werden bei der Installation von Tekton auf einem Cluster unter anderem folgende Custom Resource Definitions neu eingeführt und vom Tekton Operator überwacht (reconciled):

- Task
- TaskRun
- Pipeline
- PipelineRun

Die grundlegenste Resource ist dabei Task (abgesehen vielleicht von StepAction, welches ich hier aber nicht weiter behandle). Ein Task beschreibt eine Aktivität innerhalb einer Pipeline. Eine solche Aktivität hat einerseits Input Parameter und kann Results produzieren, zudem werden die eigentlich duchzuführenden Tätigkeiten als eine folge von Schritten (steps) in einem Task beschrieben. Zusätzlich kann einem Task persistenter Speicher (workspace) zugewiesen werden, damit die Schritte in einem Task ein gemeinsames Filesystem zum Austausch von Daten verwenden können. Dieser Speicher kann darüberhinaus auch im Rahmen einer Pipeline geteilt werdenm, die mehrere Tasks zusammenfasst.

Eine Task Resource ist wie eine Klassendefintion, erst durch Instanziierung und Parametrierung (durch das Erstellen einer TaskRun Resource) kommt ein Tassk zur Ausführung. Durch die TaskRun Resource werden die Eingabe Parameter des Task definiert und ggf. der persistente Speicher für die konkrete Task Instanz zugewiesen.

Für das Ausführen einer Task Instanz wird dabei durch den Tekton Operator ein Pod angelegt. Alle Schritte eines Tasks werden als Container im selben Pod ausgeführt. Jeder Schritt ist dabei im Task als eine Kombination aus einem Container Image und einem (Shell-)Skript definiert. Jeder Schritt kann also beliebige Aktivitäten ausführen, die nur durch die Fähigkeiten des Skript Autors und die Wahl des Container Images beschränkt sind. Schritte, die in einem Task definiert sind werden in der Reihenfolge ihrer Definition in der Task Resource ausgeführt. Die Container im Pod werden dabei im Allgemeinen mit den Rechten des ServiceAccounts 'Pipeline' ausgeführt, so dass ein Skript in einem Schritt eines Tasks mit dem Cluster auf dem der Task/Pod ausgeführt wird interagieren kann und bspw. `kubectl` oder `oc` Befehle ausführen kann. Es gilt also zu beaachten, über welche RoleBindings des verwendete ServiceAccount verfügt.

Mehrere Tasks können von einer Pipeline Resource composed werden. Dabei können Results eines Tasks als Eingabe Parameter eines weiteren Tasks verwendet werden. Tekton stellt dann sicher, dass bei der Ausführung der Pipeline Tasks erst dann ausgeführt werden, wenn die Result produzierenden Tasks erfolgreich beendet sind. Eine Pipeline Resource ist wie Task ähnlich einer Klassendefinition  - um eine Pipeline auszuführen benötigt es zusätzlich zur Pipeline Resource eine PipelineRun Resource. Erst wenn diese angelegt ist und (wie TaskRun) die Pipeline Instanz parametriert, wird de Pipeline durchgeführt. Dabei wird für jeden Task der Pipeline ein Pod angelegt und in diesem Pod werden dann alle Schritte, die im Task definiert sind (jeder in seinem eigenen Container) ausgeführt.

Um die Schritte eines Tasks ausführen zu können, müssen natürlich geeignete Container Images vorliegen. Diese müssen die in den Schritt Skripten verwendeten commands natürlich enthalten. 

## Die DSW Install Pipeline

### Annahmen (bestätigte und unbestätigte) zu Tekton Pipeline in TechZone

- Die Installationspipeline muss alle Tasks inline haben. Das ist zwar weniger schön als Tasks zu referenzieren ist aber eine Anforderung seitens TechZone
- Der ServiceAccount mit/unter dem die Pipeline Tasks arbeiten hat die Cluster Admin Rolle und kann auch zum Installieren von Operatoren u.ä., das über den Namespace in dem die Pipeline ausgeführt wird hinaus geht, verwendet werden
- Die Namespaces in die die Pipeline Software installiert, sollten von der Pipeline neu angelegt werden
- Das Problem, wie die Pull Secrets zu konfigurieren sind, ohne, dass sie direkt in der Pipelinedefinition hinterlegt sind, ist von IBM gelöst und wir verwenden diese Lösung
- Es gibt von IBM bereitgestellte Tasks, die wir verwenden dürfen (bisher nicht verwendet), die auf einem TechZone Cluster vorinstalliert sind
- Die Pipeline Quellen werden final in IBMs GitHub hinterlegt und von dort aus dem TechZone Kiosk aufgerufen

### Status (16. Februar 2026)

Die Pipeline besteht derzeit aus 9 Tasks

![DSW Install Pipeline (OpenShift Console)](/dsw-install-pipeline.png)

#### Pipeline ToC
1. [bootstrap](tekton/00-pipeline-ibm-devops-solution-workbench-install.yaml?ref_type=heads#L34)


Der Task, der das DSW helm chart installiert ist zwar gecodet aber noch nicht final getestet, da da engültige helm chart mit embedded FerretDB (anstatt MongoDB) noch nicht verfügbar ist. Zudem haben ich mich - nach Absprache mit Sales - auf die Design Time Komponenten konzentriert und die Runtime (Deployment Target, ArgoCD) derzeit noch nicht angelegt. Auch die Schema Registry fehlt noch (sollte aber nicht zu aufwändig sein, da wir jetzt wissen, dass wir den Operator verwenden können und die grundsätzliche Vorgehensweise im Schritt install-gitlab bereits einmal durchexerziert ist).

Derzeit verwenden alle Tasks und Schritte das gleiche Container Image zur Ausführung, dessen Definition ebenfalls in diesem Repo enthalten ist und welches wichtige commands wie oc, helm und jq enthält und auf Red Hats UBI 9 Base Image beruht. Siehe [k8stools](/container-images/k8stools).

Sobald das helm chart verfügbar und getestet ist, ist bei derzeitigem Stand nach Ausführen der Pipeline folgendes verfügbar:
- Keycloak installiert und 2 Nutzer in Keycloak angelegt (dswdev und dswadmin)
- Obligatorische Konfigurations Secrets angelegt
- DSW installiert
- GitLab installiert und obige Nutzer registriert
- Gruppe in GitLab angelegt und Nutzer auf dieser Gruppe berechtigt

Was offensichtlich noch fehlt:
- Konfiguration der Gitlab Tokens im Designer für beide Nutzer
- Konfiguration Asset Catalog
- Konfiguration Component Repository
- Konfiguration Schema Registry (und Installation Schema Registry)
- Konfiguration ArgoCD
- Konfiguration Deployment Target

Vor allem aber müssen noch Inhalte in GitLab importiert werden und Workspaces für mindestens den Developer Nutzer, die diese Inhalte leicht zugänglich machen konfiguriert werden. Hier sollte es möglich sein, Konzepte aus unserer Onboarding Automation zu verwenden (wenn auch nur die Konzepte).
