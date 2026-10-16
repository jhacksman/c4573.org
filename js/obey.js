"use strict";
const form = document.getElementById("run-form");
form.addEventListener("submit", (event) => {
  event.preventDefault();
  if (!form.reportValidity()) return;
  const run = document.getElementById("run-id").value;
  if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(run)) return;
  window.location.assign("https://obey-collector.c4573.org/runs/" + encodeURIComponent(run));
});
