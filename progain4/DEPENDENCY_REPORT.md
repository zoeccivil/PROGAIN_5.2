# 📊 Reporte de Dependencias - PROGRAIN 4.0/5.0

**Generado:** 2026-01-22 15:00:31

**Directorio analizado:** `E:\Dropbox\GITHUB\PROGAIN_5.3\progain4`

## 📈 Estadísticas Generales

- **Total de archivos Python:** 110
- **Módulos únicos:** 110
- **Archivos con imports:** 27
- **Archivos importados:** 53
- **Archivos huérfanos:** 37
- **Puntos de entrada:** 51

## 🔥 Top 15 Archivos Más Conectados

| Módulo | Importa | Importado por | Total |
|--------|---------|---------------|-------|
| `ui. main_window4` | 32 | 0 | 32 |
| `ui. main_window4 (ZOEC_ADM's conflicted copy 2025-12-23)` | 30 | 0 | 30 |
| `ui. modern. pages. transactions_page` | 9 | 0 | 9 |
| `main_ynab` | 9 | 0 | 9 |
| `commands. __init__` | 6 | 0 | 6 |
| `services. undo_manager` | 6 | 0 | 6 |
| `ui. main_window_modern` | 6 | 0 | 6 |
| `commands. batch_command` | 5 | 0 | 5 |
| `ui. widgets. accounts_window` | 3 | 0 | 3 |
| `firebase_explorer` | 3 | 0 | 3 |
| `ui. reports. gastos_categoria_report` | 3 | 0 | 3 |
| `scripts. list_storage_files` | 2 | 0 | 2 |
| `scripts. make_files_public` | 2 | 0 | 2 |
| `scripts. migrate_attachments` | 2 | 0 | 2 |
| `ui. widgets. cashflow_window` | 2 | 0 | 2 |

## 🟢 Puntos de Entrada

- `commands.account_commands`
- `commands.base_command`
- `commands.batch_command`
- `commands.budget_commands`
- `commands.category_commands`
- `commands.transaction_commands`
- `services.config`
- `services.firebase_client`
- `services.report_generator`
- `services.undo_manager`
- `test_main_window`
- `ui.dashboards.dashboard_gastos_avanzado_window_firebase`
- `ui.dashboards.dashboard_ingresos_vs_gastos_window_firebase`
- `ui.dialogs.attachments_viewer_dialog`
- `ui.dialogs.auditoria_categorias_firebase_dialog`
- `ui.dialogs.firebase_config_dialog`
- `ui.dialogs.firebase_inspector_dialog`
- `ui.dialogs.gestion_categorias_proyecto_dialog`
- `ui.dialogs.gestion_cuentas_maestras_dialog`
- `ui.dialogs.gestion_cuentas_proyecto_dialog`
- `ui.dialogs.gestion_presupuestos_dialog`
- `ui.dialogs.gestion_presupuestos_subcategorias_dialog`
- `ui.dialogs.gestion_subcategorias_proyecto_dialog`
- `ui.dialogs.importer_window_firebase`
- `ui.dialogs.project_dialog`
- `ui.dialogs.transaction_dialog`
- `ui.dialogs.transfer_dialog`
- `ui.dialogs.ui_selector_dialog`
- `ui.dialogs.undo_history_dialog`
- `ui.icon_manager`
- `ui.main_window4`
- `ui.main_window4 (ZOEC_ADM's conflicted copy 2025-12-23)`
- `ui.main_window_modern`
- `ui.modern.components.icon_manager`
- `ui.modern.dialogs.transaction_dialog_modern`
- `ui.modern.main_window`
- `ui.modern.theme_config`
- `ui.reports.detailed_date_report`
- `ui.reports.gastos_categoria_report`
- `ui.reports.resumen_por_cuenta_report`
- `ui.theme_constants`
- `ui.theme_manager`
- `ui.theme_manager_improved`
- `ui.widgets.accounts_window`
- `ui.widgets.cashflow_window`
- `ui.widgets.clean_card`
- `ui.widgets.header_widget`
- `ui.widgets.modern_nav_button`
- `ui.widgets.progress_dialog`
- `ui.widgets.sidebar_widget`
- `ui.widgets.transactions_widget`

## 🔴 Archivos Huérfanos

Archivos que no son importados por ningún otro archivo:

- `scripts.add_duracion_meses`
- `scripts.check_proyecto`
- `scripts.list_storage_files`
- `scripts.make_files_public`
- `scripts.migrate_attachments`
- `services.account_service`
- `services.cache_manager`
- `services.rendimiento_calculator`
- `services.transaction_service`
- `test.diagnostico_categorias`
- `test.diagnostico_completo`
- `test.diagnostico_firebase`
- `test.diganostico_transacciones`
- `ui.dashboards.dashboard_global_cuentas_window_firebase`
- `ui.dialogs.gestion_categorias_maestras_dialog`
- `ui.dialogs.import_categories_dialog`
- `ui.dialogs.irebase_config_dialog`
- `ui.dialogs.transaction_dialog_modern`
- `ui.main_window4 (ZOEC_ADM's conflicted copy 2025-12-23)`
- `ui.main_window_modern`
- `ui.modern.components.account_card`
- `ui.modern.components.clean_card`
- `ui.modern.components.nav_button`
- `ui.modern.components.rendimiento_card`
- `ui.modern.main_window`
- `ui.modern.pages.dashboard_page`
- `ui.modern.pages.obra_card`
- `ui.modern.pages.obra_dialog`
- `ui.modern.pages.obras_page`
- `ui.modern.pages.placeholder_page`
- `ui.modern.pages.transactions_page`
- `ui.modern.widgets.header`
- `ui.modern.widgets.sidebar`
- `ui.reports.account_summary_report`
- `ui.test`
- `ui.theme`
- `utils.attachment_downloader`

## ⭐ Top 10 Archivos Más Reutilizados


### `services.firebase_client` (7 veces)

Usado por:
- `firebase_explorer`
- `main_ynab`
- `scripts. migrate_attachments`
- `ui. main_window4`
- `ui. main_window4 (ZOEC_ADM's conflicted copy 2025-12-23)`
- `ui. widgets. accounts_window`
- `ui. widgets. cashflow_window`

### `commands.base_command` (7 veces)

Usado por:
- `commands. __init__`
- `commands. account_commands`
- `commands. batch_command`
- `commands. budget_commands`
- `commands. category_commands`
- `commands. transaction_commands`
- `services. undo_manager`

### `services.report_generator` (7 veces)

Usado por:
- `ui. dashboards. dashboard_gastos_avanzado_window_firebase`
- `ui. dashboards. dashboard_ingresos_vs_gastos_window_firebase`
- `ui. reports. detailed_date_report`
- `ui. reports. gastos_categoria_report`
- `ui. reports. resumen_por_cuenta_report`
- `ui. widgets. accounts_window`
- `ui. widgets. cashflow_window`

### `services.config` (5 veces)

Usado por:
- `firebase_explorer`
- `main_ynab`
- `scripts. list_storage_files`
- `scripts. make_files_public`
- `ui. modern. pages. transactions_page`

### `services.` (5 veces)

Usado por:
- `scripts. list_storage_files`
- `scripts. make_files_public`
- `scripts. migrate_attachments`
- `ui. main_window4`
- `ui. main_window4 (ZOEC_ADM's conflicted copy 2025-12-23)`

### `ui.dialogs.firebase_config_dialog` (4 veces)

Usado por:
- `firebase_explorer`
- `main_ynab`
- `ui. main_window4`
- `ui. main_window4 (ZOEC_ADM's conflicted copy 2025-12-23)`

### `ui.widgets.transactions_widget` (4 veces)

Usado por:
- `ui. main_window4`
- `ui. main_window4 (ZOEC_ADM's conflicted copy 2025-12-23)`
- `ui. main_window_modern`
- `ui. modern. pages. transactions_page`

### `ui.dialogs.project_dialog` (3 veces)

Usado por:
- `main_ynab`
- `ui. main_window4`
- `ui. main_window4 (ZOEC_ADM's conflicted copy 2025-12-23)`

### `ui.theme_manager_improved` (3 veces)

Usado por:
- `main_ynab`
- `ui. main_window4`
- `ui. main_window4 (ZOEC_ADM's conflicted copy 2025-12-23)`

### `ui` (3 veces)

Usado por:
- `main_ynab`
- `ui. main_window4`
- `ui. main_window4 (ZOEC_ADM's conflicted copy 2025-12-23)`
