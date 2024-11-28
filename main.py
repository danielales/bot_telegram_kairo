from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import telebot
from telebot import types

#bardo, dani mete mano
import google.generativeai as genai
import os
os.environ["API_KEY"] = "AIzaSyC5OOCqO21uth2OpNiI_HpVVpfS2J68aZc"
genai.configure(api_key=os.environ["API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash-latest')

#bardo out

# Token del bot de Telegram
TOKEN = "7527210724:AAFc0kxGluOo_wezme4-rA_i6JYVwAIEYNc"
bot = telebot.TeleBot(TOKEN)

# Configuración de opciones de Chrome para Selenium
options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--headless')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-setuid-sandbox')
options.add_argument('start-maximized')
options.add_argument('disable-infobars')
options.add_argument('--disable-extensions')
options.add_argument('--disable-gpu')

# URL de la página de eventos
url ="https://turismo.buenosaires.gob.ar/es/article/que-hacer-esta-semana"

# Función para extraer eventos de la página
def obtener_eventos():
    # Inicializar el driver de Chrome con las opciones
    driver = webdriver.Chrome(options=options)
    driver.get(url)  # Ingreso a la web
    print("Página cargada:", driver.title)  # Verifico que haya ingresado

    # Obtener el contenido de la página y analizar con BeautifulSoup
    content = driver.page_source
    soup = BeautifulSoup(content, "html.parser")
    driver.quit()

    # Extraer información de los eventos
    eventos = []
    for elemento in soup.find_all('div', class_='card-landing'):
        # Extraer categoría, título, día y horario, lugar, link de lugar, descripción y link de evento
        categoria = elemento.find('h4', class_='media-heading')
        titulo = elemento.find('div', class_='card-title-landing')
        diayhorario = elemento.find_all('div', class_='card-icons-landing')[0] if elemento.find_all('div', class_='card-icons-landing') else None
        lugar = elemento.find_all('div', class_='card-icons-landing')[1] if elemento.find_all('div', class_='card-icons-landing') else None
        link_lugar = lugar.find('a', class_='landing-url-map') if lugar else None



        'version original'
        #descripcion_container = elemento.find('div', class_='card-info-landing')

        #descripcion = descripcion_container.find('p') if descripcion_container else None 

        'version erronea'
        #descripcion = elemento.find('p') if elemento.find_all('p') else None 

        'version original lista para modificar'
        descripcion_container = elemento.find('div', class_='card-info-landing')

        descripcion = descripcion_container.find('p') if descripcion_container else None 



        link_evento = elemento.find('a', class_='QHS2024')

        # Almacenar evento en un diccionario
        eventos.append({
            'categoria': categoria.get_text(strip=True) if categoria else "Sin categoría",
            'titulo': titulo.get_text(strip=True) if titulo else "Sin título",
            'dia': diayhorario.get_text(strip=True) if diayhorario else "Sin día y horario",
            'lugar': lugar.get_text(strip=True) if lugar else "Sin lugar",
            'lugar-href': link_lugar['href'] if link_lugar else "Sin link al lugar",
            'descripcion': descripcion.get_text(strip=True) if descripcion else "Sin descripción",
            'Links-href': link_evento['href'] if link_evento else "Sin link de evento"
        })
    return eventos

# Obtener los eventos (reemplazo del archivo Excel)
eventos = obtener_eventos()

# Función para obtener las categorías únicas
def obtener_categorias():
    categorias = {evento['categoria'] for evento in eventos}
    return sorted(categorias)

# Filtrar eventos por categoría
def cargar_eventos_por_categoria(categoria):
    return [evento for evento in eventos if evento['categoria'].lower() == categoria.lower()]

# Comando /start para mostrar las categorías directamente
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    categorias = obtener_categorias()
    for categoria in categorias:
        markup.add(types.KeyboardButton(categoria))
    bot.send_message(message.chat.id, "¡Bienvenido! Selecciona una categoría para ver los eventos disponibles:", reply_markup=markup)

# Mostrar eventos como botones al seleccionar una categoría
@bot.message_handler(func=lambda message: message.text in obtener_categorias())
def mostrar_eventos_categoria(message):
    categoria = message.text
    eventos_categoria = cargar_eventos_por_categoria(categoria)

    if eventos_categoria:
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        for evento in eventos_categoria:
            markup.add(types.KeyboardButton(evento['titulo']))
        markup.add(types.KeyboardButton("Regresar al menú principal"))
        bot.send_message(message.chat.id, f"Eventos en la categoría '{categoria}':", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "No se encontraron eventos en esta categoría.")

# Mostrar detalles de evento al seleccionar título
@bot.message_handler(func=lambda message: any(evento['titulo'] == message.text for evento in eventos))
def mostrar_detalles_evento(message):
    evento = next((evento for evento in eventos if evento['titulo'] == message.text), None)
    if evento:
        respuesta = (f"Detalles del evento:\n\n"
                     f"Título: {evento['titulo']}\n"
                     f"Lugar: [{evento['lugar']}]({evento['lugar-href']})\n"
                     f"Día: {evento['dia']}\n"
                     f"Descripción: {evento['descripcion']}\n"
                     f"Más información: [Enlace]({evento['Links-href']})")
        bot.send_message(message.chat.id, respuesta, parse_mode="Markdown")

# Regresar al menú principal
@bot.message_handler(func=lambda message: message.text == "Regresar al menú principal")
def regresar_menu_principal(message):
    send_welcome(message)

#dani
@bot.message_handler(func=lambda message: True)
def responder_mensaje(message):
    pregunta = message.text
    respuesta = model.generate_content(pregunta)
    bot.send_message(message.chat.id, respuesta.text)
#dani2 fin quilombo

# Iniciar el bot
bot.polling()
