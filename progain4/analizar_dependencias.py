"""
Analizador de Dependencias de PROGRAIN
Ejecutar desde carpeta progain4

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
SCRIPT_DIR = Path(__file__).parent. absolute()
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
        print(f"🔍 Escaneando archivos en:  {self.root_dir}")
        
        for root, dirs, files in os.walk(self. root_dir):
            # Ignorar carpetas especiales
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'build', 'dist', '. pytest_cache', '.venv', 'venv']]
            
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
                'firebase_explorer', 'analizar_excel', 'crear_exe', 'del_duplicate',
                'analizar_dependencias', 'build', 'setup'
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
    
    def find_most_connected(self):
        """Encontrar los archivos más conectados (importan + son importados)"""
        connections = {}
        
        for module in self.all_modules:
            imports_count = len(self.imports.get(module, set()))
            imported_by_count = len(self.imported_by.get(module, set()))
            total = imports_count + imported_by_count
            
            if total > 0:
                connections[module] = {
                    'total': total,
                    'imports': imports_count,
                    'imported_by': imported_by_count
                }
        
        return sorted(connections.items(), key=lambda x: x[1]['total'], reverse=True)
    
    def generate_tree(self, module_name:  str, indent: int = 0, visited: set = None, max_depth: int = 5):
        """Generar árbol de dependencias recursivo"""
        if visited is None: 
            visited = set()
        
        if indent > max_depth:
            return [f"{'  ' * indent}├─ ...  (max depth reached)"]
        
        if module_name in visited:
            return [f"{'  ' * indent}├─ {module_name} ♻️ (circular)"]
        
        visited.add(module_name)
        
        # Símbolo según el tipo de archivo
        symbol = "📄"
        if 'main' in module_name:
            symbol = "🚀"
        elif 'dialog' in module_name:
            symbol = "💬"
        elif 'page' in module_name:
            symbol = "📋"
        elif 'widget' in module_name:
            symbol = "🧩"
        elif 'service' in module_name:
            symbol = "⚙️"
        
        lines = [f"{'  ' * indent}├─ {symbol} {module_name}"]
        
        # Mostrar qué importa este módulo
        if module_name in self.imports:
            imports_list = sorted(self.imports[module_name])
            for i, imported in enumerate(imports_list):
                is_last = (i == len(imports_list) - 1)
                lines. extend(self.generate_tree(imported, indent + 1, visited. copy(), max_depth))
        
        return lines
    
    def print_report(self):
        """Imprimir reporte visual en consola"""
        print("\n" + "="*80)
        print("📊 REPORTE DE DEPENDENCIAS - PROGRAIN 4.0/5.0")
        print("="*80)
        
        # Estadísticas generales
        print(f"\n📈 ESTADÍSTICAS GENERALES:")
        print(f"   • Total de archivos Python: {len(self.files)}")
        print(f"   • Módulos únicos: {len(self.all_modules)}")
        print(f"   • Archivos con imports: {len(self.imports)}")
        print(f"   • Archivos importados: {len(self.imported_by)}")
        
        # Archivos huérfanos
        orphans = self.find_orphans()
        print(f"\n🔴 ARCHIVOS HUÉRFANOS (no importados por nadie): {len(orphans)}")
        if orphans:
            for orphan in orphans[: 20]:  # Mostrar solo los primeros 20
                # Clasificar por tipo
                category = "📄 Otros"
                if 'dialog' in orphan:
                    category = "💬 Diálogos"
                elif 'dashboard' in orphan:
                    category = "📊 Dashboards"
                elif 'report' in orphan:
                    category = "📈 Reportes"
                elif 'widget' in orphan:
                    category = "🧩 Widgets"
                
                print(f"   {category}: {orphan}")
            if len(orphans) > 20:
                print(f"   ... y {len(orphans) - 20} más")
        else:
            print("   ✅ No hay archivos huérfanos")
        
        # Puntos de entrada
        entry_points = self.find_entry_points()
        print(f"\n🟢 PUNTOS DE ENTRADA:  {len(entry_points)}")
        for entry in entry_points[: 10]: 
            print(f"   🚀 {entry}")
        
        # Top archivos más conectados
        most_connected = self.find_most_connected()[:15]
        print(f"\n🔥 TOP 15 ARCHIVOS MÁS CONECTADOS:")
        for module, stats in most_connected:
            print(f"   • {module}")
            print(f"     ↗️  Importa: {stats['imports']} | ↙️  Importado por: {stats['imported_by']} | 🔗 Total: {stats['total']}")
        
        # Top archivos más importados
        top_imported = sorted(
            self.imported_by.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:10]
        
        print(f"\n⭐ TOP 10 ARCHIVOS MÁS REUTILIZADOS (importados):")
        for module, importers in top_imported:
            print(f"   • {module} ({len(importers)} veces)")
            # Mostrar algunos ejemplos
            examples = sorted(list(importers))[:3]
            for example in examples: 
                print(f"     └─ usado por: {example}")
        
        # Top archivos que más importan
        top_importers = sorted(
            self.imports.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:10]
        
        print(f"\n📚 TOP 10 ARCHIVOS QUE MÁS DEPENDEN DE OTROS:")
        for module, imports in top_importers: 
            print(f"   • {module} ({len(imports)} imports)")
        
        # Árbol de dependencias desde main_ynab
        print(f"\n🌳 ÁRBOL DE DEPENDENCIAS (desde main_ynab):")
        tree = self.generate_tree('main_ynab', max_depth=4)
        for line in tree[: 60]:  # Mostrar solo las primeras 60 líneas
            print(f"   {line}")
        if len(tree) > 60:
            print(f"   ...  y {len(tree) - 60} líneas más")
        
        # Detectar posibles problemas
        print(f"\n⚠️ POSIBLES PROBLEMAS DETECTADOS:")
        
        # Imports circulares
        circular = []
        for module, imports in self.imports.items():
            for imported in imports:
                if module in self.imports. get(imported, set()):
                    circular.append(f"{module} ↔️  {imported}")
        
        if circular:
            print(f"   🔄 Imports circulares encontrados: {len(circular)}")
            for circ in circular[: 5]:
                print(f"     • {circ}")
        else:
            print(f"   ✅ No se detectaron imports circulares")
        
        # Archivos con demasiadas dependencias
        heavy_files = [m for m, i in self.imports.items() if len(i) > 20]
        if heavy_files:
            print(f"   ⚖️  Archivos con >20 imports (candidatos a refactorización): {len(heavy_files)}")
            for heavy in heavy_files[:5]: 
                print(f"     • {heavy} ({len(self.imports[heavy])} imports)")
        else:
            print(f"   ✅ No hay archivos con demasiadas dependencias")
    
    def save_json_report(self, output_file: str = "dependency_report.json"):
        """Guardar reporte completo en JSON"""
        orphans = self.find_orphans()
        entry_points = self.find_entry_points()
        most_connected = self.find_most_connected()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "root_dir": str(self.root_dir),
            "statistics": {
                "total_files": len(self.files),
                "unique_modules": len(self.all_modules),
                "files_with_imports": len(self.imports),
                "files_imported":  len(self.imported_by),
                "orphan_files": len(orphans),
                "entry_points": len(entry_points)
            },
            "files": [str(f) for f in self.files],
            "orphans":  orphans,
            "entry_points": entry_points,
            "most_connected": [
                {"module": k, "total": v['total'], "imports": v['imports'], "imported_by": v['imported_by']}
                for k, v in most_connected[: 30]
            ],
            "imports": {k: list(v) for k, v in self.imports.items()},
            "imported_by": {k: list(v) for k, v in self.imported_by.items()},
            "top_imported": [
                {"module": k, "count": len(v), "examples": list(v)[:5]}
                for k, v in sorted(
                    self.imported_by. items(),
                    key=lambda x: len(x[1]),
                    reverse=True
                )[:30]
            ],
            "top_importers":  [
                {"module": k, "count": len(v), "imports": list(v)[:10]}
                for k, v in sorted(
                    self.imports.items(),
                    key=lambda x: len(x[1]),
                    reverse=True
                )[:30]
            ]
        }
        
        output_path = self.root_dir / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte JSON guardado en: {output_path}")
        return output_path
    
    def generate_graphviz(self, output_file: str = "dependency_graph.dot"):
        """Generar archivo DOT para visualización con Graphviz"""
        output_path = self.root_dir / output_file
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("digraph Dependencies {\n")
            f.write("  rankdir=LR;\n")
            f.write("  node [shape=box, style=rounded, fontname=\"Arial\"];\n")
            f.write("  edge [color=gray];\n\n")
            
            # Definir nodos con colores según categoría
            orphans = set(self.find_orphans())
            
            for module in self.all_modules:
                # Determinar color
                if module in orphans:
                    color = "lightcoral"
                elif 'main' in module:
                    color = "lightgreen"
                elif 'service' in module:
                    color = "lightblue"
                elif 'dialog' in module: 
                    color = "lightyellow"
                elif 'page' in module:
                    color = "lightcyan"
                else:
                    color = "white"
                
                # Solo el nombre del archivo
                label = module. split('.')[-1]
                
                f.write(f'  "{module}" [label="{label}", fillcolor={color}, style=filled];\n')
            
            # Definir conexiones
            f.write("\n")
            for source, targets in self.imports.items():
                for target in targets: 
                    f.write(f'  "{source}" -> "{target}";\n')
            
            # Leyenda
            f.write('\n  // Leyenda\n')
            f.write('  subgraph cluster_legend {\n')
            f.write('    label="Leyenda";\n')
            f.write('    "Main" [fillcolor=lightgreen, style=filled];\n')
            f.write('    "Service" [fillcolor=lightblue, style=filled];\n')
            f.write('    "Dialog" [fillcolor=lightyellow, style=filled];\n')
            f.write('    "Page" [fillcolor=lightcyan, style=filled];\n')
            f.write('    "Orphan" [fillcolor=lightcoral, style=filled];\n')
            f.write('  }\n')
            
            f.write("}\n")
        
        print(f"📊 Archivo Graphviz guardado en: {output_path}")
        print(f"   Para visualizar ejecuta: dot -Tpng {output_file} -o dependency_graph.png")
        print(f"   O usa visualizadores online: http://www.webgraphviz.com/")
        return output_path
    
    def generate_markdown_report(self, output_file: str = "DEPENDENCY_REPORT.md"):
        """Generar reporte en formato Markdown"""
        output_path = self.root_dir / output_file
        
        orphans = self.find_orphans()
        entry_points = self.find_entry_points()
        most_connected = self.find_most_connected()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# 📊 Reporte de Dependencias - PROGRAIN 4.0/5.0\n\n")
            f.write(f"**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Directorio analizado:** `{self.root_dir}`\n\n")
            
            f.write("## 📈 Estadísticas Generales\n\n")
            f.write(f"- **Total de archivos Python:** {len(self.files)}\n")
            f.write(f"- **Módulos únicos:** {len(self.all_modules)}\n")
            f.write(f"- **Archivos con imports:** {len(self.imports)}\n")
            f.write(f"- **Archivos importados:** {len(self.imported_by)}\n")
            f.write(f"- **Archivos huérfanos:** {len(orphans)}\n")
            f.write(f"- **Puntos de entrada:** {len(entry_points)}\n\n")
            
            f.write("## 🔥 Top 15 Archivos Más Conectados\n\n")
            f.write("| Módulo | Importa | Importado por | Total |\n")
            f.write("|--------|---------|---------------|-------|\n")
            for module, stats in most_connected[: 15]:
                f.write(f"| `{module}` | {stats['imports']} | {stats['imported_by']} | {stats['total']} |\n")
            
            f.write("\n## 🟢 Puntos de Entrada\n\n")
            for entry in entry_points: 
                f.write(f"- `{entry}`\n")
            
            f.write("\n## 🔴 Archivos Huérfanos\n\n")
            if orphans:
                f.write("Archivos que no son importados por ningún otro archivo:\n\n")
                for orphan in orphans: 
                    f.write(f"- `{orphan}`\n")
            else:
                f.write("✅ No hay archivos huérfanos\n")
            
            f.write("\n## ⭐ Top 10 Archivos Más Reutilizados\n\n")
            top_imported = sorted(
                self.imported_by.items(),
                key=lambda x: len(x[1]),
                reverse=True
            )[:10]
            
            for module, importers in top_imported:
                f.write(f"\n### `{module}` ({len(importers)} veces)\n\n")
                f.write("Usado por:\n")
                for importer in sorted(list(importers))[:10]:
                    f.write(f"- `{importer}`\n")
        
        print(f"📝 Reporte Markdown guardado en: {output_path}")
        return output_path


def main():
    """Función principal"""
    print("="*80)
    print("🔍 ANALIZADOR DE DEPENDENCIAS DE PROGRAIN")
    print("="*80)
    print(f"📂 Directorio del script: {SCRIPT_DIR}")
    print(f"📂 Raíz del proyecto: {PROJECT_ROOT}")
    print(f"📂 Analizando: {PROGAIN_DIR}")
    print("="*80)
    
    # Crear analizador
    analyzer = DependencyAnalyzer(PROGAIN_DIR)
    
    # Escanear archivos
    analyzer.scan_files()
    
    # Analizar imports
    analyzer.analyze_imports()
    
    # Imprimir reporte
    analyzer.print_report()
    
    # Guardar reportes
    analyzer.save_json_report()
    analyzer.generate_graphviz()
    analyzer.generate_markdown_report()
    
    print("\n" + "="*80)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*80)
    print("\n📁 Archivos generados:")
    print(f"   • dependency_report.json - Datos completos en JSON")
    print(f"   • dependency_graph.dot - Gráfico de dependencias (Graphviz)")
    print(f"   • DEPENDENCY_REPORT.md - Reporte legible en Markdown")
    print("\n💡 Tip: Abre DEPENDENCY_REPORT.md para ver el reporte completo")


if __name__ == "__main__":
    main()