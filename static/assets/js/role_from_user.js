document.addEventListener("alpine:init", () => {
    Alpine.data("role", () => ({
        user: window.user_id,
        role_name: "",
        error: "",
        fail: false,
        loading: false,

        async executeCreateNewRole() {
            if (this.role_name == "") {
                this.error = "Please, insert a role name";
                this.$refs.roleName.focus();
                return;
            }

            const url = window.newRoleUrl.replace("role_name", this.role_name);
            const res = await fetch(url);

            if (res.status != 200 && res.status != 400) {
                console.log(res);
                this.fail = true;
                return -1;
            }

            const data = await res.json();
            if (res.status == 400) {
                this.error = data.error;
                return -1;
            }

            return data.role_id;
        },

        async createNewRole() {
            this.error = "";
            this.fail = false;
            this.loading = true;

            const id = await this.executeCreateNewRole();
            this.loading = false;

            if (id != -1) {
                window.location.href = window.RoleUrl.replace("role_id", id);
            }
        },
    }));
});
