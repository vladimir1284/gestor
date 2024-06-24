const quotation = document.querySelector("#id_quotation");
const parts_sale = document.querySelector("#id_parts_sale");
const position = document.querySelector("#id_position");
const reason = document.querySelector("#div_id_storage_reason");

quotation.setAttribute("x-model", "quotation");
if (parts_sale) parts_sale.setAttribute("x-model", "parts_sale");

position.setAttribute("x-bind", "position");
position.setAttribute("x-model", "position");

reason.setAttribute(
  "x-show",
  "position != '' && position == 0 && (!quotation && !parts_sale)",
);
reason.setAttribute("x-cloak", true);

document.addEventListener("alpine:init", () => {
  Alpine.data("orderForm", () => {
    return {
      quotation: quotation.checked,
      parts_sale: parts_sale ? parts_sale.checked : false,
      position: position.value,
      old_position: position.value,
      positionReason: reason.value,
    };
  });

  Alpine.bind("position", () => {
    return {
      ":disabled"() {
        return this.quotation || this.parts_sale;
      },
      ":value"() {
        if (this.quotation || this.parts_sale) {
          this.old_position = this.$el.value;
          return "-10";
        }
        return this.old_position;
      },
    };
  });

  // Alpine.bind("positionReason", () => {
  //     return {
  //         ":disabled"() {
  //             return this.quotation || this.parts_sale;
  //         },
  //         ":value"() {
  //             if (this.quotation || this.parts_sale) {
  //                 this.positionReason = this.$el.value;
  //                 return "";
  //             }
  //             return this.positionReason;
  //         },
  //         ":style"() {
  //             if (this.position == "" || this.position != 0) {
  //                 return "display: none";
  //             }
  //             if (this.quotation || this.parts_sale) {
  //                 return "display: none";
  //             }
  //             return "";
  //         },
  //     };
  // });
});

// var oldValue = 0;
//
// function updatePosition() {
//     const q = quotation.checked;
//     console.log(q);
//     position.disabled = q;
//     if (q) {
//         const nullOption = document.createElement("option");
//         nullOption.value = "";
//         nullOption.text = "Null";
//         position.add(nullOption);
//         oldValue = position.value;
//         position.value = "";
//         reason.style.display = "none";
//     } else {
//         nullOption = position.querySelector('option[value=""]');
//         position.removeChild(nullOption);
//         position.value = oldValue;
//         updateReason();
//     }
// }
//
// function updateReason() {
//     const value = position.value;
//     console.log(value);
//     reason.style.display = value != "" && value == 0 ? "block" : "none";
// }
//
// position.addEventListener("change", updateReason);
// updateReason();
//
// quotation.addEventListener("change", updatePosition);
// updatePosition();
