// @ts-check

/** @type {import('alpinejs').default} */
var Alpine;

const duration = /**@type {HTMLInputElement}*/ (
  document.querySelector("#id_duration")
);
duration.setAttribute("x-model", "duration");

const location_towit = /**@type {HTMLInputElement}*/ (
  document.querySelector("#id_location_towit")
);
location_towit.setAttribute("x-model", "location");

const location_note_box = /**@type {HTMLDivElement}*/ (
  document.querySelector("#location_note_box")
);
location_note_box.setAttribute("x-show", "!location");

const trailer_discount = /**@type {HTMLInputElement}*/ (
  document.querySelector("#id_trailer_condition_discount")
);
trailer_discount.setAttribute("x-model", "trailer_discount");

const discount_box = /**@type {HTMLDivElement}*/ (
  document.querySelector("#totalDiscountBox")
);
discount_box.setAttribute("x-text", "'Total discount: ' + totalDiscount()");

document.addEventListener("alpine:init", () => {
  Alpine.data("depositDevolution", () => {
    return {
      duration: duration.checked,
      location: location_towit.checked,
      trailer_discount: parseFloat(trailer_discount.value),

      totalDiscount() {
        return (
          parseFloat(window.DEBT) +
          parseFloat(window.TOLLS) +
          (this.trailer_discount | 0.0)
        );
      },
    };
  });
});
