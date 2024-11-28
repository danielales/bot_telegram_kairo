import telebot
from telebot import types
import pandas as pd
import re
#import google.generativeai as genai
#import os
#import openpyxl

#os.environ["API_KEY"] = "AIzaSyC5OOCqO21uth2OpNiI_HpVVpfS2J68aZc"
#genai.configure(api_key=os.environ["API_KEY"])
#model = genai.GenerativeModel('gemini-1.5-flash-latest')

# Reemplaza 'TELEGRAM_BOT_TOKEN' con tu token de Telegram
TELEGRAM_BOT_TOKEN = '7603882161:AAGFRK9-FMtyrYahYwlkYXToXlGKL9-ucAQ'
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


# Cargar datos del archivo CSV utilizando pandas
archivo = 'BA_quehacer.csv'
datos = pd.read_csv(archivo)

# Obtener categorías únicas y limpias (sin duplicados)
def obtener_categorias():
    # Eliminar texto entre paréntesis y duplicados
    categorias = datos['categoria'].dropna().apply(lambda x: re.sub(r'\s*\(.*?\)', '', x).strip()).unique()
    return sorted(categorias)

# Filtrar eventos por categoría seleccionada
def cargar_eventos_por_categoria(categoria):
    eventos = datos[datos['categoria'].str.contains(categoria, case=False, na=False)]
    return eventos[['titulo', 'lugar', 'dia', 'descripcion', 'lugar-href', 'Links-href']]

# Comando /start para mostrar las categorías únicas directamente como botones
@bot.message_handler(commands=['salir'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    categorias = obtener_categorias()
    for categoria in categorias:
        markup.add(types.KeyboardButton(categoria))
    bot.send_message(message.chat.id, "Hola! Elegí una categoría para ver los eventos que hay en BA", reply_markup=markup)

# Mostrar eventos como botones al seleccionar una categoría
@bot.message_handler(func=lambda message: message.text in obtener_categorias())
def mostrar_eventos_categoria(message):
    categoria = message.text
    eventos = cargar_eventos_por_categoria(categoria)

    if not eventos.empty:
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        for _, evento in eventos.iterrows():
            markup.add(types.KeyboardButton(evento['titulo']))
        markup.add(types.KeyboardButton("Regresar al menú principal"))
        bot.send_message(message.chat.id, f"Eventos de '{categoria}':", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "No se encontraron eventos en esta categoría.")

# Mostrar detalles de evento al seleccionar título
@bot.message_handler(func=lambda message: message.text in datos['titulo'].values)
def mostrar_detalles_evento(message):
    evento = datos[datos['titulo'] == message.text].iloc[0]
    respuesta = (f"Detalles del evento:\n\n"
                 f"Título: {evento['titulo']}\n"
                 f"Lugar: [{evento['lugar']}]({evento['lugar-href']})\n"
                 f"Día y horario: {evento['dia']}\n"
                 f"Descripción: {evento['descripcion']}\n"
                 f"Más información: [Enlace]({evento['Links-href']})")
    bot.send_message(message.chat.id, respuesta, parse_mode="Markdown")

# Regresar al menú principal
@bot.message_handler(func=lambda message: message.text == "Regresar al menú principal")
def regresar_menu_principal(message):
    send_welcome(message)

# Iniciar el bot
'''
@bot.message_handler(func=lambda message: True)
def responder_mensaje(message):
    pregunta = message.text
    respuesta = model.generate_content(pregunta)
    bot.send_message(message.chat.id, respuesta.text)
'''
#print("Bot de Telegram iniciado")
bot.polling()
