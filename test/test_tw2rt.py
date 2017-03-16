import subprocess


def test_entry_duplication():
    try:
        subprocess.check_output([
            "python3",
            "tw2rt.py",
            "-v 4",
            "-f 13/03/2017T08:00",
            "-t 13/03/2017T23:59",
            "-S 1"
        ])
        assert False
    except subprocess.CalledProcessError as ex:
        assert "at least one time entry to duplicate" in ex.output.decode("utf-8")
