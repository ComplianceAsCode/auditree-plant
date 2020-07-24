# Contributing

If you want to add to plant, please familiarise yourself with the code & our [Coding Standards][]. Before you submit a PR, please [file an issue][new collab] to request collaborator access.

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

[Coding Standards]: https://github.com/ComplianceAsCode/auditree-framework/blob/master/doc/coding-standards.rst
[new collab]: https://github.com/ComplianceAsCode/auditree-plant/issues/new?template=new-collaborator.md
