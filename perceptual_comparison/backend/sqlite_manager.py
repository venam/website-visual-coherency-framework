#!/usr/bin/env python2


"""
Copyright (c) 2014, Patrick Louis <patrick at iotek do org>
All rights reserved.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    1.  The author is informed of the use of his/her code. The author does not
        have to consent to the use; however he/she must be informed.
    2.  If the author wishes to know when his/her code is being used, it the
        duty of the author to provide a current email address at the top of
        his/her code, above or included in the copyright statement.
    3.  The author can opt out of being contacted, by not providing a form of
        contact in the copyright statement.
    4.  If any portion of the author's code is used, credit must be given.
            a. For example, if the author's code is being modified and/or
               redistributed in the form of a closed-source binary program,
               then the end user must still be made somehow aware that the
               author's work has contributed to that program.
            b. If the code is being modified and/or redistributed in the form
               of code to be compiled, then the author's name in the copyright
               statement is sufficient.
    5.  The following copyright statement must be included at the beginning of
        the code, regardless of binary form or source code form.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Except as contained in this notice, the name of a copyright holder shall not
be used in advertising or otherwise to promote the sale, use or other dealings
in this Software without prior written authorization of the copyright holder.

----

The database handler/manager.

"""

import sqlite3


def get_db_connection(db_name):
    """
    get_db_connection :: String -> Sqlite3ConnectionData

    Takes the location of the db and connects to it
    Returns the connection data needed for the other functions
    """
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    return (conn, c)


def db_timestamp(db_conn):
    """
    db_timestamp :: Sqlite3ConnectionData -> String

    Takes an Sqlite3 opened connection
    Returns the timestamp generated by the db
    """
    return db_conn[1].execute(
        "select CURRENT_TIMESTAMP;"
    ).next()[0]


def try_insert_in_db(db_conn, foo, data, dir1, dir2=""):
    """
    try_insert_in_db :: Sqlite3ConnectionData -> (Sqlite3ConnectionData ->
        (String||String->String) -> Hash -> String -> Void)
                     -> Hash -> String -> String -> Bool

    A helper function to directly try inserting data in the db
    Returns a Bool (True on success, False on error)

    The function passed as argument should do the inserting job
    """
    try:
        current_timestamp = db_timestamp(db_conn)
        if dir2 == "":
            foo(db_conn, dir1, data, current_timestamp)
        else:
            foo(db_conn, dir1, dir2, data, current_timestamp)
        db_conn[0].commit()
    except Exception, e:
        print e
        return False
    return True


def do_insert_internal_in_db(db_conn, directory, data, current_timestamp):
    """
    do_insert_internal_in_db :: Sqlite3ConnectionData -> String
                          -> {(String, String) : Float,... } -> Void

    Do the actual insertion for insert_internal_comp_into_db
    """
    db_conn[1].execute(
        ("insert into internal_comparisons (directory,timestamp) " +
            "values (" +
            "'" + directory + "'," +
            "'" + current_timestamp + "');")
    )

    inserted_id = db_conn[1].execute(
        "select max(id) from internal_comparisons;"
    ).next()[0]

    for key in data:
        db_conn[1].execute(
            ("insert into internal_comparisons_results values (" +
                "'" + key[0] + "'," +
                "'" + key[1] + "'," +
                str(data[key]) + "," +
                str(inserted_id) +
                ");")
        )


def insert_internal_comp_into_db(db_conn, directory, data):
    """
    insert_internal_comp_into_db :: Sqlite3ConnectionData -> String
                                 -> {(String, String) : Float,... } -> Bool

    Takes an Sqlite3 opened connection, the directory that we've grabbed the
    data from and the actual result of the internal comparison.
    Returns False if the insert didn't work, True otherwise

    The table schema is the following:

    create table internal_comparisons (
        id integer primary key,
        directory text,
        timestamp date
    );
    directory should be a unique name

    The results are stored in a related table:
    create table internal_comparisons_results (
        first_image text,
        second_image text,
        distance double,
        comparison_id integer
    );
    directory is a foreign key that references internal_comparisons(directory)
    """
    return try_insert_in_db(
        db_conn,
        do_insert_internal_in_db,
        data, directory
    )


def do_insert_external_in_db(db_conn, dir1, dir2, data, current_timestamp):
    """
    do_insert_external_in_db :: Sqlite3ConnectionData -> String -> String
                        -> { String : Float,... } -> Void

    Do the actual insertion for insert_external_comp_into_db
    """
    db_conn[1].execute(
        ("insert into external_comparisons (directory1,directory2,timestamp) "
            + "values (" +
            "'" + dir1 + "'," +
            "'" + dir2 + "'," +
            "'" + current_timestamp + "');")
    )

    inserted_id = db_conn[1].execute(
        "select max(id) from external_comparisons;"
    ).next()[0]

    for key in data:
        db_conn[1].execute(
            ("insert into external_comparisons_results values (" +
                "'" + key + "'," +
                str(data[key]) + "," +
                str(inserted_id) +
                ");")
        )


def insert_external_comp_into_db(db_conn, dir1, dir2, data):
    """
    insert_external_comp_into_db :: Sqlite3ConnectionData -> String -> String
                                 -> { String : Float,... } -> Bool

    Takes an Sqlite3 opened connection, the 2 directory that we've compared
    and the data results of the comparison.
    Returns False if the insertion fails, True otherwise

    The table schema is the following:
    create table external_comparisons (
        id integer primary key,
        directory1 text,
        directory2 text,
        timestamp  date
    );

    The results are stored in a related table:
    create table external_comparisons_results (
        image text,
        distance double,
        comparison_id integer
    );
    directory is a foreign key that references external_comparisons(directory)
    """
    return try_insert_in_db(
        db_conn,
        do_insert_external_in_db,
        data,
        dir1,
        dir2
    )


def last_n_internal_comparisons(db_conn, n):
    """
    last_n_internal_comparisons :: Sqlite3ConnectionData -> Int -> [String]

    Takes an Sqlite3 opened connection and a number n, the last n perceptual
    tests

    Do something like the following:
    select *
        from
            internal_comparisons, internal_comparisons_results
        where
            comparison_id=id
        order by id DESC;
    """
    query = db_conn[1].execute(
        "select *" +
        "from internal_comparisons, internal_comparisons_results " +
        "where comparison_id=id " +
        "order by id DESC;"
    )
    results = query.fetchall()

    results_less_than_n = []
    temp_results = []
    current_date = ""

    for result in results:
        if result[2] != current_date:
            current_date = result[2]
            if temp_results != []:
                results_less_than_n.append(temp_results)
                temp_results = []
            n = n-1
            if n < 0:
                break
        temp_results.append(result)
    if temp_results != []:
        results_less_than_n.append(temp_results)
    return results_less_than_n


def last_n_external_comparisons(db_conn, n):
    """
    last_n_external_comparisons :: Sqlite3ConnectionData -> Int -> [String]

    Takes an Sqlite3 opened connection and a number n, the last n perceptual
    tests

    Do something like the following:
    select *
        from
            external_comparisons, external_comparisons_results
        where
            comparison_id=id
        order by id DESC;
    """
    query = db_conn[1].execute(
        "select *" +
        "from external_comparisons, external_comparisons_results " +
        "where comparison_id=id " +
        "order by id DESC;"
    )
    results = query.fetchall()

    results_less_than_n = []
    temp_results = []
    current_date = ""

    for result in results:
        if result[3] != current_date:
            current_date = result[3]
            if temp_results != []:
                results_less_than_n.append(temp_results)
                temp_results = []
            n = n-1
            if n < 0:
                break
        temp_results.append(result)
    if temp_results != []:
        results_less_than_n.append(temp_results)
    return results_less_than_n