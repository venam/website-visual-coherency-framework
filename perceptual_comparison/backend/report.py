import os
import sqlite_manager
import adapter
import shutil
from distutils import dir_util


def manage_report_dir(location, report_name):
    """
    manage_report_dir :: String -> String -> Void

    Takes a location (should exist) and a report name

    It will create a dir in that location with the same name as the report
    and initiate it with the appropriate files needed to create a report
    """
    # create the report directory
    if not os.path.exists(location + '/' + report_name):
        os.mkdir(location + '/' + report_name)
    if not os.path.exists(location + '/' + report_name + '/static'):
        # copy the initial data
        shutil.copytree(
            'content/static',
            location + '/' + report_name + '/static'
        )


def get_data_from_db(report_type, number_of_sections, location):
    """
    get_data_from_db :: String -> Int -> String -> [(data)]

    Take a report type (internal, external), a number of sections, and
    the location where the report is being created

    It will fetch the data from the db, and copy the dirs to the location

    Returns the data fetched from the db
    """
    db_conn = sqlite_manager.get_db_connection("db/data.sqlite")
    result = None
    if report_type == "external":
        result = sqlite_manager.last_n_external_comparisons(
            db_conn,
            number_of_sections
        )
    elif report_type == "internal":
        result = sqlite_manager.last_n_internal_comparisons(
            db_conn,
            number_of_sections
        )
    else:
        raise ("report type can only be 'internal' or 'external'")

    list_of_adapted_data = []
    if report_type == "external":
        for d in result:
            last_name1 = d[0][1].rstrip("/").split("/")[-1:][0]
            last_name2 = d[0][2].rstrip("/").split("/")[-1:][0]
            shutil.copytree(d[0][1], location + '/' + last_name1)
            shutil.copytree(d[0][2], location + '/' + last_name2)
            list_of_adapted_data.append(
                adapter.sqlite_external_to_report_external(d)
            )
    else:
        for d in result:
            last_name = d[0][1].rstrip("/").split("/")[-1:][0]
            shutil.copytree(d[0][1], location + '/' + last_name)
            list_of_adapted_data.append(
                adapter.sqlite_internal_to_report_internal(d)
            )
    return list_of_adapted_data


def create_report(
        report_name,
        location,
        report_type,
        number_of_sections):
    """
    create_report :: String -> String -> String -> Int -> Bool

    Takes the name of the report, the location where it's going to be created
    (it should be an existing directory), the report type (internal, external)
    , and the number of sections that should be put in the report.

    Returns a Bool (True on success, False on Failure)
    """
    try:
        manage_report_dir(location, report_name)
    except Exception, e:
        print e
        return False
    try:
        data = get_data_from_db(
            report_type,
            number_of_sections,
            location + '/' + report_name
        )
    except Exception, e:
        print e
        return False

    os.chdir(location + '/' + report_name)
    output = ""
    if report_type == "external":
        output = generate_multiple_external_reports(
            report_name,
            data
        )
    else:
        output = generate_multiple_internal_reports(report_name, data)

    open("index.html", 'w').write(output)
    return True


def generate_multiple_external_reports(report_name, data):
    """
    generate_multiple_external_reports :: string -> [(data)] -> string

    Takes the report name and related list of external comparison data
    generate a report made of external comparisons
    returns it as a string
    """
    output = generate_header(report_name)
    counter = 1
    for d in data:
        output += '<section id=' + str(counter) + '>\n'
        output += create_external_comparison_section(
            d[0],       # name
            d[1],       # date1
            d[2],       # date2
            d[3],       # dir1
            d[4],       # dir2
            d[5]        # list_of_file_distance
        )
        output += '</section>\n'
        counter += 1
    output += generate_footer(counter)
    output += "</html>\n"
    return output


def generate_footer(number):
    """
    generate_footer :: Int -> String

    Takes a string corresponding to the number of section that has been created

    Returns the corresponding footer
    """
    output = """
            </div>
       </div>

        <footer>
            <div id="social_container">
                <div id="social">
                </div>
            </div>
            <div id="end_separator"></div>
            <div id="last_footer">
                <div id="internal">
"""
    for n in range(1, number):
        output += '<span id=i_link><a href="#' + str(number-1) + '">'
        output += 'link' + str(number-1)
        output += '</a>Comparison number ' + str(number-1)
        output += '</span>\n'
    output += """
                </div>
                <div id="contact">
                    <span id="email">&copy; patrick at iotek dot org </span>
                </div>
            </div>
        </footer>
    </body>
"""
    return output


def generate_multiple_internal_reports(report_name, data):
    """
    generate_multiple_internal_reports :: string -> [(data)] -> string

    Takes the report name and related list of internal comparison data
    generate a report made of external comparisons
    returns it as a string
    """

    output = generate_header(report_name)
    sections_list = []
    js_list = []
    for d in data:
        (section, js) = create_internal_comparison_section(
            d[0],      # name
            d[1],      # date
            d[2],      # directory
            d[3]       # list_of_file_distance
        )
        sections_list.append(section)
        js_list.append(js)
    counter = 1
    for section in sections_list:
        output += '<section id=' + str(counter) + '>\n'
        output += section + '\n'
        output += '</section>\n'
        counter += 1
    output += generate_footer(counter)
    output += '<script type="text/javascript">\n'
    for js in js_list:
        output += js + '\n'
    output += '</script>\n'
    output += '</html>\n'
    return output


def generate_header(report_name):
    """
    generate_header :: String -> String

    Takes a report name
    Returns the correponding header
    """
    return """
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8" />
        <meta http-equiv="X-UA-Compatible" content="IE=edge" />
        <link rel="stylesheet" href="static/report.css" type="text/css" />
        <script src="static/flotr2.min.js"></script>
        <title>REPORT_NAME</title>
    </head>

    <body>

        <header>
            <div id="home_container">
                <a href=""><span id="home">REPORT_NAME</span></a>
            </div>
            <nav>
            </nav>
        </header>
        <div id="separator"></div>

        <div id="container">
            <div id="content">
""".replace("REPORT_NAME", report_name)


def get_internal_average(list_of_file_distance):
    """
    get_internal_average :: [(String, String, Double)] -> String

    Takes a list of distance between files [(file1, file2, distance)]
    Returns the average distance between the files
    """
    length = len(list_of_file_distance)
    total = 0.0
    for f in list_of_file_distance:
        total += f[2]
    return str(float(total)/length)


def get_internal_minimum(list_of_file_distance):
    """
    get_internal_minimum :: [(String, String, Double)] -> String

    Takes a list of distance between files [(file1, file2, distance)]
    Returns the minimum distance between the files
    """
    minimum = list_of_file_distance[0][2]
    for f in list_of_file_distance:
        if f[2] < minimum:
            minimum = f[2]
    return str(minimum)


def get_internal_maximum(list_of_file_distance):
    """
    get_internal_maximum :: [(String, String, Double)] -> String

    Takes a list of distances between files [(file1, file2, distance)]
    Returns the maximum distance between the files
    """
    maximum = list_of_file_distance[0][2]
    for f in list_of_file_distance:
        if f[2] > maximum:
            maximum = f[2]
    return str(maximum)


def generate_image_part(img1, img2, distance, dir1, dir2):
    """
    generate_image_part :: String -> String -> Double -> String -> String
                         -> String

    Takes 2 images, their perceptual distance, and the 2 dirs their are in
    It also generates the image difference in a dir named:

    diff-dir1-dir2

    Note: dir1 and dir2 should be in at the first level and not sub-dirs

    The image will be named diff_inter-img1-img2.jpeg

    Returns the part of the HTML for the image comparisons
    """
    img_output_string = ""
    img_output_string += '\n<hr>\n<p>\n'
    img_output_string += '<strong>' + img1
    img_output_string += '</strong> vs <strong>' + img2
    img_output_string += '</strong><br/>\n'
    img_output_string += '<br/>\n'
    img_output_string += '<strong>' + str(distance) + '%</strong>'
    img_output_string += '  perceptual difference\n'
    img_output_string += '</p>\n'
    img_output_string += '<img class="image" '
    img_output_string += 'src="' + dir1 + '/' + img1
    img_output_string += '"></img>\n'
    img_output_string += '<img class="diff" src="static/diff.png"></img>\n'
    img_output_string += '<img class="image" '
    img_output_string += 'src="' + dir2 + '/' + img2
    img_output_string += '"></img>\n'
    img_output_string += '<img class="eq" src="static/eq.png"></img>\n'
    img_output_string += '<img class="image" '
    img_output_string += (
        'src="' +
        generate_image_diff(img1, img2, dir1, dir2) +
        '"></img>\n'
    )
    return img_output_string


def generate_image_diff(img1, img2, dir1, dir2):
    """
    generate_image_diff :: String -> String -> String -> String -> String

    Takes 2 images and 2 directories where those images are in.
    It will create the image difference in a dir named:

    'diff-' + dir1 + '-' + dir2 + '/' + 'diff_inter' + img1 + '-' + img2

    Note: dir1 and dir2 should be in at the first level and not sub-dirs

    Returns that string
    """
    # removes the '/' just to make sure they are not subdirs
    diff_dir_location = (
        'diff-' +
        dir1.replace('/', '') +
        '-' +
        dir2.replace('/', '')
    )
    if not os.path.exists(diff_dir_location):
        os.mkdir(diff_dir_location)
    command = 'convert '
    command += dir1 + '/' + img1 + ' '
    command += dir2 + '/' + img2 + ' '
    command += '-compose difference -composite -evaluate Pow 2 '
    command += '-evaluate divide 3 -separate -evaluate-sequence Add '
    command += '-evaluate Pow 0.5 '
    command += diff_dir_location + '/' + 'diff_inter' + img1 + '-' + img2
    os.system(command)
    return diff_dir_location + '/' + 'diff_inter' + img1 + '-' + img2


def generate_internal_images_part(directory, list_of_file_distance):
    """
    generate_internal_images_part :: String -> [(String, String, Double)]
                                 -> String

    Takes a directory and a list of distances between files.
    The directory should contain those files.
    It will also generate the image difference between the 2 files and add it
    to the directory

    Returns the HTML string that is needed: img1 inter img2 = img_diff
    """
    img_output_string = ""
    for comparison in list_of_file_distance:
        img_output_string += generate_image_part(
            comparison[0],
            comparison[1],
            comparison[2],
            directory,
            directory
        )
    return img_output_string


def generate_internal_distance_vars(list_of_file_distance):
    """
    generate_internal_distance_vars :: [(String, String, Double)] -> String

    Takes a list of distances between files

    Returns something in the following form:

    It would be better to have the distances in ascending or descending order
    var d1 = [[40,0],[0]];
    var d2 = [[20,1],[0]];
    var d3 = [[30,2],[0]];
    """
    output_var = ""
    counter = 0
    for distance in list_of_file_distance:
        output_var += 'var d' + str(counter) + ' = '
        output_var += (
            '[' +
            '[' + str(distance[2]) + ',' + str(counter) + '],' +
            '[0]];\n')
        counter += 1
    output_var += '\n'
    return output_var


def generate_internal_distance_vars_with_label(list_of_file_distance):
    """
    generate_internal_distance_vars_with_label :: [(String, String, Double)
                                               -> String

    Takes a list of distances between files

    Returns something in the following form:

    It would be better to have the distances in ascending or descending order
    {
        data: d1,
        label: "http://pageblh.org/nope/blah"
    },
    {
        data: d3,
        label: "http://lol.com"
    },
    {
        data: d2,
        label: "http://thisissparta.org"
    }
    """
    output_var = ""
    counter = 0
    for distance in list_of_file_distance:
        output_var += '{\n'
        output_var += 'data: d' + str(counter) + ',\n'
        output_var += 'label: "' + distance[0] + ' vs ' + distance[1] + '"\n'
        output_var += '},\n'
        counter += 1
    return output_var


def create_internal_comparison_section(
        name,
        date,
        directory,
        list_of_file_distance):
    """
    create_internal_comparison_section :: String -> String -> String
                                        -> [(String, String, Double)]
                                        -> (String, String)

    Takes the name of the internal comparison section (shouldn't clash with
    other names), the date it has been done, the directory it has been done on
    (note that this should be the location of that dir after it has been
    copied inside the report directory, so that it can be found by the page),
    and the list of distance between the files [(file1, file2, distance)]

    Returns a tuple containing the HTML and JS needed to create the section
    """

    # start of HTML
    output_string = ""
    output_string += '\n<h1>'+name+'</h1>\n'  # set the Header of the section
    output_string += '<h2>'+date+'</h2>\n'    # set the date of the section
    output_string += '<h3>Distance</h3>\n'
    # start of the Distance part graph
    output_string += '<div class="graph" id="'+name+'_graph" ></div>\n'
    # the id of the graph is alway name_graph
    output_string += '<h3>Statistic</h3>\n'   # start of the stats part
    output_string += '<table>\n'
    output_string += '<tr>\n'
    output_string += '<td><span class="blue">Average</span> Distance:</td>\n'
    output_string += (
        '<td><strong>' +
        get_internal_average(list_of_file_distance) +
        '%</strong></td>\n')
    output_string += '</tr>\n'
    output_string += '<tr>\n'
    output_string += '<td><span class="red">Maximum</span> Distance:</td>\n'
    output_string += (
        '<td><strong>' +
        get_internal_maximum(list_of_file_distance) +
        '%</strong></td>\n')
    output_string += '</tr>\n'
    output_string += '<tr>\n'
    output_string += '<td><span class="green">Minimum</span> Distance:</td>\n'
    output_string += (
        '<td><strong>' +
        get_internal_minimum(list_of_file_distance) +
        '%</strong></td>\n')
    output_string += '</tr>\n'
    output_string += '</table>\n'

    output_string += '<h3>Visual Differences</h3>\n'
    output_string += generate_internal_images_part(
        directory,
        list_of_file_distance
    )
    # end of HTML

    # start of JS
    output_script = ''
    output_script += '(function (container, horizontal) {\n'
    output_script += 'var horizontal = (horizontal ? true : false);\n'
    output_script += generate_internal_distance_vars(list_of_file_distance)
    output_script += 'Flotr.draw(\n'
    output_script += 'container, [ //-- changing values\n'
    output_script += generate_internal_distance_vars_with_label(
        list_of_file_distance
    )
    output_script += '],          //-- end of changing values\n'
    output_script += '{\n'
    output_script += 'bars: {\n'
    output_script += 'show: true,\n'
    output_script += 'horizontal: horizontal,\n'
    output_script += 'shadowSize: 0,\n'
    output_script += 'barWidth: 0.8\n'
    output_script += '},\n'
    output_script += 'HtmlText: false,\n'
    output_script += 'legend: {\n'
    output_script += "position: 'ne',\n"
    output_script += "backgroundColor: '#D2E8FF'\n"
    output_script += '},\n'
    output_script += 'mouse: {\n'
    output_script += 'trackFormatter: function(obj) {\n'
    output_script += 'return obj.x;\n'
    output_script += '},\n'
    output_script += 'track: true,\n'
    output_script += 'relative: true\n'
    output_script += '},\n'
    output_script += 'yaxis: {\n'
    output_script += 'showLabels: false,\n'
    output_script += 'min: 0,\n'
    output_script += 'autoscaleMargin: 1\n'
    output_script += '},\n'
    output_script += 'xaxis: {\n'
    output_script += 'title: "perceptual distance",\n'
    output_script += '}\n'
    output_script += '}\n'
    output_script += ');\n'
    output_script += '})(document.getElementById("'+name+'_graph"),true);\n'
    # end of JS

    return (output_string, output_script)


def generate_external_images_part(dir1, dir2, list_of_file_distance):
    """
    generate_external_images_part :: String -> String -> [(String, Double)]
                                  -> String

    Takes 2 directories and a list of distances between files.
    The directories should contain those files.
    It will also generate the image difference between the 2 files and add it
    to a new dir

    Returns the HTML string that is needed: img1 inter img2 = img_diff
    """
    img_output_string = ""
    for comparison in list_of_file_distance:
        img_output_string += generate_image_part(
            comparison[0],
            comparison[0],
            comparison[1],
            dir1,
            dir2
        )
    return img_output_string


def create_external_comparison_section(
        name,
        date1,
        date2,
        dir1,
        dir2,
        list_of_file_distance):
    """
    create_external_comparison_section :: String -> String -> String
                                       -> String -> String
                                       -> [(String, Double)]
                                       -> String

    Takes the name of the internal comparison section (shouldn't clash with
    other names), the dates they have been done respectively,
    the directories the comparison has been done on.
    (note that this should be the location of the dirs after they have been
    copied inside the report directory, so that it can be found by the page),
    and the list of distance between the files [(file1, file2, distance)]

    Returns a string containing the HTML needed to create the section
    """
    output_string = ''
    output_string += '<h1>' + name + '</h1>'
    output_string += '<h2>' + date1 + ' vs ' + date2 + '</h2>'
    output_string += '<h3>Visual Differences</h3>'
    output_string += generate_external_images_part(
        dir1,
        dir2,
        list_of_file_distance
    )
    return output_string
