const totalAmount = window.totalAmount;

const towitInput = document.querySelector('.numberinput[x-ref="towit_payment"]')

const paymentInputs = Array.from(
  document.querySelectorAll(".numberinput"),
).filter((element) => {
  if (element.name.includes("week")) {
    return false;
  }

  if (element.getAttribute('x-ref') == 'towit_payment') {
    return false;
  }

  return true;
});

paymentInputs.forEach((e) => {
  const name = e.getAttribute("name");
  e.setAttribute("x-model", `models['${name}']`);
  // e.setAttribute("type", "text");
  // e.setAttribute("x-mask:dynamic", "$money($input, '.', '')");
});

if (towitInput) towitInput.setAttribute('x-model', 'towit')

document.addEventListener("alpine:init", () => {
  Alpine.data("payment", () => {
    return {
      models: {},
      towit: 0,
      pending: 0,

      init() {
        if (towitInput) this.towit = towitInput.value;
        paymentInputs.forEach((e) => {
          const name = e.getAttribute("name");
          this.models[name] = e.value;
        });

        this.$watch('models', () => {
          this.towit = this.pending()
        })
      },

      total() {
        let total = 0;
        for (let name in this.models) {
          total += parseFloat(this.models[name]) || 0;
        }
        return total;
      },

      pending() {
        const pend = totalAmount - this.total();
        if (pend < 0) {
          return 0;
        }
        return pend;
      },
    };
  });
});
