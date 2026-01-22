"""
Test completo del flujo de guardado de proyecto
CON FILE DIALOG para credenciales
"""

import sys
import os
from tkinter import Tk, simpledialog, filedialog, messagebox

print("=" * 70)
print("TEST DE GUARDADO DE PROYECTO")
print("=" * 70)
print()

# ===== SELECCIONAR CREDENCIALES =====
def select_credentials():
    """Seleccionar archivo de credenciales con file dialog"""
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    print("🔑 Selecciona el archivo de credenciales de Firebase...")
    
    file_path = filedialog.askopenfilename(
        title="Seleccionar credenciales Firebase",
        filetypes=[
            ("JSON files", "*.json"),
            ("All files", "*.*")
        ],
        initialdir=os.path.expanduser("~")
    )
    
    root.destroy()
    
    if not file_path:
        print("❌ No se seleccionó ningún archivo")
        return None
    
    if not os.path.exists(file_path):
        print(f"❌ El archivo no existe: {file_path}")
        return None
    
    print(f"✅ Credenciales seleccionadas: {file_path}")
    return file_path


# Seleccionar credenciales
cred_path = select_credentials()

if not cred_path: 
    print("\n❌ No se seleccionaron credenciales.  Saliendo...")
    input("\nPresiona ENTER para salir...")
    sys.exit(1)

print()

# ===== AJUSTAR PATH E IMPORTS =====
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    from datetime import datetime
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("\nAsegúrate de tener instalado firebase-admin:")
    print("  pip install firebase-admin")
    input("\nPresiona ENTER para salir...")
    sys.exit(1)

# ===== INICIALIZAR FIREBASE =====
print("🔥 Inicializando Firebase...")

try:
    # Limpiar instancia anterior si existe
    try:
        firebase_admin.get_app()
        firebase_admin.delete_app(firebase_admin.get_app())
        print("  ℹ️  Limpiando instancia anterior de Firebase")
    except ValueError:
        pass
    
    # Inicializar con credenciales
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    print("✅ Firebase inicializado correctamente")
    print()
    
except Exception as e:
    print(f"❌ Error inicializando Firebase: {e}")
    import traceback
    traceback. print_exc()
    input("\nPresiona ENTER para salir...")
    sys.exit(1)

# ===== BUSCAR PROYECTO =====
proyecto_id = "6xrAnYzdu2Ar639Udtow"
print(f"🔍 Buscando proyecto:  {proyecto_id}")
print()

try:
    doc_ref = db.collection('proyectos').document(proyecto_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        print(f"❌ Proyecto '{proyecto_id}' NO existe en Firebase")
        print("\nProyectos disponibles:")
        proyectos_ref = db.collection('proyectos').limit(5).stream()
        for i, p in enumerate(proyectos_ref, 1):
            data = p.to_dict()
            print(f"  {i}. {data. get('nombre', 'Sin nombre')} ({p.id})")
        input("\nPresiona ENTER para salir...")
        sys.exit(1)
    
    proyecto_data = doc.to_dict()
    
    print("=" * 70)
    print("DATOS ACTUALES DEL PROYECTO")
    print("=" * 70)
    print(f"Nombre:              {proyecto_data.get('nombre', 'N/A')}")
    print(f"Presupuesto Total:   {proyecto_data.get('presupuesto_total', 'NO EXISTE')}")
    print(f"Avance Físico:        {proyecto_data.get('avance_fisico', 'NO EXISTE')}")
    print(f"Duración Meses:      {proyecto_data. get('duracion_meses', 'NO EXISTE')}")
    print(f"Fecha Inicio:        {proyecto_data. get('fecha_inicio', 'NO EXISTE')}")
    print(f"Estado:              {proyecto_data.get('estado', 'NO EXISTE')}")
    print("=" * 70)
    print()
    
except Exception as e:
    print(f"❌ Error leyendo proyecto: {e}")
    import traceback
    traceback.print_exc()
    input("\nPresiona ENTER para salir...")
    sys.exit(1)

# ===== PEDIR NUEVOS VALORES =====
print("📝 INGRESA NUEVOS VALORES PARA EL PROYECTO")
print("-" * 70)
print()

root = Tk()
root.withdraw()
root.attributes('-topmost', True)

# Presupuesto
presupuesto_actual = proyecto_data.get('presupuesto_total', 0)
if isinstance(presupuesto_actual, str):
    try:
        presupuesto_actual = float(presupuesto_actual)
    except:
        presupuesto_actual = 2500000

presupuesto = simpledialog.askfloat(
    "Presupuesto Total",
    "Ingresa el presupuesto total del proyecto:\n\n(Valor actual: RD$ {: ,.2f})".format(presupuesto_actual),
    initialvalue=presupuesto_actual if presupuesto_actual > 0 else 2500000,
    minvalue=0
)

if presupuesto is None:
    root.destroy()
    print("❌ Cancelado por el usuario")
    input("\nPresiona ENTER para salir...")
    sys.exit(1)

# Avance Físico
avance_actual = proyecto_data.get('avance_fisico', 0)
if isinstance(avance_actual, str):
    try:
        avance_actual = int(avance_actual)
    except:
        avance_actual = 15

avance_fisico = simpledialog.askinteger(
    "Avance Físico",
    "Ingresa el avance físico del proyecto (%):\n\n(Valor actual: {}%)".format(avance_actual),
    initialvalue=avance_actual if avance_actual > 0 else 15,
    minvalue=0,
    maxvalue=100
)

if avance_fisico is None:
    root.destroy()
    print("❌ Cancelado por el usuario")
    input("\nPresiona ENTER para salir...")
    sys.exit(1)

# Duración
duracion_actual = proyecto_data. get('duracion_meses', 0)
if isinstance(duracion_actual, str):
    try:
        duracion_actual = int(duracion_actual)
    except:
        duracion_actual = 6

duracion_meses = simpledialog.askinteger(
    "Duración Estimada",
    "Ingresa la duración estimada en meses:\n\n(Valor actual: {} meses)".format(duracion_actual),
    initialvalue=duracion_actual if duracion_actual > 0 else 6,
    minvalue=1,
    maxvalue=120
)

root.destroy()

if duracion_meses is None:
    print("❌ Cancelado por el usuario")
    input("\nPresiona ENTER para salir...")
    sys.exit(1)

print()
print("✅ Valores ingresados:")
print(f"  Presupuesto Total:    RD$ {presupuesto: ,.2f}")
print(f"  Avance Físico:       {avance_fisico}%")
print(f"  Duración Estimada:   {duracion_meses} meses")
print()

# ===== CONFIRMAR =====
root = Tk()
root.withdraw()
root.attributes('-topmost', True)

confirmar = messagebox.askyesno(
    "Confirmar Actualización",
    f"¿Guardar estos valores en Firebase?\n\n"
    f"Proyecto: {proyecto_data.get('nombre', 'N/A')}\n"
    f"Presupuesto:  RD$ {presupuesto:,.2f}\n"
    f"Avance Físico: {avance_fisico}%\n"
    f"Duración: {duracion_meses} meses"
)

root.destroy()

if not confirmar:
    print("❌ Actualización cancelada por el usuario")
    input("\nPresiona ENTER para salir...")
    sys.exit(1)

# ===== ACTUALIZAR PROYECTO =====
print("💾 Guardando en Firebase...")
print()

try:
    # Preparar datos de actualización
    update_data = {
        'presupuesto_total': presupuesto,
        'avance_fisico': avance_fisico,
        'duracion_meses': duracion_meses,
        'fecha_actualizacion': datetime.now().isoformat()
    }
    
    # Si no tiene fecha de inicio, agregarla
    if not proyecto_data.get('fecha_inicio'):
        fecha_inicio = datetime.now().strftime('%Y-%m-%d')
        update_data['fecha_inicio'] = fecha_inicio
        print(f"  ℹ️  Agregando fecha de inicio automática: {fecha_inicio}")
    
    # Actualizar documento
    doc_ref.update(update_data)
    
    print("✅ Proyecto actualizado en Firebase")
    print()
    
except Exception as e:
    print(f"❌ Error actualizando proyecto: {e}")
    import traceback
    traceback.print_exc()
    print()
    input("\nPresiona ENTER para salir...")
    sys.exit(1)

# ===== VERIFICAR GUARDADO =====
print("🔍 Verificando que los datos se guardaron correctamente...")
print()

try:
    # Leer nuevamente desde Firebase
    doc_verificado = doc_ref.get()
    proyecto_verificado = doc_verificado.to_dict()
    
    print("=" * 70)
    print("DATOS DESPUÉS DE GUARDAR")
    print("=" * 70)
    print(f"Nombre:               {proyecto_verificado.get('nombre', 'N/A')}")
    print(f"Presupuesto Total:    {proyecto_verificado.get('presupuesto_total', 'NO EXISTE')}")
    print(f"Avance Físico:        {proyecto_verificado.get('avance_fisico', 'NO EXISTE')}")
    print(f"Duración Meses:       {proyecto_verificado.get('duracion_meses', 'NO EXISTE')}")
    print(f"Fecha Inicio:         {proyecto_verificado.get('fecha_inicio', 'NO EXISTE')}")
    print(f"Fecha Actualización:   {proyecto_verificado.get('fecha_actualizacion', 'NO EXISTE')}")
    print("=" * 70)
    print()
    
    # Verificar que los valores se guardaron correctamente
    errores = []
    
    presupuesto_guardado = proyecto_verificado.get('presupuesto_total', 0)
    avance_guardado = proyecto_verificado.get('avance_fisico', 0)
    duracion_guardada = proyecto_verificado.get('duracion_meses', 0)
    
    # Convertir a números si son strings
    try:
        presupuesto_guardado = float(presupuesto_guardado)
    except:
        presupuesto_guardado = 0
    
    try:
        avance_guardado = int(avance_guardado)
    except:
        avance_guardado = 0
    
    try: 
        duracion_guardada = int(duracion_guardada)
    except:
        duracion_guardada = 0
    
    # Comparar valores
    if abs(presupuesto_guardado - presupuesto) > 0.01:
        errores.append(f"❌ Presupuesto NO coincide (esperado: {presupuesto}, guardado: {presupuesto_guardado})")
    else:
        print(f"✅ Presupuesto guardado correctamente:  RD$ {presupuesto_guardado:,.2f}")
    
    if avance_guardado != avance_fisico:
        errores.append(f"❌ Avance Físico NO coincide (esperado: {avance_fisico}, guardado: {avance_guardado})")
    else:
        print(f"✅ Avance Físico guardado correctamente: {avance_guardado}%")
    
    if duracion_guardada != duracion_meses: 
        errores.append(f"❌ Duración NO coincide (esperado: {duracion_meses}, guardado: {duracion_guardada})")
    else:
        print(f"✅ Duración guardada correctamente: {duracion_guardada} meses")
    
    print()
    
    if errores:
        print("🚨 PROBLEMAS DETECTADOS:")
        print("-" * 70)
        for error in errores:
            print(f"  {error}")
        print()
        print("El guardado NO funcionó correctamente.")
    else:
        print("🎉 ¡TODOS LOS DATOS SE GUARDARON CORRECTAMENTE!")
        print()
        print("Ahora puedes:")
        print("  1. Abrir la aplicación PROGAIN 5.0")
        print("  2. Ir al Dashboard")
        print("  3. Deberías ver el card de rendimiento con datos")
    
    print("=" * 70)
    
except Exception as e:
    print(f"❌ Error verificando datos: {e}")
    import traceback
    traceback.print_exc()

# ===== LIMPIAR =====
try:
    firebase_admin.delete_app(firebase_admin.get_app())
except:
    pass

print()
input("Presiona ENTER para salir...")