import pytest
import os
import configparser


def __config_file():
    return os.path.join(os.path.expanduser('~'), 'tw2rt.ini')


@pytest.fixture(scope="module")
def tw_config():
    if os.environ.get('CI') is None:
        config = configparser.ConfigParser()
        config.read(__config_file())
        return {
            "endpoint": config['teamwork']['endpoint'],
            "user_agent": config['general']['user_agent'],
            "api_key": config['teamwork']['api_key'],
            "password": config['teamwork']['api_pass']
        }
    else:
        return {
            "endpoint": os.environ.get('tw_endpoint', ''),
            "user_agent": os.environ.get('user_agent', ''),
            "api_key": os.environ.get('tw_api_key', ''),
            "password": os.environ.get('tw_api_pass', '')
        }


@pytest.fixture(scope="module")
def rt_config():
    if os.environ.get('CI') is None:
        config = configparser.ConfigParser()
        config.read(__config_file())
        return {
            "endpoint": config['retoggl']['endpoint'],
            "user_agent": config['general']['user_agent'],
            "user_token": config['retoggl']['user_token'],
            "ch_user_token": config['retoggl']['ch_user_token'],
            "user_id": config['retoggl']['user_id']
        }
    else:
        return {
            "endpoint": os.environ.get('rt_endpoint'),
            "user_agent": os.environ.get('user_agent'),
            "user_token": os.environ.get('rt_user_token'),
            "ch_user_token": os.environ.get('rt_ch_user_token'),
            "user_id": os.environ.get('rt_user_id')
        }


@pytest.fixture(scope="module")
def rb_name_helper_preset():
    return {
        'MNT-228': '000000276',
        'CYB-1234': '000000084',
        'ET-0': '000000277',
        'HIVE-88': '000000297',
        'Collaboration - development': '000000084',
        'collaboration - maintenance': '000000276'
    }


@pytest.fixture(scope="module")
def tw2rt_profile_file_name():
    if os.environ.get('CI') is None:
        return __config_file()
    else:
        # prepare temporary profile file from environment values
        config = configparser.ConfigParser()
        data = {
            'teamwork': tw_config(),
            'retoggl': rt_config(),
            'general': {
                'user_agent': os.environ.get('user_agent')
            },
            'rb_name_helper': rb_name_helper_preset()
        }
        # fallback for local testing CI integration
        if os.environ.get('CI') is None:
            data['general']['user_agent'] = 'CI'
        for section, params in data.items():
            config.add_section(section)
            for param, value in params.items():
                if value is not None:
                    config.set(section, param, value)

        f_name = './.tw2rt.ini'
        with open(f_name, 'w') as f:
            config.write(f)

        return f_name
