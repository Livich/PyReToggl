import re


class RBNameHelper:
    class NameConversionError(Exception):
        pass

    NAME_TO_PROJECT_ID = 1
    NAME_TO_TASK_NAME = 0

    __prekrasnyy_format = r"(?P<ticket>(\w*-\d*))"

    __patterns = []

    def __init__(self, patterns):
        self.__patterns = patterns

    @staticmethod
    def conv_task_name_auto(name, conversion_method):
        this = RBNameHelper(
            [
                ('mnt-', '000000276'),
                ('cyb-', '000000084'),
                ('et-', '000000277'),
                ('hive-', '000000297'),
                ('collaboration - development', '000000084'),
                ('collaboration - maintenance', '000000276')
            ]
        )
        return this.conv_task_name(name, conversion_method)

    def conv_task_name(self, name, conversion_method):
        """Converts task name to project ID or to ReToggl task name

        Keyword arguments:
            name                --  the task name
            conversion_method   --  set to NAME_TO_PROJECT_ID when conversion to project id is needed
                                    or to NAME_TO_TASK_NAME when name prettifying needed
        """
        if conversion_method == RBNameHelper.NAME_TO_PROJECT_ID:
            return self.__name_to_project_id(name)
        if conversion_method == RBNameHelper.NAME_TO_TASK_NAME:
            return self.__name_to_task_name(name)

    def __name_to_project_id(self, name):
        for pattern, projectId in self.__patterns:
            if pattern in name.lower():
                return projectId
        raise RBNameHelper.NameConversionError("Cannot convert [%s] to project ID" % name)

    def __name_to_task_name(self, name):
        # FIXME: dirty hack to apply ticket names
        if 'collaboration' in name.lower():
            return 'Calling, Collaboration'

        items = RBNameHelper.__split(name)
        return items["ticket"]

    @staticmethod
    def __split(name: str):
        matched = re.match(RBNameHelper.__prekrasnyy_format, name).groupdict()
        if len(matched) == 0:
            raise RBNameHelper.NameConversionError("Cannot apply regexp to [%s]" % name)
        return matched
