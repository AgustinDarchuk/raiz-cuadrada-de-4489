from flask import Flask, render_template, request,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import matplotlib #crear los graficos
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas 
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    content = db.Column(db.String(200),nullable=False)
    completed = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.now())

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
    
    
@app.route('/contactanos', methods=['GET','POST'])
def contactanos():
    if request.method == 'POST':
        task_content= request.form.get('content')
        new_todo = Todo(content=task_content)
        db.session.add(new_todo)
        db.session.commit()
        return redirect("/contactanos")
    else:
        tasks = Todo.query.all()
        return render_template("contactanos.html", tasks=tasks)
    
    
def generate_simple_pro_chart():
    # 1. Carga y preparación (igual que antes)
    data = pandas.read_csv("data/Food_Delivery_Times.csv")
    vehicles = ["Car", "Scooter", "Bike"]
    data = data[data["Vehicle_Type"].isin(vehicles)]
    
    bins = [0, 3, 7, 20]
    labels = ['Corta (0-3km)', 'Media (3-7km)', 'Larga (+7km)']
    data['Distancia_Cat'] = pandas.cut(data['Distance_km'], bins=bins, labels=labels)
    
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

def generate_bottleneck_chart():
    # 1. Carga de datos
    data = pandas.read_csv("data/Food_Delivery_Times.csv")
    
    # 2. Preparación de datos y mapeo al español
    # Los CSV suelen tener estos valores en inglés. Los pasamos a español para el gráfico.
    mapeo_turnos = {
        'Morning': 'Mañana',
        'Afternoon': 'Tarde',
        'Evening': 'Noche',
        'Night': 'Madrugada'
    }
    data['Turno'] = data['Time_of_Day'].map(mapeo_turnos).fillna(data['Time_of_Day'])
    
    # Agrupamos por turno y calculamos el promedio de ambos tiempos
    pivot_data = data.groupby('Turno')[['Preparation_Time_min', 'Delivery_Time_min']].mean()
    
    # Reordenamos para que tenga sentido cronológico
    orden_turnos = ['Mañana', 'Tarde', 'Noche', 'Madrugada']
    turnos_existentes = [t for t in orden_turnos if t in pivot_data.index]
    pivot_data = pivot_data.reindex(turnos_existentes)
    
    # Renombramos las columnas para que la leyenda quede perfecta
    pivot_data = pivot_data.rename(columns={
        'Preparation_Time_min': 'Preparación (Restaurante)',
        'Delivery_Time_min': 'Viaje (Repartidor)'
    })
    
    # 3. Gráfico Estilo Minimalista (Apilado)
    plt.figure(figsize=(10, 6))
    ax = plt.gca()

    # Colores: Naranja Jaguar para el restaurante, Azul Marino para el repartidor
    colores = ['#FFBD00', '#2c3e50'] 

    # stacked=True es la magia que apila las barras
    pivot_data.plot(kind='bar', stacked=True, ax=ax, color=colores, width=0.6, edgecolor='white', linewidth=1)

    # 4. Limpieza Total
    plt.title("Cuello de Botella: Restaurante vs. Repartidor", fontsize=14, fontweight='bold', pad=20)
    plt.ylabel("Minutos (Promedio)", fontsize=10)
    plt.xlabel("") # Eje X limpio
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    
    # Leyenda arriba, sin recuadro
    plt.legend(title="", frameon=False, loc='upper left', ncol=2)

    # 5. Etiquetas de datos dentro de los bloques
    for container in ax.containers:
        # label_type='center' ubica el número justo en el medio de cada color
        ax.bar_label(container, fmt='%.1f', label_type='center', color='white', fontweight='bold', fontsize=10)

    plt.tight_layout()

    # 6. Guardado
    if not os.path.exists("static/plots"):
        os.makedirs("static/plots")
    
    # Lo guardamos con un nombre nuevo para que puedas tener ambos gráficos si querés
    plt.savefig("static/plots/cuello_botella.png") 
    plt.close()
    
    return "Gráfico de Cuello de Botella generado"
    
if __name__ == '__main__':
    generate_simple_pro_chart()
    generate_bottleneck_chart()
    app.run(debug=True, port=5001)