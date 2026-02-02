# Tekton Pipeline Task Scripts

This directory contains build scripts for managing Tekton task definitions in pipelines.

## Scripts

1. **inline-tasks.py** - Inlines task definitions into a pipeline file
2. **extract-tasks.py** - Extracts inlined tasks from a pipeline into separate task files

---

## Task Inliner (inline-tasks.py)

### Purpose

When deploying Tekton pipelines, you may want to have a single, self-contained pipeline file that doesn't rely on external task definitions. This script automates the process of inlining tasks into your pipeline, making it easier to deploy and version control your pipelines as standalone artifacts.

## Prerequisites

- Python 3.6 or higher
- PyYAML library

### Installing PyYAML

```bash
pip install PyYAML
```

Or if you're using a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install PyYAML
```

### Usage

#### Using the Python script directly:

```bash
python3 inline-tasks.py <pipeline-file> [output-file]
```

#### Using the shell wrapper:

```bash
chmod +x inline-tasks.sh
./inline-tasks.sh <pipeline-file> [output-file]
```

The shell wrapper performs dependency checks before running the Python script.

#### Arguments

- `<pipeline-file>`: Path to the pipeline YAML file (required)
- `[output-file]`: Path for the output file (optional)
  - If not specified, defaults to `<pipeline-file-name>-inlined.yaml`

### Examples

1. Inline tasks from `sample-pipeline.yaml` to `sample-pipeline-inlined.yaml`:
   ```bash
   python3 inline-tasks.py sample-pipeline.yaml
   ```

2. Inline tasks and specify custom output file:
   ```bash
   python3 inline-tasks.py sample-pipeline.yaml my-inlined-pipeline.yaml
   ```

3. Using the shell wrapper:
   ```bash
   ./inline-tasks.sh sample-pipeline.yaml production-pipeline.yaml
   ```

### How It Works

1. The script reads the specified pipeline YAML file
2. For each task in the pipeline that has a `taskRef` property:
   - Extracts the task reference name (supports both string and object format)
   - Looks for a file named `<taskRef-value>.yaml` in the same directory as the pipeline
   - Loads the task definition and extracts its `spec` section
   - Replaces the `taskRef` property with a `taskSpec` property containing the task's spec
3. Writes the modified pipeline to the output file with proper YAML formatting
4. **Original files remain untouched**

### File Structure

The script expects task files to be named according to their task reference. For example:

- If `taskRef: sample-task`, it looks for `sample-task.yaml`
- If `taskRef: my-custom-task`, it looks for `my-custom-task.yaml`
- If the direct match is not found, it also tries `task-<taskRef-value>.yaml`

### Example Directory Structure

```
tekton-build/
├── sample-pipeline.yaml
├── sample-task.yaml
├── another-task.yaml
├── inline-tasks.py
├── inline-tasks.sh
└── README.md
```

### YAML Formatting Features

The script preserves proper YAML formatting, including:

- **Literal block scalars** (`|`) for multi-line strings like bash scripts
- Proper indentation throughout the document
- Original structure and ordering where possible
- No unnecessary escaping or quote wrapping

This ensures the inlined pipeline remains readable and maintains the same behavior as the original pipeline with separate task definitions.

### Multiple Tasks

The script automatically handles pipelines with multiple tasks. All tasks with `taskRef` properties will be inlined in a single pass:

```yaml
# Before
spec:
  tasks:
    - name: task-one
      taskRef: sample-task
    - name: task-two
      taskRef: another-task

# After
spec:
  tasks:
    - name: task-one
      taskSpec:
        # full spec from sample-task.yaml
    - name: task-two
      taskSpec:
        # full spec from another-task.yaml
```

### Troubleshooting

#### "Task file not found" warning

Make sure the task YAML files are in the same directory as the pipeline file and are named correctly according to the taskRef value.

#### "No spec found in task file" warning

Verify that your task YAML files have a valid `spec:` section.

#### PyYAML import errors

Ensure PyYAML is installed in your Python environment:
```bash
python3 -c "import yaml" && echo "PyYAML is installed" || echo "PyYAML is NOT installed"
```

### Output

The script provides informative output during execution:

```
Reading pipeline from: sample-pipeline.yaml
Inlining task 'sample-task' from sample-task.yaml
Writing inlined pipeline to: sample-pipeline-inlined.yaml
Done!
```

---

## Task Extractor (extract-tasks.py)

### Purpose

When refactoring or modularizing Tekton pipelines, you may want to extract inlined task definitions (taskSpec) into separate, reusable task files. This script automates the process of extracting tasks from a pipeline and replacing them with taskRef references, making it easier to maintain and reuse tasks across multiple pipelines.

### Usage

#### Using the Python script directly:

```bash
python3 extract-tasks.py <pipeline-file> [output-dir]
```

#### Using the shell wrapper:

```bash
chmod +x extract-tasks.sh
./extract-tasks.sh <pipeline-file> [output-dir]
```

The shell wrapper performs dependency checks before running the Python script.

#### Arguments

- `<pipeline-file>`: Path to the pipeline YAML file with inlined tasks (required)
- `[output-dir]`: Directory where extracted task files should be saved (optional)
  - If not specified, defaults to the same directory as the pipeline file
  - The modified pipeline will be saved as `<pipeline-file-name>-extracted.yaml`

### Examples

1. Extract tasks from a pipeline to the same directory:
   ```bash
   python3 extract-tasks.py 00-pipeline-ibm-devops-solution-workbench-install.yaml
   ```
   This will create:
   - Individual task files: `bootstrap.yaml`, `create-install-namespaces.yaml`, etc.
   - Modified pipeline: `00-pipeline-ibm-devops-solution-workbench-install-extracted.yaml`

2. Extract tasks to a specific directory:
   ```bash
   python3 extract-tasks.py sample-pipeline-inlined.yaml ./tasks
   ```

3. Using the shell wrapper:
   ```bash
   ./extract-tasks.sh my-pipeline.yaml ./extracted-tasks
   ```

### How It Works

1. The script reads the specified pipeline YAML file
2. For each task in the pipeline that has a `taskSpec` property:
   - Extracts the task name and sanitizes it for use as a filename
   - Creates a complete Task definition with proper metadata and apiVersion
   - Saves the task to a file named `<task-name>.yaml`
   - Replaces the `taskSpec` property with a `taskRef` property pointing to the task name
3. Writes the modified pipeline to `<pipeline-name>-extracted.yaml`
4. **Original files remain untouched**

### Task Naming

Task files are named based on the task's `name` property in the pipeline:
- Task names are converted to lowercase
- Spaces and underscores are replaced with hyphens
- Examples:
  - Task `bootstrap` → `bootstrap.yaml`
  - Task `create-install-namespaces` → `create-install-namespaces.yaml`
  - Task `Install DSW` → `install-dsw.yaml`

### Output Structure

After extraction, you'll have:

```
directory/
├── original-pipeline.yaml              # Untouched original
├── original-pipeline-extracted.yaml    # Modified pipeline with taskRef
├── bootstrap.yaml                      # Extracted task
├── create-install-namespaces.yaml     # Extracted task
├── install-keycloak.yaml              # Extracted task
└── ...                                 # More extracted tasks
```

### YAML Formatting Features

The script preserves proper YAML formatting, including:

- **Literal block scalars** (`|`) for multi-line strings like bash scripts
- Proper indentation throughout documents
- Original structure and ordering where possible
- No unnecessary escaping or quote wrapping

This ensures both the extracted tasks and modified pipeline remain readable and maintain the same behavior as the original inlined pipeline.

### Output Example

The script provides informative output during execution:

```
Reading pipeline from: 00-pipeline-ibm-devops-solution-workbench-install.yaml
Output directory: tekton-build

Extracting task 'bootstrap'...
  Writing task to: bootstrap.yaml
Extracting task 'create-install-namespaces'...
  Writing task to: create-install-namespaces.yaml
Extracting task 'install-keycloak'...
  Writing task to: install-keycloak.yaml

Writing modified pipeline to: 00-pipeline-ibm-devops-solution-workbench-install-extracted.yaml

Summary:
  Extracted 5 task(s):
    - bootstrap.yaml
    - create-install-namespaces.yaml
    - install-keycloak.yaml
    - create-mandatory-config.yaml
    - install-dsw.yaml
  Modified pipeline: 00-pipeline-ibm-devops-solution-workbench-install-extracted.yaml

Done!
```

---

## Common Troubleshooting

### PyYAML not installed

Both scripts require PyYAML. Install it with:
```bash
pip install PyYAML
```

### Permission denied when running shell scripts

Make the scripts executable:
```bash
chmod +x inline-tasks.sh extract-tasks.sh
```

### Invalid YAML output

If the output YAML is not valid, verify that your input file is valid YAML:
```bash
python3 -c "import yaml; yaml.safe_load(open('your-file.yaml'))"
```
