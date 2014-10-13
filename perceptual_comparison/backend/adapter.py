"""
A file that is an adapter from the sqlite_manager format to the report format
"""


def sqlite_internal_to_report_internal(data):
    """
    sqlite_internal_to_report_internal ::

    internal comparison
    [(2, u'test1', u'2014-10-11 15:23:55', u'out0025.jpeg', u'out0023.jpeg',
        34.9572011221, 2)]
        -> (name, date, directory, list_of_file_distance)

    with: list_of_file_distance ::  [(String, String, Double)]

    This takes in consideration the dir will be copied into the new directory
    """
    if data == []:
        return ()
    name = "Internal Comparison - " + data[0][2]
    # dates are in this format 2014_8_28_18_21_11 like the dirs
    date_b = data[0][1].split("/")[-1:][0].split("_")
    date = (
        date_b[0] + '/' + date_b[1] + '/' + date_b[2] + ' ' +
        date_b[3] + ':' + date_b[4] + ':' + date_b[5]
    )
    directory = data[0][1].split("/")[-1:][0]
    list_of_file_distance = []
    for comparison in data:
        list_of_file_distance.append(
            (comparison[3], comparison[4], comparison[5])
        )
    list_of_file_distance.sort(lambda x, y: int(10000*x[2]-10000*y[2]))
    return (
        name,
        date,
        directory,
        list_of_file_distance
    )


def sqlite_external_to_report_external(data):
    """
    sqlite_external_to_report_external ::
    [(3, u'test1', u'test2', u'2014-10-11 09:32:43', u'out0025.jpeg',
        0.00487451466591, 3)]
    -> (name, date1, date2, dir1, dir2, list_of_file_distance)

    with: list_of_file_distance ::  [(String, Double)]

    This takes in consideration the dir1 and dir2 will be copied into the new
    directory
    """
    if data == []:
        return ()
    name = "External Comparison  - " + data[0][3]
    # dates are in this format 2014_8_28_18_21_11 like the dirs
    date1_b = data[0][1].split("/")[-1:][0].split("_")
    date1 = (
        date1_b[0] + '/' + date1_b[1] + '/' + date1_b[2] + ' ' +
        date1_b[3] + ':' + date1_b[4] + ':' + date1_b[5]
    )
    date2_b = data[0][2].split("/")[-1:][0].split("_")
    date2 = (
        date2_b[0] + '/' + date2_b[1] + '/' + date2_b[2] + ' ' +
        date2_b[3] + ':' + date2_b[4] + ':' + date2_b[5]
    )
    dir1 = data[0][1].split("/")[-1:][0]
    dir2 = data[0][2].split("/")[-1:][0]
    list_of_file_distance = []
    for comparison in data:
        list_of_file_distance.append((comparison[4], comparison[5]))
    list_of_file_distance.sort(lambda x, y: int(10000*y[1]-10000*x[1]))
    return (
        name,
        date1,
        date2,
        dir1,
        dir2,
        list_of_file_distance
    )
