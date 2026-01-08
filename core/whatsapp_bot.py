import time
import urllib.parse
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

API_URL = "http://127.0.0.1:8000/api/matches/"

def start_bot():

    print("Carregando API...")
    response = requests.get(API_URL)
    data = response.json()
    matches = data.get("matches", [])

    if not matches:
        print("Nenhum match encontrado.")
        return

    print(f"Encontrados {len(matches)} matches para enviar (modo TESTE).")

    chrome_options = Options()
    chrome_options.add_argument(r"--user-data-dir=C:\Users\User\AppData\Local\Google\Chrome\User Data")

    driver = webdriver.Chrome(options=chrome_options)

    driver.get("https://web.whatsapp.com")
    input("Escaneie o QR Code e pressione ENTER aqui no terminal...")

    m = matches[0]
    phone = m["phone"]
    msg = m["message"]

    print(f"Enviando mensagem para {phone}...")

    texto = urllib.parse.quote(msg)
    link = f"https://web.whatsapp.com/send?phone={phone}&text={texto}"
    driver.get(link)

    # ESPERAR A CAIXA DE TEXTO APARECER
    try:
        print("Aguardando a caixa de mensagem aparecer...")
        caixa = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-tab='10'][contenteditable='true']"))
        )
        print("Caixa encontrada! Enviando mensagem...")
        caixa.send_keys(Keys.ENTER)

        print("Mensagem enviada com sucesso! 🎉")

    except Exception as e:
        print("❌ Erro ao enviar mensagem:", e)

    time.sleep(5)
