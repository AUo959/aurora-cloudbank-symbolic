#!/usr/bin/env python3
"""
Generate API Catalog from FastAPI OpenAPI Schema

Extracts comprehensive API documentation from aurora_api.py
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

# Set required environment variables for FastAPI security
os.environ["CSRF_SECRET_KEY"] = "dev-secret-for-catalog-generation"
os.environ["WS_AUTH_SECRET"] = "dev-secret-for-catalog-generation"

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.aurora_api import app


def generate_api_catalog():
    """Generate comprehensive API catalog"""
    
    # Extract OpenAPI schema
    schema = app.openapi()
    
    # Save full schema
    with open("api_schema.json", "w") as f:
        json.dump(schema, f, indent=2)
    
    # Generate human-readable catalog
    catalog = {
        "title": schema.get("info", {}).get("title", "Aurora CloudBank API"),
        "version": schema.get("info", {}).get("version", "1.0.0"),
        "description": schema.get("info", {}).get("description", ""),
        "generated": datetime.now(timezone.utc).isoformat(),
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
    with open("API_CATALOG.json", "w") as f:
        json.dump(catalog, f, indent=2)
    
    # Generate markdown catalog
    generate_markdown_catalog(catalog)
    
    print("✅ API Catalog Generated:")
    print("   - api_schema.json (%d bytes)" % len(json.dumps(schema)))
    print("   - API_CATALOG.json")
    print("   - API_CATALOG.md")
    print("   - Total routes: %d" % catalog['total_routes'])
    
    return catalog


def generate_markdown_catalog(catalog):
    """Generate markdown documentation"""
    
    lines = [
        f"# {catalog['title']}",
        "",
        f"**Version:** {catalog['version']}  ",
        f"**Generated:** {catalog['generated']}  ",
        f"**Total Routes:** {catalog['total_routes']}",
        "",
        catalog.get("description", ""),
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
                lines.append(f"**Summary:** {route['summary']}  ")
            
            if route.get("description"):
                lines.append(f"{route['description']}")
            
            lines.append("")
            
            # Parameters
            if route.get("parameters"):
                lines.extend(["**Parameters:**", ""])
                for param in route["parameters"]:
                    required = "✅ Required" if param["required"] else "Optional"
                    lines.append(f"- `{param['name']}` ({param['in']}) - {required}")
                    if param.get("description"):
                        lines.append(f"  - {param['description']}")
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
                    lines.append(f"- **{status}**: {response['description']}")
                    if response.get("content"):
                        lines.append(f"  - Content: {', '.join(response['content'])}")
                lines.append("")
            
            lines.append("---")
            lines.append("")
    
    # Write markdown
    with open("API_CATALOG.md", "w") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    try:
        catalog = generate_api_catalog()
        sys.exit(0)
    except Exception as e:
        print("❌ Error generating API catalog: %s" % e, file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
