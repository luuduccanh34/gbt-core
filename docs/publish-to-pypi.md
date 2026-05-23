# Publishing GBT Core to PyPI

This guide explains how to build and publish the `gbt-core` package to the Python Package Index (PyPI) using [Poetry](https://python-poetry.org/).

## Prerequisites
- A registered account on [PyPI](https://pypi.org/).
- The PyPI account must have permission to upload to the `gbt-core` project.
- `poetry` installed on your local machine.

## Steps to Publish

### 1. Generate a PyPI API Token
1. Log in to your [PyPI account](https://pypi.org/manage/account/).
2. Navigate to **Account settings** -> **API tokens**.
3. Click **Add API token**. You can name it something like `gbt-core-publish`.
4. Set the scope to the entire account or strictly the `gbt-core` project (recommended if it already exists).
5. Copy the generated token (it usually starts with `pypi-`). *Note: This token is only displayed once!*

### 2. Configure Poetry with Your Token
Run the following command in your terminal to authenticate Poetry with your PyPI token. Replace `<your-api-token>` with the token you just copied:

```bash
poetry config pypi-token.pypi <your-api-token>
```

### 3. Build the Package
Before publishing, you need to compile the source distribution (`sdist`) and the wheel file. Run the following command:

```bash
poetry build
```

You should see output indicating success:
```text
Building gbt-core (0.1.0)
  - Building sdist
  - Built gbt_core-0.1.0.tar.gz
  - Building wheel
  - Built gbt_core-0.1.0-py3-none-any.whl
```

*(Ensure your git working tree is clean before proceeding, for example by checking `git status`)*.

### 4. Publish the Package
Once the package components are successfully built, you can finally publish the distribution to PyPI:

```bash
poetry publish
```

Expect an output confirming the successful upload:
```text
Publishing gbt-core (0.1.0) to PyPI
 - Uploading gbt_core-0.1.0.tar.gz 100%
 - Uploading gbt_core-0.1.0-py3-none-any.whl 100%
```

### 5. Updating the Package Version

When you need to release a new version (e.g., bug fixes or new features), you can easily bump the version using Poetry before building and publishing again.

1. **Bump the version**:
   For example, to bump the patch version (e.g., `0.1.0` -> `0.1.1`):
   ```bash
   poetry version patch
   ```
   *(You can also use `minor` or `major` depending on the changes)*.

2. **Build the new version**:
   ```bash
   poetry build
   ```

3. **Publish the new version**:
   ```bash
   poetry publish
   ```

**Congratulations!** The new version of `gbt-core` is now publicly available on PyPI and can be installed via `pip install "gbt-core[neo4j]"`.
