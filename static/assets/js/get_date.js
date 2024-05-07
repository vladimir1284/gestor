function getDate() {
  const date = new Date();
  const day = String(date.getDate()).padStart(2, "0");
  const month = String(date.getMonth() + 1).padStart(2, "0"); // Los meses en JavaScript empiezan desde 0
  const year = String(date.getFullYear()); // Obtiene los últimos dos dígitos del año

  const strDate = month + "/" + day + "/" + year.substring(year.length - 2);

  return strDate;
}
