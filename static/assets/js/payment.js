const totalAmount = window.totalAmount;

const towitRemainder = document.querySelector("#towitRemainder");
const towitInput = document.querySelector(
  '.numberinput[x-ref="towit_payment"]',
);
const paymentInputs = Array.from(
  document.querySelectorAll(".numberinput"),
).filter((element) => {
  if (element.name.includes("week")) {
    return false;
  }

  if (element.getAttribute("x-ref") == "towit_payment") {
    return false;
  }

  return true;
});

paymentInputs.forEach((e) => {
  const name = e.getAttribute("name");
  e.setAttribute("x-model", `models['${name}']`);
  e.setAttribute("x-on:click", `() => setValue('${name}')`);
});

if (towitInput) {
  towitInput.setAttribute("x-model", "towit");
  towitInput.setAttribute("x-on:click", "setTowitValue");
}
if (towitRemainder) {
  towitRemainder.setAttribute("x-text", "towitRemainder");
}

document.addEventListener("alpine:init", () => {
  Alpine.data("payment", () => {
    return {
      models: {},
      towit: 0,
      towitRemainder: 0,
      Remainder: 0,
      remainder: 0,

      totalAmount: 0,
      totalCharge: 0,
      totalValue: 0,

      init() {
        // Initialize models
        if (towitInput) this.towit = towitInput.value;
        paymentInputs.forEach((e) => {
          const name = e.getAttribute("name");
          this.models[name] = e.value;
        });

        // Start values
        this.update();

        // Update values on change
        this.$watch("models", () => {
          this.update();
        });
        this.$watch("towit", () => {
          this.update();
        });
      },

      total() {
        // Update total and charges
        this.totalAmount = 0;
        this.totalCharge = 0;
        for (let name in this.models) {
          const fValue = parseFloat(this.models[name] || 0);
          this.totalAmount += fValue;
          const extraHint = document.querySelector(`#hint_Card_${name}`);
          if (extraHint) {
            const chargeSplit = extraHint.innerHTML.split(":");
            const charge = parseFloat(
              chargeSplit[chargeSplit.length - 1]
                .split("%")[0]
                .replace(",", "."),
            );
            this.totalCharge += (fValue * charge) / 100;
          }
        }
      },

      pending() {
        // Update remainder and towitRemainder
        this.Remainder = 0;
        const pendTowit = totalAmount - this.totalAmount;
        this.remainder = pendTowit - this.towit;
        if (pendTowit > 0) {
          this.towitRemainder = pendTowit;
          if (this.remainder > 0) {
            this.Remainder = this.remainder;
          }
        } else {
          this.towitRemainder = 0;
        }
      },

      update() {
        this.total();
        this.pending();
        this.totalValue =
          parseFloat(this.totalAmount) +
          parseFloat(this.totalCharge) +
          parseFloat(this.towit || 0);
      },

      setValue(name) {
        if (this.models[name] != "" && this.models[name] != 0) return;
        this.models[name] = this.Remainder;
      },

      setTowitValue() {
        this.towit = this.towitRemainder;
      },
    };
  });
});

// let payment_inputs, total, submit;
// let payment, extra_charge;
// let total_value, diff_value, extra_value;
//
// window.onload = function () {
//   const urlParams = new URLSearchParams(window.location.search);
//   var message = document.getElementById("message-note");
//   var debtAmountInput = document.getElementById("debt_debt-amount");
//   // Inputs
//   payment_inputs = Array.from(
//     document.getElementsByClassName("numberinput"),
//   ).filter((element) => !element.name.includes("week"));
//
//   // Report
//   total_value = document.getElementById("total_value");
//   diff_value = document.getElementById("diff_value");
//   extra_value = document.getElementById("extra_value");
//
//   // Charge
//   total = parseFloat(
//     document.getElementById("order_total").innerHTML.replace(",", "."),
//   );
//
//   for (var i in payment_inputs) {
//     if (urlParams.toString() != "") {
//       const paramValue = urlParams.get(payment_inputs[i].name);
//       payment_inputs[i].value = paramValue !== null ? paramValue : "0";
//     } else payment_inputs[i].onclick = selectPaymentType;
//     payment_inputs[i].oninput = updateValues;
//   }
//   submit = document.getElementById("summit_btn");
//   updateValues();
//
//   // message if the client has profile pic
//   const updateMessage = () => {
//     const inputValue = parseFloat(debtAmountInput.value);
//     if (!window.associatedAvatar && inputValue !== 0 && !isNaN(inputValue)) {
//       message.innerHTML =
//         '<strong class="text-danger">!! NOTE:</strong> For security reasons, you will now be redirected to update a photo for the client to help remember their debt :)';
//     } else message.innerHTML = "";
//   };
//   debtAmountInput.addEventListener("input", updateMessage);
//   debtAmountInput.addEventListener("click", updateMessage);
// };
// function selectPaymentType() {
//   event.srcElement.value = total;
//   for (var i in payment_inputs) {
//     if (payment_inputs[i].id != event.srcElement.id) {
//       payment_inputs[i].value = 0;
//     }
//
//     payment_inputs[i].onclick = null;
//   }
//   updateValues();
// }
// function updateValues() {
//   payment = 0;
//   extra_charge = 0;
//   for (var i in payment_inputs) {
//     let data = Number(payment_inputs[i].value);
//     if (data > 0) {
//       payment += data;
//     }
//     let extra = document.getElementById("hint_" + payment_inputs[i].id);
//     if (extra != undefined) {
//       let b = extra.innerHTML.split(":");
//       extra_charge +=
//         (Number(payment_inputs[i].value) / 100) *
//         parseFloat(b[b.length - 1].split("%")[0].replace(",", "."));
//     }
//   }
//   total_value.innerHTML = `$${(payment + extra_charge).toFixed(2)}`;
//   extra_value.innerHTML = `$${extra_charge.toFixed(2)}`;
//
//   let diff = payment - total;
//   if (diff != 0) {
//     submit.disabled = true;
//     diff_value.innerHTML = `($${diff.toFixed(2)})`;
//     if (diff < 0) {
//       diff_value.style.color = "red";
//     } else {
//       diff_value.style.color = "green";
//     }
//   } else {
//     diff_value.innerHTML = "";
//     submit.disabled = false;
//   }
// }
