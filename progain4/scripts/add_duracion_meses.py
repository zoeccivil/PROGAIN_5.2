"""
Script standalone para agregar campo duracion_meses a proyectos en Firebase
NO requiere imports de progain4 - Totalmente independiente
"""

import os
import sys
from datetime import datetime
from tkinter import Tk, filedialog, messagebox
import firebase_admin
from firebase_admin import credentials, firestore
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def select_credentials_file():
    """Abrir file dialog para seleccionar archivo de credenciales"""
    root = Tk()
    root.withdraw()  # Ocultar ventana principal
    root.attributes('-topmost', True)  # Traer al frente
    
    print("\n🔑 Selecciona el archivo de credenciales de Firebase...")
    
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


def initialize_firebase(cred_path):
    """Inicializar Firebase con las credenciales"""
    try:
        # Verificar si ya está inicializado
        try:
            firebase_admin.get_app()
            logger.info("Firebase ya estaba inicializado, reiniciando...")
            firebase_admin.delete_app(firebase_admin.get_app())
        except ValueError:
            pass
        
        # Inicializar
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        logger.info("✅ Firebase inicializado correctamente")
        return db
    
    except Exception as e:
        logger.error(f"❌ Error inicializando Firebase: {e}")
        return None


def get_proyectos(db):
    """Obtener todos los proyectos de Firebase"""
    try:
        proyectos_ref = db.collection('proyectos')
        docs = proyectos_ref.stream()
        
        proyectos = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            proyectos. append(data)
        
        logger.info(f"✅ Recuperados {len(proyectos)} proyectos")
        return proyectos
    
    except Exception as e:
        logger.error(f"❌ Error obteniendo proyectos: {e}")
        return []


def update_proyecto(db, proyecto_id, updates):
    """Actualizar un proyecto en Firebase"""
    try:
        db.collection('proyectos').document(proyecto_id).update(updates)
        return True
    except Exception as e:
        logger. error(f"❌ Error actualizando proyecto {proyecto_id}: {e}")
        return False


def calcular_duracion_desde_fechas(fecha_inicio_str, fecha_fin_str):
    """Calcular duración en meses entre dos fechas"""
    try: 
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d')
        
        dias = (fecha_fin - fecha_inicio).days
        meses = round(dias / 30.44)
        
        return meses if meses > 0 else None
    except: 
        return None


def add_duracion_meses(db):
    """Agregar campo duracion_meses a todos los proyectos"""
    
    proyectos = get_proyectos(db)
    
    if not proyectos:
        print("❌ No se encontraron proyectos")
        return
    
    print(f"\n📊 Procesando {len(proyectos)} proyectos.. .\n")
    
    actualizados = 0
    ya_tienen = 0
    errores = 0
    
    for proyecto in proyectos: 
        proyecto_id = proyecto.get('id')
        nombre = proyecto.get('nombre', f'Proyecto {proyecto_id}')
        
        # Verificar si ya tiene duracion_meses
        if 'duracion_meses' in proyecto and proyecto. get('duracion_meses'):
            duracion_actual = proyecto['duracion_meses']
            print(f"⏭️  {nombre}: ya tiene duracion_meses = {duracion_actual} meses")
            ya_tienen += 1
            continue
        
        # Calcular duración
        duracion = None
        metodo = None
        
        # Intentar calcular desde fechas
        fecha_inicio = proyecto.get('fecha_inicio', '')
        fecha_fin = proyecto.get('fecha_fin_estimada', '')
        
        if fecha_inicio and fecha_fin:
            duracion = calcular_duracion_desde_fechas(fecha_inicio, fecha_fin)
            if duracion:
                metodo = "calculado desde fechas"
        
        # Si no se pudo calcular, usar default
        if not duracion:
            duracion = 6  # 6 meses por defecto
            metodo = "valor por defecto"
        
        # Actualizar en Firebase
        if update_proyecto(db, proyecto_id, {'duracion_meses': duracion}):
            print(f"✅ {nombre}: duracion_meses = {duracion} meses ({metodo})")
            actualizados += 1
        else: 
            print(f"❌ {nombre}: Error al actualizar")
            errores += 1
    
    # Resumen
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE LA MIGRACIÓN:")
    print("=" * 70)
    print(f"   Total de proyectos:      {len(proyectos)}")
    print(f"   ✅ Actualizados:          {actualizados}")
    print(f"   ⏭️  Ya tenían el campo:  {ya_tienen}")
    print(f"   ❌ Errores:              {errores}")
    print("=" * 70)


def main():
    """Función principal"""
    
    print("=" * 70)
    print("🏗️  AGREGAR CAMPO duracion_meses A PROYECTOS")
    print("=" * 70)
    print()
    print("Este script:")
    print("  1. Te pedirá seleccionar el archivo de credenciales de Firebase")
    print("  2. Revisará todos los proyectos en Firebase")
    print("  3. Calculará duración basada en fecha_inicio y fecha_fin_estimada")
    print("  4. Si no hay fechas, usará 6 meses por defecto")
    print("  5. Agregará el campo 'duracion_meses' a cada proyecto")
    print()
    
    # Confirmar
    respuesta = input("¿Continuar? (s/n): ")
    
    if respuesta.lower() != 's':
        print("❌ Operación cancelada")
        return
    
    # Seleccionar credenciales
    cred_path = select_credentials_file()
    
    if not cred_path: 
        print("❌ No se seleccionaron credenciales.  Saliendo...")
        return
    
    # Inicializar Firebase
    db = initialize_firebase(cred_path)
    
    if not db:
        print("❌ No se pudo inicializar Firebase.  Saliendo...")
        return
    
    # Ejecutar migración
    try:
        add_duracion_meses(db)
        print("\n✅ Proceso completado exitosamente")
    except Exception as e:
        print(f"\n❌ Error durante la ejecución: {e}")
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        # Limpiar
        try:
            firebase_admin.delete_app(firebase_admin.get_app())
        except:
            pass


if __name__ == '__main__': 
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado:  {e}")
        logger.error(f"Error fatal: {e}", exc_info=True)
    finally:
        input("\nPresiona ENTER para salir...")