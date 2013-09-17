from bs4 import BeautifulSoup
from csv import writer
from clint import args

input_file, output_file = args.all

w = writer(open(output_file, "wb"))
soup = BeautifulSoup(open(input_file, "rb"))


pages = soup.find_all("page")


def get_bbox(obj):
    return [float(num) for num in obj["bbox"].split(",")]


def get_middle(obj):
    bbox = get_bbox(obj)
    return ((bbox[3]-bbox[1])/2)+bbox[1]


def get_lines(page):
    lgroups = list()
    lines = [line for line in page.find_all("textline")]
    lgroups.append([lines.pop()])
    appended = False
    for line in lines:
        middle = get_middle(line)
        if len(line.text.replace("\n", "").strip()) < 1:
            continue
        for group in lgroups:
            bbox = get_bbox(group[0])
            if middle > bbox[1] and middle < bbox[3]:
                group.append(line)
                appended = True
        if not appended:
            lgroups.append([line])

    lgroups = [sorted(g, key=get_middle) for g in lgroups]
    lgroups = sorted(lgroups, key=lambda x: get_middle(x[0]), reverse=True)
    lgroups = [[l.text.replace("\n", "").encode("utf-8") for l in g] for g in lgroups]
    return lgroups


for page in pages:
    for line in get_lines(page):
        if len(line) > 2:
            w.writerow(line)
