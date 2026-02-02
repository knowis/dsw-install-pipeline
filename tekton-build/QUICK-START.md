# Quick Start Guide - Tekton Task Scripts

This guide provides quick examples for using the inline and extract task scripts.

## Prerequisites

```bash
pip install PyYAML
chmod +x *.sh
```

## Common Workflows

### 1. Extract Tasks from an Inlined Pipeline

**When to use:** You have a pipeline with inline `taskSpec` definitions and want to modularize it.

```bash
# Extract all tasks to separate files
./extract-tasks.sh my-pipeline.yaml

# Or extract to a specific directory
./extract-tasks.sh my-pipeline.yaml ./tasks
```

**Result:**
- `my-pipeline-extracted.yaml` - Modified pipeline with `taskRef` references
- Individual task files: `task-name-1.yaml`, `task-name-2.yaml`, etc.

### 2. Inline Tasks into a Pipeline

**When to use:** You want a self-contained pipeline file for deployment.

```bash
# Inline all tasks
./inline-tasks.sh my-pipeline.yaml

# Or specify output file
./inline-tasks.sh my-pipeline.yaml deployment-pipeline.yaml
```

**Result:**
- `my-pipeline-inlined.yaml` - Self-contained pipeline with all tasks embedded

### 3. Round-Trip: Extract then Inline

Test that your pipeline can be modularized and reassembled:

```bash
# 1. Extract tasks
./extract-tasks.sh original-pipeline.yaml

# 2. Inline them back
./inline-tasks.sh original-pipeline-extracted.yaml roundtrip-pipeline.yaml

# 3. Verify they're functionally equivalent
diff original-pipeline.yaml roundtrip-pipeline.yaml
```

## Real-World Examples

### Example 1: Modularize a Large Pipeline

```bash
# Start with a large inlined pipeline
./extract-tasks.sh 00-pipeline-ibm-devops-solution-workbench-install.yaml

# This creates:
# - bootstrap.yaml
# - create-install-namespaces.yaml
# - install-keycloak.yaml
# - create-mandatory-config.yaml
# - install-dsw.yaml
# - 00-pipeline-ibm-devops-solution-workbench-install-extracted.yaml
```

Now you can:
- Edit individual tasks without touching the pipeline
- Reuse tasks across multiple pipelines
- Version control tasks separately

### Example 2: Create Deployment Artifact

```bash
# Start with modular pipeline + task files
./inline-tasks.sh sample-pipeline.yaml production-ready.yaml

# Deploy the single file
kubectl apply -f production-ready.yaml
```

### Example 3: Extract to Organized Directory

```bash
# Extract all tasks to a dedicated folder
./extract-tasks.sh my-pipeline.yaml ./extracted-tasks/

# Result structure:
# extracted-tasks/
# ├── my-pipeline-extracted.yaml
# ├── task-1.yaml
# ├── task-2.yaml
# └── task-3.yaml
```

## Quick Reference Table

| Task | Command | Output |
|------|---------|--------|
| Extract tasks | `./extract-tasks.sh pipeline.yaml` | `pipeline-extracted.yaml` + task files |
| Inline tasks | `./inline-tasks.sh pipeline.yaml` | `pipeline-inlined.yaml` |
| Extract to dir | `./extract-tasks.sh pipeline.yaml ./dir` | Files in `./dir` |
| Custom output | `./inline-tasks.sh pipeline.yaml out.yaml` | `out.yaml` |

## Verify YAML Validity

```bash
# Check pipeline
python3 -c "import yaml; yaml.safe_load(open('pipeline.yaml'))"

# Check all YAML files in directory
for f in *.yaml; do 
    python3 -c "import yaml; yaml.safe_load(open('$f'))" && echo "✓ $f" || echo "✗ $f"
done
```

## Tips

1. **Original files are never modified** - Both scripts create new files
2. **Task naming** - Task files are named using lowercase with hyphens: `my-task.yaml`
3. **Scripts preserve formatting** - Multi-line scripts use `|` literal block style
4. **Multiple tasks** - Both scripts handle multiple tasks automatically
5. **Dependencies** - Only requires Python 3 and PyYAML

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `python3: command not found` | Install Python 3 |
| `No module named 'yaml'` | Run `pip install PyYAML` |
| `Permission denied` | Run `chmod +x *.sh` |
| Task file not found | Ensure task files match `taskRef` names |

## Integration with Tekton

```bash
# Extract tasks for modular development
./extract-tasks.sh my-pipeline.yaml

# Apply individual tasks
kubectl apply -f bootstrap.yaml
kubectl apply -f create-namespaces.yaml

# Apply the pipeline
kubectl apply -f my-pipeline-extracted.yaml

# --- OR ---

# Inline for single-file deployment
./inline-tasks.sh my-pipeline.yaml deployment.yaml
kubectl apply -f deployment.yaml
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check `sample-pipeline.yaml` and `sample-task.yaml` for examples
- Run the scripts on your own pipelines!