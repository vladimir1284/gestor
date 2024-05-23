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
discount_box.setAttribute(
  "x-text",
  "'Total discount on the deposit: ' + totalDiscount()",
);

const immediateInput = /**@type {HTMLInputElement}*/ (
  document.querySelector("#id_immediate_refund")
);
immediateInput.setAttribute("x-model", "immediateReturn");

const refundDateBox = /**@type {HTMLDivElement}*/ (
  document.querySelector("#refundDateBox")
);
refundDateBox.setAttribute("x-show", "!immediateReturn");

const refundNoteBox = /**@type {HTMLDivElement}*/ (
  document.querySelector("#refundNoteBox")
);
refundNoteBox.setAttribute("x-show", "immediateReturn");

document.addEventListener("alpine:init", () => {
  Alpine.data("depositDevolution", () => {
    return {
      duration: duration.checked,
      location: location_towit.checked,
      trailer_discount: parseFloat(trailer_discount.value),

      immediateReturn: immediateInput.checked,

      totalDiscount() {
        return (
          parseFloat(window.DEBT) +
          parseFloat(window.TOLLS) +
          (this.trailer_discount | 0.0)
        );
      },

      totalAmount() {
        return parseFloat(window.Total) - this.totalDiscount();
      },

      devolution() {
        return this.duration && this.location;
      },
    };
  });
});
