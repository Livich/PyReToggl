from RBNameHelper import RBNameHelper


def test_name_to_project():
    cases = {
        'MNT-228': '000000276',
        'CYB-1234': '000000084',
        'ET-0': '000000277',
        'HIVE-88': '000000297',
        'Collaboration - development': '000000084',
        'collaboration - maintenance': '000000276'
    }
    for ticket, proj_id in cases.items():
        assert proj_id == RBNameHelper.conv_task_name_auto(ticket, RBNameHelper.NAME_TO_PROJECT_ID)

def test_name_to_task_name():
    cases = {
        'collaboration (scrums time)': 'Calling, Collaboration',
        'CYB-1234': 'CYB-1234'
    }
    for ticket, task_name in cases.items():
        assert task_name == RBNameHelper.conv_task_name_auto(ticket, RBNameHelper.NAME_TO_TASK_NAME)