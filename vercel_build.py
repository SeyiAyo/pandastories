#!/usr/bin/env python
"""
Vercel build script - runs before deployment
"""
import os
import subprocess
import sys

def run_command(command):
    """Run a shell command and print output"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode

def main():
    print("=" * 50)
    print("Starting Vercel build process...")
    print("=" * 50)
    
    # Run migrations
    print("\n1. Running database migrations...")
    if run_command("python manage.py migrate --noinput") != 0:
        print("WARNING: Migrations failed, but continuing...")
    
    # Collect static files
    print("\n2. Collecting static files...")
    if run_command("python manage.py collectstatic --noinput --clear") != 0:
        print("ERROR: collectstatic failed!")
        sys.exit(1)
    
    # Verify static files were collected
    static_root = os.path.join(os.path.dirname(__file__), 'staticfiles')
    if os.path.exists(static_root):
        file_count = sum(len(files) for _, _, files in os.walk(static_root))
        print(f"\n✓ Static files collected: {file_count} files in {static_root}")
    else:
        print(f"\n✗ WARNING: Static files directory not found: {static_root}")
    
    print("\n" + "=" * 50)
    print("Build completed successfully!")
    print("=" * 50)

if __name__ == "__main__":
    main()
