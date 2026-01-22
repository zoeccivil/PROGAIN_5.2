#!/usr/bin/env python3
"""
PROGRAIN 4.0 / 5.0 Main Application Entry Point

Firebase-based personal finance management application with UI selector.
Run with: python progain4/main_ynab.py
"""

import sys
import os
import logging
import json
from typing import Optional, Tuple

# ✅ CRÍTICO: Importar QtWebEngineWidgets ANTES de QApplication
# Esto configura automáticamente Qt. AA_ShareOpenGLContexts
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_AVAILABLE = True
except ImportError:
    WEBENGINE_AVAILABLE = False
    # No loggeamos aquí porque logging aún no está configurado

# Ahora sí importar QApplication (después de QtWebEngineWidgets)
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMessageBox

# ---------------------------------------------------------------------------
# Ensure project root is on sys.path so that `import progain4.*` works
# regardless of the current working directory. 
# ---------------------------------------------------------------------------
CURRENT_DIR = os.path. dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from progain4.services.firebase_client import FirebaseClient
from progain4.services.config import ConfigManager
from progain4.ui.dialogs.firebase_config_dialog import FirebaseConfigDialog
from progain4.ui.dialogs.project_dialog import ProjectDialog

# Import theme manager
try:
    from progain4.ui.theme_manager_improved import theme_manager
    logger_temp = logging.getLogger(__name__)
    logger_temp.info("Using improved theme manager")
except ImportError:
    from progain4.ui import theme_manager
    logger_temp = logging.getLogger(__name__)
    logger_temp.info("Using standard theme manager")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Log WebEngine availability
if WEBENGINE_AVAILABLE:
    logger. info("✅ QtWebEngineWidgets loaded successfully")
else:
    logger.warning("⚠️ QtWebEngineWidgets not available - dashboards may not work")


class PROGRAIN4App: 
    """
    Main application class for PROGRAIN 4.0/5.0

    Handles: 
    - Firebase initialization with validation
    - Project selection with automatic last project loading
    - UI selection (Classic vs Modern)
    - Main window creation
    """

    def __init__(self):
        """Initialize the application"""

        # Create QApplication (Qt already configured by imports above)
        self.app = QApplication(sys.argv)

        # Set application metadata
        self.app.setApplicationName("PROGRAIN 5.0")
        self.app.setApplicationVersion("5.0.0")
        self.app.setOrganizationName("PROGRAIN")
        self.app.setOrganizationDomain("prograin.com")

        self.firebase_client:  Optional[FirebaseClient] = None
        self.main_window = None  # Can be MainWindow4 or MainWindow (modern)
        self.config_manager = ConfigManager()

        # Apply saved theme
        saved_theme = self.config_manager.get_theme()
        theme_to_apply = saved_theme if saved_theme else "light"

        try:
            theme_manager.apply_theme(self.app, theme_to_apply)
            logger.info(f"Applied theme at startup: {theme_to_apply}")
        except Exception as e: 
            logger.warning(f"Could not apply theme '{theme_to_apply}': {e}. Using default.")
            try:
                theme_manager.apply_theme(self.app, "light")
            except: 
                logger.error("Could not apply default theme")

    def run(self) -> int:
        """
        Run the application.

        Returns:
            Exit code
        """
        try:
            # Step 1: Initialize Firebase with validation
            if not self. initialize_firebase():
                logger.error("Firebase initialization failed")
                return 1

            # Step 2: Select or create project (auto-loads last project)
            proyecto_result = self.select_project()
            if not proyecto_result or not proyecto_result[0]:
                logger.info("No project selected, exiting")
                return 0

            proyecto_id, proyecto_nombre = proyecto_result

            # Step 3: Select UI (checks for saved preference first)
            ui_type = self.select_ui_interface()
            if not ui_type: 
                logger.info("No UI selected, exiting")
                return 0

            # Step 4: Launch appropriate UI
            if ui_type == "modern":
                return self.launch_modern_ui(proyecto_id, proyecto_nombre)
            else:
                return self.launch_classic_ui(proyecto_id, proyecto_nombre)

        except Exception as e:
            logger.error(f"Unexpected error in run(): {e}", exc_info=True)
            QMessageBox.critical(
                None,
                "Error Fatal",
                f"Error inesperado:\n{str(e)}\n\nRevise los logs para más detalles.",
            )
            return 1

    # ==================== FIREBASE INITIALIZATION ====================

    def initialize_firebase(self) -> bool:
        """
        Initialize Firebase connection with validation.

        Returns:
            True if initialization successful, False otherwise
        """
        logger.info("Initializing Firebase...")

        credentials_path = None
        storage_bucket = None

        # Priority 1: Environment variables (useful for development/testing)
        env_credentials = os.environ.get("FIREBASE_CREDENTIALS", "")
        env_bucket = os.environ.get("FIREBASE_STORAGE_BUCKET", "")

        if env_credentials and env_bucket and os.path.exists(env_credentials):
            logger.info("Using Firebase credentials from environment variables")

            is_valid, error_msg = self._validate_credentials_file(env_credentials)

            if is_valid:
                credentials_path = env_credentials
                storage_bucket = env_bucket
            else:
                logger.warning(f"Environment credentials invalid: {error_msg}")
                QMessageBox.warning(
                    None,
                    "Credenciales Inválidas",
                    f"Las credenciales en las variables de entorno están corruptas:\n\n{error_msg}\n\n"
                    "Por favor, configura nuevas credenciales.",
                )

        # Priority 2: Persistent configuration (INI file)
        if not credentials_path:
            saved_credentials, saved_bucket = self. config_manager.get_firebase_config()

            if saved_credentials and saved_bucket:
                if os.path.exists(saved_credentials):
                    logger.info("Validating saved Firebase credentials...")

                    is_valid, error_msg = self._validate_credentials_file(saved_credentials)

                    if is_valid:
                        logger.info("Using Firebase credentials from saved configuration")
                        credentials_path = saved_credentials
                        storage_bucket = saved_bucket
                    else:
                        logger.warning(f"Saved credentials invalid: {error_msg}")

                        QMessageBox.warning(
                            None,
                            "Credenciales Corruptas",
                            f"Las credenciales guardadas están corruptas o son inválidas:\n\n{error_msg}\n\n"
                            "Se solicitarán nuevas credenciales.",
                        )

                        self.config_manager.clear_firebase_config()
                else:
                    logger.warning(f"Saved credentials file not found: {saved_credentials}")
                    self.config_manager.clear_firebase_config()

        # If no valid credentials, show dialog
        if not credentials_path or not storage_bucket:
            logger.info("No valid credentials found, showing configuration dialog")

            QMessageBox.information(
                None,
                "Configuración de Firebase",
                "Bienvenido a PROGRAIN 5.0\n\n"
                "Para comenzar, necesitas configurar la conexión con Firebase.\n\n"
                "En el siguiente diálogo, selecciona el archivo de credenciales "
                "JSON descargado desde Firebase Console.\n\n"
                "📥 Descarga credenciales desde:\n"
                "https://console.firebase.google.com/ → Configuración → Cuentas de servicio",
            )

            dialog = FirebaseConfigDialog(parent=None, config_manager=self.config_manager)

            if dialog. exec() != FirebaseConfigDialog.DialogCode.Accepted:
                logger.info("Firebase configuration cancelled by user")
                QMessageBox.warning(
                    None,
                    "Configuración requerida",
                    "PROGRAIN requiere configuración de Firebase para funcionar.\n\n" "La aplicación se cerrará.",
                )
                return False

            credentials_path, storage_bucket = dialog.get_config()

            if not credentials_path or not storage_bucket:
                logger.error("Invalid configuration returned from dialog")
                return False

            is_valid, error_msg = self._validate_credentials_file(credentials_path)

            if not is_valid:
                QMessageBox.critical(
                    None,
                    "Credenciales Inválidas",
                    f"El archivo seleccionado no es válido:\n\n{error_msg}\n\n"
                    "Por favor, descarga nuevas credenciales desde Firebase Console.",
                )
                return False

        # Initialize Firebase client
        try:
            logger. info(f"Initializing Firebase with credentials: {credentials_path}")
            logger.info(f"Storage bucket: {storage_bucket}")

            self.firebase_client = FirebaseClient()

            if not self.firebase_client.initialize(credentials_path, storage_bucket):
                raise Exception("Firebase initialization returned False")

            logger.info("Firebase initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Error initializing Firebase: {e}")

            error_msg = str(e).lower()

            if "invalid" in error_msg or "signature" in error_msg or "jwt" in error_msg:
                dialog_msg = (
                    f"Las credenciales de Firebase son inválidas:\n\n{str(e)}\n\n"
                    "⚠️ Posibles causas:\n"
                    "• Archivo de credenciales corrupto\n"
                    "• Credenciales de un proyecto diferente\n"
                    "• Archivo modificado manualmente\n\n"
                    "📥 Solución:\n"
                    "1. Ve a Firebase Console\n"
                    "2. Configuración → Cuentas de servicio\n"
                    "3. Genera nueva clave privada\n"
                    "4. Descarga el archivo JSON\n\n"
                    "¿Desea seleccionar un nuevo archivo de credenciales?"
                )
            else:
                dialog_msg = (
                    f"No se pudo conectar con Firebase:\n\n{str(e)}\n\n"
                    "⚠️ Posibles causas:\n"
                    "• Sin conexión a Internet\n"
                    "• Firewall bloqueando conexión\n"
                    "• Nombre del bucket incorrecto\n"
                    "• Permisos insuficientes en Firebase\n\n"
                    "¿Desea reconfigurar las credenciales?"
                )

            reply = QMessageBox.critical(
                None,
                "Error de conexión con Firebase",
                dialog_msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes,
            )

            if reply == QMessageBox.StandardButton. Yes:
                self.config_manager.clear_firebase_config()

                dialog = FirebaseConfigDialog(parent=None, config_manager=self. config_manager)

                if dialog.exec() == FirebaseConfigDialog.DialogCode. Accepted:
                    credentials_path, storage_bucket = dialog.get_config()

                    is_valid, error_msg = self._validate_credentials_file(credentials_path)

                    if not is_valid:
                        QMessageBox.critical(
                            None, "Credenciales Inválidas", f"El archivo seleccionado no es válido:\n\n{error_msg}"
                        )
                        return False

                    try:
                        self.firebase_client = FirebaseClient()

                        if self.firebase_client.initialize(credentials_path, storage_bucket):
                            logger.info("Firebase initialized successfully on retry")
                            return True
                        else:
                            raise Exception("Firebase initialization failed on retry")

                    except Exception as e2:
                        logger.error(f"Error on retry: {e2}")
                        QMessageBox.critical(None, "Error", f"No se pudo inicializar Firebase:\n{str(e2)}")

            return False

    def _validate_credentials_file(self, credentials_path: str) -> Tuple[bool, str]: 
        """
        Validate that credentials file is valid JSON with correct structure. 

        Args:
            credentials_path: Path to credentials file

        Returns:
            Tuple (is_valid, error_message)
        """
        try: 
            if not os.path.exists(credentials_path):
                return False, f"El archivo no existe: {credentials_path}"

            with open(credentials_path, "r", encoding="utf-8") as f:
                creds = json.load(f)

            required_fields = [
                "type",
                "project_id",
                "private_key_id",
                "private_key",
                "client_email",
                "client_id",
                "auth_uri",
                "token_uri",
            ]

            missing_fields = [field for field in required_fields if field not in creds]

            if missing_fields:
                return False, f"Campos faltantes en credenciales: {', '.join(missing_fields)}"

            private_key = creds.get("private_key", "")
            if "\\n" not in private_key and "\n" not in private_key:
                return False, "El campo 'private_key' no tiene el formato correcto (falta \\n)"

            if creds.get("type") != "service_account":
                return False, f"Tipo de credencial inválido: {creds.get('type')} (debe ser 'service_account')"

            logger.info(f"✅ Credentials file validated:  {credentials_path}")
            logger.info(f"   Project ID: {creds.get('project_id')}")
            logger.info(f"   Client Email: {creds.get('client_email')}")

            return True, ""

        except json.JSONDecodeError as e:
            return False, f"Archivo JSON inválido: {str(e)}"
        except Exception as e:
            return False, f"Error al validar credenciales: {str(e)}"

    # ==================== PROJECT SELECTION ====================

    def select_project(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Select or load last used project automatically.

        Returns:
            Tuple of (project_id, project_name) or (None, None) if cancelled
        """
        logger.info("Loading projects...")

        try:
            proyectos = self.firebase_client. get_proyectos()
            logger.info(f"Found {len(proyectos)} existing projects")

            if not proyectos:
                logger.info("No existing projects found")

                reply = QMessageBox.question(
                    None,
                    "Sin proyectos",
                    "No se encontraron proyectos en Firebase.\n\n" "¿Desea crear un nuevo proyecto?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox. StandardButton.Yes,
                )

                if reply == QMessageBox.StandardButton.No:
                    return None, None

                dialog = ProjectDialog(proyectos=[])

                if dialog.exec() != ProjectDialog.DialogCode.Accepted:
                    return None, None

                result = dialog.get_selected_project()
                if not result or result[0] is not None: 
                    return None, None

                _, nombre, descripcion = result
                logger.info(f"Creating new project: {nombre}")

                try:
                    proyecto_id = self.firebase_client. create_proyecto(nombre, descripcion)

                    if not proyecto_id:
                        raise Exception("create_proyecto returned None")

                    logger.info(f"Project created successfully: {proyecto_id}")

                    self._save_last_project(proyecto_id, nombre)

                    return proyecto_id, nombre

                except Exception as e:
                    logger.error(f"Error creating project: {e}")
                    QMessageBox.critical(None, "Error", f"No se pudo crear el proyecto:\n{str(e)}")
                    return None, None

            # Try to load last used project
            last_project_id, last_project_name = self._load_last_project()

            if last_project_id: 
                # Verify project still exists
                proyecto_existe = False
                for p in proyectos:
                    if hasattr(p, "id"):
                        pid = p.id
                    elif hasattr(p, "get"):
                        pid = p.get("id", "")
                    else: 
                        continue

                    if str(pid) == str(last_project_id):
                        proyecto_existe = True
                        break

                if proyecto_existe:
                    logger. info(f"Loading last used project: {last_project_name} ({last_project_id})")
                    return last_project_id, last_project_name
                else:
                    logger.warning(f"Last project {last_project_id} no longer exists")

            # Fallback:  Load first available project
            primer_proyecto = proyectos[0]

            if hasattr(primer_proyecto, "id"):
                proyecto_id = str(primer_proyecto.id)
                if hasattr(primer_proyecto, "to_dict"):
                    data = primer_proyecto.to_dict()
                    proyecto_nombre = data.get("nombre", f"Proyecto {proyecto_id}")
                else:
                    proyecto_nombre = f"Proyecto {proyecto_id}"
            else:
                proyecto_id = str(primer_proyecto.get("id", ""))
                proyecto_nombre = primer_proyecto.get("nombre", f"Proyecto {proyecto_id}")

            logger.info(f"Loading first available project: {proyecto_nombre} ({proyecto_id})")

            self._save_last_project(proyecto_id, proyecto_nombre)

            return proyecto_id, proyecto_nombre

        except Exception as e: 
            logger.error(f"Error loading projects: {e}")
            QMessageBox.critical(None, "Error", f"Error al cargar proyectos desde Firebase:\n{str(e)}")
            return None, None

    def _load_last_project(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Load last used project from configuration.

        Returns:
            Tuple of (project_id, project_name) or (None, None) if not found
        """
        try:
            last_project = self.config_manager.get_last_project()
            if last_project:
                return last_project
            return None, None
        except Exception as e:
            logger.warning(f"Error loading last project:  {e}")
            return None, None

    def _save_last_project(self, proyecto_id: str, proyecto_nombre: str):
        """
        Save last used project to configuration. 

        Args:
            proyecto_id: Project ID
            proyecto_nombre: Project name
        """
        try: 
            self.config_manager. set_last_project(str(proyecto_id), str(proyecto_nombre))
            logger.debug(f"Saved last project:  {proyecto_nombre} ({proyecto_id})")
        except Exception as e:
            logger.warning(f"Error saving last project:  {e}")

    # ==================== UI SELECTION ====================

    def select_ui_interface(self) -> Optional[str]:
        """
        Show UI selector dialog.

        Returns:
            'classic' or 'modern', or None if cancelled
        """
        from progain4.ui.dialogs.ui_selector_dialog import UISelectorDialog

        # Check if there's a saved preference
        saved_ui = self. config_manager.get_ui_preference()
        if saved_ui:
            logger.info(f"Using saved UI preference: {saved_ui}")
            return saved_ui

        # Show selector dialog
        dialog = UISelectorDialog(self.config_manager)

        if dialog.exec():
            ui_type = dialog.get_selected_ui()
            logger.info(f"User selected UI:  {ui_type}")
            return ui_type

        return None

    def launch_classic_ui(self, proyecto_id: str, proyecto_nombre: str) -> int:
        """
        Launch the classic UI (MainWindow4).

        Args:
            proyecto_id: Selected project ID
            proyecto_nombre:  Selected project name

        Returns: 
            Exit code
        """
        logger.info(f"Launching CLASSIC UI for project: {proyecto_nombre}")

        from progain4.ui.main_window4 import MainWindow4

        self.main_window = MainWindow4(
            firebase_client=self.firebase_client,
            proyecto_id=proyecto_id,
            proyecto_nombre=proyecto_nombre,
            config_manager=self.config_manager,
        )

        self.main_window.project_changed.connect(self._on_project_changed)
        self.main_window.show()

        logger.info("Classic UI launched successfully")
        return self.app.exec()

    def launch_modern_ui(self, proyecto_id: str, proyecto_nombre:  str) -> int:
        """
        Launch the modern UI (MainWindow from ui. modern).

        Args:
            proyecto_id: Selected project ID
            proyecto_nombre: Selected project name

        Returns:
            Exit code
        """
        logger.info(f"Launching MODERN UI for project: {proyecto_nombre}")

        from progain4.ui.modern. main_window import MainWindow

        self.main_window = MainWindow(
            firebase_client=self.firebase_client,
            proyecto_id=proyecto_id,
            proyecto_nombre=proyecto_nombre,
            config_manager=self.config_manager,
        )

        self.main_window. show()

        logger.info("Modern UI launched successfully")
        return self.app.exec()

    def _on_project_changed(self, proyecto_id: str, proyecto_nombre: str):
        """
        Callback when user changes project from UI.

        Args:
            proyecto_id: New project ID
            proyecto_nombre:  New project name
        """
        logger.info(f"Project changed to: {proyecto_nombre} ({proyecto_id})")
        self._save_last_project(proyecto_id, proyecto_nombre)


def main():
    """Main entry point"""
    logger.info("=" * 70)
    logger.info("PROGRAIN 5.0 Starting...")
    logger.info("=" * 70)

    try:
        app = PROGRAIN4App()
        exit_code = app.run()

        logger.info("=" * 70)
        logger.info(f"PROGRAIN 5.0 Exiting with code {exit_code}")
        logger.info("=" * 70)

        sys.exit(exit_code)

    except Exception as e: 
        logger.exception("Fatal error in main(): %s", e)
        sys.exit(1)


if __name__ == "__main__": 
    main()