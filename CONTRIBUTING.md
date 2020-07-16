# Contributing

If you want to add to the prune tool, please familiarize yourself with the code & our [Coding Standards][].
Before you submit a PR, please [file an issue][new collab] to request collaborator access.

## Assumptions and pre-requisites

The following is a list of topics that contributors **should already** be comfortable
with in order to contribute to `plant`.  Details on these topics are outside of
the scope of the `plant` documentation.

- [Python][python]

  Moderate to advanced experience with Python code is necessary to contribute
  to the `plant`.

- Python [unit tests][python-unit-tests]

  An understanding of the Python unit testing framework including mocking and patching is
  expected and needed to write unit tests for any `plant` contribution.

- Auditree [compliance framework][auditree-framework]

  A typical use case for `plant` centers around adding external evidence to an evidence locker.
  To that end, a general understanding of the Auditree [compliance framework][auditree-framework] is
  useful.

## Code formatting and style

Please ensure all code contributions are formatted by `yapf` and pass all `flake8` linter requirements.
CI/CD will run `yapf` and `flake8` on all new commits and reject changes if there are failures.  If you
run `make develop` to setup and maintain your virtual environment then `yapf` and `flake8` will be executed
automatically as part of all git commits.  If you'd like to run things manually you can do so locally by using:

```shell
make code-format
make code-lint
```

## Testing

Please ensure all code contributions are covered by appropriate unit tests and that all tests run cleanly.
CI/CD will run tests on all new commits and reject changes if there are failures. You should run the test
suite locally by using:

```shell
make test
```

[Coding Standards]: https://github.com/ComplianceAsCode/auditree-plant/blob/master/doc/coding-standards.rst
[flake8]: https://gitlab.com/pycqa/flake8
[new collab]: https://github.com/ComplianceAsCode/auditree-plant/issues/new?template=new-collaborator.md
[yapf]: https://github.com/google/yapf
[python]: https://www.python.org/
[python-unit-tests]: https://docs.python.org/3/library/unittest.html
[auditree-framework]: https://github.com/ComplianceAsCode/auditree-framework
