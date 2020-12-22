#!/usr/bin/env python3

import re
import sys

next_year = '2021'

ended = False
started = False

line_regex = re.compile('^{ year: (?P<year>\d+), month: (?P<month>\d+), day: (?P<day>\d+), dt: "(?P<passage>[\w\s:-]+)" },$')

month_var = {
    '1': { 'name': 'jan', 'end': '31' },
    '2': { 'name': 'feb', 'end': '28' },
    '3': { 'name': 'mar', 'end': '31' },
    '4': { 'name': 'apr', 'end': '30' },
    '5': { 'name': 'may', 'end': '31' },
    '6': { 'name': 'jun', 'end': '30' },
    '7': { 'name': 'jul', 'end': '31' },
    '8': { 'name': 'aug', 'end': '31' },
    '9': { 'name': 'sep', 'end': '30' },
    '10': { 'name': 'oct', 'end': '31' },
    '11': { 'name': 'nov', 'end': '30' },
    '12': { 'name': 'dec', 'end': '31' }
}

outf = open('updated_passages_{}'.format(next_year), "w")
print("Opened filed update_passages_{}".format(next_year))

with open('dt.js') as file:
    line = file.readline()
    print("Started with line: {}".format(line))

    while line and not ended:

        if (line.startswith('var DT_DATA = [')):
            print("Set started=True")
            started = True
            outf.write('${} = array(\n'.format(month_var['1']['name']))
        elif (line.startswith('null]')):
            print("Set ended=True")
            ended = True
            outf.close()
            sys.exit(0)
        elif started:
            line = line.strip()
            matched = line_regex.match(line)
            print("Matching line '{}'".format(line))

            if matched:
                if matched.group('year') == next_year:
                    month = matched.group('month')
                    day = matched.group('day')
                    passage = matched.group('passage')
                    print("Found month={}, day={}, passage={}".format(month,day,passage))
                    outf.write('"{}" => "{}",\n'.format(day, passage))

                    if (day == month_var[month]['end']):
                        outf.write(');\n')
                        if (month != '12'):
                            next_month = str(int(month) + 1)
                            print("Closing var for month {}, opening for {}".format(month, next_month))
                            outf.write('${} = array(\n'.format(month_var[next_month]['name']))
            else:
                sys.exit('Processing started by line="{}" failed regexp'.format(line))

        line = file.readline()
