"""Command line utility to generate CASK reports and charts."""

import argparse

from modules.cask import (
    generate_technical_specifications,
    generate_vs_sota_comparison,
    generate_risk_assessment,
    create_architecture_flowchart,
    create_research_landscape_chart,
    create_project_gantt_chart,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate CASK assets")
    parser.add_argument("--output-dir", default="docs/cask", help="Directory for generated files")
    args = parser.parse_args()

    import os
    os.makedirs(args.output_dir, exist_ok=True)

    specs_csv = os.path.join(args.output_dir, "cask_technical_specifications.csv")
    comparison_csv = os.path.join(args.output_dir, "cask_vs_sota_comparison.csv")
    risk_csv = os.path.join(args.output_dir, "cask_risk_assessment.csv")
    arch_png = os.path.join(args.output_dir, "cask_architecture_flowchart.png")
    landscape_png = os.path.join(args.output_dir, "cask_research_landscape.png")
    gantt_png = os.path.join(args.output_dir, "cask_gantt_chart.png")

    generate_technical_specifications(specs_csv)
    generate_vs_sota_comparison(comparison_csv)
    generate_risk_assessment(risk_csv)
    create_architecture_flowchart(arch_png)
    create_research_landscape_chart(landscape_png)
    create_project_gantt_chart(gantt_png)

    print(f"CASK assets written to {args.output_dir}")


if __name__ == "__main__":
    main()
