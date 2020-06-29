# """Download all UV-Vis spectra available from NIST Chemistry Webbook."""
import os
import re
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup

# Ignore SSL certificate errors
import ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

NIST_URL = 'http://webbook.nist.gov/cgi/cbook.cgi'
EXACT_RE = re.compile('/cgi/cbook.cgi\?GetInChI=(.*?)$')
ID_RE = re.compile('/cgi/cbook.cgi\?ID=(.*?)&')
JDX_PATH = './Data/jdx/'
MOL_PATH = './Data/mol/'


def search_nist_inchi(inchi):
    """Search NIST using the specified InChI or InChIKey query and return the matching NIST ID."""
    params = dict()
    print('Searching: %s' % inchi)
    params={'InChI': inchi, 'Units': 'SI'}
    URL = NIST_URL + '?' + urllib.parse.urlencode(params)
    response = urllib.request.urlopen(URL).read()
    soup = BeautifulSoup(response,'html.parser')
    idlink = soup.find('a', href=EXACT_RE)
    if idlink:
        nistid = re.match(EXACT_RE, idlink['href']).group(1)
        print('Result: %s' % nistid)
        return nistid
    # If no match, there is a list of similar species
    # if not ids:
    #     ids = [re.match(ID_RE, link['href']).group(1) for link in soup('a', href=ID_RE)]


def search_nist_formula(formula, allow_other=False, allow_extra=False, match_isotopes=False, exclude_ions=False, has_uv=False):
    """Search NIST using the specified formula query and return the matching NIST IDs."""
    params = dict()
    print('Searching: %s' % formula)
    params = {'Formula': formula, 'Units': 'SI'}
    if allow_other:
        params['AllowOther'] = 'on'
    if allow_extra:
        params['AllowExtra'] = 'on'
    if match_isotopes:
        params['MatchIso'] = 'on'
    if exclude_ions:
        params['NoIon'] = 'on'
    if has_uv:
        params['cUV'] = 'on'
    URL = NIST_URL + '?' + urllib.parse.urlencode(params)
    response = urllib.request.urlopen(URL,context=ctx).read()
    soup = BeautifulSoup(response,'html.parser')
    ids = [re.match(ID_RE, link['href']).group(1) for link in soup('a', href=ID_RE)]
    print('Result: %s' % ids)
    return ids


def get_jdx(nistid, stype='UVVis'):
    """Download jdx file for the specified NIST ID, unless already downloaded."""
    params = dict()
    filepath = os.path.join(JDX_PATH, '%s-%s.jdx' % (nistid, stype))
    if os.path.isfile(filepath):
        print('%s %s: Already exists at %s' % (nistid, stype, filepath))
        return
    print('%s %s: Downloading' % (nistid, stype))
    params={'JCAMP': nistid, 'Type': stype, 'Index': 0}
    URL = NIST_URL + '?' + urllib.parse.urlencode(params)
    response = urllib.request.urlopen(URL).read()
    if response == '##TITLE=Spectrum not found.\n##END=\n':
        print('%s %s: Spectrum not found' % (nistid, stype))
        return
    print('Saving %s' % filepath)
    flag = 0
    try:
        response.decode()
    except:
        flag = 1
    if not flag:
        with open(filepath, 'w') as file:
            file.write(response.decode())
    return flag


def get_mol(nistid):
    """Download mol file for the specified NIST ID, unless already downloaded."""
    params = dict()
    filepath = os.path.join(MOL_PATH, '%s.mol' % nistid)
    if os.path.isfile(filepath):
        print('%s: Already exists at %s' % (nistid, filepath))
        return
    print('%s: Downloading mol' % nistid)
    params={'Str2File': nistid}
    URL = NIST_URL + '?' + urllib.parse.urlencode(params)
    response = urllib.request.urlopen(URL).read()
    if response == 'NIST    12121112142D 1   1.00000     0.00000\nCopyright by the U.S. Sec. Commerce on behalf of U.S.A. All rights reserved.\n0  0  0     0  0              1 V2000\nM  END\n':
        print('%s: MOL not found' % nistid)
        return
    print('Saving %s' % filepath)
    flag = 0
    try:
        response.decode()
    except:
        flag = 1
    if not flag:
        with open(filepath, 'w') as file:
            file.write(response.decode())

def get_all_uvvis():
    """Search NIST for all structures with UV-Vis spectra and download a JDX file for each."""
    # Each search is limited to 400 results
    # So we search by formula, allowing additional elements not specified in formula: C, CC, CCC, CCCC, etc.
    for i in range(1, 100):
        ids = search_nist_formula('C%s' % i, allow_other=True, exclude_ions=True, has_uv=True)
        print('%s spectra found' % len(ids))
        for nistid in ids:
            flag = get_jdx(nistid, stype='UVVis')
            if not flag:
                get_mol(nistid)


if __name__ == '__main__':
    #nistid = search_nist_inchi('ZYGHJZDHTFUPRJ-UHFFFAOYSA-N')
    #get_jdx(nistid)
    #get_mol(nistid)
    #search_nist_formula('C20', allow_other=True, exclude_ions=True, has_uv=True)
    get_all_uvvis()