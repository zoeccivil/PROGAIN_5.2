"""
Verificar datos de un proyecto específico en Firebase
Script STANDALONE - No requiere imports de progain4
"""

import sys
import os
from tkinter import Tk, filedialog, simpledialog
import firebase_admin
from firebase_admin import credentials, firestore

print("=" * 70)
print("VERIFICAR DATOS DEL PROYECTO EN FIREBASE")
print("=" * 70)
print()

# ===== SELECCIONAR CREDENCIALES =====
def select_credentials_file():
    """Abrir file dialog para seleccionar archivo de credenciales"""
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    print("🔑 Selecciona el archivo de credenciales de Firebase...")
    
    file_path = filedialog.askopenfilename(
        title="Seleccionar archivo de credenciales Firebase",
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
    
    print(f"✅ Archivo seleccionado: {file_path}")
    return file_path


# ===== PEDIR ID DEL PROYECTO =====
def ask_proyecto_id():
    """Pedir ID del proyecto por input"""
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    proyecto_id = simpledialog.askstring(
        "ID del Proyecto",
        "Ingresa el ID del proyecto a verificar:\n\n(Default: 6xrAnYzdu2Ar639Udtow)",
        initialvalue="6xrAnYzdu2Ar639Udtow"
    )
    
    root.destroy()
    
    return proyecto_id if proyecto_id else "6xrAnYzdu2Ar639Udtow"


# Seleccionar credenciales
cred_path = select_credentials_file()

if not cred_path: 
    print("❌ No se seleccionaron credenciales.  Saliendo...")
    input("\nPresiona ENTER para salir...")
    sys.exit(1)

print()

# Pedir ID del proyecto
proyecto_id = ask_proyecto_id()
print(f"📋 Proyecto a verificar: {proyecto_id}")
print()

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
    
    # Inicializar
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    print("✅ Firebase inicializado correctamente")
    print()
except Exception as e:
    print(f"❌ Error inicializando Firebase: {e}")
    input("\nPresiona ENTER para salir...")
    sys.exit(1)

# ===== OBTENER PROYECTOS =====
print("📊 Buscando proyecto...")
print()

try:
    proyectos_ref = db.collection('proyectos')
    docs = proyectos_ref.stream()
    
    proyectos = []
    for doc in docs:
        data = doc.to_dict()
        data['id'] = doc.id
        proyectos. append(data)
    
    print(f"✅ Recuperados {len(proyectos)} proyectos")
    print()
except Exception as e:
    print(f"❌ Error obteniendo proyectos: {e}")
    input("\nPresiona ENTER para salir...")
    sys.exit(1)

# ===== BUSCAR PROYECTO ESPECÍFICO =====
encontrado = False

for proyecto in proyectos: 
    pid = proyecto.get('id', '')
    
    if str(pid) == str(proyecto_id):
        encontrado = True
        
        print("=" * 70)
        print(f"✅ PROYECTO ENCONTRADO:  {proyecto. get('nombre', 'Sin nombre')}")
        print("=" * 70)
        print(f"ID: {pid}")
        print()
        print("📊 DATOS CLAVE PARA RENDIMIENTO:")
        print("-" * 70)
        
        # Extraer datos
        presupuesto = proyecto.get('presupuesto_total', None)
        avance = proyecto.get('avance_fisico', None)
        duracion = proyecto.get('duracion_meses', None)
        fecha = proyecto.get('fecha_inicio', None)
        estado = proyecto.get('estado', None)
        
        # Mostrar datos RAW
        print(f"  Presupuesto Total:     {presupuesto if presupuesto is not None else 'NO EXISTE'}")
        print(f"  Avance Físico:         {avance if avance is not None else 'NO EXISTE'}")
        print(f"  Duración Meses:       {duracion if duracion is not None else 'NO EXISTE'}")
        print(f"  Fecha Inicio:         {fecha if fecha else 'NO EXISTE'}")
        print(f"  Estado:                {estado if estado else 'NO EXISTE'}")
        print()
        
        # ===== VERIFICAR PROBLEMAS =====
        problemas = []
        warnings = []
        
        # Verificar Presupuesto
        if presupuesto is None:
            problemas.append("❌ Presupuesto Total NO EXISTE en Firebase")
        elif presupuesto == 0 or presupuesto == '0':
            problemas.append("❌ Presupuesto Total = 0 (debe ser mayor a 0)")
        else:
            try:
                presupuesto_num = float(presupuesto)
                print(f"  ✅ Presupuesto Total OK: RD$ {presupuesto_num: ,.2f}")
            except:
                problemas.append(f"❌ Presupuesto Total tiene formato inválido: {presupuesto}")
        
        # Verificar Avance Físico
        if avance is None:
            problemas.append("❌ Avance Físico NO EXISTE en Firebase")
        elif avance == 0 or avance == '0':
            warnings.append("⚠️  Avance Físico = 0 (proyecto sin avance)")
        else:
            try:
                avance_num = int(avance)
                print(f"  ✅ Avance Físico OK: {avance_num}%")
            except:
                problemas.append(f"❌ Avance Físico tiene formato inválido: {avance}")
        
        # Verificar Duración
        if duracion is None:
            problemas.append("❌ Duración Meses NO EXISTE en Firebase")
        elif duracion == 0: 
            problemas.append("❌ Duración Meses = 0 (debe ser mayor a 0)")
        else:
            try:
                duracion_num = int(duracion)
                print(f"  ✅ Duración OK: {duracion_num} meses")
            except:
                problemas.append(f"❌ Duración tiene formato inválido: {duracion}")
        
        # Verificar Fecha Inicio
        if not fecha:
            warnings.append("⚠️  Fecha Inicio vacía (se usará primera transacción)")
        else:
            print(f"  ✅ Fecha Inicio OK: {fecha}")
        
        print()
        print("=" * 70)
        
        # ===== MOSTRAR RESULTADOS =====
        if problemas:
            print()
            print("🚨 PROBLEMAS CRÍTICOS DETECTADOS:")
            print("-" * 70)
            for prob in problemas:
                print(f"  {prob}")
            print()
            
            if warnings:
                print("⚠️  ADVERTENCIAS:")
                print("-" * 70)
                for warn in warnings: 
                    print(f"  {warn}")
                print()
            
            print("📝 SOLUCIÓN:")
            print("-" * 70)
            print("  1. Abre la aplicación PROGAIN 5.0")
            print("  2. Ve a 'Gestión de Obras'")
            print(f"  3. Click derecho en '{proyecto. get('nombre', 'el proyecto')}'")
            print("  4. Seleccionar '✏️ Editar'")
            print("  5. Llenar los siguientes campos:")
            print()
            
            if any("Presupuesto" in str(p) for p in problemas):
                print("     💰 Presupuesto Total:")
                print("        Ingresa el presupuesto total del proyecto")
                print("        Ejemplo: 2500000")
                print()
            
            if any("Avance" in str(p) for p in problemas):
                print("     📊 Avance Físico:")
                print("        Mueve el slider al porcentaje actual de avance")
                print("        Ejemplo: 45%")
                print()
            
            if any("Duración" in str(p) for p in problemas):
                print("     ⏱️  Duración Estimada:")
                print("        Ingresa la duración estimada del proyecto")
                print("        Ejemplo: 6 meses")
                print()
            
            print("  6. Click en 'Guardar'")
            print("  7. Volver al Dashboard")
            print("  8. El rendimiento debería aparecer automáticamente")
            print()
            print("=" * 70)
        
        elif warnings:
            print()
            print("⚠️  ADVERTENCIAS (No crítico):")
            print("-" * 70)
            for warn in warnings:
                print(f"  {warn}")
            print()
            print("Los datos básicos están correctos, pero:")
            print("  • Avance Físico = 0: El proyecto no ha iniciado físicamente")
            print("  • Esto hará que el rendimiento sea 0%")
            print()
            print("Para ver métricas de rendimiento, actualiza el Avance Físico.")
            print("=" * 70)
        
        else:
            print()
            print("🎉 ¡TODOS LOS DATOS ESTÁN CORRECTOS!")
            print("=" * 70)
            print()
            print("✅ Los datos en Firebase son válidos.")
            print()
            print("Si el rendimiento NO aparece en el Dashboard,")
            print("el problema está en el código de carga.")
            print()
            print("Posibles causas:")
            print("  1. _load_project_data() no se ejecuta al inicio")
            print("  2. refresh() no llama a _update_rendimiento_card()")
            print("  3. Error en RendimientoCalculator")
            print()
            print("Verifica el log de la aplicación:")
            print("  Busca:  'Loaded project data' o 'Rendimiento calculado'")
            print()
            print("=" * 70)
        
        break

# ===== PROYECTO NO ENCONTRADO =====
if not encontrado:
    print("=" * 70)
    print(f"❌ PROYECTO '{proyecto_id}' NO ENCONTRADO")
    print("=" * 70)
    print()
    print(f"Proyectos disponibles (primeros 10):")
    print("-" * 70)
    
    for i, p in enumerate(proyectos[:10], 1):
        pid = p.get('id', 'sin-id')
        nombre = p.get('nombre', 'Sin nombre')
        print(f"  {i}. {nombre}")
        print(f"     ID: {pid}")
        print()
    
    if len(proyectos) > 10:
        print(f"  ... y {len(proyectos) - 10} más")
    
    print("=" * 70)

# ===== LIMPIAR =====
try:
    firebase_admin.delete_app(firebase_admin.get_app())
except:
    pass

print()
input("Presiona ENTER para salir...")