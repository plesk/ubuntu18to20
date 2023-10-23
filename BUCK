# Copyright 1999-2023. Plesk International GmbH. All rights reserved.
# vim:ft=python:

PRODUCT_VERSION = '1.0.0'

genrule(
    name = 'version',
    out = 'version.json',
    bash = r"""echo "{\"version\": \"%s\", \"revision\": \"`git rev-parse HEAD`\"}" > $OUT""" % (PRODUCT_VERSION),
)

python_library(
    name = 'actions.lib',
    srcs = glob(['./actions/*.py']),
)

python_library(
    name = 'ubuntu18to20.lib',
    srcs = glob(['main.py', 'messages.py']),
    deps = [
        '//common:common.lib',
        ':actions.lib',
    ],
    resources = [
        ':version',
    ],
)


python_binary(
    name = 'ubuntu18to20-script',
    platform = 'py3',
    main_module = 'main',
    deps = [
        ':ubuntu18to20.lib',
    ],
)

genrule(
    name = 'ubuntu18to20',
    srcs = [':ubuntu18to20-script'],
    out = 'ubuntu18to20',
    cmd = 'cp $(location :ubuntu18to20-script) $OUT && chmod +x $OUT',
)
