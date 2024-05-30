// @ts-check

/** @type {import('alpinejs').default} */
var Alpine;

const returnInput = /** @type {HTMLInputElement} */ (
  document.querySelector("#id_returned_amount")
);
returnInput.setAttribute("x-model", "return_amount");

const returnNote = /** @type {HTMLTextAreaElement} */ (
  document.querySelector("#id_returned_note")
);
returnNote.setAttribute("x-bind:required", "noteRequired()");

const returnNoteLabel = /** @type {HTMLLabelElement} */ (
  document.querySelector("#div_id_returned_note label")
);
returnNoteLabel.setAttribute("x-text", "noteRequired() ? 'Note*' : 'Note'");

document.addEventListener("alpine:init", () => {
  Alpine.data("OnHoldFinish", () => {
    return {
      return_amount: 0,

      /**
       * Return the total amount deposited on the deposit
       * @returns {number}
       * */
      total() {
        return globalThis.Total;
      },

      /**
       * Return the towit compensation amount
       * It is the difference between the total deposited minus the return amount.
       * @returns {number}
       * */
      towitCompensation() {
        return this.total() - this.return_amount;
      },

      /**
       * Return if the note is required or not
       * @returns {boolean}
       * */
      noteRequired() {
        return this.return_amount > 0;
      },
    };
  });
});
