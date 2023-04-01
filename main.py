import cv2
import sqlite3
from playsound import playsound
from paho.mqtt.publish import single


def read_qr_code(shot):
    try:
        detect = cv2.QRCodeDetector()
        value, points, straight_qrcode = detect.detectAndDecode(shot)
        return value
    except:
        return


def create_connection(path):
    connect = None
    try:
        connect = sqlite3.connect(path)
        print("Подключение к базе данных SQLite прошло успешно")
    except sqlite3.Error as e:
        print(f'Произошла ошибка {e}')
    return connect


def initial_account(account_id):
    current_account = (int(account_id), 0)
    cursor.execute("INSERT or IGNORE into users VALUES (?, ?);", current_account)
    connection.commit()


def carton(account_id):
    global song
    cv2.putText(image, "Ваш мусор идет в урну для картона.", (125, 200), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255),
                1)
    cv2.putText(image, "Она находится по середине.", (150, 290), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)
    cursor.execute("SELECT * FROM users WHERE userid = ?", (account_id,))
    records = cursor.fetchone()
    records = records[1] + 1
    update_account = (account_id, records)
    cursor.execute("INSERT or REPLACE into users VALUES (?, ?);", update_account)
    connection.commit()
    single("sortingtrash/main",
           payload=f'На аккаунт {account_id} был зачислен 1 балл. Баланс:{records}',
           hostname='mqtt.pi40.ru',
           port=1883,
           client_id='python_qw21',
           auth={'username': 'sortingtrash', 'password': 'e122333'})
    song = "carton.wav"


def plastic(account_id):
    global song
    cv2.putText(image, "Ваш мусор идет в урну для пластика.", (125, 200), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                (255, 255, 255), 1)
    cv2.putText(image, "Она находится справа от Вас.", (150, 290), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255),
                1)
    cursor.execute("SELECT * FROM users WHERE userid = ?", (account_id,))
    records = cursor.fetchone()
    records = records[1] + 2
    update_account = (account_id, records)
    cursor.execute("INSERT or REPLACE into users VALUES (?, ?);", update_account)
    connection.commit()
    single("sortingtrash/main",
           payload=f'На аккаунт {account_id} было зачислено 2 балла. Баланс:{records}',
           hostname='mqtt.pi40.ru',
           port=1883,
           client_id='python_qw21',
           auth={'username': 'sortingtrash', 'password': 'e122333'})
    song = "plastic.wav"


def glass(account_id):
    global song
    cv2.putText(image, "Ваш мусор идет в урну для стекла.", (125, 200), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255),
                1)
    cv2.putText(image, "Она находится слева от Вас.", (150, 290), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)
    cursor.execute("SELECT * FROM users WHERE userid = ?", (account_id,))
    records = cursor.fetchone()
    records = records[1] + 3
    update_account = (account_id, records)
    cursor.execute("INSERT or REPLACE into users VALUES (?, ?);", update_account)
    connection.commit()
    single("sortingtrash/main",
           payload=f'На аккаунт {account_id} было зачислено 3 балла. Баланс:{records}',
           hostname='mqtt.pi40.ru',
           port=1883,
           client_id='python_qw21',
           auth={'username': 'sortingtrash', 'password': 'e122333'})
    song = "glass.wav"


cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
key = -1
song = ""
loginned = False
loginned_account = None
connection = create_connection('accounts.db')
cursor = connection.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users(
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
        blue, green, red = image[240, 320]
        print(blue, green, red)
        if 130 < blue < 170 and 180 < green < 210 and 180 < red < 200:
            carton(loginned_account)
        if blue < 80 and green < 80 and red > 150:
            plastic(loginned_account)
        if blue < 60 and 50 < green < 90 and red < 40:
            glass(loginned_account)
    else:
        cv2.putText(image, "Для начала Вам нужно войти.", (170, 200), cv2.FONT_HERSHEY_COMPLEX, 0.6, (20, 20, 255), 1)
    cv2.circle(image, (320, 240), 20, (255, 255, 255), 2)
    cv2.imshow("Sorting", image)
    key = cv2.waitKey(20)
    if song != "":
        try:
            playsound(song)
        except:
            print("Ошибка проигрывания звука", end="\t")
cap.release()
cursor.execute("SELECT * FROM users;")
all_results = cursor.fetchall()
print(all_results)
