name: Bosnia Three List

on:

  # Check the three source files every hour.
  schedule:
    - cron: "0 * * * *"

  # Allow a manual run from GitHub Actions.
  workflow_dispatch:

permissions:
  contents: write

# Prevent two runs from updating the repository simultaneously.
concurrency:
  group: bosnia-three-list
  cancel-in-progress: false


jobs:

  update:
    runs-on: ubuntu-latest

    steps:

      # ------------------------------------------------------
      # Get the current bosnia3 repository
      # ------------------------------------------------------

      - name: Checkout repository
        uses: actions/checkout@v5
        with:
          fetch-depth: 0


      # ------------------------------------------------------
      # Install Python
      # ------------------------------------------------------

      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: "3.x"


      # ------------------------------------------------------
      # Generate bosnia_three_list.txt
      # ------------------------------------------------------

      - name: Generate bosnia_three_list.txt
        run: |
          python generate_bosnia_three_list.py


      # ------------------------------------------------------
      # Commit and push only when the file changed
      # ------------------------------------------------------

      - name: Update GitHub
        run: |

          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

          git add bosnia_three_list.txt

          # If nothing changed, finish successfully.
          if git diff --cached --quiet; then
            echo "No changes detected."
            exit 0
          fi

          # Commit the newly generated list.
          git commit -m "Update bosnia_three_list"

          # Get the latest version of main.
          git fetch origin main

          # Put our commit on top of the latest main.
          git rebase origin/main

          # Push the updated file.
          git push origin HEAD:main
