# Copyright 2023-2024. WebPros International GmbH. All rights reserved.
# vim:ft=python:

include_defs('//product.defs.py')


python_binary(
    name = 'ubuntu18to20.pex',
    platform = 'py3',
    build_args = ['--python-shebang', '/usr/bin/env python3'],
    main_module = 'ubuntu18to20.main',
    deps = [
        'dist-upgrader//pleskdistup:lib',
        '//ubuntu18to20:lib',
    ],
)

genrule(
    name = 'ubuntu18to20',
    srcs = [':ubuntu18to20.pex'],
    out = 'ubuntu18to20',
    cmd = 'cp $(location :ubuntu18to20.pex) $OUT && chmod +x $OUT',
)
