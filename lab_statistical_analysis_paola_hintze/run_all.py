"""Run the complete analysis in dependency order."""

import data_exploration
import power_analysis
import statistical_analysis


def main() -> None:
    data_exploration.main()
    statistical_analysis.main()
    power_analysis.main()
    print("All analysis stages completed successfully.")


if __name__ == "__main__":
    main()

