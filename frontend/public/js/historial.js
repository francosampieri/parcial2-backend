(function () {
  "use strict";

  window.ElTintero = window.ElTintero || {};

  const LIMITE = 5;

  let offset = 0;

  function elemento(id) {
    return document.getElementById(id);
  }

  function crearCelda(texto) {
    const celda = document.createElement("td");
    celda.textContent = texto;
    return celda;
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

  function actualizarPaginacion(cantidad) {
    const contenedor = elemento("historial-paginacion");
    const anterior = elemento("historial-anterior");
    const siguiente = elemento("historial-siguiente");
    const pagina = elemento("historial-pagina");
    if (!contenedor || !anterior || !siguiente || !pagina) {
      return;
    }
    const unaSolaPagina = offset === 0 && cantidad < LIMITE;
    contenedor.hidden = cantidad === 0 || unaSolaPagina;
    anterior.disabled = offset === 0;
    siguiente.disabled = cantidad < LIMITE;
    pagina.textContent = "Página " + (Math.floor(offset / LIMITE) + 1);
  }

  function crearFilaVenta(venta) {
    const fila = document.createElement("tr");
    fila.setAttribute("data-venta-id", String(venta.id));
    fila.appendChild(crearCelda(String(venta.id)));
    fila.appendChild(crearCelda(ElTintero.formato.formatearFecha(venta.fecha)));
    fila.appendChild(crearCelda(venta.clienteNombre));
    fila.appendChild(crearCelda(ElTintero.formato.formatearImporte(venta.total)));

    const celda = document.createElement("td");
    const boton = document.createElement("button");
    boton.type = "button";
    boton.className = "btn btn--secundario";
    boton.textContent = "Ver detalle";
    boton.addEventListener("click", function () {
      verDetalle(venta.id);
    });
    celda.appendChild(boton);
    fila.appendChild(celda);

    return fila;
  }

  function renderizar(ventas) {
    const tabla = elemento("historial-tabla");
    if (!tabla) {
      return;
    }
    const tbody = tabla.querySelector("tbody");
    vaciar(tbody);
    ventas.forEach(function (venta) {
      tbody.appendChild(crearFilaVenta(venta));
    });
    if (ventas.length === 0) {
      mostrar("historial-vacio", "Todavía no hay ventas registradas.");
    } else {
      ocultar("historial-vacio");
    }
  }

  async function verDetalle(id) {
    const contenedor = elemento("historial-detalle");
    contenedor.hidden = false;
    contenedor.textContent = "Cargando detalle…";

    try {
      const venta = await ElTintero.api.obtenerVenta(id);
      contenedor.textContent = "";

      const titulo = document.createElement("h3");
      titulo.textContent = "Detalle de la venta " + venta.id;
      contenedor.appendChild(titulo);

      const datos = document.createElement("p");
      datos.textContent = "Fecha: " + ElTintero.formato.formatearFecha(venta.fecha) +
        " · Cliente: " + venta.clienteNombre;
      contenedor.appendChild(datos);

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
      contenedor.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (error) {
      contenedor.textContent = error.message;
    }
  }

  async function cargar(reiniciar) {
    if (reiniciar) {
      offset = 0;
    }
    ocultar("historial-error");
    mostrar("historial-cargando", "Cargando historial…");
    try {
      const ventas = await ElTintero.api.listarVentas({ limit: LIMITE, offset: offset });
      ocultar("historial-cargando");
      renderizar(ventas);
      actualizarPaginacion(ventas.length);
    } catch (error) {
      ocultar("historial-cargando");
      mostrar("historial-error", error.message);
      actualizarPaginacion(0);
    }
  }

  function iniciar() {
    if (!elemento("historial-tabla")) {
      return;
    }
    elemento("historial-anterior").addEventListener("click", function () {
      offset = Math.max(0, offset - LIMITE);
      cargar(false);
    });
    elemento("historial-siguiente").addEventListener("click", function () {
      offset += LIMITE;
      cargar(false);
    });
    cargar(true);
  }

  ElTintero.historial = {
    iniciar: iniciar,
    cargar: cargar
  };

  iniciar();
}());
