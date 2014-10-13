"""
This file is the frontend

It helps comparing dirs and directly logs it in the db,
and generate reports
"""

from backend import report
from backend import compare
from backend import sqlite_manager
import os
import argparse
import sys


def error(msg):
    """
    error :: String -> Exits

    print an error message and exit the program with status 1
    """
    print "ERROR: "+msg
    sys.exit(1)


def create_db_conn():
    """
    create_db_conn :: SqliteConnection

    Wrapper to create the database connection to db/data.sqlite
    """
    try:
        db_conn = sqlite_manager.get_db_connection("db/data.sqlite")
    except Exception, e:
        error("Could not connect to database, check if db/data.sqlite exists.")
    return db_conn


def compare_external(dir1, dir2):
    """
    compare_external :: String -> String -> Void

    Wrapper to compare 2 dirs and save the result in the db/data.sqlite
    """
    if not os.path.exists(dir1) or not os.path.exists(dir2):
        error(dir1 + " or " + dir2 + " doesn't exist.")
    comparison_result = compare.compare_dirs(dir1, dir2)
    db_conn = create_db_conn()
    sqlite_manager.insert_external_comp_into_db(
        db_conn,
        dir1,
        dir2,
        comparison_result
    )
    print(
        "Inserted comparison between " +
        dir1 +
        " and " +
        dir2 +
        " successfully into the databse"
    )


def compare_internal(directory):
    """
    compare_internal :: String -> Void

    Wrapper to compare a dir internally and save the result in the
    db/data.sqlite
    """
    if not os.path.exists(directory):
        error(directory+" doesn't exist.")
    comparison_result = compare.compare_same_dir(directory)
    db_conn = create_db_conn()
    sqlite_manager.insert_internal_comp_into_db(
        db_conn,
        directory,
        comparison_result
    )
    print(
        "Inserted internal comparison of " +
        directory +
        " successfully into the database"
    )


def generate_internal_report(name, number):
    """
    generate_internal_report :: String -> Int -> Void

    Wrapper to compare a dir internally and save the report in reports dir
    """
    try:
        report.create_report(name, "reports", "internal", number)
    except Exception, e:
        error(e)


def generate_external_report(name, number):
    """
    generate_external_report :: String -> Int -> Void

    Wrapper to compare 2 dirs and save the report in the reports dir
    """
    try:
        report.create_report(name, "reports", "external", number)
    except Exception, e:
        error(e)


def handle_report_args(args):
    if len(args) < 3:
        print """For report generation please specify the following:
type name number

type  :  internal or external
name  :  the name of the report
number:  the number of section the report will contain
"""
    if args[0] == "external":
        generate_external_report(args[1], int(args[2]))
    elif args[0] == "internal":
        generate_internal_report(args[1], int(args[2]))
    else:
        print "The type can be or 'external' or 'internal'"
        sys.exit(1)


def handle_comparison_args(args):
    if args[0] == "external":
        if len(args) < 3:
            print "For external report please specify two directories"
        else:
            compare_external(args[1], args[2])
    elif args[0] == "internal":
        if len(args) < 2:
            print "For internal report please specify one directory"
        else:
            compare_internal(args[1])
    else:
        print "The type can be or 'external' or 'internal'"
        sys.exit(1)


HELP = "Usage: " + sys.argv[0] + " [OPTION...]" + """

  -c, --compare [type] [arg] Compare directory depending on the type:
    the type can be "external" or "internal"
    for "internal" you have to specify one directory
    for "external you have to specify two directories

  -r, --report [type] [name] [number]
                             generate a report of type [type] with the name
                             [name] compose of less than [number] of sections
    the type can be "external" or "internal"

"""

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print HELP
        sys.exit(0)
    if "compare" in sys.argv[1] or sys.argv[1] == "-c":
        handle_comparison_args(sys.argv[2:])
    elif "report" in sys.argv[1] or sys.argv[1] == "-r":
        handle_report_args(sys.argv[2:])
    else:
        print HELP
