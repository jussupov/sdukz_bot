import requests
from settings import USERNAME, PASSWORD
import json
from pprint import pprint
from bs4 import BeautifulSoup

auth_url = "https://my.sdu.edu.kz/loginAuth.php"
grand_gpa = "https://my.sdu.edu.kz/?mod=transkript"
# all
yt = "1#1"

# now
yt = "2018#2"


def login(username, password):
    session = requests.session()
    data = {
        'username': username,
        'password': password,
        'LogIn': 'Log In'
    }
    headers = {
        'content-type': 'application/x-www-form-urlencoded'
    }
    session.post(auth_url, data=data, headers=headers)
    obj = get_info(session)
    return obj


def get_info(session):
    result = {
        'status': None
    }
    r = session.get('https://my.sdu.edu.kz/index.php')
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.find('table', {'class': 'clsTbl'})
        try:
            trs = table.find_all('tr')

            dict = {}
            for tr in trs:
                try:
                    tds = tr.find_all('td')
                    dict[tds[0].text.strip().replace(' :', '')] = tds[1].text.strip()
                except Exception:
                    pass
            result['content'] = dict
            result['status'] = True
        except Exception:
            result['status'] = False
    return result


def get_grades(username, password, yt):
    session = requests.session()
    data = {
        'username': username,
        'password': password,
        'LogIn': 'Log In'
    }
    headers = {
        'content-type': 'application/x-www-form-urlencoded'
    }
    session.post(auth_url, data=data, headers=headers)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'ajx': 1,
        'mod': 'grades',
        'action': 'GetGrades',
        'yt': yt,
    }
    r = session.post('https://my.sdu.edu.kz/index.php', data=data, headers=headers);
    data = json.loads(r.content)
    soup = BeautifulSoup(data['DATA'], 'html.parser')
    table = soup.find('table', {'id': 'coursesTable'})
    rows = table.find_all('tr', {'class': 'csrow'})
    list_subjects = []
    for row in rows:
        info = row.find_all('td', {'class': 'crtd'})
        subjects = {
            "Code": info[0].text.strip(),
            "Subject": info[1].text.strip(),
            "Credits": info[2].text.strip(),
            "Total": info[5].text.strip(),
            "Letter Grade": info[6].text.strip()
        }
        list_subjects.append(subjects);

    tables = table.find_all('table', {'class': 'ctbl'})
    list_grades = []
    for i in range(len(tables)):
        tds = tables[i].find_all('td', {'class': 'crtd'})
        try:
            grades = {}
            grades['midterm1'] = tds[5].text.strip()
            grades['midterm2'] = tds[8].text.strip()
            grades['final'] = tds[11].text.strip()
            list_grades.append(grades)
        except Exception:
            pass
    i = 0
    new_list = []
    for l in list_grades:
        if i % 2 == 0:
            new_list.append(l)
        i += 1
    list = zip(list_subjects, new_list)
    arr = []
    for pair in list:
        z, x = pair
        dict = {}
        for key, value in z.items():
            dict[key] = value
        for key, value in x.items():
            dict[key] = value
        arr.append(dict)
    return arr


def current_gpa(username, password, retries=3):
    try:
        session = requests.session()
        data = {
            'username': username,
            'password': password,
            'LogIn': 'Log In'
        }
        headers = {
            'content-type': 'application/x-www-form-urlencoded'
        }
        session.post(auth_url, data=data, headers=headers)

        r = session.get(grand_gpa)
        soup = BeautifulSoup(r.content, 'html.parser')
        td = soup.find(text=lambda x: "Grand GPA" in x)
        return td
    except Exception:
        if retries != 0:
            current_gpa(username, password, retries - 1)


if __name__ == '__main__':
    current_gpa('', '')
