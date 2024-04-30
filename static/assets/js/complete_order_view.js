const position = document.querySelector("#div_id_position select");
const reason = document.querySelector("#div_id_reason");

position.setAttribute("x-model", "position");
reason.setAttribute("x-show", "showReason");
reason.setAttribute("x-cloak", true);

document.addEventListener("alpine:init", () => {
    Alpine.data("completeOrder", () => {
        return {
            position: position.value,

            init() {
                this.$watch("position", (p) => {
                    this.payment = p != "-";
                    this.pending = p != "-" && p != "";
                });
            },

            payment() {
                return this.position != "-";
            },

            pending() {
                return this.position != "-" && this.position != "";
            },

            setFlow(f) {
                this.$refs.flow.value = f;
            },

            showReason() {
                return this.position != "" && this.position == 0;
            },

            processPay() {
                if (!this.payment) return;

                this.setFlow("processPay");
                this.$refs.form.submit();
            },

            pendingPay() {
                if (!this.pending) return;

                this.setFlow("pendingPay");
                this.$refs.form.submit();
            },
        };
    });
});
