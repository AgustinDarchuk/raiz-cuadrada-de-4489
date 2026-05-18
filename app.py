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
    
@app.route('/simulacion', methods=['GET', 'POST'])
def simulacion():
    if request.method == 'POST':
        # 1. Captura de datos
        riders = max(0,int(request.form.get('riders', 10)))
        pedidos = max(0,int(request.form.get('pedidos', 100)))
        ticket = max(0.0,float(request.form.get('ticket_promedio', 1000)))
        factor = request.form.get('factor_critico', 'High_Traffic')

        # 2. Límites de capacidad física por repartidor al día
        CAPACIDAD_SIN_JAGUAR = 6   # Pedidos máximos que hace un rider al día sin optimizar
        CAPACIDAD_CON_JAGUAR = 10  # Pedidos máximos que hace un rider gracias a Jaguar

        max_pedidos_sin = riders * CAPACIDAD_SIN_JAGUAR
        max_pedidos_con = riders * CAPACIDAD_CON_JAGUAR

        # ¿Hay escasez de repartidores para cubrir la demanda actual?
        escasez_sin = pedidos > max_pedidos_sin
        pedidos_perdidos_diarios = max(0, pedidos - max_pedidos_sin)

        # Penalización por clima/tráfico (sigue aplicando a los pedidos que SÍ se pueden procesar)
        penalty = 0.22 if factor == 'High_Traffic' else 0.28
        
        # 3. Simulación a 30 días con fluctuación y topes de capacidad
        random.seed(42)
        acum_sin = []
        acum_con = []
        total_sin = 0
        total_con = 0
        days = list(range(1, 31))

        for day in days:
            # Los pedidos del mercado fluctúan +/- 15% día a día
            fluctuacion = random.uniform(0.85, 1.15)
            pedidos_del_dia = pedidos * fluctuacion
            
            # El tope de la flota limita cuántos pedidos se pueden procesar en el día realmente
            pedidos_reales_sin = min(pedidos_del_dia, max_pedidos_sin)
            pedidos_reales_con = min(pedidos_del_dia, max_pedidos_con)
            
            # Cálculo de facturación diaria aplicando la ineficiencia
            dia_sin = (pedidos_reales_sin * ticket * (1 - penalty))
            dia_con = (pedidos_reales_con * ticket)
            
            total_sin += dia_sin
            total_con += dia_con
            
            acum_sin.append(total_sin)
            acum_con.append(total_con)

        # Cálculo de métricas finales para la pantalla
        extra_mensual = total_con - total_sin
        # La eficiencia total combina la velocidad y la capacidad de absorber pedidos retenidos
        eficiencia_aumento = int(((total_con - total_sin) / max(1, total_sin)) * 100)

        # 4. Gráfico Matplotlib
        plt.figure(figsize=(10, 5))
        ax = plt.gca()

        plt.plot(days, acum_con, label='Con Jaguar Home (Optimizado)', color='#FFBD00', linewidth=3)
        plt.plot(days, acum_sin, label='Escenario Actual (Inadecuado)', color='#bdc3c7', linewidth=2, linestyle='--')
        plt.fill_between(days, acum_sin, acum_con, color='#FFBD00', alpha=0.1)
        
        plt.title("Proyección de Ingresos Netos Acumulados (30 días)", fontsize=13, fontweight='bold', pad=15)
        plt.xlabel("Días del Mes", fontsize=10)
        plt.ylabel("Facturación ($)", fontsize=10)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.grid(True, linestyle=':', alpha=0.5)
        plt.legend(frameon=False, loc='upper left', fontsize=10)
        ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))

        target_dir = "static/plots"
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        plt.savefig(os.path.join(target_dir, "prediccion_ingresos.png"))
        plt.close()

        extra_mensual_formateado = f"${extra_mensual:,.0f}".replace(",", ".")

        return render_template('simulacion.html', 
                               resultado=True, 
                               extra_mensual=extra_mensual_formateado, 
                               eficiencia=eficiencia_aumento,
                               riders=riders, pedidos=pedidos, ticket=ticket, factor=factor,
                               escasez=escasez_sin, perdidos=int(pedidos_perdidos_diarios))
    
    return render_template('simulacion.html', resultado=False)
    
    
#
@app.route('/generar-leads-ficticios')
def generar_leads():
    nombres = ["Carlos", "Martina", "Lucas", "Sofia", "Juan", "Valentina", "Mateo", "Camila", "Diego", "Elena"]
    apellidos = ["Gomez", "Rodriguez", "Fernandez", "Lopez", "Diaz", "Perez", "Romero", "Alvarez", "Torres", "Ruiz"]
    sectores = ["Gastronomía", "Retail / E-commerce", "Otros"]
    dominios = ["gmail.com", "outlook.com", "empresa.com", "delivery.co"]

    
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
    
    plt.figure(figsize=(10, 6))
    ax = plt.gca()

    colores = ['#2c3e50', '#e67e22', '#bdc3c7'] 

    pivot_data.plot(kind='bar', ax=ax, color=colores, width=0.8, edgecolor='white', linewidth=1)

    
    plt.title("Tiempos de Entrega por Distancia", fontsize=14, fontweight='bold', pad=20)
    plt.ylabel("Minutos (Promedio)", fontsize=10)
    plt.xlabel("") 
    

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    

    plt.legend(title="", frameon=False, loc='upper left', ncol=3)

    
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f', padding=3, fontsize=9)

    plt.tight_layout()

    
    if not os.path.exists("static/plots"):
        os.makedirs("static/plots")
    plt.savefig("static/plots/graph.png")
    plt.close()
    
    return "Gráfico simple generado"

def generate_weather_impact_chart():
    data = pd.read_csv("data/Food_Delivery_Times.csv")
    
    
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

    
    if not os.path.exists("static/plots"):
        os.makedirs("static/plots")
        
    plt.savefig("static/plots/impacto_clima.png")
    plt.close()
    
    return "Gráfico de clima generado"
    
def generate_traffic_impact_chart():

    ruta_csv = "data/Food_Delivery_Times.csv"
    if not os.path.exists(ruta_csv):
        print(f"Error: No se encontró el archivo en {ruta_csv}")
        return

    data = pd.read_csv(ruta_csv)
    
    
    traduccion_trafico = {
        'Low': 'Bajo', 
        'Medium': 'Medio', 
        'High': 'Alto'
    }
    data['Tráfico'] = data['Traffic_Level'].map(traduccion_trafico)
    
    
    trafico_stats = data.groupby('Tráfico')['Delivery_Time_min'].mean()
    
    
    orden = ['Bajo', 'Medio', 'Alto']
    trafico_stats = trafico_stats.reindex(orden)

    
    plt.figure(figsize=(8, 6))
    ax = plt.gca()
    
    
    colores = ['#bdc3c7', '#bdc3c7', '#FFBD00'] 
    
    trafico_stats.plot(kind='bar', ax=ax, color=colores, width=0.6, edgecolor='white')
    
    plt.title("Impacto del Tráfico en Tiempos de Entrega", fontsize=14, fontweight='bold', pad=20)
    plt.ylabel("Minutos (Promedio)", fontsize=10)
    plt.xlabel("") 
    
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.xticks(rotation=0, fontsize=11, fontweight='bold')
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    
    
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f', padding=5, fontweight='bold', fontsize=10)

    plt.tight_layout()

    
    target_dir = "static/plots"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    plt.savefig(os.path.join(target_dir, "impacto_trafico.png"))
    plt.close()
    print("Gráfico 'impacto_trafico.png' guardado con éxito.")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

            # ALTERNATIVA 2: RED DE SEGURIDAD AUTOMÁTICA (SI ESTÁ VACÍA AL ARRANCAR)
        if Contacto.query.count() == 0:
            nombres = ["Carlos", "Martina", "Lucas", "Sofia", "Juan", "Valentina", "Mateo", "Camila", "Diego", "Elena"]
            apellidos = ["Gomez", "Rodriguez", "Fernandez", "Lopez", "Diaz", "Perez", "Romero", "Alvarez", "Torres", "Ruiz"]
            sectores = ["Gastronomía", "Retail / E-commerce", "Otros"]
            dominios = ["gmail.com", "outlook.com", "empresa.com", "delivery.co"]

            for _ in range(40):
                nom = random.choice(nombres)
                ape = random.choice(apellidos)
                nombre_completo = f"{nom} {ape}"
                email = f"{nom.lower()}.{ape.lower()}@{random.choice(dominios)}"
                sector = random.choice(sectores)

                nuevo_lead = Contacto(nombre=nombre_completo, email=email, sector=sector)
                db.session.add(nuevo_lead)
                
            db.session.commit()
            print(">> [Seguridad] Base de datos vacía detectada: Se autogeneraron las 40 filas iniciales <<")

    generate_simple_pro_chart()
    generate_weather_impact_chart()
    generate_traffic_impact_chart()
    app.run(debug=True, port=5001)