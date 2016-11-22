(function(){
  var DAYS = [0, 99];

  /**
   * Get canteen order from DOM
   */
  function getDOMCanteenOrder() {
    var canteens = [];
    $('.canteen').each(function(key, elem) {
      var number = $(elem).data('canteennumber');
      if (canteens.indexOf(number) >= 0) {
        return false; // break
      }
      canteens.push(number);
    });
    return canteens;
  }

  /**
   * Get canteen order from local storage
   */
  function getCanteenOrder() {
    try {
      return JSON.parse(localStorage.getItem('canteen-order'));
    } catch(e) {
      return;
    }
  }

  /**
   * Save canteen order to local storage
   */
  function saveCanteenOrder(canteenOrder) {
    localStorage.setItem('canteen-order', JSON.stringify(canteenOrder));
  }

  /**
   * Move canteen
   */
  function moveCanteen(direction, canteenNumber) {
    if (typeof(localStorage) === undefined) {
      // not supported in this browser
      return;
    }

    canteenOrder = getCanteenOrder();
    if (canteenOrder === undefined) {
      canteenOrder = getDOMCanteenOrder();
    }

    canteenIndex = canteenOrder.indexOf(canteenNumber)
    otherCanteenIndex = canteenIndex + direction;

    if (otherCanteenIndex < 0 || otherCanteenIndex >= canteenOrder.length) {
      // do not move. is already at top or bottom
      return false;
    }

    // swap canteens
    canteenOrder[canteenIndex] = canteenOrder[otherCanteenIndex];
    canteenOrder[otherCanteenIndex] = canteenNumber;

    saveCanteenOrder(canteenOrder);
    restoreCanteenOrder();
  }
  window.moveCanteen = moveCanteen;

  /**
   * Restore the canteen order
   */
  function restoreCanteenOrder() {
    order = getCanteenOrder();
    if (order === undefined) {
      return;  // nothing saved yet
    }

    var canteenOrder = getCanteenOrder();
    if (canteenOrder === undefined) {
      return false;  // don't do anything
    }

    $.each(DAYS, function(key, day) {
      // Place all canteens starting by second behind its predecessor
      for (var i = 1; i < canteenOrder.length; i++) {
          var previousCanteen = $('#canteen-' + day + '-' + canteenOrder[i - 1]);
          var canteen = $('#canteen-' + day + '-' + canteenOrder[i]);
          canteen.insertAfter(previousCanteen);
      }
    });
  }

  $(function(){
    // hide move links if not supported
    if (typeof(localStorage) === undefined) {
      $('.move-link').hide();
    }

    restoreCanteenOrder();
  });
})();
