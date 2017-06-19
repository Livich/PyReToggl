import subprocess


def test_entry_duplication(tw2rt_profile_file_name):
    try:
        subprocess.check_output([
            "python",
            "tw2rt.py",
            "-v 4",
            "-f 01/06/2017T08:00",
            "-t 15/06/2017T23:59",
            "-S 1",
            "-p", tw2rt_profile_file_name
        ])
        assert False
    except subprocess.CalledProcessError as ex:
        assert "at least one time entry to duplicate" in ex.output.decode("utf-8")
