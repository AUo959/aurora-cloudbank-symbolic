#!/usr/bin/env python3
"""Command line interface for working with CASK assets."""

import argparse

from modules.cask_tool import (
    generate_architecture_chart,
    load_risk_assessment,
    load_specifications,
    load_vs_sota,
)


def cmd_summary() -> None:
    specs = load_specifications()
    risks = load_risk_assessment()
    comp = load_vs_sota()
    print("Specifications rows:", len(specs))
    print("Risk assessment rows:", len(risks))
    print("Comparison rows:", len(comp))


def cmd_chart(path: str) -> None:
    out = generate_architecture_chart(path)
    print("Chart written to %s", out)


def main() -> None:
    parser = argparse.ArgumentParser(description="Interact with CASK assets")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("summary", help="Print dataset summaries")
    chart_p = sub.add_parser("chart", help="Generate architecture chart")
    chart_p.add_argument("--output", default="cask_architecture.png")

    args = parser.parse_args()

    if args.command == "summary":
        cmd_summary()
    elif args.command == "chart":
        cmd_chart(args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
