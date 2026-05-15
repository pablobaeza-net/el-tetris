import json
import os


class PersistenciaTetris:
    def __init__(self):
        # Asegura que exista la carpeta datos_guardados en el mismo directorio del script
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = os.path.join(directorio_actual, "datos_guardados")
        os.makedirs(self.base_dir, exist_ok=True)
        # Intentar migrar datos legacy (jugadores.json / scores.json) si existen
        try:
            self._migrate_legacy()
        except Exception:
            # No fallamos la inicialización por errores en migración
            pass

    def _player_filepath(self, alias: str, nombre_real: str, institucion: str) -> str:
        # Reemplaza espacios por puntos según la regla de negocio
        nombre_real_clean = nombre_real.replace(' ', '.')
        institucion_clean = institucion.replace(' ', '.')
        nombre_archivo = f"{alias}_{nombre_real_clean}_{institucion_clean}.json"
        return os.path.join(self.base_dir, nombre_archivo)

    def registro(self, alias: str, nombre_real: str, institucion: str, categoria: str = None) -> dict:
        """
        Registra un nuevo jugador creando un archivo JSON individual.
        Estructura guardada: alias, nombre_real, institucion, categoria, high_score
        No se guarda 'edad'.
        """
        path = self._player_filepath(alias, nombre_real, institucion)
        if os.path.exists(path):
            raise FileExistsError("El jugador ya está registrado.")

        jugador = {
            "alias": alias,
            "nombre_real": nombre_real,
            "institucion": institucion,
            "categoria": categoria,
            "high_score": 0
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(jugador, f, indent=2, ensure_ascii=False)

        return jugador

    def login(self, alias: str, nombre_real: str, institucion: str, categoria: str = None) -> dict:
        """
        Inicia sesión de un jugador.
        - Carga el JSON del jugador.
        - Si es el primer inicio de sesión y se proporciona `categoria`, la guarda.
        Devuelve el dict del jugador.
        """
        path = self._player_filepath(alias, nombre_real, institucion)
        if not os.path.exists(path):
            raise FileNotFoundError("Jugador no registrado.")

        with open(path, "r", encoding="utf-8") as f:
            jugador = json.load(f)

        if (jugador.get("categoria") in (None, "")) and categoria:
            jugador["categoria"] = categoria
            with open(path, "w", encoding="utf-8") as f:
                json.dump(jugador, f, indent=2, ensure_ascii=False)

        return jugador

    def guardar_puntaje(self, alias: str, nombre_real: str, institucion: str, puntos: int) -> bool:
        """
        Guarda el puntaje solo si es mayor que el high_score actual.
        Retorna True si actualizó el high_score, False si no.
        """
        path = self._player_filepath(alias, nombre_real, institucion)
        if not os.path.exists(path):
            raise FileNotFoundError("Jugador no registrado.")

        with open(path, "r", encoding="utf-8") as f:
            jugador = json.load(f)

        current = jugador.get("high_score", 0)
        if puntos > current:
            jugador["high_score"] = puntos
            with open(path, "w", encoding="utf-8") as f:
                json.dump(jugador, f, indent=2, ensure_ascii=False)
            return True

        return False

    def _migrate_legacy(self) -> None:
        """Migra datos desde jugadores.json y scores.json (legacy) a archivos por jugador.
        Si se realiza la migración, los archivos legacy se renombran con extensión .bak.
        """
        jugadores_path = os.path.join(self.base_dir, "jugadores.json")
        scores_path = os.path.join(self.base_dir, "scores.json")

        if not os.path.exists(jugadores_path):
            return

        # Cargar legacy
        try:
            with open(jugadores_path, 'r', encoding='utf-8') as f:
                legacy_users = json.load(f)
        except Exception:
            return

        legacy_scores = {}
        if os.path.exists(scores_path):
            try:
                with open(scores_path, 'r', encoding='utf-8') as f:
                    legacy_scores = json.load(f)
            except Exception:
                legacy_scores = {}

        # legacy_users expected: { alias: {nombre, apellido, institucion, categoria, ...} }
        for alias, info in legacy_users.items():
            nombre = info.get('nombre', '')
            apellido = info.get('apellido', '')
            institucion = info.get('institucion', '')
            categoria = info.get('categoria')

            nombre_real = f"{nombre} {apellido}".strip()
            # obtener high score desde legacy_scores si existe
            high = 0
            for cat, scores_map in (legacy_scores.items() if isinstance(legacy_scores, dict) else []):
                if isinstance(scores_map, dict) and alias in scores_map:
                    try:
                        high = int(scores_map[alias])
                        break
                    except Exception:
                        continue

            # construir ruta y escribir archivo por jugador si no existe
            path = self._player_filepath(alias, nombre_real, institucion)
            if os.path.exists(path):
                # actualizar solo high_score/categoria si conviene
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        existing = json.load(f)
                    modified = False
                    if existing.get('high_score', 0) < high:
                        existing['high_score'] = high; modified = True
                    if (not existing.get('categoria')) and categoria:
                        existing['categoria'] = categoria; modified = True
                    if modified:
                        with open(path, 'w', encoding='utf-8') as f:
                            json.dump(existing, f, indent=2, ensure_ascii=False)
                except Exception:
                    continue
            else:
                jugador = {
                    'alias': alias,
                    'nombre_real': nombre_real,
                    'institucion': institucion,
                    'categoria': categoria,
                    'high_score': high
                }
                try:
                    with open(path, 'w', encoding='utf-8') as f:
                        json.dump(jugador, f, indent=2, ensure_ascii=False)
                except Exception:
                    continue

        # Hacer backup de los archivos legacy para no perder información
        try:
            if os.path.exists(jugadores_path):
                os.replace(jugadores_path, jugadores_path + ".bak")
        except Exception:
            pass
        try:
            if os.path.exists(scores_path):
                os.replace(scores_path, scores_path + ".bak")
        except Exception:
            pass