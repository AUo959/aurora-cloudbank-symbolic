// Tailwind v4 moved its PostCSS plugin out of the `tailwindcss` package and
// into `@tailwindcss/postcss`. Naming `tailwindcss` here failed the build with
// "It looks like you're trying to use `tailwindcss` directly as a PostCSS
// plugin". The v4 bump arrived via dependabot; nothing in CI built the
// frontend, so the breakage stayed invisible until someone ran the build by hand.
export default {
  plugins: {
    '@tailwindcss/postcss': {},
    autoprefixer: {},
  },
};
