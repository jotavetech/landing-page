/* Jotave Tech — comportamentos do site (sem dependências). */
(function () {
  "use strict";

  function save(lang) {
    try { localStorage.setItem("jt-lang", lang); } catch (e) { /* armazenamento indisponível */ }
  }

  // Idioma: a página atual registra o idioma em uso; o seletor registra a nova escolha.
  var current = document.documentElement.lang.toLowerCase() === "pt-br" ? "pt-br" : "en";
  save(current);
  document.querySelectorAll("[data-lang]").forEach(function (a) {
    a.addEventListener("click", function () { save(a.getAttribute("data-lang")); });
  });

  // Ano atual no aviso de direitos autorais.
  var year = String(new Date().getFullYear());
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = year; });

  // Menu do celular: fecha com Esc ou ao tocar fora.
  var menu = document.querySelector("details.menu");
  if (menu) {
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && menu.open) { menu.open = false; menu.querySelector("summary").focus(); }
    });
    document.addEventListener("click", function (e) {
      if (menu.open && !menu.contains(e.target)) menu.open = false;
    });
  }

  // Formulário de contato com serviço externo (FormSubmit): envia sem sair da página.
  var form = document.querySelector("[data-contact-form]");
  if (form && form.getAttribute("action") && window.fetch) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var status = form.querySelector("[data-form-status]");
      var button = form.querySelector("[type=submit]");
      var to = form.getAttribute("data-to");
      button.disabled = true;
      status.textContent = form.getAttribute("data-sending");
      fetch(form.getAttribute("action"), {
        method: "POST",
        headers: { "Accept": "application/json" },
        body: new FormData(form)
      }).then(function (r) {
        return r.json().then(function (data) {
          if (!r.ok || String(data.success) !== "true") throw new Error(data.message || "envio falhou");
        });
      }).then(function () {
        form.reset();
        // Mantém o cartão e o título; troca os campos pela mensagem de agradecimento.
        Array.prototype.forEach.call(form.children, function (el) {
          if (el !== status && el.id !== "h-form") el.hidden = true;
        });
        status.textContent = form.getAttribute("data-sent");
        status.focus();
      }).catch(function () {
        button.disabled = false;
        status.textContent = form.getAttribute("data-error").replace("{email}", to);
      });
    });
  }

  // Formulário de contato: sem serviço externo configurado, abre o e-mail do visitante.
  if (form && !form.getAttribute("action")) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var to = form.getAttribute("data-to");
      var status = form.querySelector("[data-form-status]");
      if (!to) return; // o marcador de configuração já está visível
      var labels = JSON.parse(form.getAttribute("data-labels"));
      var f = form.elements;
      var body = [
        labels.name + ": " + f.nome.value,
        labels.email + ": " + f.email.value,
        f.telefone.value ? labels.phone + ": " + f.telefone.value : "",
        "",
        f.mensagem.value
      ].filter(function (line, i) { return line !== "" || i === 3; }).join("\n");
      var href = "mailto:" + to +
        "?subject=" + encodeURIComponent(f.assunto.value + " — " + f.nome.value) +
        "&body=" + encodeURIComponent(body);
      window.location.href = href;
      if (status) status.textContent = form.getAttribute("data-opening").replace("{email}", to);
    });
  }
})();
