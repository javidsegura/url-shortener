#!/usr/bin/env python3
"""
Sync Terraform outputs to backend .env and Ansible inventory files
"""
import json
import sys
import os
from pathlib import Path
import argparse


def load_terraform_outputs(terraform_path):
    """Load terraform outputs from JSON"""
    import subprocess
    
    try:
        result = subprocess.run(
            ["terraform", "output", "-json"],
            cwd=terraform_path,
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running terraform output: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing terraform output JSON: {e}")
        sys.exit(1)


def filter_outputs_by_prefix(outputs, prefixes):
    """Filter terraform outputs by key prefixes"""
    filtered = {}
    for key, value in outputs.items():
        if any(key.startswith(prefix) for prefix in prefixes):
            filtered[key] = value['value']
    return filtered


def write_env_file(outputs, env_file_path):
    """Write filtered outputs to .env file format"""
    env_lines = []
    for key, value in outputs.items():
        # Convert key to uppercase and handle nested values
        env_key = key.upper()
        
        # Handle different value types
        if isinstance(value, (dict, list)):
            env_value = json.dumps(value)
        elif isinstance(value, bool):
            env_value = str(value).lower()
        else:
            env_value = str(value)
        
        # Escape quotes in values
        env_value = env_value.replace('"', '\\"')
        env_key = env_key.replace("BACKEND_", "")
        env_key = env_key.replace("API_", "")
        env_lines.append(f'{env_key}="{env_value}"')
    
    # Write to file
    with open(env_file_path, 'a') as f:
        f.write('\n'.join(env_lines))
        f.write('\n')


def derive_public_ip(outputs):
    """Best-effort extraction of a public IP address from Terraform outputs"""
    for key, value in outputs.items():
        key_lower = key.lower()
        if "host_ip" in key_lower:
            return str(value)
    return None


def derive_frontend_base_url(outputs, environment):
    """Derive the BASE_URL for the frontend based on environment and TF outputs.

    - dev:       http://localhost/api
    - staging:   http://<public-ip>.nip.io/api
    - production:http://<public-ip>/api (fallback to nip.io if needed)
    """
    env_lower = environment.lower()
    if env_lower == "dev":
        return "http://localhost/api/"

    public_ip = derive_public_ip(outputs) or ""

    if env_lower == "staging":
        if public_ip:
            return f"http://{public_ip}/api/"
        # Fallback sensible default
        raise ValueError("Public ip needs to be provided for staging")

    if public_ip:
        return f"http://{public_ip}/api/"


def write_frontend_env(base_url, env_file_path):
    """Write the VITE_* variables needed by the frontend."""
    lines = [f'VITE_BASE_URL="{base_url}"']
    with open(env_file_path, 'w') as f:
        f.write('\n'.join(lines))
        f.write('\n')


def write_ansible_inventory(outputs, inventory_file_path, environment):
    """Write filtered outputs to Ansible inventory format"""
    inventory_lines = []
    
    # Find host IP and connection vars
    host_ip = None
    ansible_user = None
    all_vars = {}
    
    for key, value in outputs.items():
        key_lower = key.lower()

        print(f"key is: {key} with value: {value}")
        
        # Extract host IP for webservers section
        if 'host_ip' in key_lower:
            host_ip = value
        # Extract ansible_user for host line
        elif 'ssh_user' in key_lower:
            ansible_user = value
        elif key.lower() == "ssh_private_key_file":
            ansible_key = f"ansible_{key.lower()}"
            value = ".".join(value.split(".")[1:])
            all_vars[ansible_key] = f"./terraform/environment/{environment}{value}"
        else:
            ansible_key = key.lower().replace('ansible_', '').replace('deploy_', '')
            if isinstance(value, (dict, list)):
                all_vars[ansible_key] = json.dumps(value)
            elif isinstance(value, bool):
                all_vars[ansible_key] = str(value).lower()
            else:
                all_vars[ansible_key] = str(value)
    
    # Create [all:vars] section
    if all_vars:
        inventory_lines.append('[all:vars]')
        for var_key, var_value in all_vars.items():
            inventory_lines.append(f'{var_key} = {var_value}')
        inventory_lines.append('')
    
    # Create [webservers] section
    inventory_lines.append('[webservers]')
    if host_ip:
        host_line = str(host_ip)
        if ansible_user:
            host_line += f' ansible_user={ansible_user}'
        inventory_lines.append(host_line)
    else:
        inventory_lines.append('# No host IP found in Terraform outputs')
    
    # Write to file
    with open(inventory_file_path, 'w') as f:
        f.write('\n'.join(inventory_lines))
        f.write('\n')


def main():
    parser = argparse.ArgumentParser(description='Sync Terraform outputs to various formats')
    parser.add_argument('--terraform-path', required=True, help='Path to Terraform directory')
    parser.add_argument('--environment', required=True, choices=["dev", "staging", "production"])
    parser.add_argument('--backend-env', help='Path to backend .env file')
    parser.add_argument('--frontend-env', help='Path to frontend .env file to write VITE_* vars')
    parser.add_argument('--ansible-inventory', help='Path to Ansible inventory file')
    parser.add_argument('--backend-prefixes', nargs='+', default=['backend_', 'db_', 'api_'], 
                       help='Prefixes for backend environment variables')
    parser.add_argument('--ansible-prefixes', nargs='+', default=['ansible_', 'deploy_', 'server_'],
                       help='Prefixes for Ansible variables')
    parser.add_argument('--frontend-prefixes', nargs='+', default=['frontend_', 'deploy_', 'server_'],
                       help='Prefixes for Ansible variables')
    
    args = parser.parse_args()
    
    # Load terraform outputs
    print("Loading Terraform outputs...")
    outputs = load_terraform_outputs(args.terraform_path)
    
    if not outputs:
        print("No Terraform outputs found")
        return
    
    print(f"Found {len(outputs)} Terraform outputs")
    
    # Process backend environment file
    if args.backend_env:
        print(f"Filtering outputs for backend (prefixes: {args.backend_prefixes})")
        backend_outputs = filter_outputs_by_prefix(outputs, args.backend_prefixes)
        
        if backend_outputs:
            print(f"Writing {len(backend_outputs)} backend variables to {args.backend_env}")
            write_env_file(backend_outputs, args.backend_env)
        else:
            print("No backend outputs found with specified prefixes")
    
    # Process frontend environment file
    if args.frontend_env:
        print("Deriving frontend base URL (VITE_BASE_URL)...")
        # Use all outputs for IP detection; no prefix filtering
        print(f"Filtering outputs for Ansible (prefixes: {args.frontend_prefixes})")
        frontend_outputs = filter_outputs_by_prefix(outputs, args.frontend_prefixes)

        base_url = derive_frontend_base_url(frontend_outputs, args.environment)
        print(f"Writing VITE_BASE_URL={base_url} to {args.frontend_env}")
        write_frontend_env(base_url, args.frontend_env)

    # Process Ansible inventory file
    if args.ansible_inventory:
        print(f"Filtering outputs for Ansible (prefixes: {args.ansible_prefixes})")
        ansible_outputs = filter_outputs_by_prefix(outputs, args.ansible_prefixes)
        
        if ansible_outputs:
            print(f"Writing {len(ansible_outputs)} Ansible variables to {args.ansible_inventory}")
            write_ansible_inventory(ansible_outputs, args.ansible_inventory, environment=args.environment)
        else:
            print("No Ansible outputs found with specified prefixes")
    
    print("Sync completed successfully!")


if __name__ == '__main__':
    main()