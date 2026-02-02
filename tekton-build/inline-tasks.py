#!/usr/bin/env python3
"""
Tekton Pipeline Task Inliner

This script inlines Tekton task definitions into a pipeline file by replacing
taskRef properties with taskSpec properties containing the full task specification.

Usage:
    python inline-tasks.py <pipeline-file> [output-file]

If output-file is not specified, it will default to <pipeline-file>-inlined.yaml
"""

import sys
import os
import yaml
from pathlib import Path


# Custom YAML Dumper to preserve literal block scalars for multi-line strings
class LiteralBlockDumper(yaml.SafeDumper):
    pass


def literal_block_representer(dumper, data):
    """Represent multi-line strings using literal block scalar style (|)."""
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)


# Register the custom representer for strings
LiteralBlockDumper.add_representer(str, literal_block_representer)


def load_yaml(filepath):
    """Load a YAML file and return its content."""
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)


def save_yaml(data, filepath):
    """Save data to a YAML file with proper formatting."""
    with open(filepath, 'w') as f:
        yaml.dump(data, f, Dumper=LiteralBlockDumper, default_flow_style=False, sort_keys=False, indent=2)


def find_task_file(task_ref_name, base_dir):
    """
    Find the task file based on the taskRef name.
    Looks for <task_ref_name>.yaml in the same directory.
    """
    task_file = base_dir / f"{task_ref_name}.yaml"
    if task_file.exists():
        return task_file
    
    # Also try with 'task-' prefix if direct match not found
    task_file_alt = base_dir / f"task-{task_ref_name}.yaml"
    if task_file_alt.exists():
        return task_file_alt
    
    return None


def inline_tasks(pipeline_data, base_dir):
    """
    Process pipeline data and inline all taskRef references with taskSpec.
    
    Args:
        pipeline_data: Parsed pipeline YAML data
        base_dir: Directory containing the pipeline and task files
    
    Returns:
        Modified pipeline data with inlined tasks
    """
    if 'spec' not in pipeline_data or 'tasks' not in pipeline_data['spec']:
        print("Warning: No tasks found in pipeline spec")
        return pipeline_data
    
    tasks = pipeline_data['spec']['tasks']
    
    for task in tasks:
        if 'taskRef' in task:
            task_ref = task['taskRef']
            
            # taskRef can be a string or an object with 'name' property
            if isinstance(task_ref, str):
                task_ref_name = task_ref
            elif isinstance(task_ref, dict) and 'name' in task_ref:
                task_ref_name = task_ref['name']
            else:
                print(f"Warning: Unrecognized taskRef format in task '{task.get('name', 'unknown')}'")
                continue
            
            # Find the task file
            task_file = find_task_file(task_ref_name, base_dir)
            
            if not task_file:
                print(f"Warning: Task file not found for taskRef '{task_ref_name}'")
                continue
            
            # Load the task definition
            print(f"Inlining task '{task_ref_name}' from {task_file.name}")
            task_data = load_yaml(task_file)
            
            if 'spec' not in task_data:
                print(f"Warning: No spec found in task file {task_file.name}")
                continue
            
            # Replace taskRef with taskSpec
            del task['taskRef']
            task['taskSpec'] = task_data['spec']
    
    return pipeline_data


def main():
    if len(sys.argv) < 2:
        print("Usage: python inline-tasks.py <pipeline-file> [output-file]")
        print("\nExample:")
        print("  python inline-tasks.py sample-pipeline.yaml")
        print("  python inline-tasks.py sample-pipeline.yaml output-pipeline.yaml")
        sys.exit(1)
    
    pipeline_file = Path(sys.argv[1])
    
    if not pipeline_file.exists():
        print(f"Error: Pipeline file '{pipeline_file}' not found")
        sys.exit(1)
    
    # Determine output file
    if len(sys.argv) >= 3:
        output_file = Path(sys.argv[2])
    else:
        output_file = pipeline_file.parent / f"{pipeline_file.stem}-inlined.yaml"
    
    # Get the base directory for finding task files
    base_dir = pipeline_file.parent if pipeline_file.parent != Path('.') else Path.cwd()
    
    print(f"Reading pipeline from: {pipeline_file}")
    pipeline_data = load_yaml(pipeline_file)
    
    # Inline the tasks
    modified_pipeline = inline_tasks(pipeline_data, base_dir)
    
    # Save the result
    print(f"Writing inlined pipeline to: {output_file}")
    save_yaml(modified_pipeline, output_file)
    
    print("Done!")


if __name__ == "__main__":
    main()