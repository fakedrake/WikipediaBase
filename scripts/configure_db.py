#!/usr/bin/env python

"""
Configure the WikipediaBase backend
"""

from subprocess import check_output

from wikipediabase.dbutil import Article, db


def check_postgres_running():
    check_output(['pg_isready', '-h', 'localhost', '-p', '5432'])
    print "PostgreSQL is running"


def check_redis_running():
    check_output(['redis-cli', 'ping'])
    print "Redis is running"


def check_db_exists(name):
    out = check_output(['psql', '-U', 'postgres', '-h', 'localhost',
                        '-d', 'postgres', '-lqt'])
    databases = []
    for l in out.split('\n'):
        databases.append(l.split('|')[0].strip())
    assert(name in databases)


def check_user_exists(name):
    out = check_output(['psql', '-U', 'postgres', '-h', 'localhost',
                        '-d', 'postgres', '-t', '-c', '\du;'])
    users = []
    for l in out.split('\n'):
        users.append(l.split('|')[0].strip())
    assert(name in users)


def check_psql_command(cmd):
    check_output(['psql', '-U', 'postgres', '-h', 'localhost', '-c', cmd])


def create_database_and_role(name='wikipediabase'):
    try:
        check_db_exists(name)
    except:
        check_psql_command("CREATE DATABASE %s ENCODING 'utf8';" % name)
        check_db_exists(name)
    print "Created database"

    try:
        check_user_exists(name)
    except:
        check_psql_command('CREATE USER %s;' % name)
        check_psql_command('GRANT ALL PRIVILEGES ON DATABASE %s to %s;' %
                           (name, name))
        check_user_exists(name)
    print "Created role"


def create_tables():
    db.connect()
    Article.create_table(fail_silently=True)
    print "Created tables"


def configure():
    print "Setting up the WikipediaBase backend"

    check_postgres_running()
    check_redis_running()
    create_database_and_role()
    create_tables()

    print "Successfully configured the WikipediaBase backend"


if __name__ == '__main__':
    configure()
