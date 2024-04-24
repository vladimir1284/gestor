const totalAmount = window.totalAmount;

const paymentInputs = Array.from(
    document.querySelectorAll(".numberinput"),
).filter((element) => !element.name.includes("week"));

paymentInputs.forEach((e) => {
    const name = e.getAttribute("name");
    e.setAttribute("x-model", `models['${name}']`);
    // e.setAttribute("type", "text");
    // e.setAttribute("x-mask:dynamic", "$money($input, '.', '')");
});

document.addEventListener("alpine:init", () => {
    Alpine.data("payment", () => {
        return {
            models: {},
            pending: 0,

            init() {
                paymentInputs.forEach((e) => {
                    const name = e.getAttribute("name");
                    this.models[name] = e.value;
                });
            },

            total() {
                let total = 0;
                for (let name in this.models) {
                    total += parseFloat(this.models[name]) || 0;
                }
                return total;
            },
        };
    });
});
