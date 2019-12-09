import os
import logging
from sqlalchemy import engine_from_config
from configparser import ConfigParser
import re

logger = logging.getLogger(__name__)


def get_dbpath():
    path_filename = os.getenv("ACLIB_DBPATH_FILE", "/lifecycle/.dbpath")
    if not os.path.exists(path_filename):
        logger.debug(f"Could not find dbpath file {path_filename}")
        return None, None
    with open(path_filename, 'r') as path_file:
        lines = path_file.readlines()
        if len(lines) == 0:
            logger.debug(f"Could not parse dbpath file: {path_filename} is empty")
            return None, None
        first_line = lines[0].rstrip()
        # Split at "." character
        # This should have resulted in two substrings
        split_arr = re.split("\".\"", first_line)
        if len(split_arr) != 2:
            logger.debug(
                f"Could not parse dbpath file: pattern \".\" not found in {path_filename}. Are the names escaped with double quotes?")
            return None, None
        # Split removes the two quotes
        db_name = split_arr[0] + "\""
        schema_name = "\"" + split_arr[1]
        logger.debug(f"Found database = {db_name}, schema = {schema_name} in dbpath file {path_filename}")

        return db_name, schema_name


def get_url(db_name=None, schema_name=None):
    username_filename = os.getenv("ACLIB_USERNAME_FILENAME", "/secrets/username")
    snowflake_access_token_filename = os.getenv("ACLIB_SNOWFLAKE_ACCESSS_TOKEN_FILENAME",  "/secrets/snowflake_access_token")
    credential_section = os.getenv("ACLIB_CREDENTIAL_SECTION", "nuvolos")
    if not os.path.exists(username_filename) and not os.path.exists(snowflake_access_token_filename):
        credential_filename = os.getenv("ACLIB_CREDENTIAL_FILENAME", os.path.expanduser("~") + "/.odbc.ini")
        if not os.path.exists(credential_filename):
            raise FileNotFoundError(f"Credentials file {credential_filename} not found")
        # Create engine with credentials
        cred = ConfigParser(interpolation=None)
        cred.read(credential_filename)
        credd = dict(cred.items(credential_section))
        snowflake_host = credd.get('host', "alphacruncher.eu-central-1")
        url = 'snowflake://' + credd['uid'] + ':' + credd['pwd'] + '@' + snowflake_host + '/?warehouse=' + credd['uid']
        masked_url = 'snowflake://' + credd['uid'] + ':********' + '@' + snowflake_host + '/?warehouse=' + credd['uid']
    else:
        with open(username_filename) as username, open(snowflake_access_token_filename) as access_token:
            cred_username = username.readline()
            cred_snowflake_access_token = access_token.readline()
        credd = {'username': cred_username}
        credd['snowflake_access_token'] = cred_snowflake_access_token
        snowflake_host = os.getenv("ACLIB_SNOWFLAKE_HOST", "alphacruncher.eu-central-1")
        url = 'snowflake://' + credd['username'] + ':' + credd[
            'snowflake_access_token'] + '@' + snowflake_host + '/?warehouse=' + credd['username']
        masked_url = 'snowflake://' + credd['username'] + ':********' + '@' + snowflake_host + '/?warehouse=' + credd[
            'username']

    app_db_name, app_schema_name = get_dbpath()
    db_name = db_name or app_db_name
    schema_name = schema_name or app_schema_name
    if db_name:
        url = url + '&database=' + db_name
        masked_url = masked_url + '&database=' + db_name
        if schema_name:
            url = url + '&schema=' + schema_name
            masked_url = masked_url + '&schema=' + schema_name
    logger.debug('Built SQLAlchemy URL: ' + masked_url)
    return url

def get_engine(db_name=None, schema_name=None):
    return engine_from_config({'sqlalchemy.url': get_url(db_name, schema_name), 'sqlalchemy.echo': False})


'snowflake://vinczeb:X0eKHrchduswy3Qt@alphacruncher.eu-central-1/?warehouse=vinczeb&database=STAGING/summer_school/module_1, group_1/development&schema="group_1/development"'