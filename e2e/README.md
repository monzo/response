# End to end tests

This package contains a small suite of end-to-end tests of the response package that can be run in Docker. It's mainly intended to run in CI as a pre-release smoke test of whether the response package can be installed and used in a fresh demo app install - business logic tests should be part of the main package.


## Running the tests

If you already have a `demo/.env` file set up, rename it to something else, otherwise the script will complain.

From the root of the repository, run `bash e2e/run.sh`. This script runs the demo docker-compose setup, installs response, and runs the E2E tests in a separate container.


## Development

These tests use [pytest](https://pytest.org/). It makes heavy use of pytest fixtures to set up the API and Slack clients - see code comments for more detail on what these do.

You can also run the tests locally (outside of Docker) against a running demo docker-compose install.

You can run `SKIP_CLEANUP=yes bash e2e/run.sh` to set this up with the necessary environment.
