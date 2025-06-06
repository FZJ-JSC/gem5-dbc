from g5dbc.util import files


def test_files_find(tmp_path):
    bench_dir = tmp_path / "curr" / "bench" / "work"
    other_dir = tmp_path / "other"

    bench_dir.mkdir(parents=True)
    other_dir.mkdir(parents=True)

    file1 = tmp_path / "curr" / "bench1.py"
    file2 = tmp_path / "other" / "bench2.py"
    file3 = tmp_path / "curr" / "bench" / "main.py"

    file1.touch()
    file2.touch()
    file3.touch()

    search_path = [tmp_path, tmp_path / "curr", tmp_path / "other"]

    # Test files.find
    assert file1.samefile(files.find("bench1.py", *search_path))
    assert file1.samefile(files.find("bench1", *search_path))
    assert file2.samefile(files.find("bench2.py", *search_path))
    assert file2.samefile(files.find("bench2", *search_path))
    assert file3.samefile(files.find("bench", *search_path))
    assert file3.samefile(files.find(str(file3), *search_path))
