from RBNameHelper import RBNameHelper


def test_name_to_project(rb_name_helper_preset):
    for ticket, proj_id in rb_name_helper_preset.items():
        assert proj_id == RBNameHelper.conv_task_name_auto(ticket, RBNameHelper.NAME_TO_PROJECT_ID)


def test_name_to_task_name():
    cases = {
        'collaboration (scrums time)': 'Calling, Collaboration',
        'CYB-1234': 'CYB-1234'
    }
    for ticket, task_name in cases.items():
        assert task_name == RBNameHelper.conv_task_name_auto(ticket, RBNameHelper.NAME_TO_TASK_NAME)