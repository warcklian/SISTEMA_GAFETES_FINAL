# 🧠 REGLAS DE MEMORIA - SISTEMA DE DESARROLLO

## REGLA 16: DOCUMENTACIÓN DE ESTRUCTURA DE PROYECTO

### **🧠 PRINCIPIO FUNDAMENTAL**
- **Crear documentación completa** de la estructura del proyecto
- **Especificar función de cada archivo** y sus dependencias
- **Evitar duplicación** de archivos de prueba innecesarios
- **Facilitar comprensión rápida** para nuevos desarrolladores o instancias de chat

### **📋 IMPLEMENTACIÓN OBLIGATORIA**

#### **1. ARCHIVO PROJECT_STRUCTURE.md**
- **Ubicación**: Siempre en la raíz del proyecto
- **Nombre**: `PROJECT_STRUCTURE.md`
- **Formato**: Markdown para máxima compatibilidad

#### **2. CONTENIDO OBLIGATORIO**
- **Función de cada archivo**: Qué hace y para qué sirve
- **Dependencias**: Qué archivos necesita cada uno
- **Flujos de trabajo**: Cómo se relacionan los archivos
- **Archivos críticos**: Cuáles no se pueden eliminar
- **Casos de uso**: Cómo usar el proyecto para diferentes tareas

#### **3. ESTRUCTURA DEL DOCUMENTO**
```markdown
# 📁 ESTRUCTURA DEL PROYECTO - [NOMBRE_PROYECTO]

## 🎯 **PROPÓSITO**
Este documento describe la estructura completa del proyecto, la función de cada archivo y sus dependencias.

## 📂 **ESTRUCTURA PRINCIPAL**
### **🏗️ ARCHIVOS PRINCIPALES DE PRODUCCIÓN**
- [Archivo principal]: Función, dependencias, características
- [Scripts principales]: Motor de renderizado, procesamiento
- [Configuraciones]: Archivos de configuración centralizados

### **🧪 ARCHIVOS DE PRUEBA Y DESARROLLO**
- [Archivos de prueba]: Sistema de pruebas, validaciones
- [Archivos de desarrollo]: Herramientas de desarrollo

### **📊 ARCHIVOS DE DATOS**
- [Carpetas de datos]: Fuentes, imágenes, resultados
- [Templates]: Plantillas y recursos base

### **📋 ARCHIVOS DE CONFIGURACIÓN**
- [Configs principales]: Configuración centralizada
- [Configs específicos]: Configuraciones por módulo

### **🛠️ ARCHIVOS DE UTILIDADES**
- [Instaladores]: Scripts de instalación automática
- [Verificadores]: Diagnóstico y pruebas del sistema
- [Ejemplos]: Casos de uso y documentación práctica

### **📚 ARCHIVOS DE DOCUMENTACIÓN**
- [README]: Documentación principal
- [Guías técnicas]: Documentación detallada
- [Guías de instalación]: Pasos esenciales
- [Guías de reparación]: Solución de problemas

## 🔗 **DEPENDENCIAS PRINCIPALES**
### **Flujo de Producción**:
[Archivo principal] → [Procesadores] → [Motores] → [Configs] → [Templates] → [Resultados]

### **Flujo de Pruebas**:
[Archivos de prueba] → [Motores] → [Configs] → [Templates] → [Pruebas]

## ⚠️ **ARCHIVOS CRÍTICOS**
### **NO ELIMINAR**:
- [Lista de archivos críticos que no se pueden eliminar]

### **PUEDEN REGENERARSE**:
- [Lista de archivos que se pueden regenerar]

## 🎯 **CASOS DE USO COMUNES**
### **Para [Caso específico]**:
1. [Paso 1]
2. [Paso 2]
3. [Paso 3]

## 📝 **NOTAS IMPORTANTES**
- [Notas críticas sobre el proyecto]
- [Configuraciones importantes]
- [Sistemas de recuperación]
```

### **4. ACTUALIZACIÓN AUTOMÁTICA**
- **Actualizar cuando se agreguen archivos** nuevos
- **Actualizar cuando se modifique la estructura** del proyecto
- **Mantener sincronizado** con la realidad del proyecto

## 🎯 **BENEFICIOS UNIVERSALES**

### **PARA NUEVOS DESARROLLADORES**:
- ✅ **Comprensión rápida** - Entender el proyecto en minutos
- ✅ **Evitar duplicación** - Saber qué archivos ya existen
- ✅ **Dependencias claras** - Entender qué necesita cada archivo

### **PARA NUEVAS INSTANCIAS DE CHAT**:
- ✅ **Contexto completo** - Entender la estructura sin análisis previo
- ✅ **Evitar archivos de prueba** - Usar los existentes correctamente
- ✅ **Flujos claros** - Saber cómo se relacionan los componentes

### **PARA MANTENIMIENTO**:
- ✅ **Documentación viva** - Siempre actualizada
- ✅ **Referencia rápida** - Encontrar archivos y funciones
- ✅ **Estructura clara** - Organización lógica del proyecto

## 🔧 **IMPLEMENTACIÓN PASO A PASO**

### **PASO 1: Análisis Profundo del Proyecto**
- Revisar TODOS los archivos y carpetas
- Identificar función de cada archivo
- Mapear dependencias entre archivos
- Clasificar por categorías (producción, prueba, datos, etc.)

### **PASO 2: Crear Estructura del Documento**
- Usar plantilla estándar
- Organizar por categorías lógicas
- Incluir todos los archivos encontrados
- Especificar función y dependencias

### **PASO 3: Documentar Flujos de Trabajo**
- Mapear flujo de producción
- Mapear flujo de pruebas
- Identificar archivos críticos
- Documentar casos de uso comunes

### **PASO 4: Validar y Actualizar**
- Verificar que todos los archivos estén documentados
- Confirmar que las dependencias sean correctas
- Probar que los flujos de trabajo sean válidos
- Mantener actualizado con cambios futuros

## 🎉 **RESULTADO ESPERADO**

- **Comprensión inmediata** del proyecto para cualquier persona
- **Eliminación de duplicación** de archivos de prueba
- **Flujos de trabajo claros** y documentados
- **Mantenimiento simplificado** del proyecto
- **Onboarding rápido** de nuevos desarrolladores

## 📝 **NOTAS IMPORTANTES**

- **SIEMPRE** crear este archivo al analizar un proyecto
- **NUNCA** omitir archivos importantes
- **ACTUALIZAR** cuando se modifique la estructura
- **MANTENER** en la raíz del proyecto para fácil acceso
- **USAR** como referencia principal para entender el proyecto

#### **4. COBERTURA UNIVERSAL POR TIPO DE PROYECTO**

##### **DESARROLLO WEB**:
- **Frontend (React/Vue/Angular)**: Seguir estándares oficiales del framework
- **Backend (Django/Flask/Express/Spring)**: Seguir estándares oficiales del framework
- **Microservicios**: Documentar por servicio independiente

##### **INTELIGENCIA ARTIFICIAL**:
- **Machine Learning**: Documentar estructura de datos, modelos, entrenamiento, inferencia
- **Deep Learning**: Documentar arquitecturas, entrenamiento, optimización
- **MLOps**: Documentar pipeline, deployment, monitoreo, versionado

##### **TRADING ALGORÍTMICO**:
- **Estrategias**: Documentar mercados, estrategias, riesgo, brokers
- **Backtesting**: Documentar configuraciones de prueba
- **Live Trading**: Documentar APIs, monitoreo, compliance

##### **WEB SCRAPING**:
- **Scrapy**: Seguir estándares oficiales de Scrapy
- **Selenium**: Documentar configuraciones de scraping
- **APIs**: Documentar por endpoint y sitio

##### **CIENCIA DE DATOS**:
- **Análisis**: Documentar configuraciones de análisis
- **Visualización**: Documentar configuraciones de gráficos
- **Modelos**: Documentar por tipo de modelo y dataset

##### **DESARROLLO MÓVIL**:
- **React Native**: Seguir estándares oficiales de React Native
- **Flutter**: Seguir estándares oficiales de Flutter
- **Nativo**: Documentar por plataforma (iOS/Android)

##### **BLOCKCHAIN**:
- **Smart Contracts**: Documentar por contrato
- **DeFi**: Documentar por protocolo
- **NFTs**: Documentar configuraciones de metadata

##### **MICROSERVICIOS**:
- **Por servicio**: Documentar por microservicio
- **Orquestación**: Documentar Docker, Kubernetes, CI/CD

##### **DESARROLLO DE VIDEOJUEGOS**:
- **Unity (C#)**: Seguir estándares oficiales de Unity
- **Unreal Engine (C++/Blueprint)**: Seguir estándares oficiales de Unreal
- **Godot (GDScript/C#)**: Seguir estándares oficiales de Godot
- **Web Games (JavaScript/TypeScript)**: Seguir estándares de desarrollo web
- **Mobile Games**: Seguir estándares de desarrollo móvil

##### **DESARROLLO DE APLICACIONES MÓVILES**:
- **iOS (Swift/Objective-C)**: Seguir estándares oficiales de Apple
- **Android (Kotlin/Java)**: Seguir estándares oficiales de Google
- **Cross-platform (React Native/Flutter/Xamarin)**: Seguir estándares del framework
- **Progressive Web Apps (PWA)**: Seguir estándares web modernos

##### **DESARROLLO DE ESCRITORIO**:
- **Windows (C#/C++/Python)**: Seguir estándares de Windows
- **macOS (Swift/Objective-C)**: Seguir estándares de Apple
- **Linux (C/C++/Python/Go)**: Seguir estándares de Linux
- **Cross-platform (Electron/Qt/GTK)**: Seguir estándares del framework

##### **DESARROLLO EMBEBIDO**:
- **Arduino (C/C++)**: Seguir estándares de Arduino
- **Raspberry Pi (Python/C/C++)**: Seguir estándares de Raspberry Pi
- **IoT (C/C++/Python/JavaScript)**: Seguir estándares de IoT
- **Microcontroladores**: Seguir estándares del fabricante

##### **DESARROLLO DE SISTEMAS**:
- **Sistemas Operativos (C/C++/Rust)**: Seguir estándares de sistemas
- **Drivers (C/C++/Rust)**: Seguir estándares de drivers
- **Firmware (C/C++/Assembly)**: Seguir estándares de firmware
- **Real-time Systems**: Seguir estándares de tiempo real

##### **DESARROLLO DE APLICACIONES ENTERPRISE**:
- **ERP Systems**: Seguir estándares de ERP
- **CRM Systems**: Seguir estándares de CRM
- **Financial Systems**: Seguir estándares financieros
- **Healthcare Systems**: Seguir estándares de salud

##### **DESARROLLO DE APLICACIONES CIENTÍFICAS**:
- **Simulaciones (Python/C++/Fortran)**: Seguir estándares científicos
- **Análisis Numérico**: Seguir estándares matemáticos
- **Visualización Científica**: Seguir estándares de visualización
- **HPC (High Performance Computing)**: Seguir estándares de HPC

#### **5. ESTÁNDARES OFICIALES POR LENGUAJE**

##### **Python**:
- **Django**: Estructura oficial de Django
- **Flask**: Estructura oficial de Flask
- **FastAPI**: Estructura oficial de FastAPI
- **PyTorch**: Estructura oficial de PyTorch
- **TensorFlow**: Estructura oficial de TensorFlow

##### **JavaScript/TypeScript**:
- **React**: Estructura oficial de Create React App
- **Vue.js**: Estructura oficial de Vue CLI
- **Angular**: Estructura oficial de Angular CLI
- **Node.js**: Estructura oficial de Express
- **Next.js**: Estructura oficial de Next.js

##### **Java**:
- **Spring Boot**: Estructura oficial de Spring Boot
- **Maven**: Estructura estándar de Maven
- **Gradle**: Estructura estándar de Gradle

##### **C#**:
- **.NET**: Estructura oficial de .NET
- **ASP.NET Core**: Estructura oficial de ASP.NET Core

##### **Go**:
- **Gin**: Estructura estándar de Gin
- **Echo**: Estructura estándar de Echo
- **Fiber**: Estructura estándar de Fiber

##### **Rust**:
- **Cargo**: Estructura estándar de Cargo
- **Actix**: Estructura estándar de Actix
- **Tokio**: Estructura estándar de Tokio

##### **LENGUAJES DE TRADING ALGORÍTMICO**:
- **MQL4/MQL5**: Estructura estándar de MetaTrader
- **Pine Script**: Estructura estándar de TradingView
- **EasyLanguage**: Estructura estándar de TradeStation
- **NinjaScript**: Estructura estándar de NinjaTrader

##### **LENGUAJES DE DESARROLLO DE VIDEOJUEGOS**:
- **C#**: Estructura estándar de Unity
- **C++**: Estructura estándar de Unreal Engine
- **GDScript**: Estructura estándar de Godot
- **Lua**: Estructura estándar de Love2D, Corona
- **JavaScript/TypeScript**: Estructura estándar de Phaser, Three.js

##### **LENGUAJES DE DESARROLLO MÓVIL**:
- **Swift**: Estructura estándar de iOS
- **Kotlin**: Estructura estándar de Android
- **Objective-C**: Estructura estándar de iOS legacy
- **Java**: Estructura estándar de Android legacy
- **Dart**: Estructura estándar de Flutter

##### **LENGUAJES DE DESARROLLO DE ESCRITORIO**:
- **C#**: Estructura estándar de .NET
- **C++**: Estructura estándar de Qt, GTK
- **Python**: Estructura estándar de Tkinter, PyQt
- **Electron**: Estructura estándar de Electron
- **Rust**: Estructura estándar de Tauri

##### **LENGUAJES DE DESARROLLO EMBEBIDO**:
- **C/C++**: Estructura estándar de Arduino, ESP32
- **Python**: Estructura estándar de Raspberry Pi
- **JavaScript**: Estructura estándar de Node.js IoT
- **Assembly**: Estructura estándar de microcontroladores
- **Rust**: Estructura estándar de embedded Rust

##### **LENGUAJES DE DESARROLLO DE SISTEMAS**:
- **C/C++**: Estructura estándar de sistemas operativos
- **Rust**: Estructura estándar de sistemas modernos
- **Assembly**: Estructura estándar de bajo nivel
- **Go**: Estructura estándar de servicios de sistema
- **Zig**: Estructura estándar de sistemas modernos

##### **LENGUAJES DE DESARROLLO CIENTÍFICO**:
- **Python**: Estructura estándar de NumPy, SciPy
- **C++**: Estructura estándar de HPC
- **Fortran**: Estructura estándar de computación científica
- **Julia**: Estructura estándar de computación científica
- **R**: Estructura estándar de análisis estadístico
- **MATLAB**: Estructura estándar de MATLAB

---

## REGLA 17: CONFIGURACIONES MODULARES Y PRÁCTICAS

### **🧠 PRINCIPIO FUNDAMENTAL**
- **Organizar configuraciones** según el contexto y tipo de proyecto
- **Seguir estándares** del lenguaje/framework cuando existan
- **Aplicar modularidad práctica** para proyectos sin estándares
- **Facilitar mantenimiento** y edición rápida
- **Ser aplicable** a cualquier tipo de proyecto (IA, trading, web, etc.)

### **📋 IMPLEMENTACIÓN FLEXIBLE**

#### **1. ENFOQUE SEGÚN TIPO DE PROYECTO Y LENGUAJE**

##### **Para Proyectos de Renderizado/Imagen (Python, JavaScript)**:
```bash
CONFIG/
└── config.json                   # TODO EN UN ARCHIVO
    ├── template_settings         # Configuración de plantilla
    ├── field_mapping            # Mapeo de campos (fuentes, colores, posiciones)
    ├── fonts                    # Configuración de fuentes
    └── validation               # Validaciones
```

##### **Para Proyectos Web (estándares por lenguaje)**:
```bash
# Python (Django/Flask)
CONFIG/
├── settings.py                  # Configuración principal
├── database.py                 # Base de datos
└── api.py                      # APIs externas

# Node.js (Express)
CONFIG/
├── config.js                   # Configuración principal
├── database.js                 # Base de datos
└── api.js                      # APIs externas

# Java (Spring)
src/main/resources/
├── application.yml             # Configuración principal
├── application-dev.yml        # Desarrollo
└── application-prod.yml       # Producción
```

##### **Para Proyectos de IA/ML (Python, R, Julia)**:
```bash
CONFIG/
├── config_modelos.json         # Configuración de modelos
├── config_datos.json          # Procesamiento de datos
├── config_entrenamiento.json  # Parámetros de entrenamiento
└── config_inferencia.json     # Configuración de inferencia
```

##### **Para Trading Algorítmico (Python, C++, Rust)**:
```bash
CONFIG/
├── config_mercados.json        # Configuración de mercados
├── config_estrategias.json     # Parámetros de estrategias
├── config_riesgo.json         # Gestión de riesgo
└── config_brokers.json        # Configuración de brokers
```

##### **Para Web Scraping (Python, JavaScript, Go)**:
```bash
CONFIG/
├── config_sitios.json          # Configuración de sitios objetivo
├── config_proxies.json         # Configuración de proxies
├── config_headers.json         # Headers y user agents
└── config_almacenamiento.json  # Configuración de almacenamiento
```

##### **Para Redes Neuronales (Python, PyTorch, TensorFlow)**:
```bash
CONFIG/
├── config_arquitectura.json    # Arquitectura de la red
├── config_entrenamiento.json   # Parámetros de entrenamiento
├── config_datos.json          # Preprocesamiento de datos
└── config_optimizacion.json   # Optimizadores y schedulers
```

#### **2. CRITERIOS DE DECISIÓN UNIVERSALES**

##### **SEGUIR ESTÁNDARES DEL LENGUAJE/FRAMEWORK CUANDO EXISTAN**:
- **Python**: Django (settings.py), Flask (config.py), FastAPI (settings.py)
- **JavaScript**: Node.js (config.js), React (config.js), Vue (config.js)
- **Java**: Spring (application.yml), Maven (pom.xml)
- **C#**: .NET (appsettings.json), ASP.NET Core (appsettings.json)
- **Go**: Viper (config.yaml), Cobra (config.yaml)
- **Rust**: TOML (Cargo.toml), Serde (config.toml)

##### **USAR UN SOLO ARCHIVO CUANDO**:
- **Proyectos de renderizado/imagen** (pasaportes, certificados, documentos)
- **Configuraciones interrelacionadas** (fuentes, colores, posiciones)
- **Edición frecuente** de múltiples aspectos simultáneamente
- **Proyectos cohesivos** sin estándares establecidos
- **Prototipos rápidos** y proyectos pequeños

##### **SEPARAR EN MÚLTIPLES ARCHIVOS CUANDO**:
- **Proyectos web** (estándares de la industria)
- **Configuraciones independientes** (base de datos vs. API vs. seguridad)
- **Equipos grandes** trabajando en diferentes módulos
- **Despliegues selectivos** de configuraciones
- **Proyectos enterprise** con múltiples servicios

##### **APLICAR MODULARIDAD PRÁCTICA CUANDO**:
- **No hay estándares** establecidos para el tipo de proyecto
- **Configuraciones complejas** que requieren organización
- **Múltiples entornos** (desarrollo, testing, producción)
- **Configuraciones por dominio** (modelos, datos, entrenamiento)

#### **3. ESTRUCTURA PRÁCTICA POR TIPO DE PROYECTO**

##### **Para Proyectos de Renderizado/Imagen (UN SOLO ARCHIVO)**:
```json
// CONFIG/config.json
{
  "template_settings": {
    "default_template": "PASAPORTE-VENEZUELA.psd",
    "output_format": "PNG",
    "output_quality": 300
  },
  "field_mapping": {
    "nombre": {
      "layer_name": "NOMBRES",
      "font_size": 12,
      "font_color": "#000000",
      "position": {"x": 335, "y": 917, "ancho": 134, "alto": 17}
    }
  }
}
```

##### **Para Trading Algorítmico (MÚLTIPLES ARCHIVOS)**:
```json
// CONFIG/config_mercados.json
{
  "mercados": {
    "forex": {"pares": ["EUR/USD", "GBP/USD"], "horario": "24/7"},
    "acciones": {"exchanges": ["NYSE", "NASDAQ"], "horario": "9:30-16:00"}
  }
}

// CONFIG/config_estrategias.json
{
  "estrategias": {
    "rsi": {"periodo": 14, "sobrecompra": 70, "sobreventa": 30},
    "media_movil": {"periodo_corta": 20, "periodo_larga": 50}
  }
}
```

##### **Para Redes Neuronales (MÚLTIPLES ARCHIVOS)**:
```json
// CONFIG/config_arquitectura.json
{
  "modelo": {
    "tipo": "CNN",
    "capas": [{"conv1": 32, "conv2": 64, "dense": 128},
    "activacion": "relu",
    "dropout": 0.2
  }
}

// CONFIG/config_entrenamiento.json
{
  "entrenamiento": {
    "epochs": 100,
    "batch_size": 32,
    "learning_rate": 0.001,
    "optimizer": "adam"
  }
}
```

##### **Para Web Scraping (MÚLTIPLES ARCHIVOS)**:
```json
// CONFIG/config_sitios.json
{
  "sitios": {
    "noticias": {"url": "https://ejemplo.com", "selectores": {"titulo": "h1"}},
    "productos": {"url": "https://tienda.com", "selectores": {"precio": ".price"}}
  }
}

// CONFIG/config_proxies.json
{
  "proxies": {
    "rotacion": true,
    "timeout": 30,
    "user_agents": ["Mozilla/5.0", "Chrome/91.0"]
  }
}
```

#### **4. IMPLEMENTACIÓN FLEXIBLE POR LENGUAJE**

##### **Python (UN SOLO ARCHIVO - Renderizado)**:
```python
class ConfigManager:
    def __init__(self, config_path="CONFIG/config.json"):
        self.config_path = config_path
        self.config = self._cargar_config()
    
    def _cargar_config(self):
        """Carga configuración desde un solo archivo"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def obtener_campo(self, campo):
        """Obtiene configuración de un campo específico"""
        return self.config['field_mapping'].get(campo, {})
```

##### **Python (MÚLTIPLES ARCHIVOS - IA/ML)**:
```python
class ConfigManager:
    def __init__(self, config_dir="CONFIG/"):
        self.config_dir = Path(config_dir)
        self.configs = {}
        self._cargar_configuraciones()
    
    def _cargar_configuraciones(self):
        """Carga configuraciones modulares"""
        archivos = ['modelos', 'datos', 'entrenamiento', 'inferencia']
        for archivo in archivos:
            ruta = self.config_dir / f'config_{archivo}.json'
            if ruta.exists():
                with open(ruta, 'r') as f:
                    self.configs[archivo] = json.load(f)
```

##### **JavaScript/Node.js (MÚLTIPLES ARCHIVOS)**:
```javascript
class ConfigManager {
    constructor(configDir = 'CONFIG/') {
        this.configDir = configDir;
        this.configs = {};
        this.cargarConfiguraciones();
    }
    
    cargarConfiguraciones() {
        const archivos = ['database', 'api', 'security'];
        archivos.forEach(archivo => {
            const ruta = `${this.configDir}config_${archivo}.json`;
            if (fs.existsSync(ruta)) {
                this.configs[archivo] = JSON.parse(fs.readFileSync(ruta, 'utf8'));
            }
        });
    }
}
```

##### **Go (MÚLTIPLES ARCHIVOS)**:
```go
type ConfigManager struct {
    configs map[string]interface{}
}

func NewConfigManager(configDir string) *ConfigManager {
    cm := &ConfigManager{configs: make(map[string]interface{})}
    cm.cargarConfiguraciones(configDir)
    return cm
}

func (cm *ConfigManager) cargarConfiguraciones(configDir string) {
    archivos := []string{"database", "api", "security"}
    for _, archivo := range archivos {
        ruta := fmt.Sprintf("%sconfig_%s.json", configDir, archivo)
        if data, err := ioutil.ReadFile(ruta); err == nil {
            var config interface{}
            json.Unmarshal(data, &config)
            cm.configs[archivo] = config
        }
    }
}
```

##### **Rust (MÚLTIPLES ARCHIVOS)**:
```rust
use serde_json;
use std::collections::HashMap;

pub struct ConfigManager {
    configs: HashMap<String, serde_json::Value>,
}

impl ConfigManager {
    pub fn new(config_dir: &str) -> Self {
        let mut cm = Self {
            configs: HashMap::new(),
        };
        cm.cargar_configuraciones(config_dir);
        cm
    }
    
    fn cargar_configuraciones(&mut self, config_dir: &str) {
        let archivos = vec!["database", "api", "security"];
        for archivo in archivos {
            let ruta = format!("{}config_{}.json", config_dir, archivo);
            if let Ok(data) = std::fs::read_to_string(&ruta) {
                if let Ok(config) = serde_json::from_str(&data) {
                    self.configs.insert(archivo.to_string(), config);
                }
            }
        }
    }
}
```

### **5. VENTAJAS SEGÚN EL ENFOQUE**

#### **UN SOLO ARCHIVO (Proyectos de Renderizado/Imagen)**:
- ✅ **Edición rápida** - Todo en un lugar, cambios inmediatos
- ✅ **Contexto completo** - Ver todas las configuraciones relacionadas
- ✅ **Menos referencias** - No saltar entre múltiples archivos
- ✅ **Simplicidad** - Ideal para proyectos cohesivos
- ✅ **Prototipado rápido** - Configuración centralizada

#### **MÚLTIPLES ARCHIVOS (Proyectos Web/Enterprise/IA)**:
- ✅ **Separación de responsabilidades** - Cada archivo tiene un propósito específico
- ✅ **Trabajo en equipo** - Diferentes desarrolladores en diferentes configs
- ✅ **Despliegue selectivo** - Deploy solo configuraciones necesarias
- ✅ **Escalabilidad** - Fácil agregar nuevos módulos
- ✅ **Mantenimiento especializado** - Expertos en cada área

#### **SEGUIR ESTÁNDARES DEL LENGUAJE**:
- ✅ **Compatibilidad** - Integración con ecosistema del lenguaje
- ✅ **Familiaridad** - Desarrolladores conocen la estructura
- ✅ **Herramientas** - IDEs y herramientas reconocen la estructura
- ✅ **Comunidad** - Soporte y documentación disponible

### **6. IMPLEMENTACIÓN PASO A PASO UNIVERSAL**

#### **PASO 1: Evaluar el Contexto del Proyecto**
- **¿Existe estándar del lenguaje/framework?** → SEGUIR ESTÁNDAR
- **¿Es un proyecto de renderizado/imagen?** → UN SOLO ARCHIVO
- **¿Es un proyecto web/enterprise/IA?** → MÚLTIPLES ARCHIVOS
- **¿Las configuraciones están interrelacionadas?** → UN SOLO ARCHIVO
- **¿Trabajan múltiples equipos en diferentes módulos?** → MÚLTIPLES ARCHIVOS

#### **PASO 2: Implementar Según Decisión**
##### **Para SEGUIR ESTÁNDARES**:
- **Python**: Django (settings.py), Flask (config.py)
- **JavaScript**: Node.js (config.js), React (config.js)
- **Java**: Spring (application.yml)
- **C#**: .NET (appsettings.json)
- **Go**: Viper (config.yaml)
- **Rust**: TOML (Cargo.toml)

##### **Para UN SOLO ARCHIVO**:
- Crear `CONFIG/config.json` con todas las configuraciones
- Organizar por secciones lógicas (template_settings, field_mapping, fonts, etc.)
- Mantener estructura clara y comentada

##### **Para MÚLTIPLES ARCHIVOS**:
- Crear directorio `CONFIG/`
- Separar por responsabilidades (database, api, security, etc.)
- Mantener nombres descriptivos

#### **PASO 3: Implementar Cargador Apropiado**
- **Estándar**: Usar herramientas del framework (Django settings, Spring config, etc.)
- **Un archivo**: Cargador simple que lee todo de una vez
- **Múltiples archivos**: Cargador modular que carga según necesidad

#### **PASO 4: Validar y Optimizar**
- Probar que todas las configuraciones se carguen correctamente
- Verificar que el rendimiento sea adecuado
- Documentar la estructura elegida
- Asegurar compatibilidad con herramientas del lenguaje

### **7. CASOS DE USO ESPECÍFICOS**

#### **Para Proyectos de Renderizado (UN SOLO ARCHIVO)**:
```json
// CONFIG/config.json
{
  "template_settings": {
    "default_template": "PASAPORTE-VENEZUELA.psd",
    "output_format": "PNG",
    "output_quality": 300
  },
  "field_mapping": {
    "nombre": {
      "layer_name": "NOMBRES",
      "font_size": 12,
      "font_color": "#000000",
      "position": {"x": 335, "y": 917, "ancho": 134, "alto": 17}
    }
  },
  "fonts": {
    "font_mapping": {
      "NOMBRES": "Arial",
      "LETRA.FIRMA": "BrittanySignature.ttf"
    }
  }
}
```

#### **Para Proyectos Web (MÚLTIPLES ARCHIVOS)**:
```json
// CONFIG/config_database.json
{
  "connection": {
    "host": "localhost",
    "port": 5432,
    "database": "mi_app"
  }
}

// CONFIG/config_api.json
{
  "endpoints": {
    "base_url": "https://api.ejemplo.com",
    "timeout": 30
  }
}
```

## 🎉 **RESULTADO ESPERADO**

- **Configuraciones organizadas** según el contexto y tipo de proyecto
- **Compatibilidad** con estándares del lenguaje/framework
- **Mantenimiento simplificado** y edición rápida
- **Flexibilidad** para elegir el enfoque apropiado
- **Practicidad** sobre rigidez de reglas
- **Escalabilidad** según las necesidades del proyecto
- **Aplicabilidad universal** a cualquier tipo de proyecto

## 📝 **NOTAS IMPORTANTES**

- **EVALUAR** el contexto del proyecto antes de decidir
- **PRIORIZAR** estándares del lenguaje cuando existan
- **CONSIDERAR** el tipo de proyecto (renderizado vs. web vs. IA vs. trading)
- **MANTENER** coherencia en la estructura elegida
- **DOCUMENTAR** la decisión y el razonamiento
- **ADAPTAR** a las buenas prácticas del lenguaje específico

---

#### **4. COBERTURA UNIVERSAL POR TIPO DE PROYECTO**

##### **DESARROLLO WEB**:
- **Frontend (React/Vue/Angular)**: Seguir estándares oficiales del framework
- **Backend (Django/Flask/Express/Spring)**: Seguir estándares oficiales del framework
- **Microservicios**: Archivos múltiples por servicio independiente

##### **INTELIGENCIA ARTIFICIAL**:
- **Machine Learning**: Archivos múltiples (modelos, datos, entrenamiento, inferencia)
- **Deep Learning**: Archivos múltiples (arquitectura, entrenamiento, optimización)
- **MLOps**: Archivos múltiples (pipeline, deployment, monitoreo, versionado)

##### **TRADING ALGORÍTMICO**:
- **Estrategias**: Archivos múltiples (mercados, estrategias, riesgo, brokers)
- **Backtesting**: Archivo único para configuraciones de prueba
- **Live Trading**: Archivos múltiples (APIs, monitoreo, compliance)

##### **WEB SCRAPING**:
- **Scrapy**: Seguir estándares oficiales de Scrapy
- **Selenium**: Archivo único para configuraciones de scraping
- **APIs**: Archivos múltiples por endpoint y sitio

##### **CIENCIA DE DATOS**:
- **Análisis**: Archivo único para configuraciones de análisis
- **Visualización**: Archivo único para configuraciones de gráficos
- **Modelos**: Archivos múltiples por tipo de modelo y dataset

##### **DESARROLLO MÓVIL**:
- **React Native**: Seguir estándares oficiales de React Native
- **Flutter**: Seguir estándares oficiales de Flutter
- **Nativo**: Archivos múltiples por plataforma (iOS/Android)

##### **BLOCKCHAIN**:
- **Smart Contracts**: Archivos múltiples por contrato
- **DeFi**: Archivos múltiples por protocolo
- **NFTs**: Archivo único para configuraciones de metadata

##### **MICROSERVICIOS**:
- **Por servicio**: Archivo único por microservicio
- **Orquestación**: Archivos múltiples (Docker, Kubernetes, CI/CD)

##### **CIENCIA DE DATOS**:
- **Análisis**: Archivo único para configuraciones de análisis
- **Visualización**: Archivo único para configuraciones de gráficos
- **Modelos**: Archivos múltiples por tipo de modelo

#### **5. ESTÁNDARES OFICIALES POR LENGUAJE**

##### **Python**:
- **Django**: `settings.py` (estándar oficial)
- **Flask**: `config.py` (estándar oficial)
- **FastAPI**: `settings.py` (estándar oficial)
- **PyTorch**: `configs/` (estándar oficial)
- **TensorFlow**: `configs/` (estándar oficial)

##### **JavaScript/TypeScript**:
- **React**: `config.js` (estándar oficial)
- **Vue.js**: `config.js` (estándar oficial)
- **Angular**: `config.js` (estándar oficial)
- **Node.js**: `config.js` (estándar oficial)
- **Express**: `config.js` (estándar oficial)

##### **Java**:
- **Spring Boot**: `application.yml` (estándar oficial)
- **Maven**: `pom.xml` (estándar oficial)
- **Gradle**: `build.gradle` (estándar oficial)

##### **C#**:
- **.NET**: `appsettings.json` (estándar oficial)
- **ASP.NET Core**: `appsettings.json` (estándar oficial)

##### **Go**:
- **Gin**: `config.yaml` (estándar oficial)
- **Echo**: `config.yaml` (estándar oficial)
- **Fiber**: `config.yaml` (estándar oficial)

##### **Rust**:
- **Cargo**: `Cargo.toml` (estándar oficial)
- **Actix**: `config.toml` (estándar oficial)
- **Tokio**: `config.toml` (estándar oficial)

##### **LENGUAJES DE TRADING ALGORÍTMICO**:
- **MQL4/MQL5**: `#include` y `#property` (estándar oficial)
- **Pine Script**: `@version` y `@description` (estándar oficial)
- **EasyLanguage**: `Inputs` y `Variables` (estándar oficial)
- **NinjaScript**: `using` y `namespace` (estándar oficial)

##### **LENGUAJES DE DESARROLLO DE VIDEOJUEGOS**:
- **C# (Unity)**: `using` y `namespace` (estándar oficial)
- **C++ (Unreal)**: `#include` y `#pragma` (estándar oficial)
- **GDScript (Godot)**: `extends` y `class_name` (estándar oficial)
- **Lua (Love2D)**: `require` y `local` (estándar oficial)
- **JavaScript (Phaser)**: `import` y `export` (estándar oficial)

##### **LENGUAJES DE DESARROLLO MÓVIL**:
- **Swift (iOS)**: `import` y `struct/class` (estándar oficial)
- **Kotlin (Android)**: `package` y `import` (estándar oficial)
- **Dart (Flutter)**: `import` y `class` (estándar oficial)
- **Java (Android)**: `package` y `import` (estándar oficial)
- **Objective-C (iOS)**: `#import` y `@interface` (estándar oficial)

##### **LENGUAJES DE DESARROLLO DE ESCRITORIO**:
- **C# (.NET)**: `using` y `namespace` (estándar oficial)
- **C++ (Qt)**: `#include` y `namespace` (estándar oficial)
- **Python (Tkinter)**: `import` y `class` (estándar oficial)
- **Electron**: `require` y `module.exports` (estándar oficial)
- **Rust (Tauri)**: `use` y `mod` (estándar oficial)

##### **LENGUAJES DE DESARROLLO EMBEBIDO**:
- **C/C++ (Arduino)**: `#include` y `#define` (estándar oficial)
- **Python (Raspberry Pi)**: `import` y `class` (estándar oficial)
- **JavaScript (Node.js IoT)**: `require` y `module.exports` (estándar oficial)
- **Assembly**: `section` y `global` (estándar oficial)
- **Rust (Embedded)**: `use` y `#![no_std]` (estándar oficial)

##### **LENGUAJES DE DESARROLLO DE SISTEMAS**:
- **C/C++ (OS)**: `#include` y `#define` (estándar oficial)
- **Rust (Systems)**: `use` y `#![no_std]` (estándar oficial)
- **Assembly (Low-level)**: `section` y `global` (estándar oficial)
- **Go (Services)**: `package` y `import` (estándar oficial)
- **Zig (Modern Systems)**: `const` y `pub` (estándar oficial)

##### **LENGUAJES DE DESARROLLO CIENTÍFICO**:
- **Python (NumPy/SciPy)**: `import` y `class` (estándar oficial)
- **C++ (HPC)**: `#include` y `namespace` (estándar oficial)
- **Fortran (Scientific)**: `program` y `module` (estándar oficial)
- **Julia (Scientific)**: `using` y `module` (estándar oficial)
- **R (Statistical)**: `library()` y `source()` (estándar oficial)
- **MATLAB (Scientific)**: `function` y `classdef` (estándar oficial)

#### **6. REGLAS ESPECÍFICAS PARA LENGUAJES DE TRADING ALGORÍTMICO**

##### **MQL4/MQL5 (MetaTrader)**:
```mql4
// Estructura estándar MQL4/MQL5
#property copyright "Copyright 2024"
#property link      "https://www.mql5.com"
#property version   "1.00"

// Includes
#include <Trade\Trade.mqh>

// Inputs
input double LotSize = 0.1;
input int StopLoss = 50;
input int TakeProfit = 100;

// Variables globales
CTrade trade;

// Funciones principales
int OnInit() {
    // Inicialización
    return(INIT_SUCCEEDED);
}

void OnTick() {
    // Lógica principal
}

void OnDeinit(const int reason) {
    // Limpieza
}
```

**Reglas MQL4/MQL5**:
- **Funciones concisas**: Máximo 20 líneas por función
- **Comentarios claros**: Explicar propósito de cada función
- **Estructura jerárquica**: Organizar funciones por niveles
- **Manejo de errores**: Implementar validaciones robustas
- **Optimización**: Evitar redundancias y bucles innecesarios

##### **Pine Script (TradingView)**:
```pinescript
//@version=5
indicator("Mi Estrategia", shorttitle="MS", overlay=true)

// Inputs
length = input.int(14, "Longitud RSI")
rsi_high = input.int(70, "RSI Alto")
rsi_low = input.int(30, "RSI Bajo")

// Variables
rsi = ta.rsi(close, length)

// Lógica
long_condition = rsi < rsi_low
short_condition = rsi > rsi_high

// Plot
plotshape(long_condition, "Compra", shape.triangleup, color.green)
plotshape(short_condition, "Venta", shape.triangledown, color.red)
```

**Reglas Pine Script**:
- **Simplicidad**: Mantener código claro y directo
- **Funciones incorporadas**: Usar funciones predefinidas
- **Comentarios informativos**: Explicar lógica de estrategias
- **Validación**: Probar exhaustivamente antes de usar
- **Actualización**: Mantener compatibilidad con versiones

##### **EasyLanguage (TradeStation)**:
```easylanguage
// Estructura estándar EasyLanguage
Inputs:
    Length(14),
    RSIHigh(70),
    RSILow(30);

Variables:
    RSIValue(0);

// Lógica principal
RSIValue = RSI(Close, Length);

// Condiciones
If RSIValue < RSILow Then
    Buy("Compra RSI") Next Bar at Market;

If RSIValue > RSIHigh Then
    SellShort("Venta RSI") Next Bar at Market;
```

**Reglas EasyLanguage**:
- **Planificación previa**: Diseñar estructura antes de codificar
- **Nombres descriptivos**: Usar nombres claros para variables
- **Modularidad**: Dividir en funciones reutilizables
- **Documentación**: Comentar lógica de trading
- **Testing**: Validar con backtesting antes de live

##### **NinjaScript (NinjaTrader)**:
```csharp
// Estructura estándar NinjaScript
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media;
using System.Xml.Serialization;
using NinjaTrader.Cbi;
using NinjaTrader.Gui;
using NinjaTrader.Gui.Chart;
using NinjaTrader.Gui.SuperDom;
using NinjaTrader.Gui.Tools;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
using NinjaTrader.Core.FloatingPoint;
using NinjaTrader.NinjaScript.Indicators;
using NinjaTrader.NinjaScript.DrawingTools;

namespace NinjaTrader.NinjaScript.Strategies
{
    public class MiEstrategia : Strategy
    {
        private RSI rsi;
        
        protected override void OnStateChange()
        {
            if (State == State.SetDataLoaded)
            {
                rsi = RSI(Close, 14);
            }
        }
        
        protected override void OnBarUpdate()
        {
            if (rsi[0] < 30)
                EnterLong();
            else if (rsi[0] > 70)
                EnterShort();
        }
    }
}
```

**Reglas NinjaScript**:
- **Orientación a objetos**: Usar clases y herencia
- **Gestión de estado**: Manejar correctamente OnStateChange
- **Eficiencia**: Optimizar OnBarUpdate para rendimiento
- **Manejo de datos**: Validar datos antes de procesar
- **Documentación**: Comentar estrategias y lógica

#### **7. ESTRUCTURAS DE CONFIGURACIÓN PARA TRADING**

##### **MQL4/MQL5**:
```mql4
// Configuración en archivo .mq4/.mq5
#property indicator_chart_window
#property indicator_buffers 2
#property indicator_color1 Blue
#property indicator_color2 Red

// Parámetros configurables
input int Period = 14;
input double Multiplier = 2.0;
input ENUM_TIMEFRAMES Timeframe = PERIOD_CURRENT;
```

##### **Pine Script**:
```pinescript
// Configuración en Pine Script
//@version=5
indicator("Configurable Strategy", shorttitle="CS", overlay=true)

// Inputs configurables
length = input.int(14, "Longitud", minval=1)
multiplier = input.float(2.0, "Multiplicador", minval=0.1, maxval=10.0)
timeframe = input.timeframe("", "Timeframe")
```

##### **EasyLanguage**:
```easylanguage
// Configuración en EasyLanguage
Inputs:
    Length(14),
    Multiplier(2.0),
    TimeFrame("");

Variables:
    // Variables de configuración
    ConfigValue(0);
```

##### **NinjaScript**:
```csharp
// Configuración en NinjaScript
public class MiEstrategia : Strategy
{
    [NinjaScriptProperty]
    [Range(1, int.MaxValue)]
    [Display(Name="Longitud", Description="Longitud del indicador")]
    public int Length { get; set; } = 14;
    
    [NinjaScriptProperty]
    [Range(0.1, 10.0)]
    [Display(Name="Multiplicador", Description="Multiplicador del indicador")]
    public double Multiplier { get; set; } = 2.0;
}
```

**Esta regla garantiza que cualquier proyecto tenga configuraciones organizadas, prácticas y apropiadas para su contexto específico, siguiendo estándares cuando existan y aplicando modularidad práctica cuando no los haya.**

