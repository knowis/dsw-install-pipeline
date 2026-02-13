#!/usr/bin/env python3
"""
Tekton Pipeline Task Extractor

This script extracts inlined task definitions (taskSpec) from a pipeline file
and creates separate task files, replacing taskSpec with taskRef references.

Usage:
    python extract-tasks.py <pipeline-file> [output-dir]

If output-dir is not specified, it will default to the same directory as the pipeline file.
The modified pipeline will be saved as <pipeline-file>-extracted.yaml
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


def sanitize_task_name(task_name):
    """
    Sanitize task name to be used as a filename.
    Replaces spaces and special characters with hyphens.
    """
    return task_name.lower().replace(' ', '-').replace('_', '-')


def create_task_definition(task_name, task_spec):
    """
    Create a complete Task definition from a taskSpec.
    
    Args:
        task_name: Name of the task
        task_spec: The taskSpec content
    
    Returns:
        Dictionary containing a complete Task definition
    """
    task_definition = {
        'apiVersion': 'tekton.dev/v1',
        'kind': 'Task',
        'metadata': {
            'name': task_name
        },
        'spec': task_spec
    }
    
    return task_definition


def extract_tasks(pipeline_data, output_dir):
    """
    Process pipeline data and extract all taskSpec definitions to separate files.
    
    Args:
        pipeline_data: Parsed pipeline YAML data
        output_dir: Directory where task files should be saved
    
    Returns:
        Modified pipeline data with taskRef instead of taskSpec
    """
    if 'spec' not in pipeline_data or 'tasks' not in pipeline_data['spec']:
        print("Warning: No tasks found in pipeline spec")
        return pipeline_data, []
    
    tasks = pipeline_data['spec']['tasks']
    extracted_files = []
    
    for task in tasks:
        if 'taskSpec' in task:
            task_name = task.get('name', 'unnamed-task')
            sanitized_name = sanitize_task_name(task_name)
            
            print(f"Extracting task '{task_name}'...")
            
            # Get the taskSpec
            task_spec = task['taskSpec']
            
            # Create the task definition
            task_definition = create_task_definition(sanitized_name, task_spec)
            
            # Save to file
            task_filename = f"{sanitized_name}.yaml"
            task_filepath = output_dir / task_filename
            
            print(f"  Writing task to: {task_filename}")
            save_yaml(task_definition, task_filepath)
            extracted_files.append(task_filename)
            
            # Replace taskSpec with taskRef in the pipeline
            del task['taskSpec']
            task['taskRef'] = sanitized_name
    
    return pipeline_data, extracted_files


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract-tasks.py <pipeline-file> [output-dir]")
        print("\nExample:")
        print("  python extract-tasks.py sample-pipeline-inlined.yaml")
        print("  python extract-tasks.py sample-pipeline-inlined.yaml ./tasks")
        sys.exit(1)
    
    pipeline_file = Path(sys.argv[1])
    
    if not pipeline_file.exists():
        print(f"Error: Pipeline file '{pipeline_file}' not found")
        sys.exit(1)
    
    # Determine output directory
    if len(sys.argv) >= 3:
        output_dir = Path(sys.argv[2])
    else:
        output_dir = pipeline_file.parent if pipeline_file.parent != Path('.') else Path.cwd()
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine output pipeline file
    output_pipeline = output_dir / f"{pipeline_file.stem}-extracted.yaml"
    
    print(f"Reading pipeline from: {pipeline_file}")
    print(f"Output directory: {output_dir}")
    print()
    
    pipeline_data = load_yaml(pipeline_file)
    
    # Extract the tasks
    modified_pipeline, extracted_files = extract_tasks(pipeline_data, output_dir)
    
    if not extracted_files:
        print("No inlined tasks found in the pipeline.")
        sys.exit(0)
    
    # Save the modified pipeline
    print()
    print(f"Writing modified pipeline to: {output_pipeline}")
    save_yaml(modified_pipeline, output_pipeline)
    
    print()
    print("Summary:")
    print(f"  Extracted {len(extracted_files)} task(s):")
    for filename in extracted_files:
        print(f"    - {filename}")
    print(f"  Modified pipeline: {output_pipeline.name}")
    print()
    print("Done!")


if __name__ == "__main__":
    main()