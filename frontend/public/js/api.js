(function () {
  "use strict";

  window.ElTintero = window.ElTintero || {};

  const BASE = "/api";

  function numero(valor) {
    const convertido = Number(valor);
    return Number.isFinite(convertido) ? convertido : 0;
  }

  function construirConsulta(parametros) {
    const busqueda = new URLSearchParams();
    Object.keys(parametros).forEach(function (clave) {
      const valor = parametros[clave];
      if (valor !== undefined && valor !== null && valor !== "") {
        busqueda.set(clave, String(valor));
      }
    });
    const texto = busqueda.toString();
    return texto === "" ? "" : "?" + texto;
  }

  function mensajeDeError(cuerpo, estado) {
    if (cuerpo && typeof cuerpo.detail === "string") {
      return cuerpo.detail;
    }
    if (cuerpo && Array.isArray(cuerpo.detail)) {
      const mensajes = cuerpo.detail.map(function (item) {
        return item && item.msg ? item.msg : String(item);
      }).filter(function (mensaje) {
        return mensaje !== "";
      });
      if (mensajes.length > 0) {
        return mensajes.join(" ");
      }
    }
    if (typeof cuerpo === "string" && cuerpo.trim() !== "") {
      return cuerpo;
    }
    if (estado === 404) {
      return "No se encontró el recurso solicitado.";
    }
    if (estado === 409) {
      return "La operación entra en conflicto con los datos existentes.";
    }
    if (estado === 422) {
      return "Los datos enviados no son válidos.";
    }
    return "La API respondió con un error (" + estado + ").";
  }

  async function solicitar(ruta, opciones) {
    const configuracion = Object.assign({}, opciones || {});
    configuracion.headers = Object.assign(
      { "Accept": "application/json" },
      configuracion.headers || {}
    );

    if (configuracion.body !== undefined && configuracion.body !== null &&
        typeof configuracion.body !== "string") {
      configuracion.headers["Content-Type"] = "application/json";
      configuracion.body = JSON.stringify(configuracion.body);
    }

    let respuesta;
    try {
      respuesta = await fetch(BASE + ruta, configuracion);
    } catch (error) {
      const fallo = new Error("No se pudo conectar con la API. Verificá que el backend esté disponible.");
      fallo.causa = error;
      throw fallo;
    }

    const texto = await respuesta.text();
    let cuerpo = null;
    if (texto !== "") {
      try {
        cuerpo = JSON.parse(texto);
      } catch (error) {
        cuerpo = texto;
      }
    }

    if (!respuesta.ok) {
      const fallo = new Error(mensajeDeError(cuerpo, respuesta.status));
      fallo.status = respuesta.status;
      fallo.cuerpo = cuerpo;
      throw fallo;
    }

    return cuerpo;
  }

  function normalizarLibro(libro) {
    return {
      id: libro.id,
      isbn: libro.isbn,
      titulo: libro.titulo,
      precio: numero(libro.precio),
      stock: libro.stock,
      editorialId: libro.editorial ? libro.editorial.id : null,
      editorialNombre: libro.editorial ? libro.editorial.nombre : "",
      generoId: libro.genero ? libro.genero.id : null,
      generoNombre: libro.genero ? libro.genero.nombre : "Sin clasificar",
      autores: []
    };
  }

  function normalizarLibroDetalle(libro) {
    const normalizado = normalizarLibro(libro);
    normalizado.autores = (libro.autores || []).map(function (autoria) {
      if (autoria.autor) {
        return {
          id: autoria.autor.id,
          nombre: autoria.autor.nombre,
          rol: autoria.rol,
          orden: autoria.orden
        };
      }
      return {
        id: autoria.autor_id,
        nombre: "",
        rol: autoria.rol,
        orden: autoria.orden
      };
    });
    return normalizado;
  }

  function normalizarCliente(cliente) {
    return {
      id: cliente.id,
      nombre: cliente.nombre,
      email: cliente.email
    };
  }

  function normalizarResumenVenta(venta) {
    return {
      id: venta.id,
      fecha: venta.fecha,
      total: numero(venta.total),
      clienteId: venta.cliente ? venta.cliente.id : null,
      clienteNombre: venta.cliente ? venta.cliente.nombre : ""
    };
  }

  function normalizarDetalleVenta(venta) {
    const normalizada = normalizarResumenVenta(venta);
    normalizada.renglones = (venta.renglones || []).map(function (renglon) {
      return {
        libroId: renglon.libro_id,
        tituloLibro: renglon.titulo,
        cantidad: renglon.cantidad,
        precioUnitario: numero(renglon.precio_unitario),
        subtotal: numero(renglon.subtotal)
      };
    });
    return normalizada;
  }

  async function listarLibros(filtros) {
    const opciones = filtros || {};
    const parametros = construirConsulta({
      titulo: opciones.titulo,
      limit: opciones.limit !== undefined ? opciones.limit : 20,
      offset: opciones.offset !== undefined ? opciones.offset : 0
    });
    const libros = await solicitar("/libros/" + parametros);
    return libros.map(normalizarLibro);
  }

  async function obtenerLibro(id) {
    return normalizarLibroDetalle(await solicitar("/libros/" + encodeURIComponent(id)));
  }

  async function listarEditoriales() {
    return await solicitar("/editoriales/");
  }

  async function listarGeneros() {
    return await solicitar("/generos/");
  }

  async function obtenerAutor(id) {
    return await solicitar("/autores/" + encodeURIComponent(id));
  }

  async function crearLibro(datos) {
    return normalizarLibroDetalle(await solicitar("/libros/", {
      method: "POST",
      body: datos
    }));
  }

  async function crearCliente(datos) {
    return normalizarCliente(await solicitar("/clientes/", {
      method: "POST",
      body: datos
    }));
  }

  async function obtenerCliente(id) {
    return normalizarCliente(await solicitar("/clientes/" + encodeURIComponent(id)));
  }

  async function crearVenta(datos) {
    return normalizarDetalleVenta(await solicitar("/ventas/", {
      method: "POST",
      body: datos
    }));
  }

  async function listarVentas(filtros) {
    const opciones = filtros || {};
    const parametros = construirConsulta({
      limit: opciones.limit !== undefined ? opciones.limit : 20,
      offset: opciones.offset !== undefined ? opciones.offset : 0
    });
    const ventas = await solicitar("/ventas/" + parametros);
    return ventas.map(normalizarResumenVenta);
  }

  async function obtenerVenta(id) {
    return normalizarDetalleVenta(await solicitar("/ventas/" + encodeURIComponent(id)));
  }

  ElTintero.api = {
    listarLibros: listarLibros,
    obtenerLibro: obtenerLibro,
    listarEditoriales: listarEditoriales,
    listarGeneros: listarGeneros,
    obtenerAutor: obtenerAutor,
    crearLibro: crearLibro,
    crearCliente: crearCliente,
    obtenerCliente: obtenerCliente,
    crearVenta: crearVenta,
    listarVentas: listarVentas,
    obtenerVenta: obtenerVenta,
    normalizarLibro: normalizarLibro,
    normalizarLibroDetalle: normalizarLibroDetalle,
    normalizarResumenVenta: normalizarResumenVenta,
    normalizarDetalleVenta: normalizarDetalleVenta,
    construirConsulta: construirConsulta
  };
}());
