/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    // "./static/assets/css/tailwind.css",
    "./static/assets/**/*.js",
    "./templates/**/*.html",
  ],
  theme: {
    extend: {
      screens: {
        xs: "400px",
        xxs: "200px",
      },
      colors: {
        main: "#696cff",
        mainBG: "rgba(105, 108, 255, 0.16)",
      },
    },
  },
  plugins: [],
};
