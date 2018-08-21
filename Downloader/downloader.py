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
    "Leviticus", "레위기",
    "Numbers", "민수기",
    "Deuteronomy", "신명기",
    "Joshua", "여호수아",
    "Judges", "재판관기",
    "Ruth", "룻",
    "1 Samuel", "사무엘 첫째",
    "2 Samuel", "사무엘 둘째",
    "1 Kings", "열왕기 첫째",
    "2 Kings", "열왕기 둘째",
    "2 Kings", "열왕기하",
    "1 Chronicles", "역대기 첫째",
    "2 Chronicles", "역대기 둘째",
    "Ezra", "에스라",
    "Nehemiah", "느헤미야",
    "Esther", "에스더",
    "Job", "욥",
    "Psalms", "시편",
    "Proverbs", "잠언",
    "Ecclesiastes", "전도서",
    "Song of Solomon", "솔로몬의 노래",
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
    "Mark", "마가",
    "Luke", "누가",
    "John", "요한",
    "Acts", "사도",
    "Acts", "사도행전",
    "Romans", "로마",
    "1 Corinthians", "고린도 첫째",
    "2 Corinthians", "고린도 둘째",
    "Galatians", "갈라디아",
    "Ephesians", "에베소",
    "Philippians", "빌립보",
    "Colossians", "골로새",
    "1 Thessalonians", "데살로니가 첫째",
    "2 Thessalonians", "데살로니가 둘째",
    "1 Timothy", "디모데 첫째",
    "2 Timothy", "디모데 둘째",
    "2 Timothy", "디모데후서",
    "Titus", "디도",
    "Philemon", "빌레몬",
    "Hebrews", "히브리",
    "James", "야고보",
    "1 Peter", "베드로 첫째",
    "2 Peter", "베드로 둘째",
    "1 John", "요한 첫째",
    "2 John", "요한 둘째",
    "3 John", "요한 셋째",
    "Jude", "유다",
    "Revelation", "계시록"]


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
                if s.startswith("charset="): charset = s[8:]
            contents = response.read().decode(charset)
        except Exception as err:
            raise Exception("Cannot open the URL: " + str(err));

        if cache:
            with open(cache_path, "w") as f:
                f.write(contents)

    return contents


def extract_form_field(lines, name):
    for l in lines:
        s = '<input type="hidden" name="' + name + '" value="'
        x = l.find(s)
        if x < 0: continue
        e = l.find('"', x + len(s) + 1)
        if e < 0: continue
        return l[x + len(s):e]
    raise Exception("Form field '" + name + "' does not exist on the page.")


def translate_book_name(name):
    for i in range(0, len(ENGLISH_TO_KOREAN_BOOK_NAMES), 2):
        k = ENGLISH_TO_KOREAN_BOOK_NAMES[i]
        v = ENGLISH_TO_KOREAN_BOOK_NAMES[i+1]
        if k == name or v == name:
            return k
        if name.startswith(v) or name.endswith(v):
            return k
    raise Exception("Cannot translate '" + name + "' to English.")


def sanitize_verses(verses):
    x = verses.find(" - ")
    if x <= 0: return verses

    first = verses[0:x].split(":")
    second = verses[x + 3:].split(":")
    if len(first) != 2 or len(second) != 2: return verses

    if first == second: return verses[0:x]
    elif first[0] == second[0]: return first[0] + ":" + first[1] + "-" + second[1]
    else: return verses


def get_dt_for_month(year, month):
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
                            output_dt(year, month, day, book, sanitize_verses(v))
                        entry_id += 1


def output_dt(year, month, day, book, verses):
    b = book
    v = verses
    print("{ year: " + str(year) + ", month: " + str(month) + ", day: " + str(day)
          + ", dt: \"" + b + " " + v + "\" },")


def usage():
    print("Usage: downloader.py")
    print()
    print("Options:")
    print("  -c, --cache        Cache the downloaded web pages")
    print("  -h, --help         Print this usage information and exit")
    print("  -y, --year N       Set the year")


def main():
    global cache, url

    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "chy:", ["cache", "help", "year="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    cache = False
    url = "http://www.su.or.kr/03bible/daily/bibleCalendar.do"
    year = datetime.datetime.now().year

    for o, a in opts:
        if o in ("-c", "--cache"):
            cache = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-y", "--year"):
            year = int(a)
        else:
            assert False, "unhandled option"

    try:
        print("var DT_DATA = [")
        for m in range(1, 13):
            get_dt_for_month(year, m)
        print("null]")
    except Exception as err:
        print("Error: " + str(err))
        sys.exit(1)


if __name__ == "__main__":
    main()