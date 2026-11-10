# Admin del Core de Reservas Deportivas

El módulo administrativo configura los datos que usa el sistema de reservas de canchas deportivas. Desde `/admin/` se registran los complejos y sus canchas, se definen los horarios de atención y los precios por hora, y se bloquean intervalos por mantenimiento u otros motivos. El core usa esos datos para consultar disponibilidad, calcular cotizaciones y confirmar reservas.

## Qué se administra

| Sección | Función en el sistema |
| --- | --- |
| Complejos y canchas | Definen dónde se puede reservar, qué deporte se practica y qué instalaciones están activas. Las canchas también se pueden gestionar desde el formulario del complejo. |
| Horarios de atención | Establecen los intervalos de apertura y cierre de cada cancha por día de la semana. |
| Tarifas | Definen el valor por hora de una cancha en un día y una franja. El servicio de cotización usa las tarifas activas. |
| Bloqueos | Excluyen intervalos de la disponibilidad cuando están activos. Cada bloqueo registra un motivo y un usuario asociado. |
| Usuarios | Gestionan cuentas, datos de contacto, roles y permisos de Django. |
| Reservas | Permiten consultar las reservas por cliente, cancha, complejo o estado. El panel ofrece acceso de solo lectura. |

## Administración MVC con Django

El proyecto usa Django con PostgreSQL y sigue la organización Modelo–Vista–Plantilla (MTV) de Django. Los modelos representan los datos y sus reglas. Las plantillas del admin presentan formularios y listados. Django procesa las solicitudes mediante sus vistas administrativas, que se personalizan con clases `ModelAdmin` y formularios `ModelForm`.

- [`backend/complejos/`](backend/complejos/) gestiona complejos, canchas, horarios, tarifas y bloqueos.
- [`backend/cuentas/`](backend/cuentas/) define el usuario personalizado y los validadores de cédula y teléfono.
- [`backend/reservas/`](backend/reservas/) contiene el modelo de reservas y los servicios de disponibilidad, cotización y confirmación, expuestos por la API bajo `/api/`.
- [`backend/config/urls.py`](backend/config/urls.py) conecta las rutas del panel y de la API.

## Validación de datos en el servidor

La **cédula ecuatoriana** es un dato sensible de la cuenta. Al guardar un usuario desde el panel, Django ejecuta el validador de `Usuario.cedula` si se ingresó un valor. La función `validar_cedula` comprueba que haya diez dígitos, valida el código de provincia y el tercer dígito, y calcula el dígito verificador. Si falla una comprobación, el formulario muestra el error y no guarda el cambio. El modelo también exige que la cédula sea única cuando se registra. [Modelo de usuario](backend/cuentas/models.py) · [Validador](backend/cuentas/validators.py)

El precio por hora también se valida en el servidor. Una tarifa debe tener un valor positivo y un inicio anterior al fin. Si está activa, `Tarifa.clean()` rechaza una franja que se superponga con otra tarifa activa de la misma cancha y día. [Modelo de tarifa](backend/complejos/models.py)

## Selección de registros relacionados

En el panel, la cancha se asocia a un complejo mediante un selector con autocompletado. Los formularios de horarios y bloqueos también usan autocompletado para elegir la cancha, y el bloqueo ofrece un selector para el usuario asociado. Estos controles muestran registros existentes y guardan su clave foránea. [Configuración del admin](backend/complejos/admin.py)

El formulario de tarifas tiene dos selectores, **Complejo deportivo** y **Cancha**. Al elegir el complejo, JavaScript consulta `/admin/complejos/tarifa/canchas-por-complejo/?complejo_id=<id>` para actualizar la lista de canchas. La vista devuelve las canchas de ese complejo y requiere permiso para agregar o editar tarifas. [Formulario](backend/complejos/forms.py) · [Vista del admin](backend/complejos/admin.py) · [JavaScript](backend/complejos/static/complejos/js/tarifa.js)

Al editar una tarifa, el panel muestra el complejo actual y sus canchas. Al guardar, Django valida la cancha contra las opciones del complejo seleccionado y rechaza una cancha de otro complejo.

## Ejecutar en local

Se necesita Python y una base de datos PostgreSQL creada, con un usuario que pueda aplicar las migraciones. Desde la raíz del repositorio, ejecutar en PowerShell:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

Crear `backend/.env` con los datos de la base local. Sustituir los valores de ejemplo por los propios.

```dotenv
DB_NAME=reservas_deportivas
DB_USER=usuario_local
DB_PASSWORD=contraseña_local
DB_HOST=localhost
DB_PORT=5432
```

Desde `backend/`, aplicar las migraciones, crear el superusuario y levantar el servidor de desarrollo:

```powershell
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py createsuperuser
.\venv\Scripts\python.exe manage.py runserver
```

Entrar a [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) con el superusuario creado.

## Despliegue de la demo en Render

El archivo [`render.yaml`](render.yaml) define un servicio web Django y una base PostgreSQL en el plan gratuito. Render aplica las migraciones, recopila los archivos estáticos y carga [los datos ficticios](backend/datos_demo.sql) durante la compilación. Esto incluye dos complejos, cuatro canchas y sus horarios y tarifas. Para omitir la carga en futuros despliegues, cambia `LOAD_DEMO_DATA` a `0` en el Blueprint.

1. En el [panel de Render](https://dashboard.render.com/), elige **New → Blueprint** y conecta el repositorio de GitHub.
2. Selecciona la rama que contiene `render.yaml`. En el formulario de Render, ingresa `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL` y una contraseña propia en `DJANGO_SUPERUSER_PASSWORD`. Estas variables crean el usuario en el primer despliegue y puedes quitarlas del entorno después de comprobar que inicia sesión.
3. Cuando termine el despliegue, agrega `/admin/` a la URL del servicio e inicia sesión. En **Tarifas → Agregar**, cambia entre **Demo Norte** y **Demo Sur** para comprobar el filtro de canchas.

La base PostgreSQL del plan gratuito expira a los 30 días. [Límites del plan gratuito de Render](https://render.com/docs/free)

## Comprobación manual en el panel

1. En **Usuarios**, intentar guardar un usuario con una cédula como `123`. El formulario debe indicar que se requieren diez dígitos.
2. Crear un complejo y luego una cancha. En el formulario de cancha, buscar el complejo por nombre y seleccionarlo en el autocompletado.
3. Crear un horario para la cancha e intentar guardar otro con una franja que se superponga para el mismo día. El formulario debe rechazarlo.
4. En **Tarifas**, intentar guardar un valor por hora de `0`. El formulario debe rechazarlo.
5. Crear dos complejos con una cancha cada uno. En **Tarifas**, cambiar de complejo y comprobar que el selector solo muestra las canchas del complejo elegido.
