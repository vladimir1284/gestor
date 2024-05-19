// @ts-check

/** @type {import('alpinejs').default} */
var Alpine;

const loc_towit = /** @type {HTMLInputElement}*/ (
  document.querySelector("#id_location_towit")
);
loc_towit.setAttribute("x-model", "locTowit");

const note_box = /** @type {HTMLDivElement} */ (
  document.querySelector("#div_id_location_note")
);
note_box.setAttribute("x-show", "showNote");
note_box.setAttribute("x-cloak", "true");

document.addEventListener("alpine:init", () => {
  Alpine.data("depositDiscount", () => {
    return {
      locTowit: loc_towit.checked,

      showNote() {
        return this.locTowit == false;
      },
    };
  });
});
