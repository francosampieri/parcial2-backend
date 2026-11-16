(function () {
  "use strict";

  window.ElTintero = window.ElTintero || {};

  const ROLES = ["autor", "coautor", "traductor", "ilustrador"];

  let autoresSeleccionados = [];
  let clientesSesion = [];

  function elemento(id) {
    return document.getElementById(id);
  }

  function crearCelda(texto) {
    const celda = document.createElement("td");
    celda.textContent = texto;
    return celda;
  }

  function crearOpcion(valor, texto) {
    const opcion = document.createElement("option");
    opcion.value = valor;
    opcion.textContent = texto;
    return opcion;
  }

  function vaciar(nodo) {
    while (nodo.firstChild) {
      nodo.removeChild(nodo.firstChild);
    }
  }

  function mostrar(id, texto) {
    const nodo = elemento(id);
    if (nodo) {
      nodo.textContent = texto;
      nodo.hidden = false;
    }
  }

  function ocultar(id) {
    const nodo = elemento(id);
    if (nodo) {
      nodo.textContent = "";
      nodo.hidden = true;
    }
  }

  function mostrarErrorLibros(texto) {
    ocultar("libros-mensaje-ok");
    mostrar("libros-mensaje-error", texto);
  }

  function mostrarOkLibros(texto) {
    ocultar("libros-mensaje-error");
    mostrar("libros-mensaje-ok", texto);
  }

  function mostrarErrorClientes(texto) {
    ocultar("clientes-mensaje-ok");
    mostrar("clientes-mensaje-error", texto);
  }

  function mostrarOkClientes(texto) {
    ocultar("clientes-mensaje-error");
    mostrar("clientes-mensaje-ok", texto);
  }

  async function cargarSelectores() {
    try {
      const resultados = await Promise.all([
        ElTintero.api.listarEditoriales(),
        ElTintero.api.listarGeneros()
      ]);
      const editoriales = resultados[0];
      const generos = resultados[1];

      const selectorEditorial = elemento("libros-editorial");
      const selectorGenero = elemento("libros-genero");
      if (selectorEditorial) {
        vaciar(selectorEditorial);
        selectorEditorial.appendChild(crearOpcion("", "Seleccionar editorial"));
        editoriales.forEach(function (editorial) {
          selectorEditorial.appendChild(crearOpcion(String(editorial.id), editorial.nombre));
        });
      }
      if (selectorGenero) {
        vaciar(selectorGenero);
        selectorGenero.appendChild(crearOpcion("", "Sin clasificar"));
        generos.forEach(function (genero) {
          selectorGenero.appendChild(crearOpcion(String(genero.id), genero.nombre));
        });
      }
    } catch (error) {
      mostrar("libros-error", "No se pudieron cargar editoriales y géneros: " + error.message);
    }
  }

  function crearBotonDetalle(libro) {
    const boton = document.createElement("button");
    boton.type = "button";
    boton.className = "btn btn--secundario";
    boton.textContent = "Ver autores";
    boton.addEventListener("click", function () {
      verDetalleLibro(libro.id);
    });
    return boton;
  }

  function renderizarLibros(libros) {
    const tabla = elemento("libros-tabla");
    if (!tabla) {
      return;
    }
    const tbody = tabla.querySelector("tbody");
    vaciar(tbody);

    libros.forEach(function (libro) {
      const fila = document.createElement("tr");
      fila.appendChild(crearCelda(libro.titulo));
      fila.appendChild(crearCelda(libro.isbn));
      fila.appendChild(crearCelda(libro.editorialNombre || "Editorial no disponible"));
      fila.appendChild(crearCelda(libro.generoNombre || "Sin clasificar"));
      fila.appendChild(crearCelda(ElTintero.formato.formatearPrecio(libro.precio)));
      fila.appendChild(crearCelda(String(libro.stock)));

      const celdaDetalle = document.createElement("td");
      celdaDetalle.appendChild(crearBotonDetalle(libro));
      fila.appendChild(celdaDetalle);
      tbody.appendChild(fila);
    });

    if (libros.length === 0) {
      mostrar("libros-vacio", "No hay libros registrados.");
    } else {
      ocultar("libros-vacio");
    }
  }

  async function cargarLibros() {
    if (!elemento("libros-tabla")) {
      return;
    }
    mostrar("libros-cargando", "Cargando libros…");
    ocultar("libros-error");
    try {
      const libros = await ElTintero.api.listarLibros({ limit: 100, offset: 0 });
      renderizarLibros(libros);
    } catch (error) {
      mostrar("libros-error", error.message);
    } finally {
      ocultar("libros-cargando");
    }
  }

  async function verDetalleLibro(id) {
    const contenedor = elemento("libros-detalle");
    if (!contenedor) {
      return;
    }
    contenedor.hidden = false;
    contenedor.textContent = "Cargando detalle…";
    try {
      const libro = await ElTintero.api.obtenerLibro(id);
      contenedor.textContent = "";

      const titulo = document.createElement("h3");
      titulo.textContent = libro.titulo;
      contenedor.appendChild(titulo);
      contenedor.appendChild(document.createTextNode("ISBN: " + libro.isbn));
      contenedor.appendChild(document.createElement("br"));
      contenedor.appendChild(document.createTextNode("Stock: " + libro.stock));

      const subtitulo = document.createElement("h4");
      subtitulo.textContent = "Autores";
      contenedor.appendChild(subtitulo);

      if (libro.autores.length === 0) {
        contenedor.appendChild(document.createTextNode("Sin autores registrados."));
      } else {
        const lista = document.createElement("ul");
        lista.className = "autorias-lista";
        libro.autores
          .slice()
          .sort(function (a, b) { return a.orden - b.orden; })
          .forEach(function (autoria) {
            const item = document.createElement("li");
            item.textContent = autoria.nombre + " — " + autoria.rol + " (orden " + autoria.orden + ")";
            lista.appendChild(item);
          });
        contenedor.appendChild(lista);
      }
    } catch (error) {
      contenedor.textContent = error.message;
    }
  }

  function renderizarAutores() {
    const contenedor = elemento("libros-autores-lista");
    if (!contenedor) {
      return;
    }
    vaciar(contenedor);

    if (autoresSeleccionados.length === 0) {
      contenedor.appendChild(document.createTextNode("Sin autorías agregadas."));
      return;
    }

    autoresSeleccionados.forEach(function (autoria, indice) {
      const fila = document.createElement("div");
      fila.className = "autoria-item";
      const texto = document.createElement("span");
      texto.textContent = autoria.nombre + " — " + autoria.rol + " (orden " + autoria.orden + ")";
      fila.appendChild(texto);

      const quitar = document.createElement("button");
      quitar.type = "button";
      quitar.className = "btn btn--peligro";
      quitar.textContent = "Quitar";
      quitar.addEventListener("click", function () {
        autoresSeleccionados.splice(indice, 1);
        renderizarAutores();
      });
      fila.appendChild(quitar);
      contenedor.appendChild(fila);
    });
  }

  async function agregarAutoria() {
    const campoId = elemento("libros-autor-id");
    const campoRol = elemento("libros-autor-rol");
    const campoOrden = elemento("libros-autor-orden");
    const id = Number(campoId.value);
    const rol = campoRol.value;
    const orden = Number(campoOrden.value);

    if (!Number.isInteger(id) || id <= 0) {
      mostrarErrorLibros("Ingresá un ID de autor válido.");
      return;
    }
    if (!ROLES.includes(rol)) {
      mostrarErrorLibros("Seleccioná un rol válido.");
      return;
    }
    if (!Number.isInteger(orden) || orden <= 0) {
      mostrarErrorLibros("El orden debe ser un entero mayor que cero.");
      return;
    }
    if (autoresSeleccionados.some(function (autoria) { return autoria.autor_id === id; })) {
      mostrarErrorLibros("Ese autor ya está agregado.");
      return;
    }

    try {
      const autor = await ElTintero.api.obtenerAutor(id);
      autoresSeleccionados.push({
        autor_id: autor.id,
        nombre: autor.nombre,
        rol: rol,
        orden: orden
      });
      campoId.value = "";
      ocultar("libros-mensaje-error");
      renderizarAutores();
    } catch (error) {
      mostrarErrorLibros("No se pudo validar el autor: " + error.message);
    }
  }

  function leerDatosLibro() {
    const titulo = ElTintero.formato.recortarTexto(elemento("libros-titulo").value);
    const isbn = ElTintero.formato.recortarTexto(elemento("libros-isbn").value);
    const precio = Number(elemento("libros-precio").value);
    const stock = Number(elemento("libros-stock").value);
    const editorialId = Number(elemento("libros-editorial").value);
    const generoValor = elemento("libros-genero").value;
    const errores = [];

    if (titulo === "") {
      errores.push("Ingresá el título.");
    }
    if (isbn === "") {
      errores.push("Ingresá el ISBN.");
    }
    if (!Number.isFinite(precio) || precio <= 0) {
      errores.push("El precio debe ser mayor que cero.");
    }
    if (!Number.isInteger(stock) || stock < 0) {
      errores.push("El stock debe ser un entero mayor o igual que cero.");
    }
    if (!Number.isInteger(editorialId) || editorialId <= 0) {
      errores.push("Seleccioná una editorial.");
    }
    if (autoresSeleccionados.length === 0) {
      errores.push("Agregá al menos una autoría.");
    }

    return {
      errores: errores,
      datos: {
        titulo: titulo,
        isbn: isbn,
        precio: String(precio),
        stock: stock,
        editorial_id: editorialId,
        genero_id: generoValor === "" ? null : Number(generoValor),
        autores: autoresSeleccionados.map(function (autoria) {
          return {
            autor_id: autoria.autor_id,
            rol: autoria.rol,
            orden: autoria.orden
          };
        })
      }
    };
  }

  function limpiarFormularioLibro() {
    elemento("libros-titulo").value = "";
    elemento("libros-isbn").value = "";
    elemento("libros-precio").value = "";
    elemento("libros-stock").value = "0";
    elemento("libros-editorial").value = "";
    elemento("libros-genero").value = "";
    elemento("libros-autor-id").value = "";
    elemento("libros-autor-rol").value = "autor";
    elemento("libros-autor-orden").value = "1";
    autoresSeleccionados = [];
    renderizarAutores();
  }

  async function manejarAltaLibro(evento) {
    evento.preventDefault();
    const revision = leerDatosLibro();
    if (revision.errores.length > 0) {
      mostrarErrorLibros(revision.errores.join(" "));
      return;
    }

    const boton = elemento("libros-form").querySelector('button[type="submit"]');
    if (boton) {
      boton.disabled = true;
    }
    try {
      const libro = await ElTintero.api.crearLibro(revision.datos);
      mostrarOkLibros("Libro registrado correctamente con ID " + libro.id + ".");
      limpiarFormularioLibro();
      await cargarLibros();
    } catch (error) {
      mostrarErrorLibros(error.message);
    } finally {
      if (boton) {
        boton.disabled = false;
      }
    }
  }

  function renderizarClientesSesion() {
    const tabla = elemento("clientes-tabla");
    if (!tabla) {
      return;
    }
    const tbody = tabla.querySelector("tbody");
    vaciar(tbody);
    clientesSesion.forEach(function (cliente) {
      const fila = document.createElement("tr");
      fila.appendChild(crearCelda(String(cliente.id)));
      fila.appendChild(crearCelda(cliente.nombre));
      fila.appendChild(crearCelda(cliente.email));
      tbody.appendChild(fila);
    });
  }

  function agregarClienteSesion(cliente) {
    const existe = clientesSesion.some(function (actual) {
      return actual.id === cliente.id;
    });
    if (!existe) {
      clientesSesion.push(cliente);
    }
    renderizarClientesSesion();
  }

  function leerDatosCliente() {
    const nombre = ElTintero.formato.recortarTexto(elemento("clientes-nombre").value);
    const email = ElTintero.formato.recortarTexto(elemento("clientes-email").value);
    const errores = [];

    if (nombre === "") {
      errores.push("Ingresá el nombre.");
    }
    if (!ElTintero.formato.esEmailValido(email)) {
      errores.push("Ingresá un email válido.");
    }
    return { errores: errores, datos: { nombre: nombre, email: email } };
  }

  async function manejarAltaCliente(evento) {
    evento.preventDefault();
    const revision = leerDatosCliente();
    if (revision.errores.length > 0) {
      mostrarErrorClientes(revision.errores.join(" "));
      return;
    }
    try {
      const cliente = await ElTintero.api.crearCliente(revision.datos);
      agregarClienteSesion(cliente);
      mostrarOkClientes("Cliente registrado correctamente con ID " + cliente.id + ".");
      elemento("clientes-nombre").value = "";
      elemento("clientes-email").value = "";
    } catch (error) {
      mostrarErrorClientes(error.message);
    }
  }

  async function buscarCliente() {
    const id = Number(elemento("clientes-buscar-id").value);
    const mensaje = elemento("clientes-busqueda-mensaje");
    if (!Number.isInteger(id) || id <= 0) {
      mensaje.textContent = "Ingresá un ID de cliente válido.";
      mensaje.hidden = false;
      return;
    }
    try {
      const cliente = await ElTintero.api.obtenerCliente(id);
      agregarClienteSesion(cliente);
      mensaje.textContent = "Cliente encontrado: " + cliente.nombre + ".";
      mensaje.hidden = false;
    } catch (error) {
      mensaje.textContent = error.message;
      mensaje.hidden = false;
    }
  }

  function iniciar() {
    const formularioLibros = elemento("libros-form");
    if (formularioLibros) {
      cargarSelectores();
      cargarLibros();
      renderizarAutores();
      formularioLibros.addEventListener("submit", manejarAltaLibro);
      elemento("libros-autor-agregar").addEventListener("click", agregarAutoria);
    }

    const formularioClientes = elemento("clientes-form");
    if (formularioClientes) {
      renderizarClientesSesion();
      formularioClientes.addEventListener("submit", manejarAltaCliente);
      elemento("clientes-buscar").addEventListener("click", buscarCliente);
    }
  }

  ElTintero.altas = {
    iniciar: iniciar,
    cargarLibros: cargarLibros,
    cargarSelectores: cargarSelectores
  };

  iniciar();
}());
