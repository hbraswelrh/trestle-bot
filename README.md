# trestle-bot

trestle-bot assists users in leveraging [Compliance-Trestle](https://github.com/IBM/compliance-trestle) in automated workflows or [OSCAL](https://github.com/usnistgov/OSCAL) formatted compliance content management.

> WARNING: This project is currently under initial development. APIs may be changed incompatibly from one commit to another.

## Basic Configuration


```yaml

name: Example Workflow
...

    steps:
      - uses: actions/checkout@v3
      - name: Run trestlebot
        id: trestlebot
        uses: RedHatProductSecurity/trestle-bot@main
        with:
          markdown_path: "markdown/profiles"
          oscal_model: "profile"
```

## Inputs and Outputs

Checkout [`action.yml`](./action.yml) for a full list of supported inputs and outputs.

### Additional information on workflow inputs

- `markdown_path`: This is the location for Markdown generated by the `trestle author <model>-generate` commands
- `ssp_index_path`: This is a text file that stores the component definition information by name in trestle with the ssp name. Example below

```json
 "ssp1": {
            "profile": "profile1",
            "component definitions": [
                "comp1",
                "comp2"
            ]
        },
```

## Action Behavior

The purpose of this action is to sync JSON and Markdown data with `compliance-trestle` and commit changes back to the branch or submit a pull request (if desired). Below are the main use-cases/workflows available:

- The default behavior of this action is to run a trestle `assemble` and `regenerate` tasks with the given markdown directory and model and commit the changes back to the branch the workflow ran from ( `github.ref_name` ). The branch can be changed by setting the field `branch`. If no changes exist or the changes do not exist with the file pattern set, no changes will be made and the action will exit successfully.

```yaml
  steps:
    - uses: actions/checkout@v3
    - name: Run trestlebot
      id: trestlebot
      uses: RedHatProductSecurity/trestle-bot@main
      with:
        markdown_path: "markdown/profiles"
        oscal_model: "profile"
        branch: "another-branch"
```

- If the `target_branch` field is set, a pull request will be made using the `target_branch` as the base branch and `branch` as the head branch.

```yaml
  steps:
    - uses: actions/checkout@v3
    - name: Run trestlebot
      id: trestlebot
      uses: RedHatProductSecurity/trestle-bot@main
      with:
        markdown_path: "markdown/profiles"
        oscal_model: "profile"
        branch: "autoupdate-${{ github.run_id }}"
        target_branch: "main"
        github_token: ${{ secret.GITHUB_TOKEN }}
```

- When `check_only` is set, the trestle `assemble` and `regenerate` tasks are run and the repository is checked for changes. If changes exists, the action with exit with an error.

```yaml
    steps:
      - uses: actions/checkout@v3
      - name: Run trestlebot
        id: trestlebot
        uses: RedHatProductSecurity/trestle-bot@main
        with:
          markdown_path: "markdown/profiles"
          oscal_model: "profile"
          check_only: true
```

> Note: Trestle `assemble` or `regenerate` tasks may be skipped if desired using `skip_assemble: true` or `skip_regenerate: true`, respectively. 

See `TROUBLESHOOTING.md` for additional information.