(function () {
  "use strict";

  window.ElTintero = window.ElTintero || {};

  const LIMITE = 3;

  let termino = "";
  let offset = 0;

  function elemento(id) {
    return document.getElementById(id);
  }

  function crearParrafo(texto) {
    const parrafo = document.createElement("p");
    parrafo.textContent = texto;
    return parrafo;
  }

  function ocultarMensajes() {
    ["catalogo-cargando", "catalogo-error", "catalogo-vacio", "catalogo-sin-resultados"].forEach(function (id) {
      const nodo = elemento(id);
      if (nodo) {
        nodo.hidden = true;
        nodo.textContent = "";
      }
    });
  }

  function mostrarMensaje(id, texto) {
    const nodo = elemento(id);
    if (nodo) {
      nodo.textContent = texto;
      nodo.hidden = false;
    }
  }

  function crearTarjetaLibro(libro) {
    const tarjeta = document.createElement("article");
    tarjeta.className = "card libro-tarjeta";
    tarjeta.dataset.libroId = String(libro.id);

    const titulo = document.createElement("h3");
    titulo.textContent = libro.titulo;
    tarjeta.appendChild(titulo);

    tarjeta.appendChild(crearParrafo("ISBN: " + libro.isbn));
    tarjeta.appendChild(crearParrafo("Editorial: " + (libro.editorialNombre || "Editorial no disponible")));
    tarjeta.appendChild(crearParrafo("Género: " + (libro.generoNombre || "Sin clasificar")));
    tarjeta.appendChild(crearParrafo("Precio: " + ElTintero.formato.formatearPrecio(libro.precio)));

    const boton = document.createElement("button");
    boton.type = "button";
    boton.className = "btn btn--secundario";
    boton.textContent = "Ver autores";
    boton.addEventListener("click", function () {
      abrirDetalle(libro.id);
    });
    tarjeta.appendChild(boton);

    return tarjeta;
  }

  async function abrirDetalle(id) {
    const contenedor = elemento("catalogo-detalle");
    if (!contenedor) {
      return;
    }
    contenedor.hidden = false;
    contenedor.textContent = "Cargando detalle…";

    try {
      const libro = await ElTintero.api.obtenerLibro(id);
      contenedor.textContent = "";

      const encabezado = document.createElement("h3");
      encabezado.textContent = libro.titulo;
      contenedor.appendChild(encabezado);
      contenedor.appendChild(crearParrafo("ISBN: " + libro.isbn));
      contenedor.appendChild(crearParrafo("Precio: " + ElTintero.formato.formatearPrecio(libro.precio)));
      contenedor.appendChild(crearParrafo("Stock: " + libro.stock));

      const tituloAutores = document.createElement("h4");
      tituloAutores.textContent = "Autores";
      contenedor.appendChild(tituloAutores);

      if (libro.autores.length === 0) {
        contenedor.appendChild(crearParrafo("Sin autores registrados."));
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

      contenedor.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (error) {
      contenedor.textContent = error.message;
    }
  }

  function renderizarLibros(libros) {
    const lista = elemento("catalogo-lista");
    while (lista.firstChild) {
      lista.removeChild(lista.firstChild);
    }

    libros.forEach(function (libro) {
      lista.appendChild(crearTarjetaLibro(libro));
    });

    if (libros.length === 0) {
      if (termino === "") {
        mostrarMensaje("catalogo-vacio", "No hay libros registrados.");
      } else {
        mostrarMensaje("catalogo-sin-resultados", "No se encontraron libros para «" + termino + "».");
      }
    }
  }

  function actualizarPaginacion(cantidad, totalLibros) {
    const contenedor = elemento("catalogo-paginacion");
    const anterior = elemento("catalogo-anterior");
    const siguiente = elemento("catalogo-siguiente");
    const pagina = elemento("catalogo-pagina");
    if (!contenedor || !anterior || !siguiente || !pagina) {
      return;
    }

    const hayUnaSolaPagina = offset === 0 && cantidad < LIMITE;
    contenedor.hidden = cantidad === 0 || hayUnaSolaPagina;
    anterior.disabled = offset === 0;
    siguiente.disabled = cantidad < LIMITE;
    pagina.textContent = "Página " + (Math.floor(offset / LIMITE) + 1) + " · " + totalLibros + " visibles";
  }

  async function cargar(reiniciar) {
    if (reiniciar) {
      offset = 0;
    }
    ocultarMensajes();
    mostrarMensaje("catalogo-cargando", "Cargando catálogo…");

    try {
      const libros = await ElTintero.api.listarLibros({
        titulo: termino,
        limit: LIMITE,
        offset: offset
      });
      ocultarMensajes();
      renderizarLibros(libros);
      actualizarPaginacion(libros.length, libros.length);
    } catch (error) {
      ocultarMensajes();
      mostrarMensaje("catalogo-error", error.message);
      actualizarPaginacion(0, 0);
    }
  }

  function iniciar() {
    const formulario = elemento("catalogo-buscador");
    const campo = elemento("catalogo-titulo");
    const anterior = elemento("catalogo-anterior");
    const siguiente = elemento("catalogo-siguiente");
    if (!formulario || !campo) {
      return;
    }

    formulario.addEventListener("submit", function (evento) {
      evento.preventDefault();
      termino = ElTintero.formato.recortarTexto(campo.value);
      cargar(true);
    });

    formulario.addEventListener("reset", function () {
      window.setTimeout(function () {
        termino = "";
        cargar(true);
      }, 0);
    });

    if (anterior) {
      anterior.addEventListener("click", function () {
        offset = Math.max(0, offset - LIMITE);
        cargar(false);
      });
    }

    if (siguiente) {
      siguiente.addEventListener("click", function () {
        offset += LIMITE;
        cargar(false);
      });
    }

    cargar(true);
  }

  ElTintero.catalogo = {
    iniciar: iniciar,
    cargar: cargar
  };

  iniciar();
}());
