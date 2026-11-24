# Proyecto de criptografía RSA

**Curso:** Matemática Discreta
**Autores:** [Franco Paiz, Oscar Melchor] 
**Carnets:**  [25780, 25216]
**Lenguaje:** Python 3.10 o superior  
**Interfaces:** escritorio con tkinter y ttk; web con Streamlit

## Video demostrativo del proyecto

**Enlace al video:** [Ver demostración del proyecto RSA](https://youtu.be/tcLVibDLlmE)
## 1. Descripción

Este proyecto implementa un sistema educativo de encriptación y desencriptación RSA con interfaz gráfica. El programa recibe un mensaje de texto y parámetros RSA, transforma el mensaje en bloques numéricos y calcula el cifrado mediante aritmética modular. También realiza el proceso inverso para recuperar exactamente el texto original, incluidos sus espacios.

La aplicación está dividida en un **backend**, responsable de las operaciones matemáticas y las validaciones, y un **frontend** desarrollado con `tkinter` y `ttk`, que permite ingresar los datos y consultar los resultados. La interfaz permite cambiar entre las operaciones, consultar los parámetros calculados y revisar el detalle de cada bloque. La tabla de detalles muestra la conversión ASCII y los bloques antes y después de la transformación RSA.

También incluye una interfaz web con **Streamlit**, que utiliza las mismas funciones del backend y ha sido publicada en **Streamlit Community Cloud:** [Ver despliegue del proyecto](https://encriptadorrsa-oc3rz9cszbsakskc5jwh7z.streamlit.app/). Ambas interfaces se encuentran en `frontend/` y tienen puntos de entrada independientes.

Esta implementación tiene fines académicos y **no debe utilizarse para proteger información real**: trabaja con módulos pequeños y un esquema de representación fijo, el cual es fácil de verificar

## 2. Requisitos e instalación

- Escritorio: Python **3.10 o superior** con soporte para `tkinter`, sin paquetes externos.
- Web: Python **3.11 o superior** (se recomienda **3.12**) e instalar las dependencias de `requirements.txt`.

Descargar o copiar la carpeta `proyecto_rsa` y abrir una terminal dentro de ella. Para comprobar la versión de Python:

```bash
python --version
```

Para comprobar que `tkinter` está disponible:

```bash
python -m tkinter
```

En algunos sistemas Linux es necesario instalar el paquete de soporte de Tk mediante el administrador de paquetes del sistema. No es una dependencia que deba instalarse mediante `pip`.

## 3. Ejecución

### Escritorio

Desde la raíz del proyecto:

```bash
python main.py
```

Se abrirá la aplicación **RSA Studio**, con dos secciones de navegación: **Encriptar** y **Desencriptar**. El contenido dispone de desplazamiento vertical cuando la ventana no tiene espacio suficiente. Si el comando `python` no está disponible, puede ser necesario utilizar `python3` según el sistema operativo.

### Web local

Desde la raíz del proyecto, instalar las dependencias e iniciar Streamlit:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app_streamlit.py
```

Abrir la dirección local que indique la terminal (normalmente `http://localhost:8501`). Para detener el servidor, presionar **Ctrl+C**. En Windows, si Python está instalado mediante el lanzador `py`, se puede sustituir `python` por `py` en estos comandos.

Opcionalmente, crear primero un entorno virtual con `python -m venv .venv`. En PowerShell se puede usar directamente `.\.venv\Scripts\python.exe` en lugar de `python`, sin activar el entorno.

Si Python se queda detenido al importar archivos en una carpeta sincronizada con OneDrive, se puede probar con una caché nueva dentro del entorno virtual, sin modificar el backend:

```powershell
.\.venv\Scripts\python.exe -X pycache_prefix=.venv/qa-cache -m streamlit run app_streamlit.py
```

## 4. Uso de la aplicación

### 4.1. Encriptación

1. Abrir la pestaña **Encriptar**.
2. Ingresar los números primos distintos `p` y `q`, así como el exponente público `e`.
3. Escribir el mensaje original **M**. Se admiten los caracteres ASCII imprimibles (códigos del 32 al 126), incluidos espacios, números y signos. No se admiten tildes, `ñ`, tabulaciones ni saltos de línea.
4. Presionar **Encriptar mensaje**.
5. Consultar el cifrado **C** en la tarjeta **Resultado · Cifrado C** y la longitud original **L** en el indicador **LONGITUD L** del resumen. Los botones **COPIAR RESULTADO** y **COPIAR L** permiten copiarlos por separado, sin modificar ceros ni espacios. Consultar también la llave pública `(e, n)`, los valores `n` y `φ`, el MCD y la información del relleno. La tabla presenta las parejas de caracteres, sus códigos ASCII y los bloques `m` y `c`.

**Importante:** guardar **C y L por separado**. La longitud original no se encuentra dentro de los bloques cifrados.

### 4.2. Desencriptación

1. Abrir la pestaña **Desencriptar**.
2. Ingresar los mismos valores `p`, `q` y `e` utilizados al encriptar.
3. Copiar **C** en el campo de cifrado, respetando sus bloques de seis dígitos y los espacios que los separan.
4. Escribir **L** en el campo **Longitud original L**.
5. Presionar **Desencriptar mensaje**.
6. Consultar el mensaje recuperado **M** en la tarjeta de resultado, el exponente privado `d` y la llave privada `(d, n)` en el resumen matemático, y el detalle de los bloques recuperados. El botón **COPIAR RESULTADO** conserva exactamente los caracteres originales.

El programa calcula `n` a partir de `p` y `q`; no necesita factorizar `n`.

## 5. Representación del texto y relleno

Cada carácter se convierte a su código ASCII con **tres dígitos**, conservando los ceros iniciales. Dos caracteres forman un bloque de seis dígitos: por ejemplo, `AB` corresponde a `065066` (valor numérico `65066`).

La longitud **L** se registra **antes** de añadir relleno e incluye todos los espacios originales. Si L es impar, se agrega exactamente **un espacio** (`032`) al final para completar la última pareja. Si L es par, no se agrega nada.

Durante la desencriptación, si L es impar, el programa comprueba que el último carácter recuperado sea un espacio y elimina **solo ese carácter de relleno**. Si L es par, no elimina ninguno. Por ello, los espacios originales al inicio o al final del mensaje se conservan; no se utiliza una eliminación general de espacios como `strip()`.

## 6. Ejemplo completo del enunciado

**Datos de entrada:**

```text
M = RSA
p = 367
q = 373
e = 17
```

**Cálculos y resultados esperados:**

```text
n = p*q = 136891
φ = (p-1)*(q-1) = 136152
MCD(e, φ) = 1
L = 3
Mensaje con relleno = "RSA "
Bloques originales = 082083 065032
C = 026054 123875
Llave pública = (17, 136891)
```

Para recuperar el mensaje, abrir **Desencriptar** e introducir `p = 367`, `q = 373`, `e = 17`, `C = 026054 123875` y `L = 3`.

**Resultado esperado:**

```text
d = 8009
Llave privada = (8009, 136891)
Mensaje recuperado = RSA
```

El primer bloque cifrado `026054` conserva el cero inicial. El espacio agregado después de `RSA` se elimina al recuperar el mensaje porque L es impar.

## 7. Condiciones matemáticas y algoritmos

Se comprueba que `p` y `q` sean enteros, primos y distintos. Después se calculan:

```text
n = p*q
φ = (p-1)*(q-1)
```

Las condiciones del proyecto son `126126 < n < 1000000`, `e > 1` y `MCD(e, φ) = 1`. Se admite cualquier entero `e` que las satisfaga, incluso si es mayor que `φ`.

La encriptación utiliza `c = m^e mod n`. La desencriptación calcula primero el inverso modular `d` de `e` módulo `φ`, de modo que `e*d ≡ 1 (mod φ)` y `1 <= d < φ`, y recupera cada bloque con `m = c^d mod n`.

| Archivo | Función principal | Implementación |
| --- | --- | --- |
| `backend/primalidad.py` | `es_primo` | División por tentativa hasta la raíz cuadrada entera (`math.isqrt`). |
| `backend/mcd.py` | `calcular_mcd` | Algoritmo de Euclides iterativo. |
| `backend/inverso_modular.py` | `calcular_inverso_modular` | Algoritmo extendido de Euclides. |
| `backend/exponenciacion.py` | `potencia_modular` | Cuadrados sucesivos, con división entera `//` y reducción modular en cada paso. |
| `backend/validaciones.py` | Funciones `validar_*` | Comprobación de tipos, caracteres, formato de C y longitud L. |
| `backend/rsa.py` | `calcular_parametros`, `encriptar`, `desencriptar` | Coordinación de las operaciones RSA y conversión de bloques. |

El backend **no utiliza** `math.gcd`, `pow` con módulo, `pow` para inversos ni bibliotecas criptográficas para sustituir estos algoritmos. Las funciones estándar `math.gcd` y `pow` aparecen únicamente en las pruebas como referencias independientes.

## 8. Validaciones y manejo de errores

El programa rechaza parámetros RSA incorrectos (tipos no enteros, primos repetidos o compuestos, módulo fuera del rango y exponentes no coprimos con `φ`). También rechaza mensajes vacíos o con caracteres fuera de ASCII 32–126.

En la desencriptación, **C** debe contener uno o más bloques de exactamente seis dígitos decimales, separados por un solo espacio, con `0 <= c < n`. Si hay `k` bloques, **L** debe ser `2k` o `2k-1`. Además, cada bloque recuperado debe producir dos códigos ASCII válidos; si L es impar, el último carácter debe ser un espacio.

Ante un dato inválido, la interfaz muestra un mensaje explicativo, marca la operación como pendiente de corrección y limpia los resultados anteriores para evitar presentar una salida incorrecta como válida. Los botones pueden utilizarse también con Tab y Enter o Espacio.

## 9. Pruebas y comprobaciones

Desde la raíz del proyecto, ejecutar:

```bash
python -m pruebas.test_backend
```

El archivo `pruebas/test_backend.py` contiene pruebas con `assert` organizadas en ocho grupos: primalidad, MCD, inverso modular, exponenciación modular, ejemplo oficial, mensajes válidos, validaciones y descifrado inválido.

Las comprobaciones cubren mensajes de longitud par e impar, mayúsculas, minúsculas, números, signos, espacios consecutivos y espacios originales al inicio o al final. También incluyen ceros iniciales del cifrado, exponentes públicos mayores que `φ` y rechazo de entradas incorrectas.

Las implementaciones propias de MCD, inverso modular y exponenciación modular se contrastan con `math.gcd` y `pow` **solo dentro del archivo de pruebas**. El ejemplo oficial se verifica con los resultados `C = 026054 123875`, `L = 3`, `d = 8009` y el mensaje recuperado `RSA`.

**Comprobación de entrega:** ejecutar las pruebas desde la raíz del proyecto y revisar ambas operaciones en la interfaz, incluido el manejo de entradas inválidas.

## 10. Estructura del proyecto

```text
proyecto_rsa/
├── app_streamlit.py
├── .streamlit/
│   └── config.toml
├── main.py
├── backend/
│   ├── __init__.py
│   ├── validaciones.py
│   ├── primalidad.py
│   ├── mcd.py
│   ├── inverso_modular.py
│   ├── exponenciacion.py
│   ├── modelos.py
│   └── rsa.py
├── frontend/
│   ├── __init__.py
│   ├── interfaz.py
│   ├── interfaz_streamlit.py
│   └── estilos_streamlit.css
├── pruebas/
│   ├── __init__.py
│   ├── test_backend.py
│   └── test_streamlit.py
├── README.md
└── requirements.txt
```

`main.py` inicia la aplicación. `backend/` contiene las operaciones y los modelos de resultados; `frontend/interfaz.py` define la clase `AplicacionRSA`; y `pruebas/` contiene las comprobaciones automáticas.

## 11. Alcance

El proyecto reproduce el procedimiento RSA requerido y prioriza que los cálculos puedan revisarse y explicarse. No implementa generación automática de claves, protocolos de comunicación ni mecanismos de seguridad para uso real.

## 12. Interfaz y portapapeles

La interfaz utiliza los colores: Prussian Blue (`#0A1128`) como fondo, Deep Navy (`#001F54`) en tarjetas, Yale Blue (`#034078`) en campos y encabezados, Cerulean (`#1282A2`) en acciones, y White (`#FEFCFB`) en textos principales. Los resultados se muestran en tarjetas de solo lectura; el copiado utiliza el portapapeles de Tkinter y no recorta espacios ni modifica los ceros iniciales.

Los cálculos RSA se encuentran en `backend/` y la presentación en `frontend/`. La interfaz de escritorio no se ha modificado para añadir la web. `requirements.txt` declara Streamlit para la nueva interfaz; `.streamlit/config.toml` y `frontend/estilos_streamlit.css` adaptan la paleta y las tarjetas al navegador.


### Límites de la interfaz web

Para mantener acotado el trabajo en el servidor compartido, la web admite hasta **2000 caracteres de mensaje**, **6999 caracteres de cifrado** (1000 bloques), **32 caracteres por parámetro** y cuatro caracteres para L. Comprueba que p y q estén entre 2 y 999999 antes de llamar al backend. Estos límites se aplican solo en la presentación web; los algoritmos y las reglas matemáticas del backend permanecen intactos. Se sigue permitiendo e mayor que φ dentro del límite de entrada web.

### Comprobaciones de la interfaz web

Después de instalar las dependencias:

```bash
python -m pruebas.test_backend
python -m unittest pruebas.test_streamlit
```

Las pruebas web comprueban el ejemplo oficial, recuperación exacta de espacios, limpieza de resultados ante errores, límites web y aislamiento de sesiones.


## DISCLAIMER

La realización de este proyecto fue asistida con IA, como apoyo en la estructura del proyecto y selección de tecnologías para
la implementación de la interfaz
