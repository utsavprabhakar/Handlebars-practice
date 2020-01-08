import re
import pandas as pd
import io
from pybars import Compiler
import unicodedata

#national
##national1 heading
##national1 content
##national1 risk
##national2 heading
##national2 content
##national2 risk

#north

bad_strings = ["'", "&", "$"]
subs_strings = ["xxx","yyy","zzz"]

LATIN_1_CHARS = (
    ('\xe2\x80\x99', "'"),
    ('\xc3\xa9', 'e'),
    ('\xe2\x80\x89', ' '),
    ('\xe2\x80\x90', '-'),
    ('\xe2\x80\x91', '-'),
    ('\xe2\x80\x92', '-'),
    ('\xe2\x80\x93', '-'),
    ('\xe2\x80\x94', '-'),
    ('\xe2\x80\x94', '-'),
    ('\xe2\x80\x98', "'"),
    ('\xe2\x80\x9b', "'"),
    ('\xe2\x80\x9c', '"'),
    ('\xe2\x80\x9c', '"'),
    ('\xe2\x80\x9d', '"'),
    ('\xe2\x80\x9e', '"'),
    ('\xe2\x80\x9f', '"'),
    ('\xe2\x80\xa6', '...'),
    ('\xe2\x80\xb2', "'"),
    ('\xe2\x80\xb3', "'"),
    ('\xe2\x80\xb4', "'"),
    ('\xe2\x80\xb5', "'"),
    ('\xe2\x80\xb6', "'"),
    ('\xe2\x80\xb7', "'"),
    ('\xe2\x81\xba', "+"),
    ('\xe2\x81\xbb', "-"),
    ('\xe2\x81\xbc', "="),
    ('\xe2\x81\xbd', "("),
    ('\xe2\x81\xbe', ")"),
    ("'","xxx"),
    ("&","yyy"),
    ("$","zzz"),
)

class News:
    def __init__(self, topic, intro, risk):
        self.topic = topic
        self.intro = intro
        self.risk = risk


def preprocess(line):  # replaces chars like ' or & with a random string which can be re replaced when the data is processed. was facing encoding issues.
    for i in xrange(len(bad_strings)):
        line = line + ""
        line.replace(bad_strings[i],subs_strings[i])
        # print(x)
    return line

def postprocess(line):
    x = ""
    for i in xrange(len(bad_strings)):
        line = line.replace(subs_strings[i],bad_strings[i]);
    return line

def clean_latin1(data):
    try:
        return data.encode('utf-8')
    except UnicodeDecodeError:
        print('******')
        print('\n')
        data = data.decode('iso-8859-1')
        for _hex, _char in LATIN_1_CHARS:
            data = data.replace(_hex, _char)
        return data.encode('utf8')

def populate_state(wordlist, locations, mapping):
    i=0
    print('wordlist=\s',len(wordlist))
    cur_state = ''
    for line in wordlist:
        # print(type(line))
        line = line.strip()
        words = line.split(' ')
        # line = preprocess(line)
        # print(words)
        # print(len(line))
        if(len(line)==0):
            continue
        if len(words)==1:
            cur_state = words[0].lower()
            i=0
            continue
        index = mapping[cur_state]
        length = len(locations[index])
        # print(length)
        if length==0 or i==0:
            locations[index].append(News('', '', ''))
        if i==0:
            # topic
            cur = locations[index]
            cur[len(cur)-1].topic = line
            i=1
        elif i==1:
            # intro
            starting_word = line.split(' ')[0]
            if starting_word.lower()=='risk':
                cur = locations[index]
                temp = line.split(':')
                tempstr = ""
                for i in range(1,len(temp)):
                    tempstr += " "+temp[i]
                cur[len(cur) - 1].risk = tempstr.strip()
                i = 0
            else:
                cur = locations[index]
                cur[len(cur) - 1].intro = line
                i=2
        else:
            cur = locations[index]
            temp = line.split(':')
            tempstr = ""
            for i in range(1, len(temp)):
                tempstr += " " + temp[i]
            cur[len(cur) - 1].risk = tempstr.strip()
            # cur[len(cur) - 1].risk = line.split(':')[1]
            i = 0
    return


def populate_parsed_data(locations, mapping):
    for i in xrange(6):
        # print(i)
        locations[i] = []
    with io.open('sample.txt', "r") as file:
        wordlist = []
        lines = file.readlines()
        # clean_latin1(lines)
        for data in lines:
            data = clean_latin1(data)
            for _hex, _char in LATIN_1_CHARS:
                data = data.replace(_hex, _char)
            wordlist.append(data)
        # print(wordlist[0])
        # print(len(wordlist[0].strip()))
        # print(wordlist[2])
        # print(wordlist)
        populate_state(wordlist, locations, mapping)
        # print(locations[1])


def create_mappings(mapping):
    mapping['national'] = 0
    mapping['north'] = 1
    mapping['south'] = 2
    mapping['east'] = 3
    mapping['west'] = 4
    mapping['international'] = 5

def _list(this, options, items):
    result = []
    for thing in items:
        # //result.append(u'<li>')
        result.extend(options['fn'](thing))
        # result.append(u'</li>')
    # result.append(u'</ul>')
    return result

helpers = {'list': _list}


def create_templates(source,locations,isSingle):
    compiler = Compiler()
    # Compile the template
    template = compiler.compile(source)
    # Add partials
    # header = compiler.compile(u'<h1>People</h1>')
    # partials = {'header': header}
    # Render the template
    if not isSingle:
        output = template({'location': locations},helpers=helpers)
    else:
        output = template({
            'risk': locations.risk,
            'topic': locations.topic,
            'intro' : locations.intro
        }, helpers=helpers)
    # print(output.encode('utf-8'))
    # output = unicodedata.normalize('NFKD', output).encode('ascii', 'ignore'
    output = unicodedata.normalize('NFKD', output).encode('ascii', 'ignore')
    # print(type(output))
    return output


def main():
    # define two dictionaries to store mapping and data of different locations
    locations = {}
    mapping = {}
    news = [] #array of strings. 0-national,1-north, 2-south,3-east,4-west,5-internatonal
    for i in xrange(6):
        news.append("")
    create_mappings(mapping) # maps string(eg national) with number corresponding to array index(eg 0)
    populate_parsed_data(locations,mapping) # reads input from sample text , cleans it, and populates the locations dict containing location wise news
    # templates for various locations
    source_north = u"<tr><td class='td_states'><h3><span><b>North</b></span></h3><div class='first_news_div'><h3 class='first_news_h3'>{{topic}}</h3><p class='p_intro'>{{intro}}</p></div></td></tr><tr><td class='td_others'><div style='border-right:3px solid #b91c12 !important;border-left:3px solid #555555 !important;padding-left:20px !important;padding-right:20px !important;'><p  class = 'para'><span style='color:#b91c12 !important;font-size:20px !important'><b>Risk Comment:</b></span>{{risk}}</p></div></td></tr>"
    source_south = u"<tr><td class='td_states'><h3><span><b>South</b></span></h3><div class='first_news_div'><h3 class='first_news_h3'>{{topic}}</h3><p class='p_intro'>{{intro}}</p></div></td></tr><tr><td class='td_others'><div style='border-right:3px solid #b91c12 !important;border-left:3px solid #555555 !important;padding-left:20px !important;padding-right:20px !important;'><p  class = 'para'><span style='color:#b91c12 !important;font-size:20px !important'><b>Risk Comment:</b></span>{{risk}}</p></div></td></tr>"
    source_east =  u"<tr><td class='td_states'><h3><span><b>East</b></span></h3><div class='first_news_div'><h3 class='first_news_h3'>{{topic}}</h3><p class='p_intro'>{{intro}}</p></div></td></tr><tr><td class='td_others'><div style='border-right:3px solid #b91c12 !important;border-left:3px solid #555555 !important;padding-left:20px !important;padding-right:20px !important;'><p  class = 'para'><span style='color:#b91c12 !important;font-size:20px !important'><b>Risk Comment:</b></span>{{risk}}</p></div></td></tr>"
    source_west = u"<tr><td class='td_states'><h3><span><b>West</b></span></h3><div class='first_news_div'><h3 class='first_news_h3'>{{topic}}</h3><p class='p_intro'>{{intro}}</p></div></td></tr><tr><td class='td_others'><div style='border-right:3px solid #b91c12 !important;border-left:3px solid #555555 !important;padding-left:20px !important;padding-right:20px !important;'><p  class = 'para'><span style='color:#b91c12 !important;font-size:20px !important'><b>Risk Comment:</b></span>{{risk}}</p></div></td></tr>"
    source_international = u"<tr><td class='td_states'><h3><span><b>International</b></span></h3><div class='first_news_div'><h3 class='first_news_h3'>{{topic}}</h3><p class='p_intro'>{{intro}}</p></div></td></tr><tr><td class='td_others'><div style='border-right:3px solid #b91c12 !important;border-left:3px solid #555555 !important;padding-left:20px !important;padding-right:20px !important;'><p  class = 'para'><span style='color:#b91c12 !important;font-size:20px !important'><b>Risk Comment:</b></span>{{risk}}</p></div></td></tr>"
    source_top = u"<tr><td class='top_news'><h3><span><b>National</b></span></h3><div class='first_news_div'><h3 class='first_news_h3'>{{topic}}</h3><p class='p_intro'>{{intro}}</p></div></td></tr><tr><td class='td_others'><div style='border-right:3px solid #b91c12 !important;border-left:3px solid #555555 !important;padding-left:20px !important;padding-right:20px !important;'><p  class = 'para'><span style='color:#b91c12 !important;font-size:20px !important'><b>Risk Comment:</b></span>{{risk}}</p></div></td></tr>"
    source_others =  u"{{#list location}}<tr><td class='td_others'><div class='second_news_div'><h3 class='second_news_h3'>{{topic}}</h3><p class='p_intro'>{{intro}}</p></div></td></tr><tr><td class='td_others'><div style='border-right:3px solid #b91c12 !important;border-left:3px solid #555555 !important;padding-left:20px !important;padding-right:20px !important;'><p  class = 'para'><span style='color:#b91c12 !important;font-size:20px !important'><b>Risk Comment:</b></span> {{risk}}</p></div></td></tr>{{/list}}"
    sources = []
    sources.append(source_top)
    sources.append(source_north)
    sources.append(source_south)
    sources.append(source_east)
    sources.append(source_west)
    sources.append(source_international)
    sources.append(source_others)
    for i in xrange(6):
        news[i] = news[i]+create_templates(sources[i], locations[i][0],True)

    for i in xrange(6):
        news[i] = news[i]+ create_templates(sources[6],locations[i][1:],False)
    # x = create_templates(source_others,locations[0][1:])
    # x = create_templates(source_top,locations[0][0])
    # news[0] = news[0]+x
    final_html = ''
    for str in news:
        final_html = final_html + str
    header = "<div><table align='center' cellspacing='10px' cellpadding='0' ><tr><td><img src='http://kcom.work/sis-emailer4/01.jpg' style='display:block' width='900'></td></tr>"
    footer = "<tr><td><img src='http://kcom.work/sis-emailer4/02.jpg' style='display:block;margin-top:30px !important' width='900'></td></tr></table></div><style>table {width:750px !important;border-collapse: collapse !important;border:1px solid #e8e8e8 !important}h3 span {color : #b91c12 !important;background: #cfcdcd !important;font-family:'calibri';font-size:30px !important;padding-left:25px;padding-right:25px;padding-top:3px;padding-bottom:3px;margin-bottom:5px  !important;margin-bottom:0px;}.top_news {padding-left:45px !important;padding-right:45px !important;padding-top:50px  !important}.first_news_div {border-left:3px solid #b91c12 !important;border-right:3px solid #555555 !important;padding-left:20px !important;padding-right:20px !important;padding-top:0px !important}.second_news_div {border-left:3px solid #b91c12 !important;border-right:3px solid #555555 !important;padding-left:20px !important;padding-right:20px !important;}.first_news_h3 {font-family:'calibri';font-size:20px !important;color:#b91c12 !important;margin-bottom:7px;}.second_news_h3 {font-family:'calibri';font-size:20px !important;color:#b91c12 !important;margin-bottom:7px !important;margin-top:7px !important;}.td_states {padding-left:45px !important;padding-right:45px !important;padding-top:10px  !important}.td_others {padding-left:45px !important;padding-right:45px !important;}.p_intro {font-family:'calibri';font-size:16px ;color:#333333 !important;margin-bottom:15px  !important;margin-top:7px !important;text-align:justify !important;"
    footer2 = "}.para {font-family:'calibri';font-size:16px; color:#333333 !important;margin-top:7px  !important;margin-bottom:15px  !important;text-align:justify !important;}</style>"
    yo = header + final_html + footer + footer2
    lo = postprocess(yo)
    print(lo)





if __name__ == "__main__":
    main()