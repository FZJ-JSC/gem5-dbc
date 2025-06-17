from pathlib import Path

from g5dbc.manager.options.from_args import from_args
from g5dbc.manager.resources.resource_add import resource_add
from g5dbc.manager.resources.resource_del import resource_del

_arch = """arm64:
"""

_resource = """\
- bintype: {}
  name: {}
  version: {}
  metadata: {}
  path: {}
  md5hash: d41d8cd98f00b204e9800998ecf8427e
"""


def test_resource_db_add(tmp_path: Path):
    bench_dir = tmp_path / "curr" / "bench" / "work"
    artfs_dir = tmp_path / "artifacts" / "arm64" / "objects"
    conf_dir = tmp_path / "user" / "config"
    data_dir = tmp_path / "user" / "shared"

    bench_dir.mkdir(parents=True)
    artfs_dir.mkdir(parents=True)
    conf_dir.mkdir(parents=True)
    data_dir.mkdir(parents=True)

    disk_file = tmp_path / "artifacts" / "arm64" / "objects" / "disk.img"
    boot_file = tmp_path / "artifacts" / "arm64" / "objects" / "boot.arm64-V2"
    linux_img = tmp_path / "artifacts" / "arm64" / "objects" / "vmlinux"
    index_yml = tmp_path / "artifacts" / "index.yaml"
    file4 = conf_dir / "artifacts.yaml"
    file5 = bench_dir / "work.yaml"

    disk_file.touch()
    boot_file.touch()
    linux_img.touch()
    index_yml.touch()
    file4.touch()

    # Add disk.img to index in user_config_dir
    A = "arm64"
    T = "DISK"
    N = "disk.img"
    V = "debian"
    M = "/dev/vda2"
    a = disk_file
    cmd_line = f"-a {a} -A {A} -T {T} -N {N} -V {V} -M {M}".split()
    expect_0 = _arch + _resource.format(T, N, V, M, a)
    resource_add(
        from_args(
            conf_dir=conf_dir,
            data_dir=data_dir,
            args=cmd_line,
        )
    )
    assert file4.read_text(encoding="utf-8") == expect_0

    # Add disk.img to artifacts/index.yaml
    # Path should be relative
    A = "arm64"
    T = "DISK"
    N = "disk.img"
    V = "debian"
    M = "/dev/vda2"
    a = disk_file
    i = index_yml.parent
    cmd_line = f"-a {a} -i {i} -A {A} -T {T} -N {N} -V {V} -M {M}".split()
    expect_0 = _arch + _resource.format(T, N, V, M, a.relative_to(i))
    resource_add(
        from_args(
            conf_dir=conf_dir,
            data_dir=data_dir,
            args=cmd_line,
        )
    )
    assert i.joinpath("index.yaml").read_text(encoding="utf-8") == expect_0

    # Add disk.img to bench_dir
    A = "arm64"
    T = "DISK"
    N = "disk.img"
    V = "debian"
    M = "/dev/vda2"
    a = disk_file
    i = bench_dir
    cmd_line = f"-a {a} -i {i} -A {A} -T {T} -N {N} -V {V} -M {M}".split()
    expect_0 = _arch + _resource.format(T, N, V, M, a)
    resource_add(
        from_args(
            conf_dir=conf_dir,
            data_dir=data_dir,
            args=cmd_line,
        )
    )
    assert i.joinpath("index.yaml").read_text(encoding="utf-8") == expect_0

    # Add disk.img to bench_dir/work.yaml
    A = "arm64"
    T = "DISK"
    N = "disk.img"
    V = "debian"
    M = "/dev/vda2"
    a = disk_file
    i = file5
    cmd_line = f"-a {a} -i {i} -A {A} -T {T} -N {N} -V {V} -M {M}".split()
    expect_0 = _arch + _resource.format(T, N, V, M, a)
    resource_add(
        from_args(
            conf_dir=conf_dir,
            data_dir=data_dir,
            args=cmd_line,
        )
    )
    assert i.read_text(encoding="utf-8") == expect_0

    # Update disk.img in artifacts/index.yaml
    A = "arm64"
    T = "DISK"
    N = "disk.img"
    V = "debian-testing"
    M = "/dev/vda2"
    a = disk_file
    i = index_yml.parent
    cmd_line = f"-a {a} -i {i} -A {A} -T {T} -N {N} -V {V} -M {M}".split()
    expect_1 = _arch + _resource.format(T, N, V, M, a.relative_to(i))
    resource_add(
        from_args(
            conf_dir=conf_dir,
            data_dir=data_dir,
            args=cmd_line,
        )
    )
    assert i.joinpath("index.yaml").read_text(encoding="utf-8") == expect_1

    # Add boot.arm64 to artifacts/index.yaml
    A = "arm64"
    T = "BOOT"
    N = "boot.arm64"
    V = "V2"
    M = "V2"
    a = boot_file
    i = index_yml.parent
    cmd_line = f"-a {a} -i {i} -A {A} -T {T} -N {N} -V {V} -M {M}".split()
    expect_2 = expect_1 + _resource.format(T, N, V, M, a.relative_to(i))
    resource_add(
        from_args(
            conf_dir=conf_dir,
            data_dir=data_dir,
            args=cmd_line,
        )
    )
    assert i.joinpath("index.yaml").read_text(encoding="utf-8") == expect_2

    # Add Linux Kernel to artifacts/index.yaml
    A = "arm64"
    T = "KERNEL"
    N = "vmlinux"
    V = "5.15.68"
    M = "earlyprintk=pl011,0x1c090000 console=ttyAMA0 lpj=19988480 norandmaps rw loglevel=8"
    a = linux_img
    i = index_yml.parent
    cmd_line = f"-a {a} -i {i} -A {A} -T {T} -N {N} -V {V} -M".split() + [M]
    expect_3 = expect_2 + _resource.format(T, N, V, M, a.relative_to(i))
    expect_4 = expect_1 + _resource.format(T, N, V, M, a.relative_to(i))
    resource_add(
        from_args(
            conf_dir=conf_dir,
            data_dir=data_dir,
            args=cmd_line,
        )
    )
    assert i.joinpath("index.yaml").read_text(encoding="utf-8") == expect_3

    # Remove boot.arm64 from artifacts/index.yaml
    d = boot_file
    i = index_yml.parent
    cmd_line = f"-d {d} -i {i}".split()
    resource_del(
        from_args(
            conf_dir=conf_dir,
            data_dir=data_dir,
            args=cmd_line,
        )
    )
    assert i.joinpath("index.yaml").read_text(encoding="utf-8") == expect_4
