/* MathJax 3 配置（主库由 site.js 按需加载，避免每个页面都下载 1MB） */
window.MathJax = {
  tex: {
    inlineMath: [
      ["\\(", "\\)"],
    ],
    displayMath: [
      ["\\[", "\\]"],
    ],
    processEscapes: true,
    processEnvironments: true,
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex",
  },
  startup: {
    typeset: false,
  },
};
