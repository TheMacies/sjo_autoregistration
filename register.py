import grequests
import requests
from bs4 import BeautifulSoup, SoupStrainer


def register(url, data):
    spam_requests(url, "post", data=data)


def get_registration_url(url, chosen_course, payload, method="get"):
    if method == "get":
        lt_response = spam_requests(url, "get", data=payload)
    else:
        lt_response = spam_requests(url, "post", data=payload)
    courses = BeautifulSoup(lt_response.content, 'html.parser').findAll('tr')[1:]
    for course in courses:
        if course.find('td').text == chosen_course:
            registration_url = "https://ssl.sjo.pw.edu.pl" + course.find('a')['href']
            return registration_url


def spam_requests(url, method, **kwargs):
    if method == "get":
        response = s.get(url, **kwargs)
    else:
        response = s.post(url, **kwargs)
    if response.status_code == 200:
        return response
    else:
        return spam_requests(url, method, **kwargs)


index = input('Podaj nr albumu')
first_name = input('Podaj imie')
last_name = input('Podaj nazwisko')
faculty = input('Podaj pełną nazwę wydziału')
desired_course = input('Podaj symbol lektoratu ( np . 001/Z/16/17 )')
year = input('Podaj rok studiow')
term = input('Podaj semestr Studiow')

# index = 0
# first_name = ""
# last_name = ""
# faculty = ""
# desired_course = ""
# year = 1
# term = 1

course_number = -1
language_number = -1

while course_number < 1 or course_number > 2:
    print("""
    Wybierz jezyk dla ktorego chcesz wprowadzic punkty:
        [1] Lektorat Tematyczne
        [2] Lektorat Inne-Jezyki
        \n
    """)
    course_number = int(input("Numer: "))


registration_url = ""
s = requests.session()

login_page_response = spam_requests('https://ssl.sjo.pw.edu.pl/index.php/site/login', "get")
login_page = BeautifulSoup(login_page_response.content, 'html.parser')

faculty_id = -1
options = login_page.findAll('option')

for option in options:
    if option.text == faculty:
        faculty_id = option['value']
        break

if faculty_id is -1:
    print('Błędny wydział')
    exit()

login_payload = {"LoginForm[wydzial]": faculty_id, "LoginForm[imie]": first_name, "LoginForm[nazwisko]": last_name,
                 "LoginForm[album]": index, "YII_CSRF_TOKEN": login_page_response.cookies['YII_CSRF_TOKEN']}

index_page_response = spam_requests('https://ssl.sjo.pw.edu.pl/index.php/site/login', "post", data=login_payload)

if index_page_response.url == 'https://ssl.sjo.pw.edu.pl/index.php/site/login':
    print('bledne dane logowania')
    exit()

if course_number == 1:
    get_language_link_payload = {"YII_CSRF_TOKEN": login_page_response.cookies['YII_CSRF_TOKEN']}
    registration_url = get_registration_url("https://ssl.sjo.pw.edu.pl/index.php/lt", desired_course, get_language_link_payload)
else:
    while language_number < 1 or language_number > 8:
        print("""
        Wybierz jezyk dla ktorego chcesz wprowadzic punkty:
            [1] chiński
            [2] francuski
            [3] hiszpański
            [4] japoński
            [5] niemiecki
            [6] rosyjski
            [7] szwedzki
            [8] włoski\n
        """)
        language_number = int(input("Numer: "))

    test_points = int(input("Podaj punkty za test: \n"))

    test_payload = {"TestJezykowyForm[jezyk]": language_number, "TestJezykowyForm[punkty]": test_points,
                    "yt0": "Zapisz",
                    "YII_CSRF_TOKEN": login_page_response.cookies['YII_CSRF_TOKEN']}

    spam_requests("https://ssl.sjo.pw.edu.pl/index.php/dj/default/index", "post", data=test_payload)

    get_language_link_payload = {"ZapisyForm[jezyk]": language_number, "yt0": "Dalej >>",
                                 "YII_CSRF_TOKEN": login_page_response.cookies['YII_CSRF_TOKEN']}
    registration_url = get_registration_url("https://ssl.sjo.pw.edu.pl/index.php/dj/default/wyborJezyka", desired_course,
                               get_language_link_payload, method="post")

register_payload = {
    "YII_CSRF_TOKEN": login_page_response.cookies['YII_CSRF_TOKEN'],
    "ZapisyForm[rokStudiow]": year,
    "ZapisyForm[semestrStudiow]": term
}

register(registration_url, register_payload)

print('Pomyslnie zapisano :)')
