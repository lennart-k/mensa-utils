(function(){
  var DAYS = [0, 99];
  var authenticated = !!parseInt($('#auth').html());

  // Source of getCookie: https://docs.djangoproject.com/en/dev/ref/csrf/
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) == (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  /**
   * Convert each element of a list to int.
   *
   * @param list
   */
  function string_list_to_int_list(list) {
    var result = [];
    $.each(list, function(index, item) {
      result.push(parseInt(item));
    });

    return result;
  }

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
   * Send canteen order to server.
   */
  function sendCanteenOrder(canteenOrder, hiddenCanteens) {
    var csrf_token = getCookie('csrftoken');
    $.ajax({
      url: '/userconfig/save/',
      type: 'POST',
      data: {
        csrfmiddlewaretoken: csrf_token,
        canteen_order: canteenOrder.join(','),
        hidden_canteens: hiddenCanteens.join(',')
      }
    });
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

    sendCanteenOrder(canteenOrder, getHiddenCanteens());
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

    sendCanteenOrder(canteenOrder, hiddenCanteens);
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

    sendCanteenOrder(canteenOrder, []);
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
   * Use canteen order sent by server (if available).
   */
  function loadCanteenOrderFromServer() {
    if (!authenticated) {
      return;
    }
    var available = !!parseInt($('#userConfigAvailable').html());
    if (!available) {
      return;
    }

    var canteenOrder = $('#serverCanteenOrder').html();
    var hiddenCanteens = $('#serverHiddenCanteens').html();

    if (canteenOrder === '') {
      canteenOrder = [];
    } else {
      canteenOrder = string_list_to_int_list(canteenOrder.split(','));
    }
    if (hiddenCanteens === '') {
      hiddenCanteens = [];
    } else {
      hiddenCanteens = string_list_to_int_list(hiddenCanteens.split(','));
    }

    saveCanteenOrder(canteenOrder);
    saveHiddenCanteens(hiddenCanteens);

    // do not restore canteen order as this is triggered afterwards anyway
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
      $('.canteen-' + canteenNumber).hide();
    });
  }

  /**
   * Set heights of canteens to be equal to each other when screen
   * is wide enough.
   */
  function updateResponsiveHeights() {
    if ($(window).width() < 992) {
      // screen is too narrow, set all heights to auto
      $('.canteen').css('height', 'auto');
    } else {
      // screen is wide enough, iterate through all canteens to set height explicitly
      $.each(getDOMCanteenOrder(), function(index, canteenNumber) {
        var height = 0;
        $.each(DAYS, function(index, day) {
          var elem = $('#canteen-' + day + '-' + canteenNumber);
          var currentHeight = elem.outerHeight();
          if (currentHeight > height) {
            height = currentHeight;
          }
        });
        $('.canteen-' + canteenNumber).css('height', height);
      });
    }
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
    loadCanteenOrderFromServer();
    restoreCanteenOrder();
    updateResponsiveHeights();
    $(window).resize(updateResponsiveHeights);
  });
})();
