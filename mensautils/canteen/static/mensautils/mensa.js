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
        return; // continue
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
      var canteenOrder = JSON.parse(localStorage.getItem('canteen-order'));
      if (Array.isArray(canteenOrder)) {
        return canteenOrder;
      }
      return getDOMCanteenOrder();
    } catch(e) {
      return getDOMCanteenOrder();
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
    var canteenOrder = getCanteenOrder();
    if (hiddenCanteens.indexOf(canteenNumber) >= 0 ||
        canteenOrder.indexOf(canteenNumber) < 0) {
      // already hidden or not known
      return true;
    }

    hiddenCanteens.push(canteenNumber);

    saveHiddenCanteens(hiddenCanteens);
    hideHiddenCanteens();

    // delete element from canteen order
    canteenOrder.splice(canteenOrder.indexOf(canteenNumber), 1);
    saveCanteenOrder(canteenOrder);
    hideUnnecessaryCanteenButtons(canteenOrder);

    $('#showHiddenCanteensLink').show();
  }
  window.hideCanteen = hideCanteen;

  /**
   * Show all hidden canteens again.
   */
  function showHiddenCanteens() {
    if (typeof(localStorage) === 'undefined') {
      // not supported in this browser
      return;
    }

    var hiddenCanteens = getHiddenCanteens();
    var canteenOrder = getCanteenOrder();
    $.each(hiddenCanteens, function(key, canteenNumber) {
      canteenOrder.push(canteenNumber);
    });
    saveCanteenOrder(canteenOrder);
    saveHiddenCanteens([]);
    restoreCanteenOrder();
    $('.canteen').show();
    $('#showHiddenCanteensLink').hide();
  }
  window.showHiddenCanteens = showHiddenCanteens;

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

    // Place all canteens starting by second behind its predecessor
    $.each(DAYS, function(index, day) {
      for (var i = 1; i < canteenOrder.length; i++) {
        var previousCanteen = $('#canteen-' + day + '-' + canteenOrder[i - 1]);
        var canteen = $('#canteen-' + day + '-' + canteenOrder[i]);
        canteen.insertAfter(previousCanteen);
      }
    });

    hideUnnecessaryCanteenButtons(canteenOrder);
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
    if (hiddenCanteens.length === 0) {
      $('#showHiddenCanteensLink').hide();
    }
    $.each(hiddenCanteens, function(key, canteenNumber) {
      $('#canteen-' + canteenNumber).hide();
    });
  }

  /**
   * check integrity of local storage. Purge it if not given.
   */
  function integrityCheck() {
    if (typeof(localStorage) === 'undefined') {
      // not supported in this browser
      return;
    }

    var availableCanteens = getDOMCanteenOrder();
    var canteenOrder = getCanteenOrder();
    var hiddenCanteens = getHiddenCanteens();
    $.each(availableCanteens, function(key, canteenNumber) {
      if (canteenOrder.indexOf(canteenNumber) < 0 &&
          hiddenCanteens.indexOf(canteenNumber) < 0) {
        // check failed, add canteen
        canteenOrder.push(canteenNumber)
      }
    });
    // make sure that no canteen is in list of orders which does not exist
    $.each(canteenOrder, function(index, canteenNumber) {
      if (availableCanteens.indexOf(canteenNumber) < 0) {
        canteenOrder.splice(index, 1);
      }
    });

    saveCanteenOrder(canteenOrder);
  }

  $(function(){
    // hide move links if not supported
    if (typeof(localStorage) === 'undefined') {
      $('.move-link').hide();
    }

    integrityCheck();
    restoreCanteenOrder();
  });
})();
