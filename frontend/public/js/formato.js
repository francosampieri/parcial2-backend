(function () {
  "use strict";

  window.ElTintero = window.ElTintero || {};

  const formateadorPrecio = new Intl.NumberFormat("es-AR", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  });

  const formateadorImporte = new Intl.NumberFormat("es-AR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });

  const formateadorFecha = new Intl.DateTimeFormat("es-AR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  });

  function formatearPrecio(valor) {
    return "$" + formateadorPrecio.format(Number(valor) || 0);
  }

  function formatearImporte(valor) {
    return "$" + formateadorImporte.format(Number(valor) || 0);
  }

  function formatearFecha(valor) {
    if (valor === undefined || valor === null || valor === "") {
      return "";
    }
    const fecha = new Date(valor);
    if (Number.isNaN(fecha.getTime())) {
      return String(valor);
    }
    return formateadorFecha.format(fecha);
  }

  function redondear2(valor) {
    return Math.round((Number(valor) || 0) * 100) / 100;
  }

  function recortarTexto(valor) {
    if (valor === undefined || valor === null) {
      return "";
    }
    return String(valor).trim();
  }

  function esEmailValido(email) {
    return /^[^\s@]+@[^\s@]+\.[A-Za-z]{2,}$/.test(recortarTexto(email));
  }

  ElTintero.formato = {
    formatearPrecio: formatearPrecio,
    formatearImporte: formatearImporte,
    formatearFecha: formatearFecha,
    redondear2: redondear2,
    recortarTexto: recortarTexto,
    esEmailValido: esEmailValido
  };
}());
