# Lead list — Clínicas dentales de Valencia (España)

Muestra de trabajo real de investigación de datos B2B: **10 clínicas dentales reales de la ciudad de Valencia**, construida únicamente con fuentes públicas, sin APIs de pago, sin registros y sin contactar a nadie.

- **Fecha de recogida:** 9 de septiembre de 2026
- **Archivo de datos:** `samples/lead_list_valencia_dental.csv` (UTF-8, separado por comas)
- **Filas:** 10 (cabecera + 10 registros)

## Metodología

1. **Descubrimiento.** Búsqueda web de clínicas dentales con dominio propio en Valencia ciudad. Solo se consideraron negocios con página de contacto publicada en su propio dominio (se descartaron agregadores y fichas de terceros como fuente primaria).
2. **Verificación página por página.** Para cada clínica se descargó la página de contacto (o la home, si el contacto está allí) y se extrajeron los datos directamente del HTML:
   - Emails: enlaces `mailto:` y texto visible.
   - Teléfonos: enlaces `tel:` y texto visible.
   - Nombre oficial: `<title>` / `og:site_name` del propio sitio.
3. **Emails ofuscados.** Tres sitios (BonDent, Aliaga y otros con Cloudflare) no publican el email en texto plano: lo codifican con la protección anti-scraping de Cloudflare (`data-cfemail` / `/cdn-cgi/l/email-protection#`). Se decodificó el payload hexadecimal (XOR con el primer byte, el algoritmo público estándar de Cloudflare) y **el email solo se incluyó si la decodificación dio una dirección coherente y el sitio confirma el dominio**. Ejemplo verificado: BonDent → `clinica.bondent@gmail.com`.
4. **Regla anti-invención.** Ningún campo se rellenó por inferencia. Si un dato no aparecía en la fuente, se dejó vacío (`""`). No se construyeron emails por patrón (p. ej. deducir `info@dominio` sin verlo publicado).
5. **Trazabilidad.** La columna `fuente` contiene la URL exacta de la página de la que se extrajo cada fila. Todo registro es reproducible visitando esa URL.
6. **Sustitución por fallo de carga.** Si un sitio no cargaba, la clínica se sustituía por otra. Caso real: `bogardental.com` tiene el certificado TLS caducado para clientes estrictos; se comprobó que el contenido servido es legítimo (la página incluye `mailto:clinica@bogardental.com` y teléfonos enlazados) y se documenta aquí como limitación.

## Qué campos son verificados vs. no verificados

| Campo | Estado | Evidencia |
|---|---|---|
| `nombre` | **Verificado** | Tomado del `<title>` o `og:site_name` del sitio oficial. |
| `web` | **Verificado** | Dominio que sirvió la página de contacto (HTTP 200 al descargarla, salvo Bogar: ver limitación 1). |
| `email` | **Verificado en fuente** para las 10 filas: aparece literalmente en la página citada (`mailto:`, texto plano o decodificación Cloudflare del propio HTML). | No se envió ningún email de prueba: verificado = *publicado en la fuente*, no = *buzón activo*. |
| `telefono` | **Verificado en fuente**: aparece en la página citada (enlace `tel:` o texto de contacto). | No se llamó a ningún número: verificado = *publicado*, no = *en servicio*. |
| `fuente` | **Verificado**: URL real visitada y con los datos extraídos de ella. | — |

Ninguna fila contiene datos de memoria, de agregadores sin confirmar o inventados.

## Los 10 registros

| # | Clínica | Fuente consultada |
|---|---|---|
| 1 | Valencia Dental | valenciadental.es/contact/ |
| 2 | Badía Clínica Dental | teresabadia.com/contacto/ |
| 3 | Clínica Doctor Moreno (sede Valencia) | clinicadoctormoreno.com/contacto/ |
| 4 | Clínica Dental BonDent | clinicadentalvalenciabondent.com/contacto/ |
| 5 | Bogar Dental | bogardental.com/ |
| 6 | Clínica Dentados | clinicadentados.es/contacto/ |
| 7 | Clínica Oral Dental | clinicaoraldental.com/contacto/ |
| 8 | Clínica Dental Ciudad de las Ciencias | clinicadentalcciencias.es/contacto/ |
| 9 | Clínica Aliaga | clinicaaliaga.com/contacto/ |
| 10 | Santamarta Roig Dental | santamartaroigdental.com/contacto-clinica-dental-en-valencia/ |

Nota: Clínica Doctor Moreno tiene dos sedes (Valencia y Cullera). La fila usa exclusivamente los datos de la **sede de Valencia** (Avda. Blasco Ibáñez, 94), que es la que corresponde al ámbito geográfico de la lista.

## Limitaciones honestas

1. **El certificado TLS de bogardental.com está caducado.** Los clientes HTTP estrictos rechazan la conexión; los datos se extrajeron del contenido servido por el sitio, que es coherente y legítimo, pero cualquier automatización que consuma esta lista debe saber que ese dominio falla la validación estándar de certificado. Un comprador real debería verificarlo por teléfono antes de campañas.
2. **"Verificado en fuente" no es "dato activo".** Los emails y teléfonos están publicados por las propias clínicas en la fecha indicada, pero no se enviaron emails ni se hicieron llamadas de prueba (el encargo prohíbe contactar a nadie). Un buzón publicado puede estar derivado, lleno o abandonado; la deliverabilidad real es desconocida.
3. **Los datos publicados caducan y la web es una foto del momento.** La muestra refleja lo que los sitios publicaban el 9 de septiembre de 2026. Clínicas que cambian de gestor, de dominio o cierran dejarán la fila obsoleta sin aviso. Además, la búsqueda inicial sesgó la lista hacia clínicas con buena presencia web: negocios sin página de contacto pública (o solo con ficha en Google Maps/directorios) quedaron sistemáticamente fuera, por lo que la lista **no** es un censo exhaustivo del sector dental en Valencia.

## Nota de privacidad (2026-09-09)
- Emails redactados en el CSV publicado: los buzones en dominios de correo personal (gmail) y los buzones nominativos (nombre de persona) se sustituyen por "[email en <web oficial> — redactado]". Se conserva la fuente para verificación.
- Solo se publican buzones funcionales del dominio propio del negocio (info@, clinica@, recepcion@...): datos de contacto EMPRESARIALES públicos.
- El dominio teresabadia.com es el dominio oficial de la propia clínica (marca del negocio), no un dato personal de particular; se conserva por trazabilidad.
- Teléfonos: líneas de la clínica, no personales.
