from requests_html import HTMLSession
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup
import codecs
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import sys
import io

import requests
import textract
import tempfile

import fasttext

from iso639 import languages

#SRX_SEGMENTER
import lxml.etree
import regex
from typing import (
    List,
    Set,
    Tuple,
    Dict,
    Optional
)


class SrxSegmenter:
    """Handle segmentation with SRX regex format.
    """
    def __init__(self, rule: Dict[str, List[Tuple[str, Optional[str]]]], source_text: str) -> None:
        self.source_text = source_text
        self.non_breaks = rule.get('non_breaks', [])
        self.breaks = rule.get('breaks', [])

    def _get_break_points(self, regexes: List[Tuple[str, str]]) -> Set[int]:
        return set([
            match.span(1)[1]
            for before, after in regexes
            for match in regex.finditer('({})({})'.format(before, after), self.source_text)
        ])

    def get_non_break_points(self) -> Set[int]:
        """Return segment non break points
        """
        return self._get_break_points(self.non_breaks)

    def get_break_points(self) -> Set[int]:
        """Return segment break points
        """
        return self._get_break_points(self.breaks)

    def extract(self) -> Tuple[List[str], List[str]]:
        """Return segments and whitespaces.
        """
        non_break_points = self.get_non_break_points()
        candidate_break_points = self.get_break_points()

        break_point = sorted(candidate_break_points - non_break_points)
        source_text = self.source_text

        segments = []  # type: List[str]
        whitespaces = []  # type: List[str]
        previous_foot = ""
        for start, end in zip([0] + break_point, break_point + [len(source_text)]):
            segment_with_space = source_text[start:end]
            candidate_segment = segment_with_space.strip()
            if not candidate_segment:
                previous_foot += segment_with_space
                continue

            head, segment, foot = segment_with_space.partition(candidate_segment)

            segments.append(segment)
            whitespaces.append('{}{}'.format(previous_foot, head))
            previous_foot = foot
        whitespaces.append(previous_foot)

        return segments, whitespaces


def parse(srx_filepath: str) -> Dict[str, Dict[str, List[Tuple[str, Optional[str]]]]]:
    """Parse SRX file and return it.
    :param srx_filepath: is soruce SRX file.
    :return: dict
    """
    tree = lxml.etree.parse(srx_filepath)
    namespaces = {
        'ns': 'http://www.lisa.org/srx20'
    }

    rules = {}

    for languagerule in tree.xpath('//ns:languagerule', namespaces=namespaces):
        rule_name = languagerule.attrib.get('languagerulename')
        if rule_name is None:
            continue

        current_rule = {
            'breaks': [],
            'non_breaks': [],
        }

        for rule in languagerule.xpath('ns:rule', namespaces=namespaces):
            is_break = rule.attrib.get('break', 'yes') == 'yes'
            rule_holder = current_rule['breaks'] if is_break else current_rule['non_breaks']

            beforebreak = rule.find('ns:beforebreak', namespaces=namespaces)
            beforebreak_text = '' if beforebreak.text is None else beforebreak.text

            afterbreak = rule.find('ns:afterbreak', namespaces=namespaces)
            afterbreak_text = '' if afterbreak.text is None else afterbreak.text

            rule_holder.append((beforebreak_text, afterbreak_text))

        rules[rule_name] = current_rule

    return rules


def segmenta(cadena):
    segmenter = SrxSegmenter(rules[srxlang],cadena)
    segments=segmenter.extract()
    resposta=[]
    for segment in segments[0]:
        segment=segment.replace("’","'")
        resposta.append(segment)
    #resposta="\n".join(resposta)
    return(resposta)

def get_text(soup):
    alltext=[]
    text = soup.find_all(text=True)
    for t in text:
        if t.parent.name not in blacklist:
            if t.parent.name in ["p","h1","h2","h3","h4","h5","b","strong","i","em","mark","small","del","ins","sub","sup"]:
                if len(t.strip())>0:
                    alltext.append(t.strip())
    return(alltext)

def arreglaOLD(text):
    text=text.split("\n")
    joined=True
    for i in range(0,len(text)):
        if joined:
            joined=False
            continue
        else:
            try:
                if text[i+1].strip()[0].islower():
                    text[i]=text[i]+" "+text[i+1]
                    joined=True
            except:
                pass
    
    text="\n".join(text)
    return(text)

def arreglaOLD2(text):
    text=text.split("\n")
    text2=""
    joined=True
    for i in range(0,len(text)):
        print("TI:",text[i])
        try:
            if text[i+1].strip()[0].islower():
                text2=text2+text[i]+" "+text[i+1]
            else:
                text2=text[i]+"\n"
            
        except:
            text2=text2+" "+text[i]
        print("T2:",text2)
    return(text2)

def arregla(text):
    
    textlist=text.split("\n")
    textlist2=[]
    i=0
    for t in textlist:
        try:
            if textlist[i+1].strip()[0].isupper():
                textlist2.append(t+"@SALTPARA@")
            else:
                textlist2.append(t)
        except:
            textlist2.append(t)
        i+=1
    aux="".join(textlist2)
    aux2=aux.replace("@SALTPARA@","\n")
    return(aux2)
    

blacklist = [
    '[document]',

   'noscript',
    'header',
    'html',
    'meta',
    'head', 
    'input',
    'script',
    # there may be more elements you don't want, such as "style", etc.
]

fentrada=sys.argv[1]
#fsortida=sys.argv[2]

fsortida=fentrada.replace(".txt","EXTRACTED_TEXT")

entrada=codecs.open(fentrada,"r",encoding="utf-8")

LDmodel="lid.176.bin"
modelFT = fasttext.load_model(LDmodel)

srxfile="segment.srx"
rules = parse(srxfile)
available_languages=rules.keys()

outputfiles=[]
repeatedcontrol={}

for linia in entrada:
    link=linia.rstrip()
    print("LINK:",link)
    if link.endswith(".pdf") or link.endswith(".PDF"):
        r = requests.get(link)
        f = io.BytesIO(r.content)
        with tempfile.NamedTemporaryFile(delete=True) as temp:
            temp.write(f.read())
            temp.flush()
            text = textract.process(temp.name,encoding='utf-8',extension=".pdf",method='pdftotext').decode("utf-8", "replace")
            text=arregla(text)
            #text=" ".join(text.split())
    else:
        session = HTMLSession()
        try:
            response = session.get(link)
            
            try:
                response.html.render()
            except:
                session.close()
            soup = BeautifulSoup(response.html.html, "html.parser")
            text=get_text(soup)
            #text="\n".join(text)
            #print(text)
        
        except IOError as e:
                if e==KeyboardInterrupt:
                    sys.exit(0)
                else:
                    print("ERROR:",sys.exc_info())
        session.close()            
    textmod=" ".join(text).replace("\n"," ")
    DL=modelFT.predict(textmod, k=1)
    L=DL[0][0].replace("__label__","")
    confL=DL[1][0]
    srxlang=languages.get(alpha2=L).name       
    print(L,confL,srxlang)

    if not L in repeatedcontrol:
        repeatedcontrol[L]=[]

     
    if not srxlang in available_languages:
        print("WARNING: language "+srxlang+" not available in "+srxfile+". Available languages: "+", ".join(available_languages))
    paras=text#.split("\n")
    filename=fsortida+"-"+L+".txt"
    sortida=codecs.open(filename,"a",encoding="utf-8")
    for para in paras:
        segments=segmenta(para)
        for segment in segments:            
            if not segment in repeatedcontrol[L]:
                sortida.write(segment+"\n")
                print(segment)
                repeatedcontrol[L].append(segment)
    sortida.close()
        
