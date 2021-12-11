from flask import Flask, request, render_template
from zipfile import ZipFile
import sqlite3
import csv
import os.path
import time
import requests

app = Flask(__name__, static_url_path='')
app.config["DEBUG"] = True

ac_headers = []
ac_oc = []
caac_oc = []
AreaCodesOfficeCodes = []
AreaCodesOnly = []
fivex_codes = []
codes900 = []
FGDCICCodes = []
FGBCICCodes = []
N11Codes = []
results = []

now = time.time()
days_old = now - 60 * 60 * 24 * 10  # 10 days old...Number of seconds in 10 days
new_database_file = False

myport = '5000'
myip = 'localhost'
myurl = 'http://' + myip + ':' + myport

FilePath = '/home/mike/PycharmProjects/nanpa/static/NANPA/'
USACMapPath = '/home/mike/PycharmProjects/nanpa/static/USACMaps/'

USACMapFilePath = '/USACMaps/'
StateFilePath = '/USStateMaps/'
USTerritoryFilePath = '/USTerritoryACMaps/'
CanadaFilePath = '/CanadaACMaps/'
CountryFilePath = '/CountryACMaps/'
ACOCDownloadUrl = 'https://nationalnanpa.com/nanp1/allutlzd.zip'
ACDownloadUrl = 'https://nationalnanpa.com/nanp1/npa_report.csv'
CanadaOCDownloadUrl = 'http://www.cnac.ca/data/COCodeStatus_ALL.zip'

LinkHome = 'http://' + myip + ':' + myport
LinkACMaps = 'http://' + myip + ':' + myport + '/acmaps?state='

LinkAnchor = '<a href="http://'
LinkByAC = LinkAnchor + myip + ':' + myport + '/areacodes?npa='
LinkByOC = LinkAnchor + myip + ':' + myport + '/officecodes?npa-nxx='

States = {
    'AK': 'Alaska',
    'AL': 'Alabama',
    'AR': 'Arkansas',
    'AZ': 'Arizona',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DC': 'District of Columbia',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'IA': 'Iowa',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'MA': 'Massachusetts',
    'MD': 'Maryland',
    'ME': 'Maine',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MO': 'Missouri',
    'MS': 'Mississippi',
    'MT': 'Montana',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'NE': 'Nebraska',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NV': 'Nevada',
    'NY': 'New York',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VA': 'Virginia',
    'VT': 'Vermont',
    'WA': 'Washington',
    'WI': 'Wisconsin',
    'WV': 'West Virginia',
    'WY': 'Wyoming'
}

USTerritory = {
    'AS': 'American Somoa',
    'GU': 'Guam',
    'PUERTO RICO': 'PR',
    'USVI': 'US Virgin Islands',
    'CNMI': 'Northern Marianna Islands'
}

CanadaPTAbbr = {
    'AB': 'Alberta',
    'BC': 'British Columbia',
    'MB': 'Manitoba',
    'NB': 'New Brunswick',
    'NL': 'Newfoundland and Labrador',
    'ON': 'Ontario',
    'NS-PEI': 'NOVA SCOTIA - PRINCE EDWARD ISLAND',
    'QC': 'Quebec',
    'SK': 'Saskatchewan',
    'YT-NWT-NU': 'YUKON-NW TERR. - NUNAVUT'
}

CanadaPT = {
    'ALBERTA': 'AB',
    'BRITISH COLUMBIA': 'BC',
    'MANITOBA': 'MB',
    'NEW BRUNSWICK': 'NB',
    'NEWFOUNDLAND AND LABRADOR': 'NL',
    'NOVA SCOTIA': 'NS',
    'ONTARIO': 'ON',
    'NOVA SCOTIA - PRINCE EDWARD ISLAND': 'PEI',
    'QUEBEC': 'QC',
    'SASKATCHEWAN': 'SK',
    'YUKON-NW TERR. - NUNAVUT': 'YT-NWT-NU',
}

Country = {
    'JAMAICA': 'JAMAICA',
    'BAHAMAS': 'BAHAMAS',
    'BARBADOS': 'BARBADOS',
    'ANTIGUA/BARBUDA': 'ANTIGUA/BARBUDA',
    'BRITISH VIRGIN ISLANDS': 'BRITISH VIRGIN ISLANDS',
    'CAYMAN ISLANDS': 'CAYMAN ISLANDS',
    'BERMUDA': 'BERMUDA',
    'GRENADA': 'GRENADA',
    'TURKS & CAICOS ISLANDS': 'TURKS & CAICOS ISLANDS',
    'MONTSERRAT': 'MONTSERRAT',
    'SINT MAARTEN': 'SINT MAARTEN',
    'ST. LUCIA': 'ST. LUCIA',
    'DOMINICA': 'DOMINICA',
    'ST. VINCENT & GRENADINES': 'ST. VINCENT & GRENADINES',
    'DOMINICAN REPUBLIC': 'DOMINICAN REPUBLIC',
    'TRINIDAD & TOBAGO': 'TRINIDAD & TOBAGO',
    'ST. KITTS & NEVIS': 'ST. KITTS & NEVIS'
}

# check to see if the database file exists and if older than 20 days.
if os.path.isfile(FilePath + 'pn.db'):
    fileCreation = os.path.getctime(FilePath + 'pn.db')
    # Here we need to release pn.db or it will show 'in use' when trying to rename it...
if fileCreation < days_old:
    if os.path.isfile(FilePath + 'old_pn.db'):
        os.remove(FilePath + 'old_pn.db')
    if os.path.isfile(FilePath + 'pn.db'):
        os.renames(FilePath + 'pn.db', FilePath + 'old_pn.db')
    if os.path.isfile(FilePath + 'old_npa_report.csv'):
        os.remove(FilePath + 'old_npa_report.csv')
    if os.path.isfile(FilePath + 'npa_report.csv'):
        os.renames(FilePath + 'npa_report.csv', FilePath + 'old_npa_report.csv')
    if os.path.isfile(FilePath + 'old_allutlzd.txt'):
        os.remove(FilePath + 'old_allutlzd.txt')
    if os.path.isfile(FilePath + 'allutlzd.txt'):
        os.renames(FilePath + 'allutlzd.txt', FilePath + 'old_allutlzd.txt')
    if os.path.isfile(FilePath + 'allutlzd.zip'):
        os.remove(FilePath + 'allutlzd.zip')
    if os.path.isfile(FilePath + 'old_COCodeStatus_ALL.csv'):
        os.remove(FilePath + 'old_COCodeStatus_ALL.csv')
    if os.path.isfile(FilePath + 'COCodeStatus_ALL.csv'):
        os.renames(FilePath + 'COCodeStatus_ALL.csv', FilePath + 'old_COCodeStatus_ALL.csv')
    if os.path.isfile(FilePath + 'COCodeStatus_ALL.zip'):
        os.remove(FilePath + 'COCodeStatus_ALL.zip')

# will download the file if it's missing.
if not os.path.isfile(FilePath + 'npa_report.csv'):
    r = requests.get(ACDownloadUrl, allow_redirects=True)
    open(FilePath + 'npa_report.csv', 'wb').write(r.content)

# will download the zipped file if it's missing, and extract the contents.
if not os.path.isfile(FilePath + 'allutlzd.zip'):
    r = requests.get(ACOCDownloadUrl, allow_redirects=True)
    open(FilePath + 'allutlzd.zip', 'wb').write(r.content)
    with ZipFile(FilePath + 'allutlzd.zip', 'r') as zipObj:
        zipObj.extractall(FilePath)

# will download the zipped Canada OC file if it's missing, and extract the contents.
if not os.path.isfile(FilePath + 'COCodeStatus_ALL.zip'):
    r = requests.get(CanadaOCDownloadUrl, allow_redirects=True)
    open(FilePath + 'COCodeStatus_ALL.zip', 'wb').write(r.content)
    with ZipFile(FilePath + 'COCodeStatus_ALL.zip', 'r') as zipObj:
        zipObj.extractall(FilePath)


# if the database file doesn't exist, it will be created when the sqlite conn instance is created.
if not os.path.isfile(FilePath + 'pn.db'):
    new_database_file = True

# Waited to declare the connection to pn.db until after checking if it exists.
conn = sqlite3.connect(FilePath + 'pn.db')
cur = conn.cursor()


# If a new database file was created, add content
if new_database_file is True:
    # Creates a new sqlite table 'oc' for US office-codes.
    with open(FilePath + 'allutlzd.txt', 'r', newline='\n') as OCs:
        OC = csv.reader(OCs, delimiter='\t')
        for Row in OC:
            ac_oc.append(Row)
    # Headers need some fixing up
    oc_headers = ac_oc[0]
    oc_headers[-1] = 'InService'
    oc_fixed_headers = []
    for item in oc_headers:
        myitem = item.replace('-', '')
        myitem = myitem.replace('/', '')
        myitem = myitem.replace(' ', '')
        oc_fixed_headers.append(myitem)
    cur.execute('CREATE TABLE oc (' + oc_fixed_headers[0] + ' text, ' +
                oc_fixed_headers[1] + ' text, ' + oc_fixed_headers[2] + ' text, ' +
                oc_fixed_headers[3] + ' text, ' + oc_fixed_headers[4] + ' text, ' +
                oc_fixed_headers[5] + ' text, ' + oc_fixed_headers[6] + ' text, ' +
                oc_fixed_headers[7] + ' text, ' + oc_fixed_headers[8] + ' text, ' +
                oc_fixed_headers[9] + ' text, ' + oc_fixed_headers[10] + ' text);')
    ac_oc.pop(0)
    ac_oc = [[item.replace("'", '') for item in row] for row in ac_oc]
    ac_oc = [[item.replace('"', '') for item in row] for row in ac_oc]
    ac_oc = [[item.strip() for item in row] for row in ac_oc]
    cur.executemany("insert into oc values(?,?,?,?,?,?,?,?,?,?,?)", ac_oc)
    conn.commit()
    OCs.close()

    # Creates a new sqlite table 'ac' for North America area-codes.
    area_codes = []
    with open(FilePath + 'npa_report.csv', 'r', newline='\n') as ACs:
        AC = csv.reader(ACs, delimiter=',')
        for Row in AC:
            area_codes.append(Row)
    area_codes.pop(0)
    ac_headers = area_codes[0]
    # No need to fix these headers, but keep this filler line just in case I need to fix them in the future...
    ac_fixed_headers = ac_headers
    cur.execute('CREATE TABLE ac (' + ac_fixed_headers[0] + ' text, ' +
                ac_fixed_headers[1] + ' text, ' + ac_fixed_headers[2] + ' text, ' +
                ac_fixed_headers[3] + ' text, ' + ac_fixed_headers[4] + ' text, ' +
                ac_fixed_headers[5] + ' text, ' + ac_fixed_headers[6] + ' text, ' +
                ac_fixed_headers[7] + ' text, ' + ac_fixed_headers[8] + ' text, ' +
                ac_fixed_headers[9] + ' text, ' + ac_fixed_headers[10] + ' text, ' +
                ac_fixed_headers[11] + ' text, ' + ac_fixed_headers[12] + ' text, ' +
                ac_fixed_headers[13] + ' text, ' + ac_fixed_headers[14] + ' text, ' +
                ac_fixed_headers[15] + ' text, ' + ac_fixed_headers[16] + ' text, ' +
                ac_fixed_headers[17] + ' text, ' + ac_fixed_headers[18] + ' text, ' +
                ac_fixed_headers[19] + ' text, ' + ac_fixed_headers[20] + ' text, ' +
                ac_fixed_headers[21] + ' text, ' + ac_fixed_headers[22] + ' text, ' +
                ac_fixed_headers[23] + ' text, ' + ac_fixed_headers[24] + ' text, ' +
                ac_fixed_headers[25] + ' text, ' + ac_fixed_headers[26] + ' text, ' +
                ac_fixed_headers[27] + ' text, ' + ac_fixed_headers[28] + ' text, ' +
                ac_fixed_headers[29] + ' text, ' + ac_fixed_headers[30] + ' text, ' +
                ac_fixed_headers[31] + ' text);')
    area_codes.pop(0) #Deletes the file date that is first entry in file
    area_codes = [[item.replace("'", '') for item in row] for row in area_codes]
    area_codes = [[item.replace('"', '') for item in row] for row in area_codes]
    area_codes = [[item.strip() for item in row] for row in area_codes]
    # some rows are missing the dialing info at the end.
    # 3 of the areacodes have an extra field that needs removed. I raised the issue with NANPA.
    for row in area_codes:
        if len(row) == 17:
            row.extend(["", "", "", "", "", "", "", "", "", "", "", "", "", "", ""])
        if len(row) == 33:
            row.pop(22)
        if len(row) != 32:
            print(row)
    cur.executemany("insert into ac values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    area_codes)
    conn.commit()
    ACs.close()

    # Creates a new sqlite table 'caoc' for Canada office-codes.
    with open(FilePath + 'COCodeStatus_ALL.csv', 'r', newline='\n') as CAOCs:
        CAOC = csv.reader(CAOCs, delimiter=',')
        for Row in CAOC:
            caac_oc.append(Row)
    # Headers need some fixing up
    caoc_headers = caac_oc[0]
    caoc_fixed_headers = []
    for item in caoc_headers:
        myitem = item.replace('-', '')
        myitem = myitem.replace('/', '')
        myitem = myitem.replace('(', '')
        myitem = myitem.replace(')', '')
        myitem = myitem.replace(' ', '')
        caoc_fixed_headers.append(myitem)
    cur.execute('CREATE TABLE caoc (' + caoc_fixed_headers[0] + ' text, ' +
                caoc_fixed_headers[1] + ' text, ' + caoc_fixed_headers[2] + ' text, ' +
                caoc_fixed_headers[3] + ' text, ' + caoc_fixed_headers[4] + ' text, ' +
                caoc_fixed_headers[5] + ' text, ' + caoc_fixed_headers[6] + ' text);')
    caac_oc.pop(0)
    caac_oc.pop(0)
    caac_oc = [[item.replace("'", '') for item in row] for row in caac_oc]
    caac_oc = [[item.replace('"', '') for item in row] for row in caac_oc]
    caac_oc = [[item.strip() for item in row] for row in caac_oc]
    cur.executemany("insert into caoc values(?,?,?,?,?,?,?)", caac_oc)
    conn.commit()
    CAOCs.close()

    # create a new OCN Company list.
    ocnlist = []
    cur.execute("select OCN, Company from oc;")
    row = cur.fetchone()
    while row:
        if row not in ocnlist and row[0] != '':
            ocnlist.append(row)
        row = cur.fetchone()
    ocnlist.sort()
    cur.execute("CREATE TABLE ocn ('OCN', 'Company')")
    cur.executemany("insert into ocn values(?,?)", ocnlist)
    conn.commit()

    # Creates a new fivex table
    with open(FilePath + 'All5XXNXXCodesReport.txt', 'r', newline='\n') as file_in:
        fivex = csv.reader(file_in, delimiter='\t')
        for Row in fivex:
            fivex_codes.append(Row)
        fivex_codes.pop(0)  # Deletes the first row from the list.
        fivex_headers = fivex_codes[0]
        cur.execute('CREATE TABLE fivex (' + fivex_headers[0] + ' text, ' +
                    fivex_headers[1] + ' text, ' + fivex_headers[2] + ' text, ' +
                    fivex_headers[3] + ' text, ' + fivex_headers[4] + ' text);')
        fivex_codes.pop(0)
        cur.executemany("insert into fivex values(?,?,?,?,?)", fivex_codes)
        conn.commit()


# 900 Codes
with open(FilePath + '900codes.csv', 'r', newline='\n') as file_in:
    c900 = csv.reader(file_in, delimiter=',')
    for Row in c900:
        codes900.append(Row)
    codes900.pop(0)  # Deletes the first row from the list.

# FGB-CIC Codes
with open(FilePath + 'FGB-CIC.csv', 'r', newline='\n') as CICBs:
    CICBCode = csv.reader(CICBs, delimiter=',')
    for Row in CICBCode:
        FGBCICCodes.append(Row)
# FGD-CIC Codes
with open(FilePath + 'FGD-CIC.csv', 'r', newline='\n') as CICDs:
    CICDCode = csv.DictReader(CICDs, delimiter=',')
    for Row in CICDCode:
        FGDCICCodes.append(Row)
# N11Codes
with open(FilePath + 'N11-Codes.csv', 'r', newline='\n') as N11s:
    N11Code = csv.reader(N11s, delimiter=',')
    for Row in N11Code:
        N11Codes.append(Row)
    N11Codes.pop(0)  # Deletes the first row from the list.


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html', LinkHome=LinkHome, LinkACMaps=LinkACMaps, States=States
                           , CanadaPTAbbr=CanadaPTAbbr, USTerritory=USTerritory, Country=Country)


@app.route('/officecodes', methods=['GET'])
def officecodes():
    conn = sqlite3.connect(FilePath + 'pn.db')
    cur = conn.cursor()

    use = {
        'AS':'AS indicates codes that are assigned to a service provider.',
        'RV':'RV indicates codes that have been reserved by a service provider. The identity of the service provider is considered proprietary information and will not be shown.',
        'VC':'VC indicates codes that are vacant; they are available for assignment to a service provider.',
        'PR':'PR indicates codes that are protected for a split; that is, these codes are assigned in the old or the new NPA and can not be assigned in the other NPA until after the end of permissive dialing.',
        'UA':'UA indicates codes that are unavailable for assignment. These codes include, but are not limited to, test and special use codes (e.g., 958, 959, 555, time), N11 and other unique codes (e.g., 976, 950), codes set aside for pooling, and codes with special dialing arrangements (e.g., 7-digit dialing cross NPA boundary).'
    }
    acoc_headers = []
    acoc_return = {}
    caoc_headers = []
    ac_headers = []
    ac_return = {}
    mapfile = ''
    state_name = ''
    state = ''
    country = ''
    RateCenter = ''
    ocn = ''
    companyname = ''

    if 'npa-nxx' in request.args:
        npanxx = request.args['npa-nxx']
        npa_code = npanxx[0:3]
        office_code = npanxx[4:7]
        if len(npanxx) == 7:
            cur.execute("PRAGMA table_info(oc);")
            row = cur.fetchall()
            for item in row:
                acoc_headers.append(item[1])

            cur.execute("PRAGMA table_info(caoc);")
            row = cur.fetchall()
            for item in row:
                caoc_headers.append(item[1])

            cur.execute("PRAGMA table_info(ac);")
            row = cur.fetchall()
            for item in row:
                ac_headers.append(item[1])

            try:
                cur.execute("select * from oc where NPANXX='" + npanxx + "'")
                acoc_tuple = cur.fetchall()
                ocn = acoc_tuple[0][2]
                companyname = acoc_tuple[0][3]
                RateCenter = acoc_tuple[0][4]
                state = acoc_tuple[0][0]
                if state == 'PR':
                    state = 'PUERTO RICO'
                acoc_return = dict(zip(acoc_headers, acoc_tuple[0]))
            except:
                try:
                    cur.execute("select * from caoc where NPA='" + npa_code + "' and COCodeNXX='" + office_code + "'")
                    acoc_tuple = cur.fetchall()
                    ocn = acoc_tuple[0][3]
                    companyname=acoc_tuple[0][2]
                    RateCenter = acoc_tuple[0][5]
                    state = acoc_tuple[0][0]
                    if state == 'PR':
                        state = 'PUERTO RICO'
                    acoc_return = dict(zip(caoc_headers, acoc_tuple[0]))
                except:
                    return render_template("error.html", LinkHome=LinkHome, error="Unable to find " + npanxx)
            try:
                cur.execute("select * from ac where NPA_ID='" + npa_code + "'")
                ac_tuple = cur.fetchall()
                country = ac_tuple[0][9]
                ac_return = dict(zip(ac_headers, ac_tuple[0]))
            except:
                return render_template("error.html", LinkHome=LinkHome, error="Unable to find " + npa_code)

            if country == 'US':
                if state in States:
                    state_name = States[state]
                    return render_template("ac-oc.html", LinkHome=LinkHome, ac_return=ac_return, use=use,
                                           state_name=state_name, state=state, country=country, acoc_return=acoc_return,
                                           npanxx=npanxx, npa_code=npa_code, myurl=myurl, USACMapFilePath=USACMapFilePath,
                                           StateFilePath=StateFilePath, RateCenter=RateCenter, ocn=ocn, companyname=companyname)
                if state == 'VI':
                    state = 'USVI'
                if state == 'NN':
                    state = 'CNMI'
                if state in USTerritory:
                    if state == 'PUERTO RICO':
                        state_name = USTerritory[state]
                        mapfile = 'Puerto_Rico_787_939.gif'
                    if state == 'AS':
                        state_name = USTerritory[state]
                        mapfile = 'American_Samoa_684.gif'
                    if state == 'GU':
                        state_name = USTerritory[state]
                        mapfile = 'Guam_671.gif'
                    if state == 'CNMI':
                        state_name = USTerritory[state]
                        mapfile = 'Northern_Marianna_Islands_670.gif'
                    if state == 'USVI':
                        state_name = USTerritory[state]
                        mapfile = 'US_Virgin_Islands_340.gif'
                    return render_template("territory-ac-oc.html", LinkHome=LinkHome, ac_tuple=ac_tuple, npanxx=npanxx
                                           , ac_return=ac_return, state_name=state_name, state=state, country=country
                                           , npa_code=npa_code, myurl=myurl, acoc_return=acoc_return
                                           , USTerritoryFilePath=USTerritoryFilePath, mapfile=mapfile
                                           , RateCenter=RateCenter, use=use, ocn=ocn, companyname=companyname)
            if country == 'CANADA':
                state_name = ac_tuple[0][8]
                state = CanadaPT[state_name]
                if state_name == 'QUEBEC':
                    mapfile = 'qc-s.png'
                if state_name == 'BRITISH COLUMBIA':
                    mapfile = 'bc-s.png'
                if state_name == 'ONTARIO':
                    mapfile = 'on-s.png'
                return render_template("canada-ac-oc.html", LinkHome=LinkHome, ac_return=ac_return, companyname=companyname,
                                       state_name=state_name, state=state, country=country, acoc_return=acoc_return,
                                       npanxx=npanxx, npa_code=npa_code, myurl=myurl, CanadaFilePath=CanadaFilePath,
                                       mapfile=mapfile, RateCenter=RateCenter, ocn=ocn)
        return render_template("error.html", LinkHome=LinkHome, error="Unable to find... " + npanxx)
    return render_template("error.html", LinkHome=LinkHome, error='URL is not correct.')


@app.route('/compstate', methods=['GET'])
def compstate():
    conn = sqlite3.connect(FilePath + 'pn.db')
    cur = conn.cursor()

    cs_list = []
    state = ''

    if 'cs' in request.args:
        state = request.args['cs']
    try:
        cur.execute("select OCN, Company from oc where State='" + state + "' order by Company")
        row = cur.fetchall()
        for each in row:
            if each[0] != '' and each not in cs_list:
                cs_list.append(each)
        return render_template("cs.html", LinkHome=LinkHome, myurl=myurl, cs_list=cs_list, state=state)
    except:
        return render_template("error.html", LinkHome=LinkHome, error="Unable to find ")


@app.route('/rcstate', methods=['GET'])
def rcstate():
    conn = sqlite3.connect(FilePath + 'pn.db')
    cur = conn.cursor()

    rcs_list = []
    state = ''

    if 'rcs' in request.args:
        state = request.args['rcs']
    try:
        cur.execute("select RateCenter from oc where State='" + state + "' order by RateCenter")
        row = cur.fetchall()
        for each in row:
            if each[0] != '' and each[0] not in rcs_list:
                rcs_list.append(each[0])
        return render_template("rcs.html", LinkHome=LinkHome, myurl=myurl, rcs_list=rcs_list, state=state)
    except:
        return render_template("error.html", LinkHome=LinkHome, error="Unable to find ")


@app.route('/ratecenter', methods=['GET'])
def ratecenter():
    conn = sqlite3.connect(FilePath + 'pn.db')
    cur = conn.cursor()

    acoc_headers = []
    ac_oc_list = []
    ac_oc_companylist = []
    acoc_return = {}
    ac_headers = []
    ac_return = {}
    mapfile = ''
    state_name = ''
    country = ''
    RateCenter = ''

    if 'rc' in request.args and 'state' in request.args and 'country' in request.args:
        RateCenter = request.args['rc']
        state = request.args['state']
        country = request.args['country']

        if country == 'US':
            if state == 'PUERTO RICO':
                state = 'PR'
            if state == 'USVI':
                state = 'VI'
            if state == 'CNMI':
                state = 'NN'
            try:
                cur.execute("select NPANXX, Company from oc where RateCenter='" + RateCenter +
                            "' and State='" + state + "' order by NPANXX")
                row = cur.fetchone()
                while row:
                    ac_oc_list.append(row)
                    row = cur.fetchone()
                cur.execute("select NPANXX, Company from oc where RateCenter='" + RateCenter +
                            "' and State='" + state + "' order by Company,NPANXX")
                row = cur.fetchone()
                while row:
                    ac_oc_companylist.append(row)
                    row = cur.fetchone()
                return render_template("rc.html", LinkHome=LinkHome, myurl=myurl, RateCenter=RateCenter
                                       , ac_oc_list=ac_oc_list, ac_oc_companylist=ac_oc_companylist, state=state)
            except:
                return render_template("error.html", LinkHome=LinkHome, error="Unable to find " + RateCenter)
        if country == 'CANADA':
            try:
                cur.execute("select NPA, COCodeNXX, Company from caoc where RateCenter='"
                            + RateCenter + "' order by NPA, COCodeNXX")
                row = cur.fetchone()
                while row:
                    ac_oc_list.append(row)
                    row = cur.fetchone()
                cur.execute("select NPA, COCodeNXX, Company from caoc where RateCenter='"
                            + RateCenter + "' order by Company, NPA, COCodeNXX")
                row = cur.fetchone()
                while row:
                    ac_oc_companylist.append(row)
                    row = cur.fetchone()
                return render_template("carc.html", LinkHome=LinkHome, myurl=myurl, RateCenter=RateCenter
                                       , ac_oc_list=ac_oc_list, ac_oc_companylist=ac_oc_companylist, state=state)
            except:
                return render_template("error.html", LinkHome=LinkHome, error="Unable to find " + RateCenter)
    return render_template("error.html", LinkHome=LinkHome, error='URL is not correct.')


@app.route('/company', methods=['GET'])
def company():
    conn = sqlite3.connect(FilePath + 'pn.db')
    cur = conn.cursor()

    acoc_headers = []
    ac_oc_list = []
    ac_oc_rclist = []
    acoc_return = {}
    ac_headers = []
    ac_return = {}
    mapfile = ''
    state_name = ''
    country = ''
    ocn = ''
    companyname = ''

    if 'ocn' in request.args:
        ocn = request.args['ocn']
        companyname = request.args['companyname']
        country = request.args['country']
        state = request.args['state']
        if state == 'PUERTO RICO':
            state = 'PR'
        if state == 'USVI':
            state = 'VI'
        if state == 'CNMI':
            state = 'NN'
        if country == 'US':
            try:
                cur.execute("select NPANXX, RateCenter from oc where OCN='" + ocn + "' and State='" + state + "'")
                row = cur.fetchone()
                while row:
                    ac_oc_list.append(row)
                    row = cur.fetchone()

                cur.execute("select NPANXX, RateCenter from oc where OCN='" + ocn + "' and State='"
                            + state + "' order by RateCenter, NPANXX")
                row = cur.fetchone()
                while row:
                    ac_oc_rclist.append(row)
                    row = cur.fetchone()
                return render_template("ocn.html", LinkHome=LinkHome, myurl=myurl, ocn=ocn
                                       , ac_oc_list=ac_oc_list, companyname=companyname, state=state
                                       , ac_oc_rclist=ac_oc_rclist)
            except:
                return render_template("error.html", LinkHome=LinkHome, error="Unable to find " + ocn)
        if country == 'CANADA':
            try:
                cur.execute("select NPA, COCodeNXX, RateCenter from caoc where OCN='"
                            + ocn + "' order by NPA, COCodeNXX")
                row = cur.fetchone()
                while row:
                    ac_oc_list.append(row)
                    row = cur.fetchone()
                cur.execute("select NPA, COCodeNXX, RateCenter from caoc where OCN='"
                            + ocn + "' order by RateCenter, NPA, COCodeNXX")
                row = cur.fetchone()
                while row:
                    ac_oc_rclist.append(row)
                    row = cur.fetchone()
                return render_template("ca-ocn.html", LinkHome=LinkHome, myurl=myurl, ocn=ocn, state=state
                                       , ac_oc_list=ac_oc_list, ac_oc_rclist=ac_oc_rclist
                                       , companyname=companyname)
            except:
                return render_template("error.html", LinkHome=LinkHome, error="Unable to find " + ocn)
    return render_template("error.html", LinkHome=LinkHome, error='URL is not correct.')


@app.route('/companyall', methods=['GET'])
def companyall():
    conn = sqlite3.connect(FilePath + 'pn.db')
    cur = conn.cursor()

    ocnall_list = []

    try:
        cur.execute("select Company, OCN, State from oc where Company is not '' and OCN is not '' order by Company, State")
        row = cur.fetchone()
        while row:
            if row not in ocnall_list:
                ocnall_list.append(row)
            row = cur.fetchone()
        return render_template("ocn-all.html", LinkHome=LinkHome, myurl=myurl, ocnall_list=ocnall_list)
    except:
        return render_template("error.html", LinkHome=LinkHome, error="Unable to find OCN")



@app.route('/areacodes', methods=['GET'])
def areacodes():
    conn = sqlite3.connect(FilePath + 'pn.db')
    cur = conn.cursor()

    ac_tuple = ()
    ac_headers = []
    ac_oc_list = []
    acoclist_as = []
    acoclist_rv = []
    acoclist_vc = []
    acoclist_pr = []
    acoclist_ua = []
    acoclist_inservice = []
    acoclist_forspecialuse = []
    acoclist_other = []

    ac_return = {}

    state_name = ''
    state = ''
    country = ''
    mapfile = ''

    if 'npa' in request.args and len(request.args['npa']) == 3:
        npa_code = request.args['npa']
        npanxx = str(npa_code) + '-'

        cur.execute("PRAGMA table_info(ac);")
        row = cur.fetchall()
        for item in row:
            ac_headers.append(item[1])
        try:
            cur.execute("select * from ac where NPA_ID='" + npa_code + "'")
            ac_tuple = cur.fetchall()
            state = ac_tuple[0][8]
            country = ac_tuple[0][9]
            ac_return = dict(zip(ac_headers, ac_tuple[0]))
        except:
            return render_template("error.html", error="Unable to find " + npa_code)

        if country == 'US':
            cur.execute("select NPANXX, use from oc where NPANXX like " + " '%" + npanxx + "%'")
            row = cur.fetchone()
            while row:
                ac_oc_list.append(row)
                row = cur.fetchone()
            for item in ac_oc_list:
                if item[1] == 'AS':
                    acoclist_as.append(item[0][-3:])
                elif item[1] == 'RV':
                    acoclist_rv.append(item[0][-3:])
                elif item[1] == 'VC':
                    acoclist_vc.append(item[0][-3:])
                elif item[1] == 'PR':
                    acoclist_pr.append(item[0][-3:])
                elif item[1] == 'UA':
                    acoclist_ua.append(item[0][-3:])
            if state in States:
                state_name = States[state]
                return render_template("ac.html", LinkHome=LinkHome, ac_tuple=ac_tuple, ac_return=ac_return
                                       , ac_oc_list=ac_oc_list, state_name=state_name, npa_code=npa_code, myurl=myurl
                                       , USACMapFilePath=USACMapFilePath, StateFilePath=StateFilePath
                                       , acoclist_as=acoclist_as, acoclist_rv=acoclist_rv, acoclist_vc=acoclist_vc
                                       , acoclist_pr=acoclist_pr, acoclist_ua=acoclist_ua)
            if state in USTerritory:
                if state == 'PUERTO RICO':
                    state_name = USTerritory[state]
                    mapfile = 'Puerto_Rico_787_939.gif'
                if state == 'AS':
                    state_name = USTerritory[state]
                    mapfile = 'American_Samoa_684.gif'
                if state == 'GU':
                    state_name = USTerritory[state]
                    mapfile = 'Guam_671.gif'
                if state == 'CNMI':
                    state_name = USTerritory[state]
                    mapfile = 'Northern_Marianna_Islands_670.gif'
                if state == 'USVI':
                    state_name = USTerritory[state]
                    mapfile = 'US_Virgin_Islands_340.gif'
                return render_template("territory-ac.html", LinkHome=LinkHome, ac_tuple=ac_tuple, ac_return=ac_return
                                       , state_name=state_name, npa_code=npa_code, myurl=myurl, ac_oc_list=ac_oc_list
                                       , USTerritoryFilePath=USTerritoryFilePath, mapfile=mapfile
                                       , acoclist_as=acoclist_as, acoclist_rv=acoclist_rv, acoclist_vc=acoclist_vc
                                       , acoclist_pr=acoclist_pr, acoclist_ua=acoclist_ua)
        if country == 'CANADA':
            cur.execute("select COCodeNXX, Status from caoc where NPA='" + npa_code + "'")
            row = cur.fetchone()
            while row:
                ac_oc_list.append(row)
                row = cur.fetchone()
            for item in ac_oc_list:
                if item[1] == 'In Service':
                    acoclist_inservice.append(item[0])
                elif item[1] == 'For Special Use':
                    acoclist_forspecialuse.append(item[0])
                else:
                    acoclist_other.append(item[0])
            if state == 'QUEBEC':
                state_name == 'QUEBEC'
                mapfile = 'qc-s.png'
            if state == 'BRITISH COLUMBIA':
                state_name == 'BRITISH COLUMBIA'
                mapfile = 'bc-s.png'
            if state == 'ONTARIO':
                state_name == 'ONTARIO'
                mapfile = 'on-s.png'
            state = CanadaPT[state]
            return render_template("canada-ac.html", LinkHome=LinkHome, ac_tuple=ac_tuple, ac_return=ac_return
                                   , state_name=state_name, state=state, npa_code=npa_code, myurl=myurl
                                   , CanadaFilePath=CanadaFilePath, mapfile=mapfile
                                   , acoclist_inservice=acoclist_inservice
                                   , acoclist_forspecialuse=acoclist_forspecialuse
                                   , acoclist_other=acoclist_other)
        mapfile = ''
        if state == 'JAMAICA':
            state_name == 'JAMAICA'
            mapfile = 'Jamaica_876.gif'
        if state == 'BAHAMAS':
            state_name == 'BAHAMAS'
            mapfile = 'Bahamas_242.gif'
        if state == 'BARBADOS':
            state_name == 'BARBADOS'
            mapfile = 'Barbados_246.gif'
        if state == 'ANTIGUA/BARBUDA':
            state_name == 'ANTIGUA/BARBUDA'
            mapfile = 'Antigua_and_Barbuda_268.gif'
        if state == 'BRITISH VIRGIN ISLANDS':
            state_name == 'BRITISH VIRGIN ISLANDS'
            mapfile = 'British_Virgin_Islands_284.gif'
        if state == 'CAYMAN ISLANDS':
            state_name == 'CAYMAN ISLANDS'
            mapfile = 'Cayman_Islands_345.gif'
        if state == 'BERMUDA':
            state_name == 'BERMUDA'
            mapfile = 'Bermuda_441.gif'
        if state == 'GRENADA':
            state_name == 'GRENADA'
            mapfile = 'Grenada_473.gif'
        if 'TURKS' in state:
            state_name == 'TURKS'
            mapfile = 'Jamaica_876.gif'
        if state == 'MONTSERRAT':
            state_name == 'MONTSERRAT'
            mapfile = 'Montserrat_664.gif'
        if state == 'SINT MAARTEN':
            state_name == 'SINT MAARTEN'
            mapfile = 'Sint_Maarten_721.gif'
        if 'ST. LUCIA' in state:
            state_name == 'Saint Lucia'
            mapfile = 'Saint_Lucia_758.gif'
        if state == 'DOMINICA':
            state_name == 'DOMINICA'
            mapfile = 'Dominica_767.gif'
        if 'VINCENT' in state:
            state_name == 'Saint Vincent and The Grenadines'
            mapfile = 'Saint_Vincent_and_The_Grenadines_784.gif'
        if state == 'DOMINICAN REPUBLIC':
            state_name == 'Dominican Republic'
            mapfile = 'Dominican_Republic_809_829_849.gif'
        if 'TRINIDAD' in state:
            state_name == 'Trinidad and Tobago'
            mapfile = 'Trinidad_and_Tobago_868.gif'
        if 'ST. KITTS' in state:
            state_name == 'Saint Kitts and Nevis'
            mapfile = 'Saint_Kitts_and_Nevis_869.gif'
        return render_template("country-ac.html", LinkHome=LinkHome, ac_tuple=ac_tuple, ac_return=ac_return
                               , state_name=state_name, npa_code=npa_code, myurl=myurl
                               , CountryFilePath=CountryFilePath, mapfile=mapfile)
    return render_template("error.html", LinkHome=LinkHome, error='URL is not correct')

@app.route('/aclist', methods=['GET'])
def aclist():
    conn = sqlite3.connect(FilePath + 'pn.db')
    cur = conn.cursor()
    try:
        cur.execute("select NPA_ID, type_of_code, location, country, assigned, reserved, in_service from ac order by NPA_ID")
        row = cur.fetchone()
        ac_list_assigned = []
        ac_list_unassigned = []
        ac_list_reserved = []
        if row is not None:
            while row:
                list_row = list(row)
                if list_row[4] == "Yes":
                    acla = dict(zip(['NPA_ID', 'type_of_code', 'location', 'country'], row))
                    ac_list_assigned.append(acla)
                elif list_row[5] == 'Yes':
                    aclr = dict(zip(['NPA_ID', 'type_of_code', 'location', 'country'], row))
                    ac_list_reserved.append(aclr)
                else:
                    aclu = dict(zip(['NPA_ID', 'type_of_code', 'location', 'country'], row))
                    ac_list_unassigned.append(aclu)
                row = cur.fetchone()
        return render_template("aclist-npa.html", LinkHome=LinkHome, myurl=myurl, ac_list_assigned=ac_list_assigned
                               , ac_list_reserved=ac_list_reserved, ac_list_unassigned=ac_list_unassigned)
    except:
        return render_template("error.html", LinkHome=LinkHome, error='Error getting the list of NPAs.')


@app.route('/acmaps', methods=['GET'])
def acmaps():
    conn = sqlite3.connect(FilePath + 'pn.db')
    cur = conn.cursor()

    mapfile = ''
    statename = ''
    if 'state' in request.args:
        state = str(request.args['state']).upper()
        StateACs = []
        if state in States:
            cur.execute("select NPA_ID from ac where LOCATION='" + state + "'")
            row = cur.fetchone()
            while row:
                row = str(row).replace('(', '')
                row = str(row).replace(')', '')
                row = str(row).replace('[', '')
                row = str(row).replace(']', '')
                row = str(row).replace(',', '')
                row = str(row).replace("'", '')
                StateACs.append(row)
                row = cur.fetchone()
            statename = States[state]
            return render_template("maps.html", LinkHome=LinkHome, statename=statename, StateACs=StateACs, state=state
                                   , USACMapFilePath=USACMapFilePath, StateFilePath=StateFilePath)
        elif state in CanadaPT:
            cur.execute("select NPA_ID from ac where LOCATION='" + state + "'")
            row = cur.fetchone()
            while row:
                row = str(row).replace('(', '')
                row = str(row).replace(')', '')
                row = str(row).replace('[', '')
                row = str(row).replace(']', '')
                row = str(row).replace(',', '')
                row = str(row).replace("'", '')
                StateACs.append(row)
                row = cur.fetchone()
            statename = CanadaPT[state]
            if state == 'BRITISH COLUMBIA':
                mapfile = 'bc-s.png'
            elif state == 'ONTARIO':
                mapfile = 'on-s.png'
            elif state == 'QUEBEC':
                mapfile = 'qc-s.png'
            return render_template("canada-maps.html", LinkHome=LinkHome, statename=statename
                                   , StateACs=StateACs, state=state, CanadaFilePath=CanadaFilePath
                                   , mapfile=mapfile)
        elif state in USTerritory:
            cur.execute("select NPA_ID from ac where LOCATION='" + state + "'")
            row = cur.fetchone()
            while row:
                row = str(row).replace('(', '')
                row = str(row).replace(')', '')
                row = str(row).replace('[', '')
                row = str(row).replace(']', '')
                row = str(row).replace(',', '')
                row = str(row).replace("'", '')
                StateACs.append(row)
                row = cur.fetchone()
            statename = USTerritory[state]
            if state == 'AS':
                mapfile = 'American_Samoa_684.gif'
            if state == 'GU':
                mapfile = 'Guam_671.gif'
            if state == 'PUERTO RICO':
                mapfile = 'Puerto_Rico_787_939.gif'
            if state == 'USVI':
                mapfile = 'US_Virgin_Islands_340.gif'
            if state == 'CNMI':
                mapfile = 'Northern_Marianna_Islands_670.gif'
            return render_template("territory-maps.html", LinkHome=LinkHome, statename=statename
                                   , StateACs=StateACs, state=state, USTerritoryFilePath=USTerritoryFilePath
                                   , mapfile=mapfile)
        else:
            cur.execute("select NPA_ID from ac where LOCATION like '%" + state + "%'")
            row = cur.fetchone()
            while row:
                row = str(row).replace('(', '')
                row = str(row).replace(')', '')
                row = str(row).replace('[', '')
                row = str(row).replace(']', '')
                row = str(row).replace(',', '')
                row = str(row).replace("'", '')
                StateACs.append(row)
                row = cur.fetchone()
        if state == 'JAMAICA':
            mapfile = 'Jamaica_876.gif'
        if state == 'BAHAMAS':
            mapfile = 'Bahamas_242.gif'
        if state == 'BARBADOS':
            mapfile = 'Barbados_246.gif'
        if state == 'ANTIGUA/BARBUDA':
            mapfile = 'Antigua_and_Barbuda_268.gif'
        if state == 'BRITISH VIRGIN ISLANDS':
            mapfile = 'British_Virgin_Islands_284.gif'
        if state == 'CAYMAN ISLANDS':
            mapfile = 'Cayman_Islands_345.gif'
        if state == 'BERMUDA':
            mapfile = 'Bermuda_441.gif'
        if state == 'GRENADA':
            mapfile = 'Grenada_473.gif'
        if 'TURKS' in state:
            mapfile = 'Jamaica_876.gif'
        if state == 'MONTSERRAT':
            mapfile = 'Montserrat_664.gif'
        if state == 'SINT MAARTEN':
            mapfile = 'Sint_Maarten_721.gif'
        if 'ST. LUCIA' in state:
            mapfile = 'Saint_Lucia_758.gif'
        if state == 'DOMINICA':
            mapfile = 'Dominica_767.gif'
        if 'VINCENT' in state:
            mapfile = 'Saint_Vincent_and_The_Grenadines_784.gif'
        if state == 'DOMINICAN REPUBLIC':
            mapfile = 'Dominican_Republic_809_829_849.gif'
        if 'TRINIDAD' in state:
            mapfile = 'Trinidad_and_Tobago_868.gif'
        if 'ST. KITTS' in state:
            mapfile = 'Saint_Kitts_and_Nevis_869.gif'
        return render_template("country-maps.html", LinkHome=LinkHome
                               , StateACs=StateACs, state=state, CountryFilePath=CountryFilePath, mapfile=mapfile)
    else:
        return render_template("error.html", LinkHome=LinkHome, error='The URL appears to be incorrect.')


@app.route('/5xx', methods=['GET'])
def fivexlist():
    conn = sqlite3.connect(FilePath + 'pn.db')
    cur = conn.cursor()

    list5xx = []

    if '5xxlist' in request.args:
        cur.execute("select * from fivex")
        row = cur.fetchone()
        while row:
            list5xx.append(row)
            row = cur.fetchone()
        return render_template("5xx.html", LinkHome=LinkHome, list5xx=list5xx)
    else:
        return render_template("error.html", LinkHome=LinkHome, error='The URL appears to be incorrect.')


@app.route('/900', methods=['GET'])
def list900():
    if '900list' in request.args:
        return render_template("900.html", LinkHome=LinkHome, codes900=codes900)
    else:
        return render_template("error.html", LinkHome=LinkHome, error='The URL appears to be incorrect.')


@app.route('/fgbcic', methods=['GET'])
def fgbcic():
    if 'cic' in request.args:
        return render_template("fgbcic.html", LinkHome=LinkHome, FGBCICCodes=FGBCICCodes)
    else:
        return render_template("error.html", LinkHome=LinkHome, error='The URL appears to be incorrect.')


@app.route('/fgdcic', methods=['GET'])
def fgdcic():
    if 'cic' in request.args:
        cic_code = request.args['cic']
        if len(cic_code) == 4:
            if any(item['CIC'] == cic_code for item in FGDCICCodes):
                search_item_cic = next(item for item in FGDCICCodes if item["CIC"] == cic_code)
                cic_return = []
                cicr = {}
                for item in search_item_cic.items():
                    cic_return.append(item)
                    cicr[item[0]] = item[1]
                return render_template("fgdcic.html", LinkHome=LinkHome, cicr=cicr, cic_code=cic_code)
            else:
                return render_template("error.html", LinkHome=LinkHome, error="Unable to find " + cic_code)
        else:
            return render_template("error.html", LinkHome=LinkHome, error="The CIC code is not 4 digits 'example: 0222'")
    else:
        return render_template("error.html", LinkHome=LinkHome, error='The URL appears to be incorrect.')


@app.route('/n11', methods=['GET'])
def n11():
    if 'n11' in request.args:
        all_n11_codes = []
        for item in N11Codes:
            all_n11_codes.append(item)
        return render_template("n11.html", LinkHome=LinkHome, all_n11_codes=all_n11_codes)
    else:
        return render_template("error.html", LinkHome=LinkHome, error='The URL appears to be incorrect.')


app.run(host=myip, port=myport)
