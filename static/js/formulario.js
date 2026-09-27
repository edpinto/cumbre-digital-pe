// Validación en el navegador para dar feedback inmediato.
// El servidor vuelve a validar todo, así que esto es solo una ayuda visual.

const formulario = document.getElementById("formulario");

// Expresión regular para validar el formato del correo electrónico
const REGEX_EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

// Reglas de validación por campo: cada una devuelve un mensaje de error o cadena vacía
const reglas = {
  nombre: (valor) => {
    if (!valor) return "Por favor, ingresa tu nombre completo.";
    if (valor.length < 3) return "El nombre debe tener al menos 3 caracteres.";
    return "";
  },
  email: (valor) => {
    if (!valor) return "Por favor, ingresa tu correo electrónico.";
    if (!REGEX_EMAIL.test(valor)) return "El formato del correo no es válido (ej. nombre@empresa.com).";
    return "";
  },
  empresa: (valor) => {
    if (!valor) return "Por favor, ingresa el nombre de tu empresa u organización.";
    return "";
  },
  area: (valor) => {
    if (!valor) return "Por favor, selecciona un área de interés.";
    return "";
  }
};

// Valida un campo individual y muestra u oculta su mensaje de error
function validarCampo(id) {
  const elemento = document.getElementById(id);
  const contenedor = elemento.closest(".campo");
  const mensaje = reglas[id](elemento.value.trim());

  document.getElementById("error-" + id).textContent = mensaje;
  contenedor.classList.toggle("invalido", mensaje !== "");
  elemento.setAttribute("aria-invalid", mensaje !== "" ? "true" : "false");

  return mensaje === "";
}

// Quita el error de un campo en cuanto el usuario lo corrige
Object.keys(reglas).forEach((id) => {
  const elemento = document.getElementById(id);
  const evento = elemento.tagName === "SELECT" ? "change" : "input";
  elemento.addEventListener(evento, () => {
    if (elemento.closest(".campo").classList.contains("invalido")) {
      validarCampo(id);
    }
  });
});

// Si hay errores, se detiene el envío; si todo está bien, el formulario se envía al servidor
formulario.addEventListener("submit", (e) => {
  const resultados = Object.keys(reglas).map(validarCampo);
  if (resultados.every(Boolean)) return;

  e.preventDefault();
  const primerError = formulario.querySelector(".campo.invalido input, .campo.invalido select");
  if (primerError) primerError.focus();
});

// Si el servidor devolvió errores, enfocar el primer campo con error
const errorDelServidor = formulario.querySelector(".campo.invalido input, .campo.invalido select");
if (errorDelServidor) errorDelServidor.focus();
