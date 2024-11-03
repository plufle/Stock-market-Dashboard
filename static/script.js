var tickers = JSON.parse(localStorage.getItem("tickers")) || [];
var lastPrices = {};
var counter = 25;

function startUpdateCycle() {
  updatePrices();
  setInterval(function () {
    counter--;
    $("#counter").text(counter);
    if (counter <= 0) {
      updatePrices();
      counter = 25;
    }
  }, 1000);
}

$(document).ready(function () {
  tickers.forEach(function (t) {
    addTickerToGrid(t);
  });
  updatePrices();

  $("#add-ticker-form").submit(function (e) {
    e.preventDefault();
    var newTicker = $("#new-ticker").val().toUpperCase();
    if (!tickers.includes(newTicker)) {
      tickers.push(newTicker);
      localStorage.setItem("tickers", JSON.stringify(tickers));
      addTickerToGrid(newTicker);
    }
    $("new-ticker").val("");
    updatePrices();
  });
  $("#tickers-grid").on("click", ".remove-btn", function () {
    var tickerToRemove = $(this).data("ticker");
    tickers = tickers.filter((t) => t !== tickerToRemove);
    localStorage.setItem("tickers", JSON.stringify(tickers));
    $(`#${tickerToRemove}`).remove();
  });

  $("#tickers-grid").on("click", ".predict-btn", function () {
    var tic = $(this).data("ticker");
    predict(tic);
  });

  startUpdateCycle();
});

function addTickerToGrid(ticker) {
  $("#tickers-grid").append(
    `<tr id="${ticker}">
          <td>${ticker}</td>
          <td id="${ticker}--price"></td>
          <td id="${ticker}--pct"></td>
          <td id="${ticker}--pre"><button class="predict-btn" data-ticker="${ticker}">Predict</button></td>
          <td><button class="remove-btn" data-ticker="${ticker}">Remove</button></td>
    </tr>`
  );
}
//`<div id="${ticker}" class="stock-box"><h2>${ticker}</h2><p id="${ticker}--price"></p><p id="${ticker}--pct"></p><button class="remove-btn" data-ticker="${ticker}">Remove</button></div>`

function predict(ticker) {
  $.ajax({
    url: "/get_prediction",
    type: "POST",
    data: JSON.stringify({ ticker: ticker }),
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    beforeSend: function () {
      $(`#${ticker}--pre`).text(`Predicting...`);
    },
    success: function (data) {
      var pre = parseFloat(data.prediction.toFixed(2));
      console.log(pre);
      pre += pre * 0.04;
      $(`#${ticker}--pre`).text(`$ ${pre.toFixed(2)}`);
    },
  });
}
function updatePrices() {
  tickers.forEach(function (ticker) {
    $.ajax({
      url: "/get_stock_data",
      type: "POST",
      data: JSON.stringify({ ticker: ticker }),
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: function (data) {
        var changePercent =
          ((data.currentPrice - data.openPrice) / data.openPrice) * 100;

        $(`#${ticker}--price`).text(`$ ${data.currentPrice.toFixed(2)}`);
        $(`#${ticker}--pct`).text(`% ${changePercent.toFixed(2)}`);
      },
    });
  });
}
