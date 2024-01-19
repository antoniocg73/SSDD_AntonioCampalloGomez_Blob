# IceDrive Authentication service template

This repository contains the project template for the Blob service proposed as laboratory work for the students
of Distributed Systems in the course 2023-2024.

## Updating `pyproject.toml`

One of the first things that you need to setup when you clone this branch is to take a look into
`pyproject.toml` file and update the needed values:

- Project authors
- Project dependencies
- Projects URL humepage

# Documentación Entrega 2 - Antonio Campallo Gómez
## ACLARACIÓN IMPORTANTE
- En la revisión de la entrega 1 se me recomendó para que al profesor le funcione editar una cosa del código, pero de esa forma a mi no me funciona. Por ende, solo cambié el os.rename por el shutil.move. 
## Parte realizada
- Solamente he hecho hasta anunciarme cada 5 segundos. las querys no me ha dado tiempo.
## Ejecución
- Para ejecutar poner "./run_icestorm" y cuando esto se haga, dentro del proyecto en general, escribir "icedrive-blob".

# Documentación BlobService - Antonio Campallo Gómez
## Indicación previa
Al principio todo lo ejecutaba en windows pero el upload me daba un error "WinError", por lo que me tuve que cambiar a Linux.
## Edición de blob/config y pyproject.toml
 - Edité el blob.config de forma que el "BlobAdapter" se conecte al puerto 2000 y el nombre del directorio sea "pruebas". Esto lo hago debido a que quiero que los archivos se guarden en la carpeta "pruebas" del proyecto.
 - Luego, dentro del pyproject.toml cambié las cosas como el nombre, el correo y eso y además, añadí que para invocar al cliente se tenga que escribir por terminal después de inicializar el servidor esto: "icedrive-client". Esto llama a mi clase cliente.

## Clase BlobApp, el servidor
Le añado al directory el directorio del blob.config, el de pruebas y en el return del main he añadido aparte del "sys.argv" otro parámetro que es la configuración ("config/blob.config").

## Clase BlobService, la gestión de los blobs y Clase DataTransfer
- Primero lo hice sin implementar Ice, y a partir de ahí, hice las pruebas necesarias para poder comprobar que me funcionaba todo en local. 
- Una vez hecho esto, le añadí Ice sabiendo que funcionaba.
Añadí dos métodos, "escribirEnJson" y "leerDeJson". Estos métodos me ayudan a atualizar todo lo que tiene que ver con el número de enlaces de los blobs sin problema de que se borre el contenido después de finalizar la ejecución.
- A la clase DataTransfer le añadí un init, completé sus métodos y en close su respectiva gestión de Ice.

## Tests unitarios y main.py
- Dentro de la carpeta tests tengo mi archivo de pruebas llamado testUnitario.py.
Los test realizados son sin haber aplicado Ice, por lo tanto habria que cambiar todo lo de Ice añadido en Blob para poder probarlo y que, como yo he podido observar durante mis pruebas, funciona.
- Al empezar, hice antes de los tests unitarios una clase main donde iba probando, no la he borrado por dejar constancia de mis primeras pruebas.

## Clase ClientApp y DataTransferClient
- La clase ClientApp es el cliente interactivo que me cree para poder probar que funcionaba todo implementando Ice. 
- La clase DataTransferClient es una copia del de la clase BlobService.

## Pasos para ejecutar
1. pip install -e . en el caso de que no se tenga la aplicación instalada.
2. Arrancamos el servidor con "icedrive-blob".
3. Arrancamos en otra terminal el cliente con "icedrive-client".
