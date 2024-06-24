document.addEventListener("alpine:init", () => {
    Alpine.data("maintenanceCard", () => {
        return {
            show: false,
            client_avatar: "",
            client_name: "",
            client_payment: 0,
            client_phone: "",
            notes: [],
            towit_payment: 0,

            showRepStatus(data) {
                console.log(data);

                this.client_avatar = data.client_avatar;
                this.client_name = data.client_name;
                this.client_payment = data.client_payment;
                this.client_phone = data.client_phone;

                this.notes = data.notes;
                this.towit_payment = data.towit_payment;

                this.show = true;
            },

            closeRepStatus() {
                this.show = false;
            },
        };
    });
});
