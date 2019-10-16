aclib - The alphacruncher python library
========================================

Installation
============

.. code:: bash

    $ pip install aclib

Usage
=====
The library provides 2 convenience functions for connecting to the remote database with your credentials.
It assumes that you have a credential file ``~/.odbc.ini`` in the following format

::

    [datahub]
    uid = <username>
    pwd = <password>

You can then get the SQLAlchemy connection string, or create an SQLAlchemy engine directly:

::

    >>> from aclib import get_url, get_engine
    >>> get_url()
    'snowflake://<username>:<password>@alphacruncher.eu-central-1/?warehouse=<username>'
    >>> get_url("db_name","schema_name")
    'snowflake://<username>:<password>@alphacruncher.eu-central-1/?warehouse=<username>&database=db_name&schema=schema_name'
    >>> eng = get_engine("db_name","schema_name")

Source: https://github.com/datahub-ac/python-connector