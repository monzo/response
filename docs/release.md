# Release Process

_Note: this can only be done by collaborators with write access_

1. Bump the version in [setup.py](../setup.py), commit to `master` and push
1. Go to https://github.com/monzo/response/releases, click "Draft a new release"
1. Enter the new tag version. This should be in the format `release-<major>.<minor>.<patch>`, e.g. `release-0.1.5`
1. Enter a bit of detail about what’s gone in since the last release, maybe include a list of the PRs
1. Travis CI should automatically pick up the tag and start a new build/test/deploy run. Keep an eye on https://travis-ci.org/monzo/response for this
1. This will push to PyPI, and generally takes around 5-10 minutes. If you want to check it’s uploaded successfully, go to https://pypi.org/project/django-incident-response/, which will always display the latest semver pushed to PyPI 