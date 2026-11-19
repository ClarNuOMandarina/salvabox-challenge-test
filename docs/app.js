"use strict";

/* Fake demo data only. No real personal data. */
var BOXES = /*BOXES_START*/[
  {"id": "b1", "cafeteria": "Cantina Centrala", "dish": "Tocanita de legume cu orez", "diet": "vegetarian", "price": 12, "pickup": "19:00-20:00", "left": 4},
  {"id": "b2", "cafeteria": "Cantina Leu", "dish": "Curry de naut vegan", "diet": "vegan", "price": 14, "pickup": "18:30-19:30", "left": 3},
  {"id": "b3", "cafeteria": "Cantina Regie", "dish": "Snitel de pui cu cartofi", "diet": "omnivor", "price": 18, "pickup": "19:00-20:30", "left": 5},
  {"id": "b4", "cafeteria": "Cantina Centrala", "dish": "Paste cu sos de rosii", "diet": "vegetarian", "price": 10, "pickup": "18:00-19:00", "left": 2},
  {"id": "b5", "cafeteria": "Cantina Leu", "dish": "Salata vegana cu quinoa", "diet": "vegan", "price": 16, "pickup": "18:00-19:00", "left": 0},
  {"id": "b6", "cafeteria": "Cantina Regie", "dish": "Ciorba de burta", "diet": "omnivor", "price": 15, "pickup": "19:30-20:30", "left": 1},
  {"id": "b7", "cafeteria": "Cantina Centrala", "dish": "Mancare de fasole cu ciolan", "diet": "omnivor", "price": 13, "pickup": "19:00-20:00", "left": 3}
]/*BOXES_END*/;

/*
 * Pure rule: keeps price <= maxPrice and left > 0.
 * diet "oricare" keeps all; "vegetarian" keeps vegetarian AND vegan;
 * "vegan" keeps vegan only. Returns a new array sorted by price ascending.
 * Does not touch the DOM.
 */
function filterBoxes(boxes, maxPrice, diet) {
  var limit = Number(maxPrice);
  var out = [];
  for (var i = 0; i < boxes.length; i++) {
    var b = boxes[i];
    if (b.left <= 0) { continue; }
    if (b.price > limit) { continue; }
    var dietOk = false;
    if (diet === "oricare") {
      dietOk = true;
    } else if (diet === "vegetarian") {
      dietOk = (b.diet === "vegetarian" || b.diet === "vegan");
    } else if (diet === "vegan") {
      dietOk = (b.diet === "vegan");
    }
    if (dietOk) { out.push(b); }
  }
  out.sort(function (a, b) { return a.price - b.price; });
  return out;
}

/* Diet label in Romanian for display. */
function dietLabel(diet) {
  if (diet === "vegan") { return "Vegan"; }
  if (diet === "vegetarian") { return "Vegetarian"; }
  return "Omnivor";
}

/* Random pickup code SB- + 4 digits. */
function makePickupCode() {
  var n = Math.floor(Math.random() * 10000);
  var s = String(n);
  while (s.length < 4) { s = "0" + s; }
  return "SB-" + s;
}

/* ----- DOM wiring (not used by tests) ----- */
if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", function () {
    var form = document.getElementById("filterForm");
    var maxPriceInput = document.getElementById("maxPrice");
    var dietSelect = document.getElementById("diet");
    var results = document.getElementById("results");
    var emptyState = document.getElementById("emptyState");
    var reservation = document.getElementById("reservation");

    function render() {
      var list = filterBoxes(BOXES, maxPriceInput.value, dietSelect.value);
      results.innerHTML = "";
      if (list.length === 0) {
        emptyState.hidden = false;
        return;
      }
      emptyState.hidden = true;
      for (var i = 0; i < list.length; i++) {
        results.appendChild(renderCard(list[i]));
      }
    }

    function renderCard(box) {
      var li = document.createElement("li");
      li.className = "box-card";

      var dish = document.createElement("h2");
      dish.className = "box-dish";
      dish.textContent = box.dish;
      li.appendChild(dish);

      var meta = document.createElement("p");
      meta.className = "box-meta";
      meta.textContent = box.cafeteria + " \u00b7 " + dietLabel(box.diet);
      li.appendChild(meta);

      var info = document.createElement("p");
      info.className = "box-info";
      info.textContent = box.price + " RON \u00b7 Ridicare " + box.pickup + " \u00b7 " + box.left + " ramase";
      li.appendChild(info);

      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "btn btn-reserve";
      btn.textContent = "Rezerva";
      btn.addEventListener("click", function () { reserve(box); });
      li.appendChild(btn);

      return li;
    }

    function reserve(box) {
      if (box.left <= 0) { return; }
      box.left = box.left - 1;
      var code = makePickupCode();
      reservation.hidden = false;
      reservation.innerHTML = "";

      var h = document.createElement("h2");
      h.textContent = "Rezervare confirmata";
      reservation.appendChild(h);

      var p1 = document.createElement("p");
      p1.className = "res-code";
      p1.textContent = "Cod de ridicare: " + code;
      reservation.appendChild(p1);

      var p2 = document.createElement("p");
      p2.textContent = box.dish + " \u00b7 " + box.cafeteria + " \u00b7 Ridicare " + box.pickup;
      reservation.appendChild(p2);

      render();
    }

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      render();
    });

    render();
  });
}

/* Export for any non-browser consumer (ignored in the browser). */
if (typeof module !== "undefined" && module.exports) {
  module.exports = { filterBoxes: filterBoxes, BOXES: BOXES };
}
