const elements = document.querySelectorAll("#guarantor input");

elements.forEach((e) => {
  e.removeAttribute("required");
  e.setAttribute("x-bind:required", "has_guarantor");
});
