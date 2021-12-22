#!/usr/bin/env python3
import datetime
import getopt
import os.path
import sys
import urllib.parse
import urllib.request

ENGLISH_TO_KOREAN_BOOK_NAMES = [
    "Genesis", "창세기",
    "Exodus", "탈출기",
    "Exodus", "출애굽기",
    "Leviticus", "레위기",
    "Numbers", "민수기",
    "Deuteronomy", "신명기",
    "Joshua", "여호수아",
    "Judges", "재판관기",
    "Judges", "사사기",
    "Ruth", "룻",
    "Ruth", "룻기",
    "1 Samuel", "사무엘 첫째",
    "1 Samuel", "사무엘상",
    "2 Samuel", "사무엘 둘째",
    "2 Samuel", "사무엘하",
    "1 Kings", "열왕기 첫째",
    "1 Kings", "열왕기상",
    "2 Kings", "열왕기 둘째",
    "2 Kings", "열왕기하",
    "1 Chronicles", "역대기 첫째",
    "1 Chronicles", "역대상",
    "2 Chronicles", "역대기 둘째",
    "2 Chronicles", "역대하",
    "Ezra", "에스라",
    "Nehemiah", "느헤미야",
    "Esther", "에스더",
    "Job", "욥",
    "Psalm", "시편",
    "Proverbs", "잠언",
    "Ecclesiastes", "전도서",
    "Song of Solomon", "솔로몬의 노래",
    "Song of Solomon", "아가",
    "Isaiah", "이사야",
    "Jeremiah", "예레미야",
    "Lamentations", "애가",
    "Lamentations", "예레미야애가",
    "Ezekiel", "에스겔",
    "Daniel", "다니엘",
    "Hosea", "호세아",
    "Joel", "요엘",
    "Amos", "아모스",
    "Obadiah", "오바댜",
    "Jonah", "요나",
    "Micah", "미가",
    "Nahum", "나훔",
    "Habakkuk", "하박국",
    "Zephaniah", "스바냐",
    "Haggai", "학개",
    "Zechariah", "스가랴",
    "Malachi", "말라기",
    "Matthew", "마태",
    "Matthew", "마태복음",
    "Mark", "마가",
    "Mark", "마가복음",
    "Luke", "누가",
    "Luke", "누가복음",
    "John", "요한",
    "John", "요한복음",
    "Acts", "사도",
    "Acts", "사도행전",
    "Romans", "로마",
    "Romans", "로마서",
    "1 Corinthians", "고린도 첫째",
    "1 Corinthians", "고린도전서",
    "2 Corinthians", "고린도 둘째",
    "2 Corinthians", "고린도후서",
    "Galatians", "갈라디아",
    "Galatians", "갈라디아서",
    "Ephesians", "에베소",
    "Ephesians", "에베소서",
    "Philippians", "빌립보",
    "Philippians", "빌립보서",
    "Colossians", "골로새",
    "Colossians", "골로새서",
    "1 Thessalonians", "데살로니가 첫째",
    "1 Thessalonians", "데살로니가전서",
    "2 Thessalonians", "데살로니가 둘째",
    "2 Thessalonians", "데살로니가후서",
    "1 Timothy", "디모데 첫째",
    "1 Timothy", "디모데전서",
    "2 Timothy", "디모데 둘째",
    "2 Timothy", "디모데후서",
    "Titus", "디도",
    "Titus", "디도서",
    "Philemon", "빌레몬",
    "Philemon", "빌레몬서",
    "Hebrews", "히브리",
    "Hebrews", "히브리서",
    "James", "야고보",
    "James", "야고보서",
    "1 Peter", "베드로 첫째",
    "1 Peter", "베드로전서",
    "2 Peter", "베드로 둘째",
    "2 Peter", "베드로후서",
    "1 John", "요한 첫째",
    "1 John", "요한일서",
    "2 John", "요한 둘째",
    "2 John", "요한이서",
    "3 John", "요한 셋째",
    "3 John", "요한삼서",
    "Jude", "유다",
    "Jude", "유다서",
    "Revelation", "계시록",
    "Revelation", "요한계시록"]

def get_cache_path_for_month(year, month):
    return "cache-" + "{:0>4d}".format(year) + "-" + "{:0>2d}".format(month) + ".html"


def get_webpage_for_month(year, month):
    global cache, url

    this_year = datetime.datetime.now().year
    if year < this_year - 1 or year > this_year + 1:
        raise Exception("Year out of range")
    if month < 1 or month > 12:
        raise Exception("Invalid month")

    contents = None
    if cache:
        cache_path = get_cache_path_for_month(year, month);
        if os.path.isfile(cache_path):
            with open(cache_path) as f:
                contents = f.read()
    else:
        cache_path = None

    if contents is None:
        data = urllib.parse.urlencode({
            "day": 1,
            "init": "",
            "month": month,
            "selectMonth": month,
            "selectYear": year,
            "year": year,
        }).encode()

        try:
            request = urllib.request.Request(url, data=data)
            response = urllib.request.urlopen(request)

            charset = "utf-8"
            content_type = response.getheader("Content-Type", default="charset=utf-8").split(";")
            for s in content_type:
                if s.startswith("charset="):
                    charset = s[8:]
            contents = response.read().decode(charset)
        except Exception as err:
            raise Exception("Cannot open the URL: " + str(err))

        if cache:
            with open(cache_path, "w") as f:
                f.write(contents)

    return contents


def extract_form_field(lines, name):
    for l in lines:
        s = '<input type="hidden" name="' + name + '" value="'
        x = l.find(s)
        if x < 0:
            continue
        e = l.find('"', x + len(s) + 1)
        if e < 0:
            continue
        return l[x + len(s):e]
    raise Exception("Form field '" + name + "' does not exist on the page.")


def translate_book_name(name):
    for i in range(0, len(ENGLISH_TO_KOREAN_BOOK_NAMES), 2):
        k = ENGLISH_TO_KOREAN_BOOK_NAMES[i]
        v = ENGLISH_TO_KOREAN_BOOK_NAMES[i+1]
        if k == name or v == name:
            return k
    raise Exception("Cannot translate '" + name + "' to English.")


def sanitize_verses(verses):
    x = verses.find(" - ")
    if x <= 0: return verses

    first = verses[0:x].split(":")
    second = verses[x + 3:].split(":")
    if len(first) != 2 or len(second) != 2: return verses

    if first == second:
        return verses[0:x]
    elif first[0] == second[0]:
        return first[0] + ":" + first[1] + "-" + second[1]
    else:
        return verses


def output_dt_for_month(year, month, output):
    contents = get_webpage_for_month(year, month)
    lines = contents.split("\n")

    # Verify month and year
    if str(year) != extract_form_field(lines, "year").strip():
        raise Exception("Form field 'year' on the page does not match the expected value.")
    if str(month) != extract_form_field(lines, "month").strip():
        raise Exception("Form field 'month' on the page does not match the expected value.")

    # Extract the DT text
    MATCH_DAY = "javascript:fnReturnDay("
    MATCH_ENTRY = "<div class=\"subj\">"
    day = None
    book = None
    entry_id = 0
    for l in lines:
        if day is None:
            if l.find("<td ") >= 0:
                x = l.find(MATCH_DAY)
                if x >= 0:
                    e = l.find(")", x + len(MATCH_DAY))
                    if e >= 0:
                        day = int(l[x + len(MATCH_DAY):e].strip())
                        entry_id = 0
        else:
            if l.find("</td") >= 0:
                day = None
            elif l.find(MATCH_ENTRY) >= 0:
                x = l.find(MATCH_ENTRY)
                if x >= 0:
                    e = l.find("</div>", x + len(MATCH_ENTRY))
                    if e >= 0:
                        v = l[x + len(MATCH_ENTRY):e].replace("&nbsp;", "").strip()
                        if entry_id == 0:
                            if v != "": book = translate_book_name(v)
                        elif entry_id == 1:
                            if book is None:
                                raise Exception("Cannot determine the book name for DT")
                            output.output_dt(year, month, day, book, sanitize_verses(v))
                        entry_id += 1


class OutputCsv:

    def before_output(self):
        print("year,month,day,dt")

    def output_dt(self, year, month, day, book, verses):
        b = book
        v = verses
        print(str(year) + "," + str(month) + "," + str(day)
              + "," + b + " " + v)

    def after_output(self):
        pass


class OutputJson:

    def before_output(self):
        print("var DT_DATA = [")

    def output_dt(self, year, month, day, book, verses):
        b = book
        v = verses
        print("{ year: " + str(year) + ", month: " + str(month) + ", day: " + str(day)
              + ", dt: \"" + b + " " + v + "\" },")

    def after_output(self):
        print("null]")


def usage():
    print("Usage: downloader.py")
    print()
    print("Options:")
    print("  -c, --csv          Print as CSV")
    print("  -h, --help         Print this usage information and exit")
    print("  -j, --json         Print as JSON")
    print("  -n, --no-cache     Do not cache the downloaded web pages")
    print("  -y, --year N       Set the year")


def main():
    global cache, url

    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "chjny:",
                                       ["csv", "help", "json", "no-cache", "year="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    output = OutputJson()
    cache = True
    url = "http://www.su.or.kr/03bible/daily/bibleCalendar.do"
    year = datetime.datetime.now().year

    for o, a in opts:
        if o in ("-c", "--csv"):
            output = OutputCsv()
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-j", "--json"):
            output = OutputJson()
        elif o in ("-n", "--no-cache"):
            cache = False
        elif o in ("-y", "--year"):
            year = int(a)
        else:
            assert False, "unhandled option"

    try:
        output.before_output()
        for m in range(1, 13):
            output_dt_for_month(year, m, output)
        output.after_output()
    except Exception as err:
        print("Error: " + str(err))
        sys.exit(1)


if __name__ == "__main__":
    main()
