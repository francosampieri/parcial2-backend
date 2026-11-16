(function () {
  "use strict";

  window.ElTintero = window.ElTintero || {};

  let libros = [];
  let cliente = null;
  let renglones = [];
  let enviando = false;

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

  function mostrar(tipo, texto) {
    const ok = elemento("ventas-mensaje-ok");
    const error = elemento("ventas-mensaje-error");
    if (!ok || !error) {
      return;
    }
    if (tipo === "ok") {
      ok.textContent = texto;
      ok.hidden = false;
      error.textContent = "";
      error.hidden = true;
    } else {
      error.textContent = texto;
      error.hidden = false;
      ok.textContent = "";
      ok.hidden = true;
    }
  }

  function limpiarMensajes() {
    ["ventas-mensaje-ok", "ventas-mensaje-error"].forEach(function (id) {
      const nodo = elemento(id);
      if (nodo) {
        nodo.textContent = "";
        nodo.hidden = true;
      }
    });
  }

  async function cargarLibros() {
    const selector = elemento("ventas-libro");
    if (!selector) {
      return;
    }
    try {
      libros = await ElTintero.api.listarLibros({ limit: 100, offset: 0 });
      vaciar(selector);
      selector.appendChild(crearOpcion("", "Seleccionar libro"));
      libros.forEach(function (libro) {
        selector.appendChild(crearOpcion(String(libro.id), libro.titulo));
      });
    } catch (error) {
      mostrar("error", "No se pudo cargar el catálogo: " + error.message);
    }
  }

  function buscarLibro(id) {
    return libros.find(function (libro) {
      return libro.id === id;
    });
  }

  async function resolverCliente() {
    const campo = elemento("ventas-cliente-id");
    const id = Number(campo.value);
    if (!Number.isInteger(id) || id <= 0) {
      cliente = null;
      elemento("ventas-cliente-nombre").textContent = "";
      return false;
    }
    try {
      cliente = await ElTintero.api.obtenerCliente(id);
      elemento("ventas-cliente-nombre").textContent = "Cliente: " + cliente.nombre;
      return true;
    } catch (error) {
      cliente = null;
      elemento("ventas-cliente-nombre").textContent = "";
      mostrar("error", "No se pudo encontrar el cliente: " + error.message);
      return false;
    }
  }

  function indiceDeRenglon(libroId) {
    return renglones.findIndex(function (renglon) {
      return renglon.libroId === libroId;
    });
  }

  function crearFilaRenglon(renglon) {
    const libro = buscarLibro(renglon.libroId);
    const titulo = libro ? libro.titulo : "Libro " + renglon.libroId;
    const precio = libro ? libro.precio : 0;
    const subtotal = ElTintero.formato.redondear2(renglon.cantidad * precio);

    const fila = document.createElement("tr");
    fila.setAttribute("data-libro-id", String(renglon.libroId));
    fila.appendChild(crearCelda(titulo));

    const celdaCantidad = document.createElement("td");
    const campoCantidad = document.createElement("input");
    campoCantidad.type = "number";
    campoCantidad.min = "1";
    campoCantidad.step = "1";
    campoCantidad.value = String(renglon.cantidad);
    campoCantidad.setAttribute("aria-label", "Cantidad de «" + titulo + "»");
    celdaCantidad.appendChild(campoCantidad);
    fila.appendChild(celdaCantidad);

    fila.appendChild(crearCelda(ElTintero.formato.formatearImporte(precio)));
    fila.appendChild(crearCelda(ElTintero.formato.formatearImporte(subtotal)));

    const celdaAcciones = document.createElement("td");
    const boton = document.createElement("button");
    boton.type = "button";
    boton.className = "btn btn--peligro";
    boton.setAttribute("data-accion", "quitar");
    boton.setAttribute("aria-label", "Quitar «" + titulo + "» de la venta");
    boton.textContent = "Quitar";
    celdaAcciones.appendChild(boton);
    fila.appendChild(celdaAcciones);

    return fila;
  }

  function renderizarRenglones() {
    const tbody = document.querySelector("#venta-renglones tbody");
    if (!tbody) {
      return;
    }
    vaciar(tbody);
    renglones.forEach(function (renglon) {
      tbody.appendChild(crearFilaRenglon(renglon));
    });
    const vacio = elemento("ventas-renglones-vacio");
    if (vacio) {
      vacio.hidden = renglones.length !== 0;
    }
  }

  function recalcular() {
    const total = renglones.reduce(function (acumulado, renglon) {
      const libro = buscarLibro(renglon.libroId);
      return acumulado + (libro ? renglon.cantidad * libro.precio : 0);
    }, 0);
    const etiqueta = elemento("ventas-total");
    if (etiqueta) {
      etiqueta.textContent = ElTintero.formato.formatearImporte(ElTintero.formato.redondear2(total));
    }
  }

  function validarCantidad(texto) {
    if (texto === "") {
      return { error: "Ingresá una cantidad." };
    }
    const cantidad = Number(texto);
    if (!Number.isFinite(cantidad)) {
      return { error: "Ingresá una cantidad válida." };
    }
    if (!Number.isInteger(cantidad)) {
      return { error: "La cantidad debe ser un número entero." };
    }
    if (cantidad <= 0) {
      return { error: "La cantidad debe ser mayor que cero." };
    }
    return { cantidad: cantidad };
  }

  function agregarRenglon() {
    const selector = elemento("ventas-libro");
    const campoCantidad = elemento("ventas-cantidad");
    const libroId = Number(selector.value);
    if (!Number.isInteger(libroId) || libroId <= 0 || !buscarLibro(libroId)) {
      mostrar("error", "Seleccioná un libro válido.");
      return;
    }
    if (indiceDeRenglon(libroId) !== -1) {
      mostrar("error", "Ese libro ya está en la venta.");
      return;
    }
    const revision = validarCantidad(ElTintero.formato.recortarTexto(campoCantidad.value));
    if (revision.error) {
      mostrar("error", revision.error);
      return;
    }

    renglones.push({ libroId: libroId, cantidad: revision.cantidad });
    limpiarMensajes();
    renderizarRenglones();
    recalcular();
    selector.value = "";
    campoCantidad.value = "1";
  }

  function quitarRenglon(libroId) {
    const indice = indiceDeRenglon(libroId);
    if (indice === -1) {
      return;
    }
    renglones.splice(indice, 1);
    limpiarMensajes();
    renderizarRenglones();
    recalcular();
  }

  function manejarCambioCantidad(evento) {
    const objetivo = evento.target;
    if (!objetivo || objetivo.tagName !== "INPUT") {
      return;
    }
    const fila = objetivo.closest("tr");
    if (!fila) {
      return;
    }
    const libroId = Number(fila.getAttribute("data-libro-id"));
    const indice = indiceDeRenglon(libroId);
    if (indice === -1) {
      return;
    }
    const revision = validarCantidad(ElTintero.formato.recortarTexto(objetivo.value));
    if (revision.error) {
      mostrar("error", revision.error);
      renderizarRenglones();
      return;
    }
    renglones[indice].cantidad = revision.cantidad;
    limpiarMensajes();
    renderizarRenglones();
    recalcular();
  }

  function manejarClicRenglones(evento) {
    const objetivo = evento.target;
    if (!objetivo || typeof objetivo.closest !== "function") {
      return;
    }
    const boton = objetivo.closest('[data-accion="quitar"]');
    if (!boton) {
      return;
    }
    const fila = boton.closest("tr");
    if (fila) {
      quitarRenglon(Number(fila.getAttribute("data-libro-id")));
    }
  }

  function renderizarConfirmada(venta) {
    const contenedor = elemento("ventas-confirmada");
    if (!contenedor) {
      return;
    }
    contenedor.hidden = false;
    contenedor.textContent = "";

    const titulo = document.createElement("h3");
    titulo.textContent = "Venta " + venta.id + " registrada";
    contenedor.appendChild(titulo);

    const fecha = document.createElement("p");
    fecha.textContent = "Fecha: " + ElTintero.formato.formatearFecha(venta.fecha);
    contenedor.appendChild(fecha);

    const tabla = document.createElement("table");
    tabla.className = "tabla";
    const thead = document.createElement("thead");
    const filaEncabezado = document.createElement("tr");
    ["Libro", "Cantidad", "Precio unitario", "Subtotal"].forEach(function (texto) {
      const celda = document.createElement("th");
      celda.setAttribute("scope", "col");
      celda.textContent = texto;
      filaEncabezado.appendChild(celda);
    });
    thead.appendChild(filaEncabezado);
    tabla.appendChild(thead);

    const tbody = document.createElement("tbody");
    venta.renglones.forEach(function (renglon) {
      const fila = document.createElement("tr");
      fila.appendChild(crearCelda(renglon.tituloLibro));
      fila.appendChild(crearCelda(String(renglon.cantidad)));
      fila.appendChild(crearCelda(ElTintero.formato.formatearImporte(renglon.precioUnitario)));
      fila.appendChild(crearCelda(ElTintero.formato.formatearImporte(renglon.subtotal)));
      tbody.appendChild(fila);
    });
    tabla.appendChild(tbody);
    contenedor.appendChild(tabla);

    const total = document.createElement("p");
    total.innerHTML = "<strong>Total: " + ElTintero.formato.formatearImporte(venta.total) + "</strong>";
    contenedor.appendChild(total);

    const enlace = document.createElement("a");
    enlace.href = "historial.html";
    enlace.textContent = "Ver historial";
    contenedor.appendChild(enlace);
  }

  async function confirmarVenta() {
    if (enviando) {
      return;
    }
    limpiarMensajes();
    elemento("ventas-confirmada").hidden = true;

    const idCliente = Number(elemento("ventas-cliente-id").value);
    if (!cliente || cliente.id !== idCliente) {
      const encontrado = await resolverCliente();
      if (!encontrado) {
        if (elemento("ventas-mensaje-error").hidden) {
          mostrar("error", "Seleccioná un cliente válido.");
        }
        return;
      }
    }
    if (renglones.length === 0) {
      mostrar("error", "Agregá al menos un renglón.");
      return;
    }

    const boton = elemento("ventas-confirmar");
    enviando = true;
    if (boton) {
      boton.disabled = true;
    }

    try {
      const venta = await ElTintero.api.crearVenta({
        cliente_id: cliente.id,
        renglones: renglones.map(function (renglon) {
          return { libro_id: renglon.libroId, cantidad: renglon.cantidad };
        })
      });
      renderizarConfirmada(venta);
      mostrar("ok", "Venta registrada correctamente.");

      elemento("ventas-cliente-id").value = "";
      elemento("ventas-cliente-nombre").textContent = "";
      elemento("ventas-libro").value = "";
      elemento("ventas-cantidad").value = "1";
      cliente = null;
      renglones = [];
      renderizarRenglones();
      recalcular();
    } catch (error) {
      mostrar("error", error.message);
    } finally {
      enviando = false;
      if (boton) {
        boton.disabled = false;
      }
    }
  }

  function iniciar() {
    const tabla = elemento("venta-renglones");
    if (!tabla) {
      return;
    }

    cargarLibros();
    renderizarRenglones();
    recalcular();

    elemento("ventas-cliente-buscar").addEventListener("click", resolverCliente);
    elemento("ventas-agregar").addEventListener("click", agregarRenglon);
    elemento("ventas-confirmar").addEventListener("click", confirmarVenta);

    const tbody = tabla.querySelector("tbody");
    tbody.addEventListener("change", manejarCambioCantidad);
    tbody.addEventListener("click", manejarClicRenglones);
  }

  ElTintero.ventas = {
    iniciar: iniciar,
    cargarLibros: cargarLibros
  };

  iniciar();
}());
