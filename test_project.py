import unittest
import time
from io import BytesIO
from unittest import TestCase
import subprocess
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import base64
import matplotlib
matplotlib.use('Agg')  # Usar backend 'Agg' para evitar errores si no hay acceso a pantalla

# Importar las clases del código principal
from project_poo import Ping, Mediciones, Graficador, BotRPA  # Ajusta la importación según tu código

class TestPing(TestCase):

    def test_ping_success(self):
        ping = Ping()
        latency, error = ping.ejecutar('8.8.8.8')  # Dirección IP de Google DNS
        self.assertIsNotNone(latency)  # Asegurarse de que obtuviste una latencia
        self.assertIsNone(error)  # No debe haber error


class TestMediciones(TestCase):

    def test_ejecutar_mediciones(self):
        mediciones = Mediciones()
        mediciones.realizar_mediciones('8.8.8.8', 3)  # Realizamos 3 mediciones
        self.assertGreater(len(mediciones.latencias), 0)  # Comprobar que se hicieron mediciones

    def test_analizar_datos(self):
        mediciones = Mediciones()
        mediciones.realizar_mediciones('8.8.8.8', 3)  # Realizamos 3 mediciones
        anomalías_modelo, anomalías_umbral = mediciones.analizar_datos()
        self.assertGreater(len(anomalías_modelo), 0)  # Comprobar que se detectaron anomalías con el modelo

    def test_generar_csv_data(self):
        mediciones = Mediciones()
        mediciones.realizar_mediciones('8.8.8.8', 3)  # Realizamos 3 mediciones
        data = mediciones.generar_csv_data()
        self.assertGreater(len(data), 0)  # Asegurarse de que el CSV tenga datos


class TestGraficador(TestCase):

    def test_graficar_latencias(self):
        graficador = Graficador()
        latencias = [0.1, 0.2, 0.3]
        img = graficador.graficar_latencias(latencias)
        self.assertIsNotNone(img)  # Asegurarse de que no sea None

    def test_graficar_ancho_banda(self):
        graficador = Graficador()
        ancho_banda = [10, 5, 3]
        img = graficador.graficar_ancho_banda(ancho_banda)
        self.assertIsNotNone(img)  # Asegurarse de que no sea None


class TestBotRPA(TestCase):

    def test_ejecutar_mediciones(self):
        bot = BotRPA()
        bot.ejecutar_mediciones('8.8.8.8', 3)
        self.assertTrue(bot.mediciones_completadas)  # Asegurarse de que las mediciones se completaron

    def test_graficar_latencias(self):
        bot = BotRPA()
        bot.ejecutar_mediciones('8.8.8.8', 3)
        latencias_img = bot.graficar_latencias()
        self.assertIsNotNone(latencias_img)  # Asegurarse de que no sea None

    def test_graficar_ancho_banda(self):
        bot = BotRPA()
        bot.ejecutar_mediciones('8.8.8.8', 3)
        ancho_banda_img = bot.graficar_ancho_banda()
        self.assertIsNotNone(ancho_banda_img)  # Asegurarse de que no sea None

    def test_generar_csv_data(self):
        bot = BotRPA()
        bot.ejecutar_mediciones('8.8.8.8', 3)
        data = bot.generar_csv_data()
        self.assertGreater(len(data), 0)  # Asegurarse de que se generen datos en el CSV

    def test_explicar_anomalias_con_ia(self):
        bot = BotRPA()
        bot.ejecutar_mediciones('8.8.8.8', 3)
        mensaje = bot.explicar_anomalias_con_ia()
        self.assertIsNotNone(mensaje)  # Asegurarse de que se obtiene una respuesta


if __name__ == '__main__':
    unittest.main()
