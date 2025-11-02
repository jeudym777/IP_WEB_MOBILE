"""
Gestor de temas para la aplicación.
"""

import flet as ft
from typing import Dict, Any
from enum import Enum


class AppTheme(Enum):
    """Temas disponibles para la aplicación."""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class ThemeManager:
    """Gestor de temas de la aplicación."""
    
    def __init__(self):
        """Inicializa el gestor de temas."""
        self.current_theme = AppTheme.LIGHT
        
        # Colores personalizados para el tema claro
        self.light_colors = {
            'primary': ft.Colors.BLUE_600,
            'primary_variant': ft.Colors.BLUE_800,
            'secondary': ft.Colors.GREEN_500,
            'background': ft.Colors.GREY_50,
            'surface': ft.Colors.WHITE,
            'error': ft.Colors.RED_500,
            'on_primary': ft.Colors.WHITE,
            'on_secondary': ft.Colors.WHITE,
            'on_background': ft.Colors.GREY_900,
            'on_surface': ft.Colors.GREY_900,
            'on_error': ft.Colors.WHITE,
        }
        
        # Colores personalizados para el tema oscuro
        self.dark_colors = {
            'primary': ft.Colors.BLUE_400,
            'primary_variant': ft.Colors.BLUE_600,
            'secondary': ft.Colors.GREEN_400,
            'background': ft.Colors.GREY_900,
            'surface': ft.Colors.GREY_800,
            'error': ft.Colors.RED_400,
            'on_primary': ft.Colors.GREY_900,
            'on_secondary': ft.Colors.GREY_900,
            'on_background': ft.Colors.WHITE,
            'on_surface': ft.Colors.WHITE,
            'on_error': ft.Colors.GREY_900,
        }
    
    def get_theme_data(self, theme: AppTheme) -> ft.Theme:
        """
        Obtiene los datos del tema especificado.
        
        Args:
            theme: Tema a obtener
            
        Returns:
            Datos del tema para Flet
        """
        if theme == AppTheme.DARK:
            return ft.Theme(
                color_scheme=ft.ColorScheme(
                    primary=self.dark_colors['primary'],
                    primary_container=self.dark_colors['primary_variant'],
                    secondary=self.dark_colors['secondary'],
                    background=self.dark_colors['background'],
                    surface=self.dark_colors['surface'],
                    error=self.dark_colors['error'],
                    on_primary=self.dark_colors['on_primary'],
                    on_secondary=self.dark_colors['on_secondary'],
                    on_background=self.dark_colors['on_background'],
                    on_surface=self.dark_colors['on_surface'],
                    on_error=self.dark_colors['on_error'],
                ),
                font_family="Segoe UI"
            )
        else:  # LIGHT theme
            return ft.Theme(
                color_scheme=ft.ColorScheme(
                    primary=self.light_colors['primary'],
                    primary_container=self.light_colors['primary_variant'],
                    secondary=self.light_colors['secondary'],
                    background=self.light_colors['background'],
                    surface=self.light_colors['surface'],
                    error=self.light_colors['error'],
                    on_primary=self.light_colors['on_primary'],
                    on_secondary=self.light_colors['on_secondary'],
                    on_background=self.light_colors['on_background'],
                    on_surface=self.light_colors['on_surface'],
                    on_error=self.light_colors['on_error'],
                ),
                font_family="Segoe UI"
            )
    
    def apply_theme(self, page: ft.Page, theme: AppTheme = None) -> None:
        """
        Aplica un tema a la página.
        
        Args:
            page: Página de Flet
            theme: Tema a aplicar (usa el actual si no se especifica)
        """
        if theme is not None:
            self.current_theme = theme
        
        if self.current_theme == AppTheme.AUTO:
            # En modo auto, usar el tema del sistema si está disponible
            page.theme_mode = ft.ThemeMode.SYSTEM
        elif self.current_theme == AppTheme.DARK:
            page.theme_mode = ft.ThemeMode.DARK
            page.dark_theme = self.get_theme_data(AppTheme.DARK)
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            page.theme = self.get_theme_data(AppTheme.LIGHT)
        
        page.update()
    
    def toggle_theme(self, page: ft.Page) -> AppTheme:
        """
        Alterna entre tema claro y oscuro.
        
        Args:
            page: Página de Flet
            
        Returns:
            Nuevo tema aplicado
        """
        if self.current_theme == AppTheme.LIGHT:
            new_theme = AppTheme.DARK
        elif self.current_theme == AppTheme.DARK:
            new_theme = AppTheme.AUTO
        else:
            new_theme = AppTheme.LIGHT
        
        self.apply_theme(page, new_theme)
        return new_theme
    
    def get_status_colors(self) -> Dict[str, str]:
        """
        Obtiene los colores para diferentes estados.
        
        Returns:
            Diccionario con colores de estado
        """
        if self.current_theme == AppTheme.DARK:
            return {
                'success': ft.Colors.GREEN_400,
                'warning': ft.Colors.AMBER_400,
                'error': ft.Colors.RED_400,
                'info': ft.Colors.BLUE_400,
                'neutral': ft.Colors.GREY_400
            }
        else:
            return {
                'success': ft.Colors.GREEN_600,
                'warning': ft.Colors.AMBER_600,
                'error': ft.Colors.RED_600,
                'info': ft.Colors.BLUE_600,
                'neutral': ft.Colors.GREY_600
            }
    
    def get_button_style(self, variant: str = "primary") -> Dict[str, Any]:
        """
        Obtiene el estilo para botones.
        
        Args:
            variant: Variante del botón (primary, secondary, danger)
            
        Returns:
            Diccionario con propiedades de estilo
        """
        colors = self.get_status_colors()
        
        styles = {
            'primary': {
                'bgcolor': colors['info'],
                'color': ft.Colors.WHITE,
            },
            'secondary': {
                'bgcolor': colors['neutral'],
                'color': ft.Colors.WHITE,
            },
            'success': {
                'bgcolor': colors['success'],
                'color': ft.Colors.WHITE,
            },
            'danger': {
                'bgcolor': colors['error'],
                'color': ft.Colors.WHITE,
            }
        }
        
        return styles.get(variant, styles['primary'])