from g5dbc.manager.options.from_args import from_args


def test_cmd_args_add_artifact(tmp_path):
    bench_dir = tmp_path / "curr" / "bench" / "work"
    artfs_dir = tmp_path / "artifacts" / "arm64" / "objects"
    conf_dir = tmp_path / "user" / "config"
    data_dir = tmp_path / "user" / "shared"

    bench_dir.mkdir(parents=True)
    artfs_dir.mkdir(parents=True)
    conf_dir.mkdir(parents=True)
    data_dir.mkdir(parents=True)

    file1 = tmp_path / "artifacts" / "arm64" / "objects" / "disk.img"
    file2 = tmp_path / "artifacts" / "index.yaml"
    file3 = conf_dir / "artifacts.yaml"

    file1.touch()
    file2.touch()
    file3.touch()

    # Test command line options
    cmd_line = f"-a {file1}".split()
    opts = from_args(
        conf_dir=conf_dir,
        data_dir=data_dir,
        args=cmd_line,
    )
    assert opts.command == "resource_add"
    assert file1.samefile(opts.resource_add)
    assert file3.samefile(opts.artifact_index[0])

    # Test command line options
    cmd_line = f"-a {file1} -i {file2}".split()
    opts = from_args(
        conf_dir=conf_dir,
        data_dir=data_dir,
        args=cmd_line,
    )
    assert opts.command == "resource_add"
    assert file1.samefile(opts.resource_add)
    assert file2.samefile(opts.artifact_index[0])


def test_cmd_args_del_artifact(tmp_path):
    bench_dir = tmp_path / "curr" / "bench" / "work"
    artfs_dir = tmp_path / "artifacts" / "arm64" / "objects"
    conf_dir = tmp_path / "user" / "config"
    data_dir = tmp_path / "user" / "shared"

    bench_dir.mkdir(parents=True)
    artfs_dir.mkdir(parents=True)
    conf_dir.mkdir(parents=True)
    data_dir.mkdir(parents=True)

    file1 = tmp_path / "artifacts" / "arm64" / "objects" / "disk.img"
    file2 = tmp_path / "artifacts" / "index.yaml"
    file3 = conf_dir / "artifacts.yaml"

    file1.touch()
    file2.touch()
    file3.touch()

    # Test command line options
    cmd_line = f"-d {file1}".split()
    opts = from_args(
        conf_dir=conf_dir,
        data_dir=data_dir,
        args=cmd_line,
    )
    assert opts.command == "resource_del"
    assert file1.samefile(opts.resource_del)
    assert file3.samefile(opts.artifact_index[0])

    # Test command line options
    cmd_line = f"-d {file1} -i {file2}".split()
    opts = from_args(
        conf_dir=conf_dir,
        data_dir=data_dir,
        args=cmd_line,
    )
    assert opts.command == "resource_del"
    assert file1.samefile(opts.resource_del)
    assert file2.samefile(opts.artifact_index[0])
