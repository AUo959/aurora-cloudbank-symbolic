#!/bin/bash
set -euo pipefail

echo "Aurora CI/CD Maintenance Script"
echo "==============================="

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

remove_dir_if_present() {
  local target="$1"
  if [ -d "$target" ]; then
    find "$target" -mindepth 1 -delete 2>/dev/null || true
    rmdir "$target" 2>/dev/null || true
    echo "  cleaned directory: $target"
  fi
}

remove_file_if_present() {
  local target="$1"
  if [ -f "$target" ]; then
    rm -f "$target"
    echo "  cleaned file: $target"
  fi
}

echo "Cleaning up temporary files..."
if [ -d /tmp ]; then
  while IFS= read -r codeql_dir; do
    [ -n "$codeql_dir" ] || continue
    remove_dir_if_present "$codeql_dir"
  done < <(find /tmp -mindepth 1 -maxdepth 1 -type d -name 'codeql-*' 2>/dev/null || true)
fi
remove_file_if_present "/home/runner/work/_temp/proxy.log"
remove_dir_if_present ".pytest_cache"
while IFS= read -r cache_dir; do
  [ -n "$cache_dir" ] || continue
  remove_dir_if_present "$cache_dir"
done < <(find . -type d -name '__pycache__' -not -path './.git/*' -not -path './.venv/*' 2>/dev/null || true)
find . -name "*.pyc" -not -path "./.git/*" -not -path "./.venv/*" -delete 2>/dev/null || true
find . -name "*.pyo" -not -path "./.git/*" -not -path "./.venv/*" -delete 2>/dev/null || true
echo "Temporary files cleaned"

echo "Checking workflow files..."
if [ -d ".github/workflows" ]; then
  for workflow in .github/workflows/*.yml; do
    if [ -f "$workflow" ]; then
      echo "  found: $(basename "$workflow")"
      if command_exists python3; then
        if python3 -c "import yaml" >/dev/null 2>&1; then
          python3 -c "import pathlib, yaml; yaml.safe_load(pathlib.Path('$workflow').read_text())" >/dev/null 2>&1 && echo "    valid YAML" || echo "    invalid YAML"
        else
          echo "    skipped YAML validation (pyyaml missing)"
        fi
      fi
    fi
  done
else
  echo "  no .github/workflows directory found"
fi

echo "Checking Node.js setup..."
if [ -f "package.json" ]; then
  echo "  package.json found"
  command_exists npm && npm --version >/dev/null && echo "    npm available" || echo "    npm not available"
  command_exists node && node --version >/dev/null && echo "    node available" || echo "    node not available"
else
  echo "  no package.json found (Node.js CI will be skipped)"
fi

echo "Checking Python setup..."
if [ -f "requirements.txt" ]; then
  echo "  requirements.txt found"
  command_exists python3 && python3 --version && echo "    python3 available" || echo "    python3 not available"
  command_exists pip3 && pip3 --version >/dev/null && echo "    pip3 available" || echo "    pip3 not available"
else
  echo "  no requirements.txt found"
fi

echo "Checking Aurora-specific files..."
aurora_files=(
  "symbolic_config.yaml"
  "devcontainer.json"
  "modules/symbolic_core/sonnet4_integration_hub.py"
  "aurora_api.py"
)

for file in "${aurora_files[@]}"; do
  if [ -f "$file" ]; then
    echo "  $file"
  else
    echo "  missing: $file"
  fi
done

echo "Checking for common CI issues..."
if rg -n '^(<<<<<<< |>>>>>>> |\|\|\|\|\|\|\| )' . -g '!.git' -g '!.venv' -g '!node_modules' 2>/dev/null; then
  echo "  merge conflict markers found"
else
  echo "  no merge conflict markers"
fi

echo "Checking for large files..."
find . -size +50M -type f 2>/dev/null | head -5 | while read -r file; do
  echo "  large file: $file ($(du -h "$file" | cut -f1))"
done

echo
echo "CI/CD Status Report"
echo "==================="
echo "Date: $(date)"
echo "Repository: $(basename "$(pwd)")"
echo
echo "Workflow Files:"
ls -la .github/workflows/*.yml 2>/dev/null | wc -l | xargs echo "  Count:"
echo
echo "Project Files:"
[ -f "package.json" ] && echo "  Node.js project" || echo "  No Node.js project"
[ -f "requirements.txt" ] && echo "  Python project" || echo "  No Python project"
[ -f "devcontainer.json" ] && echo "  DevContainer configured" || echo "  No DevContainer"
[ -f "symbolic_config.yaml" ] && echo "  Aurora configured" || echo "  No Aurora config"
echo
echo "Recommendations:"
echo "  1. Review workflow files for syntax errors"
echo "  2. Ensure all dependencies are properly specified"
echo "  3. Test locally before pushing to avoid CI failures"
echo "  4. Monitor CI logs for proxy.log and cleanup issues"
echo
echo "Maintenance complete"
