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
   * Get hidden canteens.
   */
  function getHiddenCanteens() {
    try {
      var hiddenCanteens = JSON.parse(localStorage.getItem('hidden-canteens'));
      if (Array.isArray(hiddenCanteens)) {
        return hiddenCanteens;
      }
      return [];
    } catch(e) {
      return [];
    }
  }

  /**
   * Save canteen order to local storage
   */
  function saveHiddenCanteens(hiddenCanteens) {
    localStorage.setItem('hidden-canteens', JSON.stringify(hiddenCanteens));
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
    if (typeof(localStorage) === 'undefined') {
      // not supported in this browser
      return;
    }

    var canteenOrder = getCanteenOrder();
    if (canteenOrder === undefined || canteenOrder === null) {
      canteenOrder = getDOMCanteenOrder();
    }

    var canteenIndex = canteenOrder.indexOf(canteenNumber);
    var otherCanteenIndex = canteenIndex + direction;

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
   * Hide a canteen.
   *
   * @param canteenNumber
   */
  function hideCanteen(canteenNumber) {
    if (typeof(localStorage) === 'undefined') {
      // not supported in this browser
      return;
    }

    var hiddenCanteens = getHiddenCanteens();
    if (hiddenCanteens.indexOf(canteenNumber) >= 0) {
      // already hidden
      return true;
    }

    hiddenCanteens.push(canteenNumber);
    saveHiddenCanteens(hiddenCanteens);
    hideHiddenCanteens();
  }
  window.hideCanteen = hideCanteen;

  /**
   * Restore the canteen order
   */
  function restoreCanteenOrder() {
    var order = getCanteenOrder();
    if (order === undefined) {
      return;  // nothing saved yet
    }

    var canteenOrder = getCanteenOrder();
    if (canteenOrder === undefined || canteenOrder === null) {
      hideUnnecessaryCanteenButtons(getDOMCanteenOrder());
      return false;  // don't do anything (except for hiding unnecessary buttons)
    }

    $.each(DAYS, function(key, day) {
      // Place all canteens starting by second behind its predecessor
      for (var i = 1; i < canteenOrder.length; i++) {
          var previousCanteen = $('#canteen-' + day + '-' + canteenOrder[i - 1]);
          var canteen = $('#canteen-' + day + '-' + canteenOrder[i]);
          canteen.insertAfter(previousCanteen);
      }
    });

    hideUnnecessaryCanteenButtons(getCanteenOrder());
    hideHiddenCanteens();
  }

  /**
   * Hide up button of highest and down button of lowest canteens
   */
  function hideUnnecessaryCanteenButtons(canteenOrder) {
    $('.move-link').show();
    // hide first and last up/down buttons
    var first = canteenOrder[0];
    var last = canteenOrder[canteenOrder.length - 1];
    $('.up-' + first).hide();
    $('.down-' + last).hide();
  }

  /**
   * hide hidden canteens.
   */
  function hideHiddenCanteens() {
    var hiddenCanteens = getHiddenCanteens();
    $.each(hiddenCanteens, function(key, canteenNumber) {
      $('.canteen-' + canteenNumber).hide();
    });
  }

  $(function(){
    // hide move links if not supported
    if (typeof(localStorage) === 'undefined') {
      $('.move-link').hide();
    }

    restoreCanteenOrder();
  });
})();
