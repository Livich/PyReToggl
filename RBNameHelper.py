import re

class RBNameHelper:
    class NameConversionError(Exception):
        pass

    NAME_TO_PROJECT_ID = 1
    NAME_TO_TASK_NAME = 0

    __prekrasnyy_format = r"(?P<ticket>(\w*-\d*))"

    @staticmethod
    def conv_task_name(name, conversion_method):
        """Converts task name to project ID or to ReToggl task name

        Keyword arguments:
            name                --  the task name
            conversion_method   --  set to NAME_TO_PROJECT_ID when conversion to project id is needed
                                    or to NAME_TO_TASK_NAME when name prettifying needed
        """
        if conversion_method == RBNameHelper.NAME_TO_PROJECT_ID:
            return RBNameHelper.__name_to_project_id(name)
        if conversion_method == RBNameHelper.NAME_TO_TASK_NAME:
            return RBNameHelper.__name_to_task_name(name)

    @staticmethod
    def __name_to_project_id(name):
        # If ticket name matches pattern, use well-known project
        if 'mnt-' in name.lower():
            return '000000276'  # Maintenance
        if 'cyb-' in name.lower():
            return '000000084'  # Development
        if 'et-' in name.lower():
            return '000000277'  # Elm Tree Project
        if 'hive-' in name.lower():
            return '000000297'  # HIVE project
        if 'collaboration' in name.lower() and 'development' in name.lower():
           return '000000084' # Development
        if 'collaboration' in name.lower() and 'maintenance' in name.lower():
           return '000000276' # Maintenance

        raise RBNameHelper.NameConversionError("Cannot convert [%s] to project ID" % name)

    @staticmethod
    def __name_to_task_name(name):
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