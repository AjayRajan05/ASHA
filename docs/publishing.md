# PyPI Publishing Setup

PrivySHA uses [trusted publishing](https://docs.pypi.org/trusted-publishers/) via GitHub Actions.

## One-time configuration

1. **PyPI project** — Create or open the [privysha](https://pypi.org/project/privysha/) project on PyPI.

2. **Trusted publisher** — In PyPI → Your project → Publishing → Add a new pending publisher:
   - PyPI project name: `privysha`
   - Owner: `AjayRajan05` (or your GitHub org)
   - Repository: `privySHA`
   - Workflow: `publish.yml`
   - Environment: `pypi`

3. **GitHub environment** — In the GitHub repo → Settings → Environments → New environment:
   - Name: `pypi`
   - Optional: require reviewers before publish

4. **Publish a release** — After CI is green on `main`:

   - Go to GitHub → Releases → **Draft a new release**
   - Tag: `v1.0.0` (must match semver in `pyproject.toml`)
   - Publish the release

   The `.github/workflows/publish.yml` workflow runs when a release is **published**
   (or via manual **workflow_dispatch**). It runs the test suite, builds the wheel,
   and uploads to PyPI.

## Local verification (before releasing)

```bash
pip install -e ".[dev]"
pytest tests_v2/ tests/ -m "not slow"
python benchmarks/run_benchmarks.py
python -m build
twine check dist/*
pip install dist/*.whl --force-reinstall
python -c "from privysha import process; print(process('hello'))"
```

These steps are also enforced in CI on Ubuntu 3.11.

## Updating benchmark baseline

After a good local benchmark run:

```bash
python benchmarks/run_benchmarks.py --save --update-baseline
git add benchmarks/baseline/results.json benchmarks/baseline/summary.md
```

CI compares against `benchmarks/baseline/results.json` for regression detection.
