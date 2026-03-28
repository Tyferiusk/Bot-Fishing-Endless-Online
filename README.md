# 🎣 PescaBot - Bot Automático de Pesca Endless Online

**Bot de pesca automatizado para juegos que utiliza visión por computadora (OpenCV) para detectar el momento del pique y ejecutar la acción de pescar automáticamente.**

![Versión](https://img.shields.io/badge/version-1.0-blue)
![Python](https://img.shields.io/badge/Python-3.7+-green)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-red)
![Licencia](https://img.shields.io/badge/license-MIT-lightgrey)

---

## ✨ Características

- 🎯 **Detección visual** con OpenCV (reconoce la imagen del "pique")
- ⌨️ **Simulación de teclado** con WinAPI (compatible con AltGr/Ctrl+Alt)
- 🖱️ **Selección de región** para optimizar la búsqueda
- ⏸️ **Pausa/Reanudación** con tecla F10
- 📊 **Contador de capturas** en tiempo real
- 🖥️ **Interfaz por terminal** con estado dinámico en una sola línea
- 🔧 **Configurable** (confianza, intervalo, cooldown, etc.)

---

## 🛡️ ¿Es seguro?

**Este script está diseñado para ser utilizado en juegos que permiten macros o automatización.**

- 🔓 **Código abierto** - Puedes revisar cada línea
- 📖 **Solo simula teclas** - No inyecta código en juegos
- 🚫 **No modifica memoria** - No es un cheat en memoria
- 👤 **Requiere tu consentimiento** - Debes ejecutarlo manualmente

> ⚠️ **Advertencia**: Verifica las reglas del juego antes de usar. Algunos juegos prohíben la automatización. Úsalo bajo tu propia responsabilidad.

---

## 📋 Requisitos

- Python 3.7 o superior
- Windows (por el uso de `keybd_event` para AltGr)
- Bibliotecas Python:
pyautogui
opencv-python
numpy
keyboard
