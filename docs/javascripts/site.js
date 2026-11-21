/* ==========================================================================
   site.js — 站点交互
   - 按路径给 body 打上 academic / home / life 标记（CSS 据此切换视觉）
   - 邮箱反爬：字符码解码后才生成 mailto
   - 隐藏生活页的悬浮入口（含英文站链接）
   - MathJax 按需加载
   - 给未来的交互组件留一个 window.ZL 接口
   ========================================================================== */

(function () {
  "use strict";

  var MATHJAX_SRC = "https://unpkg.com/mathjax@3/es5/tex-mml-chtml.js";
  var mathjaxLoading = false;

  function isEnglish() {
    return window.location.pathname.indexOf("/en/") === 0;
  }

  function sectionName() {
    var path = window.location.pathname;
    var rest = path.slice(isEnglish() ? "/en/".length : 1);
    if (rest === "" || rest === "index.html") {
      return "home";
    }
    if (rest === "life" || rest.startsWith("life/")) {
      return "life";
    }
    return "academic";
  }

  function markSection() {
    document.body.setAttribute("data-zl", sectionName());
    document.body.setAttribute("data-zl-lang", isEnglish() ? "en" : "zh");
  }

  /* --- 邮箱：字符码解码 ------------------------------------------------ */
  function decodeCodes(codes) {
    if (!codes) {
      return "";
    }
    var chars = codes.split(",").map(function (code) {
      return String.fromCharCode(Number(code));
    });
    return chars.join("");
  }

  function decorateEmails() {
    document.querySelectorAll(".zl-email").forEach(function (el) {
      if (el.getAttribute("data-ready") === "1") {
        return;
      }
      var user = decodeCodes(el.getAttribute("data-u"));
      var domain = decodeCodes(el.getAttribute("data-d"));
      if (!user || !domain) {
        return;
      }
      var address = user + "@" + domain;
      el.textContent = "";

      var link = document.createElement("a");
      link.className = "zl-email__link";
      link.href = "mailto:" + address;
      link.textContent = address;

      var copy = document.createElement("button");
      copy.type = "button";
      copy.className = "zl-email__copy";
      copy.textContent = "复制";

      copy.addEventListener("click", function () {
        var done = function (ok) {
          copy.textContent = ok ? "已复制" : "复制失败";
          window.setTimeout(function () {
            copy.textContent = "复制";
          }, 1600);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(address).then(
            function () {
              done(true);
            },
            function () {
              done(false);
            }
          );
        } else {
          done(false);
        }
      });

      el.appendChild(link);
      el.appendChild(copy);
      el.setAttribute("data-ready", "1");
    });
  }

  /* --- 隐藏生活页入口 -------------------------------------------------- */
  function updateLifeFloat() {
    var existing = document.querySelector(".zl-life-float");
    if (sectionName() === "life") {
      if (existing) {
        existing.parentNode.removeChild(existing);
      }
      return;
    }
    if (!existing) {
      existing = document.createElement("a");
      existing.className = "zl-life-float";
      existing.textContent = "✦";
      document.body.appendChild(existing);
    }
    var english = isEnglish();
    var label = english ? "Beyond Physics" : "物理之外";
    existing.setAttribute("aria-label", label);
    existing.setAttribute("title", label);
    existing.setAttribute("href", english ? "/en/life/" : "/life/");
  }

  /* --- MathJax 按需加载 ------------------------------------------------ */
  function typesetMath() {
    var mj = window.MathJax;
    if (!mj || !mj.typesetPromise) {
      return;
    }
    if (mj.startup && mj.startup.promise) {
      mj.startup.promise.then(function () {
        mj.typesetClear();
        mj.texReset();
        mj.typesetPromise();
      });
    } else {
      mj.typesetClear();
      mj.texReset();
      mj.typesetPromise();
    }
  }

  function ensureMathJax() {
    if (window.MathJax && window.MathJax.typesetPromise) {
      return;
    }
    if (mathjaxLoading) {
      return;
    }
    mathjaxLoading = true;
    var script = document.createElement("script");
    script.src = MATHJAX_SRC;
    script.async = true;
    script.onload = function () {
      mathjaxLoading = false;
      typesetMath();
    };
    script.onerror = function () {
      mathjaxLoading = false;
    };
    document.head.appendChild(script);
  }

  function setupMath() {
    if (!document.querySelector(".arithmatex")) {
      return;
    }
    if (window.MathJax && window.MathJax.typesetPromise) {
      typesetMath();
    } else {
      ensureMathJax();
    }
  }

  /* --- 给未来交互组件的接口 -------------------------------------------- */
  window.ZL = window.ZL || {};
  window.ZL.version = "2.0";
  window.ZL.loadScript = function (src) {
    return new Promise(function (resolve, reject) {
      var existing = document.querySelector('script[src="' + src + '"]');
      if (existing) {
        resolve();
        return;
      }
      var script = document.createElement("script");
      script.src = src;
      script.async = true;
      script.onload = function () {
        resolve();
      };
      script.onerror = reject;
      document.head.appendChild(script);
    });
  };
  window.ZL.mount = function (selector, init) {
    document.querySelectorAll(selector).forEach(function (el) {
      if (el.getAttribute("data-zl-mounted") === "1") {
        return;
      }
      el.setAttribute("data-zl-mounted", "1");
      init(el);
    });
  };

  function setup() {
    markSection();
    decorateEmails();
    updateLifeFloat();
    setupMath();

    // 未来页面的挂载点：<div data-widget="xxx"></div>
    window.ZL.mount("[data-widget]", function (el) {
      el.setAttribute("data-widget-ready", "1");
    });
  }

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(setup);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setup);
  } else {
    setup();
  }
})();
