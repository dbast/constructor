import subprocess
import sys
import tempfile

import pytest

from constructor.shar import preprocess, read_header_template


@pytest.mark.parametrize('osx', [False, True])
@pytest.mark.parametrize('direct_execute_post_install', [False, True])
@pytest.mark.parametrize('direct_execute_pre_install', [False, True])
@pytest.mark.parametrize('batch_mode', [False, True])
@pytest.mark.parametrize('keep_pkgs', [False, True])
@pytest.mark.parametrize('has_conda', [False, True])
@pytest.mark.parametrize('has_license', [False, True])
@pytest.mark.parametrize('initialize_conda', [False, True])
@pytest.mark.parametrize('initialize_by_default', [False, True])
@pytest.mark.parametrize('has_post_install', [False, True])
@pytest.mark.parametrize('has_pre_install', [False, True])
@pytest.mark.parametrize('arch', ['x86', 'x86_64', ' ppc64le', 's390x', 'aarch64'])
def test_linux_template_processing(
        osx, arch, has_pre_install, has_post_install, initialize_conda,
        initialize_by_default, has_license, has_conda, keep_pkgs, batch_mode,
        direct_execute_pre_install, direct_execute_post_install):
    template = read_header_template()
    processed = preprocess(template, {
       'has_license': has_license,
       'osx': osx,
       'batch_mode': batch_mode,
       'keep_pkgs': keep_pkgs,
       'has_conda': has_conda,
       'x86': arch == 'x86',
       'x86_64': arch == 'x86_64',
       'ppc64le': arch == 'ppc64le',
       's390x': arch == 's390x',
       'aarch64': arch == 'aarch64',
       'linux': not osx,
       'has_pre_install': has_pre_install,
       'direct_execute_pre_install': direct_execute_pre_install,
       'has_post_install': has_post_install,
       'direct_execute_post_install': direct_execute_post_install,
       'initialize_conda': initialize_conda,
       'initialize_by_default': initialize_by_default,
    })
    assert '#if' not in processed
    assert '#else' not in processed
    assert '#endif' not in processed


@pytest.mark.skipif(sys.platform != "linux", reason="requires shellcheck >=0.7.0")
@pytest.mark.parametrize("osx", [False, True])
@pytest.mark.parametrize("direct_execute_post_install", [True])
@pytest.mark.parametrize("direct_execute_pre_install", [True])
@pytest.mark.parametrize("batch_mode", [True])
@pytest.mark.parametrize("keep_pkgs", [True])
@pytest.mark.parametrize("has_conda", [False, True])
@pytest.mark.parametrize("has_license", [True])
@pytest.mark.parametrize("initialize_conda", [True])
@pytest.mark.parametrize("initialize_by_default", [True])
@pytest.mark.parametrize("has_post_install", [True])
@pytest.mark.parametrize("has_pre_install", [False])
@pytest.mark.parametrize("arch", ["x86_64", "aarch64"])
def test_template_shellcheck(
    osx,
    arch,
    has_pre_install,
    has_post_install,
    initialize_conda,
    initialize_by_default,
    has_license,
    has_conda,
    keep_pkgs,
    batch_mode,
    direct_execute_pre_install,
    direct_execute_post_install,
):
    template = read_header_template()
    processed = preprocess(
        template,
        {
            "has_license": has_license,
            "osx": osx,
            "batch_mode": batch_mode,
            "keep_pkgs": keep_pkgs,
            "has_conda": has_conda,
            "x86": arch == "x86",
            "x86_64": arch == "x86_64",
            "ppc64le": arch == "ppc64le",
            "s390x": arch == "s390x",
            "aarch64": arch == "aarch64",
            "linux": not osx,
            "has_pre_install": has_pre_install,
            "direct_execute_pre_install": direct_execute_pre_install,
            "has_post_install": has_post_install,
            "direct_execute_post_install": direct_execute_post_install,
            "initialize_conda": initialize_conda,
            "initialize_by_default": initialize_by_default,
        },
    )

    with tempfile.NamedTemporaryFile(mode="w", suffix=".sh") as f:
        f.write(processed)
        f.flush()

        cmd = [
            "shellcheck",
            # https://www.shellcheck.net/wiki/SC2034
            "--exclude=SC2034",
            f"{f.name}",
        ]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        sc_stdout, _ = p.communicate()
        findings = (
            sc_stdout.decode(sys.stdout.encoding).replace("\r\n", "\n").splitlines()
        )

    assert findings == []
    assert p.returncode == 0
