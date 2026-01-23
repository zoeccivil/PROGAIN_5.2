"""
Analizador de Dependencias de PROGRAIN
Ejecutar desde:  E:\Dropbox\GITHUB\PROGAIN_5.3\progain4\

Analiza todos los archivos Python y genera: 
1. Mapa de conexiones entre módulos
2. Lista de archivos huérfanos (no importados)
3. Árbol de dependencias
4. Reporte visual en consola y archivo JSON
"""

import os
import sys
import re
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# ✅ Configuración autónoma:  Detectar la raíz del proyecto
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR. parent
PROGAIN_DIR = SCRIPT_DIR

# Agregar al path para imports
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class DependencyAnalyzer: 
    """Analizador de dependencias de archivos Python"""
    
    def __init__(self, root_dir:  Path):
        self.root_dir = root_dir
        self.files = []
        self.imports = defaultdict(set)  # archivo -> {archivos que importa}
        self.imported_by = defaultdict(set)  # archivo -> {archivos que lo importan}
        self.all_modules = set()
        
    def scan_files(self):
        """Escanear todos los archivos Python"""
        print(f"🔍 Escaneando archivos en: {self.root_dir}")
        
        for root, dirs, files in os.walk(self.root_dir):
            # Ignorar carpetas especiales
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'build', 'dist', '.pytest_cache']]
            
            for file in files: 
                if file.endswith('.py'):
                    filepath = Path(root) / file
                    rel_path = filepath.relative_to(self.root_dir)
                    self.files.append(rel_path)
                    
                    # Convertir a nombre de módulo
                    module_name = str(rel_path).replace(os.sep, '. ').replace('.py', '')
                    self.all_modules.add(module_name)
        
        print(f"✅ Encontrados {len(self.files)} archivos Python")
        return self.files
    
    def analyze_imports(self):
        """Analizar imports en cada archivo"""
        print(f"\n🔬 Analizando imports...")
        
        # Patrón para detectar imports
        import_pattern = re.compile(r'^\s*(?:from|import)\s+([\w.]+)', re.MULTILINE)
        
        for filepath in self.files:
            full_path = self.root_dir / filepath
            module_name = str(filepath).replace(os.sep, '. ').replace('.py', '')
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Encontrar todos los imports
                matches = import_pattern.findall(content)
                
                for match in matches:
                    # Solo nos interesan imports del proyecto
                    if match.startswith('progain4'):
                        imported_module = match.replace('progain4.', '')
                        
                        # Agregar a las relaciones
                        self.imports[module_name].add(imported_module)
                        self.imported_by[imported_module].add(module_name)
                        
            except Exception as e:
                print(f"⚠️ Error leyendo {filepath}: {e}")
        
        print(f"✅ Análisis completado")
    
    def find_orphans(self):
        """Encontrar archivos que no son importados por nadie"""
        orphans = []
        
        for filepath in self.files:
            module_name = str(filepath).replace(os.sep, '.').replace('.py', '')
            
            # Archivos especiales que no cuentan como huérfanos
            special_files = [
                'main_ynab', '__init__', 'test_', 'mapa_app', 'mapeador',
                'firebase_explorer', 'analizar_excel', 'crear_exe', 'del_duplicate'
            ]
            
            is_special = any(special in module_name for special in special_files)
            
            # Si no es importado por nadie y no es especial
            if module_name not in self.imported_by and not is_special: 
                orphans.append(module_name)
        
        return sorted(orphans)
    
    def find_entry_points(self):
        """Encontrar puntos de entrada (archivos que no importan nada del proyecto)"""
        entry_points = []
        
        for filepath in self.files:
            module_name = str(filepath).replace(os.sep, '.').replace('.py', '')
            
            # Si no importa nada del proyecto
            if module_name not in self.imports or not self.imports[module_name]:
                # Pero es importado por otros (o es main)
                if module_name in self.imported_by or 'main' in module_name:
                    entry_points.append(module_name)
        
        return sorted(entry_points)
    
    def generate_tree(self, module_name: str, indent:  int = 0, visited: set = None):
        """Generar árbol de dependencias recursivo"""
        if visited is None: 
            visited = set()
        
        if module_name in visited:
            return [f"{'  ' * indent}├─ {module_name} (circular)"]
        
        visited. add(module_name)
        lines = [f"{'  ' * indent}├─ {module_name}"]
        
        # Mostrar qué importa este módulo
        if module_name in self.imports:
            for imported in sorted(self.imports[module_name]):
                lines.extend(self.generate_tree(imported, indent + 1, visited. copy()))
        
        return lines
    
    def print_report(self):
        """Imprimir reporte visual en consola"""
        print("\n" + "="*80)
        print("📊 REPORTE DE DEPENDENCIAS - PROGRAIN 4.0/5.0")
        print("="*80)
        
        # Estadísticas generales
        print(f"\n📈 ESTADÍSTICAS GENERALES:")
        print(f"   • Total de archivos Python: {len(self.files)}")
        print(f"   • Archivos con imports: {len(self.imports)}")
        print(f"   • Archivos importados: {len(self.imported_by)}")
        
        # Archivos huérfanos
        orphans = self. find_orphans()
        print(f"\n🔴 ARCHIVOS HUÉRFANOS (no importados por nadie): {len(orphans)}")
        if orphans:
            for orphan in orphans[: 20]:  # Mostrar solo los primeros 20
                print(f"   • {orphan}")
            if len(orphans) > 20:
                print(f"   ...  y {len(orphans) - 20} más")
        
        # Puntos de entrada
        entry_points = self.find_entry_points()
        print(f"\n🟢 PUNTOS DE ENTRADA:  {len(entry_points)}")
        for entry in entry_points[: 10]: 
            print(f"   • {entry}")
        
        # Top archivos más importados
        top_imported = sorted(
            self.imported_by.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:10]
        
        print(f"\n🔥 TOP 10 ARCHIVOS MÁS IMPORTADOS:")
        for module, importers in top_imported:
            print(f"   • {module} ({len(importers)} veces)")
        
        # Top archivos que más importan
        top_importers = sorted(
            self. imports.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:10]
        
        print(f"\n📚 TOP 10 ARCHIVOS QUE MÁS IMPORTAN:")
        for module, imports in top_importers:
            print(f"   • {module} ({len(imports)} imports)")
        
        # Árbol de dependencias desde main_ynab
        print(f"\n🌳 ÁRBOL DE DEPENDENCIAS (desde main_ynab):")
        tree = self.generate_tree('main_ynab')
        for line in tree[: 50]:  # Mostrar solo las primeras 50 líneas
            print(f"   {line}")
        if len(tree) > 50:
            print(f"   ...  y {len(tree) - 50} líneas más")
    
    def save_json_report(self, output_file: str = "dependency_report.json"):
        """Guardar reporte completo en JSON"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "root_dir": str(self.root_dir),
            "statistics": {
                "total_files": len(self.files),
                "files_with_imports": len(self.imports),
                "files_imported":  len(self.imported_by)
            },
            "files": [str(f) for f in self.files],
            "orphans": self.find_orphans(),
            "entry_points": self.find_entry_points(),
            "imports": {k: list(v) for k, v in self.imports.items()},
            "imported_by": {k: list(v) for k, v in self.imported_by.items()},
            "top_imported": [
                {"module": k, "count": len(v)}
                for k, v in sorted(
                    self.imported_by. items(),
                    key=lambda x: len(x[1]),
                    reverse=True
                )[:20]
            ],
            "top_importers": [
                {"module": k, "count": len(v)}
                for k, v in sorted(
                    self.imports.items(),
                    key=lambda x: len(x[1]),
                    reverse=True
                )[:20]
            ]
        }
        
        output_path = self.root_dir / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte guardado en: {output_path}")
        return output_path
    
    def generate_graphviz(self, output_file: str = "dependency_graph.dot"):
        """Generar archivo DOT para visualización con Graphviz"""
        output_path = self.root_dir / output_file
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("digraph Dependencies {\n")
            f.write("  rankdir=LR;\n")
            f.write("  node [shape=box, style=rounded];\n\n")
            
            # Definir nodos
            orphans = set(self.find_orphans())
            for module in self.all_modules:
                color = "red" if module in orphans else "lightblue"
                label = module. split('.')[-1]  # Solo el nombre del archivo
                f.write(f'  "{module}" [label="{label}", fillcolor={color}, style=filled];\n')
            
            # Definir conexiones
            f.write("\n")
            for source, targets in self.imports.items():
                for target in targets: 
                    f.write(f'  "{source}" -> "{target}";\n')
            
            f.write("}\n")
        
        print(f"📊 Archivo Graphviz guardado en: {output_path}")
        print(f"   Para visualizar: dot -Tpng {output_file} -o dependency_graph.png")
        return output_path


def main():
    """Función principal"""
    print("="*80)
    print("🔍 ANALIZADOR DE DEPENDENCIAS DE PROGRAIN")
    print("="*80)
    print(f"📂 Directorio del script: {SCRIPT_DIR}")
    print(f"📂 Raíz del proyecto:  {PROJECT_ROOT}")
    print(f"📂 Analizando:  {PROGAIN_DIR}")
    print("="*80)
    
    # Crear analizador
    analyzer = DependencyAnalyzer(PROGAIN_DIR)
    
    # Escanear archivos
    analyzer. scan_files()
    
    # Analizar imports
    analyzer.analyze_imports()
    
    # Imprimir reporte
    analyzer.print_report()
    
    # Guardar reportes
    analyzer.save_json_report()
    analyzer.generate_graphviz()
    
    print("\n" + "="*80)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*80)


if __name__ == "__main__":
    main()