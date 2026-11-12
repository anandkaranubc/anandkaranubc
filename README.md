<picture>
  <source media="(max-width: 600px) and (prefers-color-scheme: dark)" srcset="assets/hero-phone-dark.svg">
  <source media="(max-width: 600px)" srcset="assets/hero-phone-light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/hero-light.svg">
  <img src="assets/hero.svg" width="100%" alt="A pixel portrait of Karan Anand beside his name in a pixel typeface, two lines reading 'numerical kernels for stdlib. tools that get people into open source.', and a tilted passport-style stamp: 'merged. 580 pull requests into stdlib, dec 2024 to date'.">
</picture>

<p><a href="https://gitintogsoc.me/start/"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/plate-git-into-gsoc-dark.svg"><source media="(prefers-color-scheme: light)" srcset="assets/plate-git-into-gsoc-light.svg"><img src="assets/plate-git-into-gsoc.svg" width="100%" alt="The top of gitintogsoc.me in a pixel frame: the headline 'where would you fit?' in the same pixel typeface, and a paragraph explaining that the four questions run in your browser."></picture></a></p>

**git into gsoc** asks four questions and names the Google Summer of Code organizations that fit, with the evidence: the official list, each ideas page, and whether a repository has merged newcomers' pull requests lately. In the browser, in the terminal, or from your AI assistant. [Site](https://gitintogsoc.me/start/), [code](https://github.com/anandkaranubc/git-into-gsoc).

<p><a href="https://anandkaranubc.github.io/gitgoblin/"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/plate-gitgoblin-dark.svg"><source media="(prefers-color-scheme: light)" srcset="assets/plate-gitgoblin-light.svg"><img src="assets/plate-gitgoblin.svg" width="49.4%" align="top" alt="The gitgoblin website in a pixel frame: the headline 'digs up forgotten work. ships it.' beside the edge of a terminal; the goblin peeks over the top of the frame."></picture></a> <a href="https://longhand-sand.vercel.app"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/plate-longhand-dark.svg"><source media="(prefers-color-scheme: light)" srcset="assets/plate-longhand-light.svg"><img src="assets/plate-longhand.svg" width="49.4%" align="top" alt="The Longhand website in a pixel frame: 'Practise MATH 100 on paper. Check it here.' with two buttons, Start practising and Try a mock midterm."></picture></a></p>

**gitgoblin** reads a repository the way a careful new maintainer would and finds the work it needs: unclaimed issues, CI about to break, docs that contradict the code. Its agent runs the project's own tests and gets an independent review before you decide whether to open the pull request. [Site](https://anandkaranubc.github.io/gitgoblin/), [code](https://github.com/anandkaranubc/gitgoblin). **longhand** sets first-year calculus in course order, by the test each topic comes before, with mock papers laid out like the real ones and the reasoning written out. [Site](https://longhand-sand.vercel.app).

The stamp is [stdlib](https://github.com/stdlib-js/stdlib), the standard library for JavaScript and Node.js: numerical kernels in C and JavaScript since December 2024, from single-precision trigonometry to the Jacobi elliptic functions, including a Google Summer of Code 2025 project on special mathematical functions. The change I would show first is [#15676](https://github.com/stdlib-js/stdlib/pull/15676), two parentheses: `1.0 / STDLIB_CONSTANT_FLOAT64_NAN` used to expand to `1.0 / 0.0/0.0`, which is `inf`.

<details>
<summary>Four more</summary>

- [#6511](https://github.com/stdlib-js/stdlib/pull/6511) `hypotf(±∞, NaN)` now returns +∞, as IEEE 754-2019 requires.
- [#6142](https://github.com/stdlib-js/stdlib/pull/6142) and [#7806](https://github.com/stdlib-js/stdlib/pull/7806) `rempio2f` and `kernel-sincosf`: reducing a float32 argument modulo π/2, and the sine and cosine kernels that rest on it.
- [#6965](https://github.com/stdlib-js/stdlib/pull/6965) `ellipj` in C: the Jacobi elliptic functions.
- [#15576](https://github.com/stdlib-js/stdlib/pull/15576) `truncated-normal/pdf` now normalizes before squaring, so extreme inputs no longer overflow or underflow.

</details>
