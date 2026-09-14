import re
from pathlib import Path
from urllib.request import urlopen


# ============================================================
# SOURCE FILES
# ============================================================

BH_URL = "https://raw.githubusercontent.com/chiewww/BHposta/main/bh_posta_countries.txt"
MOSTAR_URL = "https://raw.githubusercontent.com/chiewww/mostarpost/main/output.txt"
SRPSKE_URL = "https://raw.githubusercontent.com/chiewww/srpskepost/main/output.txt"


# ============================================================
# MASTER LIST — POSTCROSSING NUMBERS
# ============================================================

MASTER_TEXT = r"""
1|Afghanistan
2|Åland Islands
3|Albania
4|Algeria
5|American Samoa
6|Andorra
7|Angola
8|Anguilla
9|Antarctica
10|Antigua & Barbuda
11|Argentina
12|Armenia
13|Aruba
14|Australia
15|Austria
16|Azerbaijan
17|Bahamas
18|Bahrain
19|Bangladesh
20|Barbados
21|Belarus
22|Belgium
23|Belize
24|Benin
25|Bermuda
26|Bhutan
27|Bolivia
28|Bonaire, Sint Eustatius and Saba
29|Bosnia-Herzegovina
30|Botswana
31|Brazil
32|British Indian Ocean Territory
33|Brunei
34|Bulgaria
35|Burkina Faso
36|Burundi
37|Cabo Verde
38|Cambodia
39|Cameroon
40|Canada
41|Cayman Islands
42|Central African Republic
43|Chad
44|Chile
45|China
46|Christmas Island
47|Cocos Islands
48|Colombia
49|Comoros
50|Congo
51|Dem. Rep. Of Congo
52|Cook Islands
53|Costa Rica
54|Côte d'Ivoire
55|Croatia
56|Cuba
57|Curaçao
58|Cyprus
59|Czechia
60|Denmark
61|Djibouti
62|Dominica
63|Dominican Republic
64|Ecuador
65|Egypt
66|El Salvador
67|Equatorial Guinea
68|Eritrea
69|Estonia
70|Eswatini /Swaziland
71|Ethiopia
72|Falkland Islands /Malvinas
73|Faroe Islands
74|Fiji
75|Finland
76|France
77|French Guiana
78|French Polynesia
79|French Southern Territories
80|Gabon
81|Gambia
82|Georgia
83|Germany
84|Ghana
85|Gibraltar
86|Greece
87|Greenland
88|Grenada
89|Guadeloupe
90|Guam
91|Guatemala
92|Guernsey
93|Guinea
94|Guinea-Bissau
95|Guyana
96|Haiti
97|Honduras
98|Hong Kong
99|Hungary
100|Iceland
101|India
102|Indonesia
103|Iran
104|Iraq
105|Ireland
106|Isle of Man
107|Israel
108|Italy
109|Jamaica
110|Japan
111|Jersey
112|Jordan
113|Kazakhstan
114|Kenya
115|Kiribati
116|Korea(North)
117|Korea(South)
118|Kosovo
119|Kuwait
120|Kyrgyzstan
121|Laos
122|Latvia
123|Lebanon
124|Lesotho
125|Liberia
126|Libya
127|Liechtenstein
128|Lithuania
129|Luxembourg
130|Macao
131|Madagascar
132|Malawi
133|Malaysia
134|Maldives
135|Mali
136|Malta
137|Marshall Islands
138|Martinique
139|Mauritania
140|Mauritius
141|Mayotte
142|Mexico
143|Micronesia
144|Moldova
145|Monaco
146|Mongolia
147|Montenegro
148|Montserrat
149|Morocco
150|Mozambique
151|Myanmar
152|Namibia
153|Nauru / Naoero
154|Nepal
155|Netherlands
156|New Caledonia
157|New Zealand
158|Nicaragua
159|Niger
160|Nigeria
161|Niue
162|Norfolk Island
163|Northern Mariana Islands
164|North Macedonia
165|Norway
166|Oman
167|Pakistan
168|Palau
169|Palestine
170|Panama
171|Papua New Guinea
172|Paraguay
173|Peru
174|Philippines
175|Pitcairn
176|Poland
177|Portugal
178|Puerto Rico
179|Qatar
180|Réunion
181|Romania
182|Russia
183|Rwanda
184|Saint Barthélemy
185|Saint Helena, Ascension and Tristan da Cunha
186|Saint Kitts and Nevis
187|Saint Lucia
188|Saint Martin
189|Saint Pierre & Miquelon
190|Saint Vincent and the Grenadines
191|Samoa
192|San Marino
193|Sao Tome and Principe
194|Saudi Arabia
195|Senegal
196|Serbia
197|Seychelles
198|Sierra Leone
199|Singapore
200|Sint Maarten
201|Slovakia
202|Slovenia
203|Solomon Islands
204|Somalia
205|South Africa
206|South Georgia and S. Sandwich Islands
207|South Sudan
208|Spain
209|Sri Lanka
210|Sudan
211|Suriname
212|Svalbard and Jan Mayen
213|Sweden
214|Switzerland
215|Syria
216|Taiwan
217|Tajikistan
218|Tanzania
219|Thailand
220|Timor-Leste
221|Togo
222|Tokelau
223|Tonga
224|Trinidad and Tobago
225|Tunisia
226|Turkey
227|Turkmenistan
228|Turks and Caicos Islands
229|Tuvalu
230|Uganda
231|Ukraine
232|United Arab Emirates
233|United Kingdom
234|Uruguay
235|U.S.A.
236|U.S. Minor Outlying Islands
237|Uzbekistan
238|Vanuatu
239|Vatican
240|Venezuela
241|Vietnam
242|Virgin Islands (UK)
243|Virgin Islands of the USA
244|Wallis & Futuna
245|Western Sahara
246|Yemen
247|Zambia
248|Zimbabwe
"""


MASTER = {}

for line in MASTER_TEXT.strip().splitlines():
    number, name = line.split("|", 1)
    MASTER[int(number)] = name


# ============================================================
# DOWNLOAD SOURCE FILES
# ============================================================

def download(url):
    print("Downloading:", url)

    request = __import__("urllib.request", fromlist=["Request"]).Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


bh_text = download(BH_URL)
mostar_text = download(MOSTAR_URL)
srpske_text = download(SRPSKE_URL)


# ============================================================
# EXTRACT POSTCROSSING NUMBERS
# ============================================================

def numbers_from_text(text):
    """
    Extract numbers that appear as standalone integers.

    Only numbers 1-248 can become destinations.
    """
    return {
        int(x)
        for x in re.findall(r"(?<!\d)(\d{1,3})(?!\d)", text)
        if 1 <= int(x) <= 248
    }


# ============================================================
# BH POSTA
#
# Use destinations under:
#   SUSPENDED COUNTRIES
#   UNKNOWN COUNTRIES
#
# Both categories are treated as unavailable/suspended.
# ============================================================

def extract_bh(text):
    upper = text.upper()

    wanted = [
        "SUSPENDED COUNTRIES",
        "UNKNOWN COUNTRIES",
    ]

    positions = []

    for heading in wanted:
        pos = upper.find(heading)
        if pos >= 0:
            positions.append(pos)

    if not positions:
        raise RuntimeError(
            "Could not find 'SUSPENDED COUNTRIES' or "
            "'UNKNOWN COUNTRIES' in BH Posta file."
        )

    # Extract from the first relevant heading onward.
    relevant = text[min(positions):]

    # Stop at obvious next major section if present.
    relevant_upper = relevant.upper()

    stop_headings = [
        "AVAILABLE COUNTRIES",
        "COUNTRIES AVAILABLE",
        "ACTIVE COUNTRIES",
    ]

    stop_positions = []

    for heading in stop_headings:
        pos = relevant_upper.find(heading)
        if pos > 0:
            stop_positions.append(pos)

    if stop_positions:
        relevant = relevant[:min(stop_positions)]

    return numbers_from_text(relevant)


bh = extract_bh(bh_text)


# ============================================================
# MOSTAR
#
# Definition:
# "Countries in the master 248 destinations that are not on
# this file"
#
# Therefore:
#   suspended = master destinations NOT appearing in Mostar file
# ============================================================

mostar_numbers_in_file = numbers_from_text(mostar_text)

mostar = set(MASTER) - mostar_numbers_in_file


# ============================================================
# SRPSKE
#
# Definition:
# "Countries in the master 248 destinations that are not
# available = UKUPNO"
#
# Extract the destination numbers from the UKUPNO section.
# ============================================================

def extract_srpske(text):
    upper = text.upper()

    pos = upper.find("UKUPNO")

    if pos < 0:
        raise RuntimeError(
            "Could not find 'UKUPNO' in Srpske file."
        )

    relevant = text[pos:]

    return numbers_from_text(relevant)


srpske = extract_srpske(srpske_text)


# ============================================================
# ONLY MASTER-LIST DESTINATIONS
# ============================================================

bh &= set(MASTER)
mostar &= set(MASTER)
srpske &= set(MASTER)


# ============================================================
# SUSPENDED AT LEAST ONE
# ============================================================

union = bh | mostar | srpske


# ============================================================
# OUTPUT
# ============================================================

output = []

output.append("BOSNIA THREE LIST")
output.append("")
output.append("1. SUSPENDED AT LEAST ONE")
output.append(f"TOTAL: {len(union)}")
output.append("")

for number in sorted(union):
    letters = []

    if number in bh:
        letters.append("B")

    if number in mostar:
        letters.append("M")

    if number in srpske:
        letters.append("S")

    output.append(
        f"{number} {MASTER[number]} ({', '.join(letters)})"
    )


output.append("")
output.append("2. SUSPENDED DESTINATIONS FOR BH POSTA")
output.append(f"TOTAL: {len(bh)}")
output.append("")

for number in sorted(bh):
    output.append(f"{number} {MASTER[number]}")


output.append("")
output.append("3. SUSPENDED DESTINATIONS FOR MOSTAR")
output.append(f"TOTAL: {len(mostar)}")
output.append("")

for number in sorted(mostar):
    output.append(f"{number} {MASTER[number]}")


output.append("")
output.append("4. SUSPENDED DESTINATIONS FOR SRPSKE")
output.append(f"TOTAL: {len(srpske)}")
output.append("")

for number in sorted(srpske):
    output.append(f"{number} {MASTER[number]}")


# ============================================================
# WRITE FILE
# ============================================================

output_file = Path("bosnia_three_list.txt")

output_file.write_text(
    "\n".join(output) + "\n",
    encoding="utf-8"
)

print()
print("========================================")
print("bosnia_three_list.txt CREATED")
print("========================================")
print(f"BH Posta:          {len(bh)}")
print(f"Mostar:            {len(mostar)}")
print(f"Srpske:            {len(srpske)}")
print(f"Suspended at least one: {len(union)}")
print("========================================")
