import cv2
import sqlite3
from playsound import playsound
from paho.mqtt.publish import single


def read_qr_code(image):
    try:
        detect = cv2.QRCodeDetector()
        value, points, straight_qrcode = detect.detectAndDecode(image)
        return value
    except:
        return


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Подключение к базе данных SQLite прошло успешно")
    except sqlite3.Error as e:
        print(f'Произошла ошибка {e}')
    return connection


def initial_account(account):
    current_account = (int(account), 0)
    cur.execute("INSERT or IGNORE into users VALUES (?, ?);", current_account)
    connection.commit()


def carton(account):
    global song
    cv2.putText(image, "Ваш мусор идет в урну для картона.", (125, 200), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255),
                1)
    cv2.putText(image, "Она находится по середине.", (150, 290), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)
    cur.execute("SELECT * FROM users WHERE userid = ?", (account, ))
    records = cur.fetchone()
    records = records[1] + 1
    update_account = (account, records)
    cur.execute("INSERT or REPLACE into users VALUES (?, ?);", update_account)
    connection.commit()
    single("sortingtrash/main",
           payload=f'На аккаунт {account} был зачислен 1 балл. Баланс:{records}',
           hostname='mqtt.pi40.ru',
           port=1883,
           client_id='python_qw21',
           auth={'username':'sortingtrash','password':'e122333'})
    song = "carton.wav"


def plastic(account):
    global song
    cv2.putText(image, "Ваш мусор идет в урну для пластика.", (125, 200), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                (255, 255, 255), 1)
    cv2.putText(image, "Она находится справа от Вас.", (150, 290), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255),
                1)
    cur.execute("SELECT * FROM users WHERE userid = ?", (account, ))
    records = cur.fetchone()
    records = records[1] + 2
    update_account = (account, records)
    cur.execute("INSERT or REPLACE into users VALUES (?, ?);", update_account)
    connection.commit()
    single("sortingtrash/main",
           payload=f'На аккаунт {account} было зачислено 2 балла. Баланс:{records}',
           hostname='mqtt.pi40.ru',
           port=1883,
           client_id='python_qw21',
           auth={'username':'sortingtrash','password':'e122333'})
    song = "plastic.wav"


def glass(account):
    global song
    cv2.putText(image, "Ваш мусор идет в урну для стекла.", (125, 200), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255),
                1)
    cv2.putText(image, "Она находится слева от Вас.", (150, 290), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)
    cur.execute("SELECT * FROM users WHERE userid = ?", (account, ))
    records = cur.fetchone()
    records = records[1] + 3
    update_account = (account, records)
    cur.execute("INSERT or REPLACE into users VALUES (?, ?);", update_account)
    connection.commit()
    single("sortingtrash/main",
           payload=f'На аккаунт {account} было зачислено 3 балла. Баланс:{records}',
           hostname='mqtt.pi40.ru',
           port=1883,
           client_id='python_qw21',
           auth={'username':'sortingtrash','password':'e122333'})
    song = "glass.wav"


cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
key = -1
song = ""
loginned = False
connection = create_connection('accounts.db')
cur = connection.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS users(
   userid INT PRIMARY KEY,
   points INT);""")
connection.commit()

while key == -1:
    song = ""
    isRead, image = cap.read()
    account = read_qr_code(image)
    if account is not None and account != "":
        initial_account(account)
        loginned = True
        loginned_account = account
    if loginned:
        b, g, r = image[240, 320]
        if 130 < b < 170 and 180 < g < 210 and 180 < r < 200:
            carton(loginned_account)
        if b < 40 and g < 40 and r > 150:
            plastic(loginned_account)
        if b < 60 and 50 < g < 90 and r < 40:
            glass(loginned_account)
    else:
        cv2.putText(image, "Для начала Вам нужно войти.", (170, 200), cv2.FONT_HERSHEY_COMPLEX, 0.6, (20, 20, 255), 1)
    cv2.imshow("Sorting", image)
    key = cv2.waitKey(20)
    if song != "":
        try:
            playsound(song)
        except:
            print("Ошибка проигрывания звука", end="\t")
cap.release()
cur.execute("SELECT * FROM users;")
all_results = cur.fetchall()
print(all_results)
