from flask import Flask, render_template, request, redirect , url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import matplotlib #crear los graficos
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import os
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

#MODELOS DE LA BASE DE DATOS
class Todo(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    content = db.Column(db.String(200),nullable=False)
    completed = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.now())
#modifica Jhon tabla modelo
class Contacto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    sector = db.Column(db.String(50), nullable=False)
#modifica Jhon fin tabla modelo

#RUTAS DE LA APLICACION
@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        task_content= request.form.get('content')
        new_todo = Todo(content=task_content)
        db.session.add(new_todo)
        db.session.commit()
        return redirect("/")
    else:
        tasks = Todo.query.all()
        return render_template("index.html", tasks=tasks)
    
@app.route('/analisis', methods=['GET','POST'])
def analisis():
    if request.method == 'POST':
        task_content= request.form.get('content')
        new_todo = Todo(content=task_content)
        db.session.add(new_todo)
        db.session.commit()
        return redirect("/analisis")
    else:
        tasks = Todo.query.all()
        return render_template("analisis.html", tasks=tasks)
    
@app.route('/simulacion', methods=['GET','POST'])
def simulacion():
    if request.method == 'POST':
        task_content= request.form.get('content')
        new_todo = Todo(content=task_content)
        db.session.add(new_todo)
        db.session.commit()
        return redirect("/simulacion")
    else:
        tasks = Todo.query.all()
        return render_template("simulacion.html", tasks=tasks)
    
    
#
@app.route('/generar-leads-ficticios')
def generar_leads():
    nombres = ["Carlos", "Martina", "Lucas", "Sofia", "Juan", "Valentina", "Mateo", "Camila", "Diego", "Elena"]
    apellidos = ["Gomez", "Rodriguez", "Fernandez", "Lopez", "Diaz", "Perez", "Romero", "Alvarez", "Torres", "Ruiz"]
    sectores = ["Gastronomía", "Retail / E-commerce", "Otros"]
    dominios = ["gmail.com", "outlook.com", "empresa.com", "delivery.co"]

    # Limpia datos previos para no acumular infinitamente al recargar
    Contacto.query.delete()

    for _ in range(40):
        nom = random.choice(nombres)
        ape = random.choice(apellidos)
        nombre_completo = f"{nom} {ape}"
        email = f"{nom.lower()}.{ape.lower()}@{random.choice(dominios)}"
        sector = random.choice(sectores)

        nuevo_lead = Contacto(nombre=nombre_completo, email=email, sector=sector)
        db.session.add(nuevo_lead)
        
    db.session.commit()
    return "¡Se han generado 40 formularios de contacto ficticios en la base de datos!"
#
@app.route('/contactanos', methods=['GET','POST'])
def contactanos():
    mensajes = Contacto.query.all()
    
    total_solicitudes = len(mensajes)
    sector_lider = "Ninguno"
    porcentaje_gastronomia = 0

    if total_solicitudes > 0:
        # Procesamos las métricas comerciales usando Pandas
        data = [{'sector': m.sector} for m in mensajes]
        df = pd.DataFrame(data)
        
        conteo_sectores = df['sector'].value_counts()
        sector_lider = conteo_sectores.idxmax()
        
        if "Gastronomía" in conteo_sectores:
            total_gastro = conteo_sectores["Gastronomía"]
            porcentaje_gastronomia = round((total_gastro / total_solicitudes) * 100, 1)

    stats_comerciales = {
        'total': total_solicitudes,
        'lider': sector_lider,
        'pct_gastro': porcentaje_gastronomia
    }

    return render_template("contactanos.html", mensajes=mensajes, stats_biz=stats_comerciales)
    '''
    if request.method == 'POST':
        task_content= request.form.get('content')
        new_todo = Todo(content=task_content)
        db.session.add(new_todo)
        db.session.commit()
        return redirect("/contactanos")
    else:
        tasks = Todo.query.all()
        return render_template("contactanos.html", tasks=tasks)
    '''
@app.route('/enviar', methods=['POST'])
def enviar():
    nombre_user = request.form.get('nombre')
    email_user = request.form.get('email')
    sector_user = request.form.get('sector')
    
    if nombre_user and email_user:
        nuevo_contacto = Contacto(nombre=nombre_user, email=email_user, sector=sector_user)
        db.session.add(nuevo_contacto)
        db.session.commit()
        
    return redirect(url_for('contactanos'))

def generate_simple_pro_chart():
    # 1. Carga y preparación (igual que antes)
    data = pd.read_csv("data/Food_Delivery_Times.csv")
    vehicles = ["Car", "Scooter", "Bike"]
    data = data[data["Vehicle_Type"].isin(vehicles)]
    
    bins = [0, 3, 7, 20]
    labels = ['Corta (0-3km)', 'Media (3-7km)', 'Larga (+7km)']
    data['Distancia_Cat'] = pd.cut(data['Distance_km'], bins=bins, labels=labels)
    
    pivot_data = data.pivot_table(index='Distancia_Cat', columns='Vehicle_Type', values='Delivery_Time_min', aggfunc='mean')
    
    pivot_data = pivot_data.rename(columns={
        'Car': 'Auto',
        'Scooter': 'Moto',
        'Bike': 'Bicicleta'
    })
    
    # 2. Gráfico Estilo Minimalista
    plt.figure(figsize=(10, 6))
    ax = plt.gca()

    # Colores sólidos y modernos
    # Azul Marino (Car), Naranja (Scooter), Gris (Bike)
    colores = ['#2c3e50', '#e67e22', '#bdc3c7'] 

    pivot_data.plot(kind='bar', ax=ax, color=colores, width=0.8, edgecolor='white', linewidth=1)

    # 3. Limpieza Total
    plt.title("Tiempos de Entrega por Distancia", fontsize=14, fontweight='bold', pad=20)
    plt.ylabel("Minutos (Promedio)", fontsize=10)
    plt.xlabel("") # Quitamos el título del eje X para que sea más limpio
    
    # Quitar bordes innecesarios
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    
    # Leyenda simple arriba
    plt.legend(title="", frameon=False, loc='upper left', ncol=3)

    # Etiquetas de datos simples sobre las barras
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f', padding=3, fontsize=9)

    plt.tight_layout()

    # 4. Guardado
    if not os.path.exists("static/plots"):
        os.makedirs("static/plots")
    plt.savefig("static/plots/graph.png")
    plt.close()
    
    return "Gráfico simple generado"

def generate_weather_impact_chart():
    data = pd.read_csv("data/Food_Delivery_Times.csv")
    
    # Mapeo a español
    traduccion_clima = {
        'Clear': 'Despejado', 'Rainy': 'Lluvia', 'Snowy': 'Nieve', 
        'Foggy': 'Niebla', 'Windy': 'Viento'
    }
    data['Clima'] = data['Weather'].map(traduccion_clima)
    
    clima_stats = data.groupby('Clima')['Delivery_Time_min'].mean().sort_values()

    plt.figure(figsize=(10, 6))
    colores = ['#bdc3c7', '#bdc3c7', '#bdc3c7', '#bdc3c7', '#e67e22'] 
    
    clima_stats.plot(kind='barh', color=colores, width=0.7)
    
    plt.title("Impacto del Clima en el Tiempo de Entrega", fontsize=14, fontweight='bold')
    plt.xlabel("Minutos Promedio")
    plt.ylabel("")
    plt.grid(axis='x', linestyle='--', alpha=0.3)
    
    for i, v in enumerate(clima_stats):
        plt.text(v + 1, i, f"{v:.1f} min", va='center', fontweight='bold')

    plt.tight_layout()

    # --- LO QUE FALTABA ---
    if not os.path.exists("static/plots"):
        os.makedirs("static/plots")
        
    plt.savefig("static/plots/impacto_clima.png")
    plt.close()
    
    return "Gráfico de clima generado"
    
def generate_traffic_impact_chart():
    # 1. Verificación de ruta segura
    ruta_csv = "data/Food_Delivery_Times.csv"
    if not os.path.exists(ruta_csv):
        print(f"Error: No se encontró el archivo en {ruta_csv}")
        return

    data = pd.read_csv(ruta_csv)
    
    # 2. Mapeo a español
    traduccion_trafico = {
        'Low': 'Bajo', 
        'Medium': 'Medio', 
        'High': 'Alto'
    }
    data['Tráfico'] = data['Traffic_Level'].map(traduccion_trafico)
    
    # 3. Agrupar y calcular promedio
    trafico_stats = data.groupby('Tráfico')['Delivery_Time_min'].mean()
    
    # Ordenar lógicamente de menor a mayor tráfico
    orden = ['Bajo', 'Medio', 'Alto']
    trafico_stats = trafico_stats.reindex(orden)

    # 4. Configuración del gráfico
    plt.figure(figsize=(8, 6))
    ax = plt.gca()
    
    # Colores: Gris para Bajo/Medio, Naranja Jaguar para el crítico (Alto)
    colores = ['#bdc3c7', '#bdc3c7', '#FFBD00'] 
    
    trafico_stats.plot(kind='bar', ax=ax, color=colores, width=0.6, edgecolor='white')
    
    plt.title("Impacto del Tráfico en Tiempos de Entrega", fontsize=14, fontweight='bold', pad=20)
    plt.ylabel("Minutos (Promedio)", fontsize=10)
    plt.xlabel("") # Eje X limpio
    
    # 5. Limpieza visual
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.xticks(rotation=0, fontsize=11, fontweight='bold')
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    
    # Etiquetas de datos sobre las barras
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f', padding=5, fontweight='bold', fontsize=10)

    plt.tight_layout()

    # 6. Guardado seguro
    target_dir = "static/plots"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    plt.savefig(os.path.join(target_dir, "impacto_trafico.png"))
    plt.close()
    print("Gráfico 'impacto_trafico.png' guardado con éxito.")

if __name__ == '__main__':
    #crea la base de datos y las tablas
    with app.app_context():
        db.create_all()
    #despues genera los graficos
    generate_simple_pro_chart()
    generate_weather_impact_chart()
    generate_traffic_impact_chart()
    #enciende el sercidor local
    app.run(debug=True, port=5001)