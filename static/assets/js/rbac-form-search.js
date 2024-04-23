const accordionCollapse = document.querySelectorAll(
  ".accordion-collapse.collapse",
);
const accordionButton = document.querySelectorAll(
  ".accordion-button.collapsed",
);
const accordionElements = document.querySelectorAll(
  ".accordion-collapse .accordion-body .controls label",
);

accordionCollapse.forEach((e) => {
  e.setAttribute(":class", '{show: $store.search.search != ""}');
});
accordionButton.forEach((e) => {
  e.setAttribute(":class", '{collapsed: $store.search.search == ""}');
});
accordionElements.forEach((e) => {
  e.setAttribute("x-show", "() => match($el)");
});

document.addEventListener("alpine:init", () => {
  Alpine.data("RBACSearch", () => {
    return {
      match(element) {
        const etext = element.innerText.toLowerCase();
        const text = Alpine.store("search").search;
        const fields = text.toLowerCase().split(" ");
        for (let f of fields) {
          if (etext.indexOf(f) == -1) {
            return false;
          }
        }
        return true;
      },
    };
  });
});
