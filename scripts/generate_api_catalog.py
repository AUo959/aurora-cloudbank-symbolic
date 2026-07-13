#!/usr/bin/env python3
"""
Generate API Catalog from FastAPI OpenAPI Schema

Extracts comprehensive API documentation from aurora_api.py

Usage:
    python scripts/generate_api_catalog.py                  # writes to docs/api/
    python scripts/generate_api_catalog.py --output-dir .   # writes to cwd
"""

import argparse
import json
import os
import secrets
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Assemble the app with process-local generation fixtures. These values exist
# only for this process, are never serialized, and avoid reading operator
# credentials while preserving security/monitoring routes in the OpenAPI tree.
for env_name in (
    "CSRF_SECRET_KEY",
    "WS_AUTH_SECRET",
    "JWT_SECRET_KEY",
    "MONITORING_SIGNING_KEY",
):
    os.environ[env_name] = secrets.token_hex(32)

os.environ["AURORA_ENV"] = "test"
os.environ["AURORA_ALLOW_DEV_AUTH_FIXTURE"] = "true"
for role in ("ADMIN", "OPERATOR", "OBSERVER"):
    os.environ[f"AURORA_DEV_{role}_PASSWORD"] = secrets.token_urlsafe(32)

for credential_name in (
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "OPENAI_ADMIN_KEY",
    "OPENAI_API_KEY",
):
    os.environ.pop(credential_name, None)
os.environ.pop("AURORA_AUTH_USERS_FILE", None)
os.environ.pop("AURORA_AUTH_USERS_JSON", None)

# Add project root to path
project_root = Path(__file__).parent.parent
invocation_cwd = Path.cwd()
sys.path.insert(0, str(project_root))
os.chdir(project_root)

# Default output directory is docs/api/ relative to the project root so that
# generated snapshots land in the tracked location regardless of cwd.
DEFAULT_OUTPUT_DIR = project_root / "docs" / "api"

from api.aurora_api import app  # noqa: E402  # import after generation env isolation


def resolve_output_dir(value: str) -> Path:
    """Resolve CLI output paths against the caller's original directory."""
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = invocation_cwd / path
    return path.resolve()


def get_source_commit() -> str:
    """Return the Git commit whose assembled app is being documented."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return result.stdout.strip() or "unknown"


def generate_api_catalog(output_dir: Path = DEFAULT_OUTPUT_DIR):
    """Generate comprehensive API catalog"""

    # Extract OpenAPI schema
    schema = dict(app.openapi())
    generated_at = datetime.now(timezone.utc).isoformat()
    source_commit = get_source_commit()
    schema["x-generated-at"] = generated_at
    schema["x-source-commit"] = source_commit

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save full schema
    with open(output_dir / "api_schema.json", "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)
        f.write("\n")

    # Generate human-readable catalog
    catalog = {
        "title": schema.get("info", {}).get("title", "Aurora CloudBank API"),
        "version": schema.get("info", {}).get("version", "1.0.0"),
        "description": schema.get("info", {}).get("description", ""),
        "generated": generated_at,
        "generated_at": generated_at,
        "source_commit": source_commit,
        "total_routes": len(schema.get("paths", {})),
        "routes": []
    }

    # Process routes
    paths = schema.get("paths", {})
    for path, methods in sorted(paths.items()):
        for method, details in methods.items():
            if method.lower() in ["get", "post", "put", "delete", "patch"]:
                route_info = {
                    "method": method.upper(),
                    "path": path,
                    "summary": details.get("summary", ""),
                    "description": details.get("description", ""),
                    "tags": details.get("tags", []),
                    "parameters": [],
                    "request_body": None,
                    "responses": {}
                }

                # Extract parameters
                if "parameters" in details:
                    for param in details["parameters"]:
                        route_info["parameters"].append({
                            "name": param.get("name"),
                            "in": param.get("in"),
                            "required": param.get("required", False),
                            "description": param.get("description", ""),
                            "schema": param.get("schema", {})
                        })

                # Extract request body
                if "requestBody" in details:
                    route_info["request_body"] = {
                        "required": details["requestBody"].get("required", False),
                        "content": list(details["requestBody"].get("content", {}).keys())
                    }

                # Extract responses
                for status_code, response in details.get("responses", {}).items():
                    route_info["responses"][status_code] = {
                        "description": response.get("description", ""),
                        "content": list(response.get("content", {}).keys())
                    }

                catalog["routes"].append(route_info)

    # Save catalog
    with open(output_dir / "API_CATALOG.json", "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2)
        f.write("\n")

    # Generate markdown catalog
    generate_markdown_catalog(catalog, output_dir)

    print("✅ API Catalog Generated:")
    print("   - %s/api_schema.json (%d bytes)" % (output_dir, len(json.dumps(schema))))
    print("   - %s/API_CATALOG.json" % output_dir)
    print("   - %s/API_CATALOG.md" % output_dir)
    print("   - Total routes: %d" % catalog['total_routes'])

    return catalog


def generate_markdown_catalog(catalog, output_dir: Path = DEFAULT_OUTPUT_DIR):
    """Generate markdown documentation"""

    def clean_text(value):
        return "\n".join(line.rstrip() for line in str(value).splitlines()).strip()

    lines = [
        f"# {catalog['title']}",
        "",
        f"**Version:** {catalog['version']}",
        f"**Generated:** {catalog['generated_at']}",
        f"**Source Commit:** `{catalog['source_commit']}`",
        f"**Total Routes:** {catalog['total_routes']}",
        "",
        clean_text(catalog.get("description", "")),
        "",
        "---",
        "",
        "## Table of Contents",
        ""
    ]

    # Group routes by tag
    routes_by_tag = {}
    for route in catalog["routes"]:
        tags = route.get("tags", ["Untagged"])
        for tag in tags:
            if tag not in routes_by_tag:
                routes_by_tag[tag] = []
            routes_by_tag[tag].append(route)

    # Add TOC
    for tag in sorted(routes_by_tag.keys()):
        lines.append(f"- [{tag}](#{tag.lower().replace(' ', '-')})")

    lines.extend(["", "---", ""])

    # Add route details by tag
    for tag in sorted(routes_by_tag.keys()):
        lines.extend([
            f"## {tag}",
            "",
            f"**Routes:** {len(routes_by_tag[tag])}",
            ""
        ])

        for route in sorted(routes_by_tag[tag], key=lambda r: r["path"]):
            lines.extend([
                f"### `{route['method']} {route['path']}`",
                ""
            ])

            if route.get("summary"):
                lines.append(f"**Summary:** {clean_text(route['summary'])}")

            if route.get("description"):
                lines.append(clean_text(route["description"]))

            lines.append("")

            # Parameters
            if route.get("parameters"):
                lines.extend(["**Parameters:**", ""])
                for param in route["parameters"]:
                    required = "✅ Required" if param["required"] else "Optional"
                    lines.append(f"- `{param['name']}` ({param['in']}) - {required}")
                    if param.get("description"):
                        lines.append(f"  - {clean_text(param['description'])}")
                lines.append("")

            # Request body
            if route.get("request_body"):
                lines.extend([
                    "**Request Body:**",
                    f"- Required: {'Yes' if route['request_body']['required'] else 'No'}",
                    f"- Content Types: {', '.join(route['request_body']['content'])}",
                    ""
                ])

            # Responses
            if route.get("responses"):
                lines.extend(["**Responses:**", ""])
                for status, response in sorted(route["responses"].items()):
                    lines.append(f"- **{status}**: {clean_text(response['description'])}")
                    if response.get("content"):
                        lines.append(f"  - Content: {', '.join(response['content'])}")
                lines.append("")

            lines.append("---")
            lines.append("")

    # Write markdown
    with open(output_dir / "API_CATALOG.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip() + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Aurora API catalog snapshots")
    parser.add_argument(
        "--output-dir",
        type=resolve_output_dir,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory to write api_schema.json, API_CATALOG.json, and API_CATALOG.md "
             "(default: docs/api/ relative to project root)",
    )
    args = parser.parse_args()

    try:
        catalog = generate_api_catalog(output_dir=args.output_dir)
        sys.exit(0)
    except Exception as e:
        print("❌ Error generating API catalog: %s" % e, file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
