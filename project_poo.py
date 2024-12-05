import matplotlib
matplotlib.use('Agg')  # Usar backend 'Agg' para evitar errores
import time
import subprocess
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from flask import Flask, render_template, jsonify
import openai

# Configurar API key de OpenAI
openai.api_key = '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'

# Clase Ping: realiza pings y devuelve latencias
class Ping:
    @staticmethod
    def ejecutar(host):
        try:
            start_time = time.time()
            subprocess.run(['ping', '-n', '1', host], capture_output=True, text=True, check=True)
            latency = time.time() - start_time
            return latency, None
        except subprocess.CalledProcessError as e:
            print(f"Error en el ping a {host}: {e}")
            return None, None

# Clase Mediciones: administra mediciones y análisis
class Mediciones:
    def __init__(self):
        self.latencias = []
        self.anomalias_modelo = []
        self.anomalias_umbral = []

    def realizar_mediciones(self, host, num_mediciones):
        self.latencias = []
        for _ in range(num_mediciones):
            latency, _ = Ping.ejecutar(host)
            if latency is not None:
                self.latencias.append(latency)
            time.sleep(0.5)

    def analizar_datos(self):
        if len(self.latencias) < 2:
            return [], []
        model = IsolationForest(contamination=0.1)
        preds = model.fit_predict(np.array(self.latencias).reshape(-1, 1))

        # Detectar anomalías por umbral y modelo
        self.anomalias_umbral = [d for d in self.latencias if d > 0.2]
        self.anomalias_modelo = [d for i, d in enumerate(self.latencias) if preds[i] == -1]
        return self.anomalias_modelo, self.anomalias_umbral

    def calcular_ancho_banda(self):
        return [1 / lat if lat > 0 else None for lat in self.latencias]

    def generar_csv_data(self):
        if not self.latencias:
            return []
        
        ancho_banda = self.calcular_ancho_banda()
        anomalias_combinadas = set(self.anomalias_modelo + self.anomalias_umbral)
        anomalía_latencia = ["Sí" if lat in anomalias_combinadas else "No" for lat in self.latencias]

        df = pd.DataFrame({
            "Medición": list(range(1, len(self.latencias) + 1)),
            "Latencia (s)": self.latencias,
            "Ancho de Banda (bps)": ancho_banda,
            "Anomalía Latencia": anomalía_latencia
        })
        return df.to_dict(orient="records")

# Clase Graficador: genera gráficos a partir de los datos
class Graficador:
    @staticmethod
    def graficar_latencias(latencias):
        if not latencias:
            return None
        plt.figure(figsize=(12, 5))
        x_values = range(1, len(latencias) + 1)
        plt.plot(x_values, latencias, label="Latencias", marker='o', color='orange')
        plt.title("Medición de Latencias")
        plt.xlabel("Número de Medición")
        plt.ylabel("Tiempo (s)")
        plt.legend()
        plt.grid()

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        plt.close()
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    @staticmethod
    def graficar_ancho_banda(ancho_banda):
        if not ancho_banda:
            return None
        plt.figure(figsize=(12, 5))
        x_values = range(1, len(ancho_banda) + 1)
        plt.plot(x_values, ancho_banda, label="Ancho de Banda", marker='x', color='teal')
        plt.title("Medición de Ancho de Banda")
        plt.xlabel("Número de Medición")
        plt.ylabel("Ancho de Banda (bps)")
        plt.legend()
        plt.grid()

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        plt.close()
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

# Clase BotRPA: coordina todo el flujo
class BotRPA:
    def __init__(self):
        self.mediciones = Mediciones()
        self.mediciones_completadas = False

    def ejecutar_mediciones(self, host, num_mediciones):
        self.mediciones.realizar_mediciones(host, num_mediciones)
        self.mediciones.analizar_datos()
        self.mediciones_completadas = True

    def graficar_latencias(self):
        return Graficador.graficar_latencias(self.mediciones.latencias)

    def graficar_ancho_banda(self):
        return Graficador.graficar_ancho_banda(self.mediciones.calcular_ancho_banda())

    def generar_csv_data(self):
        return self.mediciones.generar_csv_data()

    def explicar_anomalias_con_ia(self):
        anomalías_modelo, anomalías_umbral = self.mediciones.analizar_datos()
        prompt = f"""
        Explícame cómo afectan al rendimiento de la red las siguientes anomalías en la latencia:
        1. Detectadas por Isolation Forest: {anomalías_modelo}.
        2. Detectadas por umbral (>0.2s): {anomalías_umbral}.
        ¿Qué medidas podrían tomarse?
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un asistente experto en rendimiento de redes."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            return str(e)

# Flask App
app = Flask(__name__)
bot = BotRPA()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/iniciar_mediciones')
def iniciar_mediciones():
    bot.ejecutar_mediciones('8.8.8.8', 15)
    return jsonify({"status": "Mediciones iniciadas"})

@app.route('/obtener_resultados')
def obtener_resultados():
    if bot.mediciones_completadas:
        latencias_img = bot.graficar_latencias()
        ancho_banda_img = bot.graficar_ancho_banda()
        csv_data = bot.generar_csv_data()
        return jsonify({
            "completadas": True,
            "latencias_img": latencias_img,
            "ancho_banda_img": ancho_banda_img,
            "csv_data": csv_data
        })
    return jsonify({"completadas": False})

@app.route('/explicar_anomalias')
def explicar_anomalias():
    mensaje = bot.explicar_anomalias_con_ia()
    return jsonify({"mensaje": mensaje})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
