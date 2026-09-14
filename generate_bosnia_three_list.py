import re
from urllib.request import urlopen, Request

OUTPUT_FILE = "output_bosnia3.txt"

BH_URL = "https://raw.githubusercontent.com/chiewww/BHposta/main/bh_posta_countries.txt"
MOSTAR_URL = "https://raw.githubusercontent.com/chiewww/mostarpost/main/output.txt"
SRPSKE_URL = "https://raw.githubusercontent.com/chiewww/srpskepost/main/output.txt"

EXCLUDED_NUMBERS = {29}

MASTER_LIST = """
1 Afghanistan
2 Åland Islands
3 Albania
4 Algeria
5 American Samoa
6 Andorra
7 Angola
8 Anguilla
9 Antarctica
10 Antigua & Barbuda
11 Argentina
12 Armenia
13 Aruba
14 Australia
15 Austria
16 Azerbaijan
17 Bahamas
18 Bahrain
19 Bangladesh
20 Barbados
21 Belarus
22 Belgium
23 Belize
24 Benin
25 Bermuda
26 Bhutan
27 Bolivia
28 Bonaire, Sint Eustatius and Saba
29 Bosnia-Herzegovina
30 Botswana
31 Brazil
32 British Indian Ocean Territory
33 Brunei
34 Bulgaria
35 Burkina Faso
36 Burundi
37 Cabo Verde
38 Cambodia
39 Cameroon
40 Canada
41 Cayman Islands
42 Central African Republic
43 Chad
44 Chile
45 China
46 Christmas Island
47 Cocos Islands
48 Colombia
49 Comoros
50 Congo
51 Dem. Rep. Of Congo
52 Cook Islands
53 Costa Rica
54 Côte d'Ivoire
55 Croatia
56 Cuba
57 Curaçao
58 Cyprus
59 Czechia
60 Denmark
61 Djibouti
62 Dominica
63 Dominican Republic
64 Ecuador
65 Egypt
66 El Salvador
67 Equatorial Guinea
68 Eritrea
69 Estonia
70 Eswatini /Swaziland
71 Ethiopia
72 Falkland Islands /Malvinas
73 Faroe Islands
74 Fiji
75 Finland
76 France
77 French Guiana
78 French Polynesia
79 French Southern Territories
80 Gabon
81 Gambia
82 Georgia
83 Germany
84 Ghana
85 Gibraltar
86 Greece
87 Greenland
88 Grenada
89 Guadeloupe
90 Guam
91 Guatemala
92 Guernsey
93 Guinea
94 Guinea-Bissau
95 Guyana
96 Haiti
97 Honduras
98 Hong Kong
99 Hungary
100 Iceland
101 India
102 Indonesia
103 Iran
104 Iraq
105 Ireland
106 Isle of Man
107 Israel
108 Italy
109 Jamaica
110 Japan
111 Jersey
112 Jordan
113 Kazakhstan
114 Kenya
115 Kiribati
116 Korea(North)
117 Korea(South)
118 Kosovo
119 Kuwait
120 Kyrgyzstan
121 Laos
122 Latvia
123 Lebanon
124 Lesotho
125 Liberia
126 Libya
127 Liechtenstein
128 Lithuania
129 Luxembourg
130 Macao
131 Madagascar
132 Malawi
133 Malaysia
134 Maldives
135 Mali
136 Malta
137 Marshall Islands
138 Martinique
139 Mauritania
140 Mauritius
141 Mayotte
142 Mexico
143 Micronesia
144 Moldova
145 Monaco
146 Mongolia
147 Montenegro
148 Montserrat
149 Morocco
150 Mozambique
151 Myanmar
152 Namibia
153 Nauru / Naoero
154 Nepal
155 Netherlands
156 New Caledonia
157 New Zealand
158 Nicaragua
159 Niger
160 Nigeria
161 Niue
162 Norfolk Island
163 Northern Mariana Islands
164 North Macedonia
165 Norway
166 Oman
167 Pakistan
168 Palau
169 Palestine
170 Panama
171 Papua New Guinea
172 Paraguay
173 Peru
174 Philippines
175 Pitcairn
176 Poland
177 Portugal
178 Puerto Rico
179 Qatar
180 Réunion
181 Romania
182 Russia
183 Rwanda
184 Saint Barthélemy
185 Saint Helena, Ascension and Tristan da Cunha
186 Saint Kitts and Nevis
187 Saint Lucia
188 Saint Martin
189 Saint Pierre & Miquelon
190 Saint Vincent and the Grenadines
191 Samoa
192 San Marino
193 Sao Tome and Principe
194 Saudi Arabia
195 Senegal
196 Serbia
197 Seychelles
198 Sierra Leone
199 Singapore
200 Sint Maarten
201 Slovakia
202 Slovenia
203 Solomon Islands
204 Somalia
205 South Africa
206 South Georgia and S. Sandwich Islands
207 South Sudan
208 Spain
209 Sri Lanka
210 Sudan
211 Suriname
212 Svalbard and Jan Mayen
213 Sweden
214 Switzerland
215 Syria
216 Taiwan
217 Tajikistan
218 Tanzania
219 Thailand
220 Timor-Leste
221 Togo
222 Tokelau
223 Tonga
224 Trinidad and Tobago
225 Tunisia
226 Turkey
227 Turkmenistan
228 Turks and Caicos Islands
229 Tuvalu
230 Uganda
231 Ukraine
232 United Arab Emirates
233 United Kingdom
234 Uruguay
235 U.S.A.
236 U.S. Minor Outlying Islands
237 Uzbekistan
238 Vanuatu
239 Vatican
240 Venezuela
241 Vietnam
242 Virgin Islands (UK)
243 Virgin Islands of the USA
244 Wallis & Futuna
245 Western Sahara
246 Yemen
247 Zambia
248 Zimbabwe
"""


def parse_master_list():
    master = {}

    for line in MASTER_LIST.strip().splitlines():
        match = re.match(r"^\s*(\d+)\s+(.+?)\s*$", line)

        if match:
            number = int(match.group(1))
            name = match.group(2)

            if number not in EXCLUDED_NUMBERS:
                master[number] = name

    expected = 248 - len(EXCLUDED_NUMBERS)

    if len(master) != expected:
        raise RuntimeError(
            f"Expected {expected} usable master destinations, "
            f"but found {len(master)}."
        )

    return master


def download_text(url):
    request = Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def extract_number_from_line(line):
    match = re.match(
        r"^\s*(\d{1,3})(?:\s+|[.)\-:]\s*)",
        line
    )

    if not match:
        return None

    number = int(match.group(1))

    if 1 <= number <= 248:
        return number

    return None


def extract_all_listed_numbers(text, master_numbers):
    numbers = set()

    for line in text.splitlines():
        number = extract_number_from_line(line)

        if number is not None and number in master_numbers:
            numbers.add(number)

    return numbers


def normalize_heading(line):
    value = line.strip().upper()
    value = re.sub(r"\s+", " ", value)
    value = value.rstrip(":").strip()
    return value


def parse_bh_suspensions(text, master_numbers):
    """
    BH Posta suspended destinations are ONLY the destinations
    listed under:

        SUSPENDED COUNTRIES
        UNKNOWN COUNTRIES

    Rules:
    - Combine both sections.
    - Ignore ??? entries.
    - Ignore UKUPNO / totals / headings.
    - Only accept destination numbers from the master list.
    - Remove duplicate Postcrossing numbers.
    """

    lines = text.splitlines()
    suspended_numbers = set()

    target_headings = {
        "SUSPENDED COUNTRIES",
        "UNKNOWN COUNTRIES",
    }

    current_section = None

    for line in lines:
        stripped = line.strip()
        heading = normalize_heading(line)

        # ----------------------------------------------------
        # Start either of the two required BH Posta sections.
        # ----------------------------------------------------

        if heading in target_headings:
            current_section = heading
            continue

        # ----------------------------------------------------
        # If we are inside one of the two sections, ONLY
        # numbered destination lines are relevant.
        #
        # Do NOT stop on uppercase text.
        # ----------------------------------------------------

        if current_section in target_headings:

            number = extract_number_from_line(stripped)

            if number is not None:
                if number in master_numbers:
                    suspended_numbers.add(number)

    return suspended_numbers


def parse_mostar_listed(text, master_numbers):
    return extract_all_listed_numbers(
        text,
        master_numbers
    )


def parse_mostar_suspensions(text, master_numbers):
    listed = parse_mostar_listed(
        text,
        master_numbers
    )

    return master_numbers - listed


def parse_srpske_suspensions(text, master_numbers):
    """
    Srpske:
    ONLY destinations listed under SUSPENDOVANE ZEMLJE.

    UKUPNO is ignored and does not determine the list.
    """

    lines = text.splitlines()
    suspended = set()
    in_section = False

    for line in lines:
        heading = normalize_heading(line)

        if heading == "SUSPENDOVANE ZEMLJE":
            in_section = True
            continue

        if not in_section:
            continue

        # UKUPNO is only a count.
        if heading.startswith("UKUPNO"):
            continue

        # Do not treat arbitrary uppercase text as a boundary.
        # Stop only at known section headings.
        if heading in {
            "DOZVOLJENE ZEMLJE",
            "DOZVOLJENE DRŽAVE",
            "DOZVOLJENE DRZAVE",
            "OSTALE ZEMLJE",
            "OSTALE DRŽAVE",
            "OSTALE DRZAVE",
            "ZABRANJENE ZEMLJE",
            "ZABRANJENE DRŽAVE",
            "ZABRANJENE DRZAVE",
        }:
            break

        number = extract_number_from_line(line)

        if number is not None and number in master_numbers:
            suspended.add(number)

    return suspended


def write_section(file, title, numbers, master):
    file.write(f"{title}\n")
    file.write("=" * len(title) + "\n")
    file.write(f"Total: {len(numbers)}\n\n")

    for number in sorted(numbers):
        file.write(
            f"{number} {master[number]}\n"
        )

    file.write("\n")


def main():
    master = parse_master_list()
    master_numbers = set(master.keys())

    print(f"Usable master destinations: {len(master_numbers)}")

    print("Downloading BH Posta...")
    bh_text = download_text(BH_URL)

    print("Downloading Mostar...")
    mostar_text = download_text(MOSTAR_URL)

    print("Downloading Srpske...")
    srpske_text = download_text(SRPSKE_URL)

    # ========================================================
    # BH POSTA
    # ========================================================

    bh_suspended = parse_bh_suspensions(
        bh_text,
        master_numbers
    )

    bh_listed = extract_all_listed_numbers(
        bh_text,
        master_numbers
    )

    # ========================================================
    # MOSTAR
    # ========================================================

    mostar_listed = parse_mostar_listed(
        mostar_text,
        master_numbers
    )

    mostar_suspended = (
        master_numbers - mostar_listed
    )

    # ========================================================
    # SRPSKE
    # ========================================================

    srpske_suspended = parse_srpske_suspensions(
        srpske_text,
        master_numbers
    )

    srpske_listed = extract_all_listed_numbers(
        srpske_text,
        master_numbers
    )

    # ========================================================
    # SECTION 1
    # ========================================================

    suspended_at_least_one = (
        bh_suspended
        | mostar_suspended
        | srpske_suspended
    )

    # ========================================================
    # SECTION 2
    # ========================================================

    all_listed = (
        bh_listed
        | mostar_listed
        | srpske_listed
    )

    missing_from_all_three = (
        master_numbers - all_listed
    )

    # ========================================================
    # OUTPUT
    # ========================================================

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        # ----------------------------------------------------
        # 1. SUSPENDED AT LEAST ONE
        # ----------------------------------------------------

        title = "1. Suspended at least one"

        file.write(f"{title}\n")
        file.write("=" * len(title) + "\n")
        file.write(
            "Countries suspended by BH Posta, Mostar, "
            "and/or Srpske.\n"
        )
        file.write(
            "B = BH Posta, M = Mostar, S = Srpske\n"
        )
        file.write(
            f"Total: {len(suspended_at_least_one)}\n\n"
        )

        for number in sorted(suspended_at_least_one):
            letters = []

            if number in bh_suspended:
                letters.append("B")

            if number in mostar_suspended:
                letters.append("M")

            if number in srpske_suspended:
                letters.append("S")

            file.write(
                f"{number} {master[number]} "
                f"({', '.join(letters)})\n"
            )

        file.write("\n")

        # ----------------------------------------------------
        # 2. MISSING FROM ALL 3
        # ----------------------------------------------------

        title = "2. Missing from all 3 text files"

        file.write(f"{title}\n")
        file.write("=" * len(title) + "\n")
        file.write(
            "Countries from the 248-country master list "
            "that are NOT LISTED on the BH Posta, Mostar, "
            "or Srpske text files.\n"
        )
        file.write(
            f"Total: {len(missing_from_all_three)}\n\n"
        )

        for number in sorted(missing_from_all_three):
            file.write(
                f"{number} {master[number]}\n"
            )

        file.write("\n")

        # ----------------------------------------------------
        # 3. BH POSTA
        # ----------------------------------------------------

        write_section(
            file,
            "3. BH Posta suspensions",
            bh_suspended,
            master
        )

        # ----------------------------------------------------
        # 4. MOSTAR
        # ----------------------------------------------------

        write_section(
            file,
            "4. Mostar suspensions",
            mostar_suspended,
            master
        )

        # ----------------------------------------------------
        # 5. SRPSKE
        # ----------------------------------------------------

        title = "5. Srpske suspensions"

        file.write(f"{title}\n")
        file.write("=" * len(title) + "\n")
        file.write(
            "Suspended countries are ONLY those listed "
            "under 'SUSPENDOVANE ZEMLJE' in the Srpske "
            "output file.\n"
        )
        file.write(
            f"Total: {len(srpske_suspended)}\n\n"
        )

        for number in sorted(srpske_suspended):
            file.write(
                f"{number} {master[number]}\n"
            )

        file.write("\n")

    # ========================================================
    # CONSOLE SUMMARY
    # ========================================================

    print()
    print("==========================================")
    print("Bosnia Three List updated successfully")
    print("==========================================")
    print(f"Master destinations used: {len(master_numbers)}")
    print("Excluded destination #29: Bosnia-Herzegovina")
    print(
        f"Suspended at least one: "
        f"{len(suspended_at_least_one)}"
    )
    print(
        f"Missing from all 3 files: "
        f"{len(missing_from_all_three)}"
    )
    print(
        f"BH Posta suspensions: "
        f"{len(bh_suspended)}"
    )
    print(
        f"Mostar suspensions: "
        f"{len(mostar_suspended)}"
    )
    print(
        f"Srpske suspensions: "
        f"{len(srpske_suspended)}"
    )
    print()
    print(f"Output file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
