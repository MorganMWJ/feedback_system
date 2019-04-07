


$(document).ready(function() {
  //save the panels user has open
  function savePanels() {
    var visiblePanels = [];
    $(".remember_visibility").each(function(index) {
      if ($(this).is(':visible')) {
        visiblePanels.push("#" + $(this).attr('id'));
      }
    });
    localStorage.setItem("visiblePanelList", JSON.stringify(visiblePanels));
  }

  //hide the panels the user previously had hidden
  var visiblePanels = JSON.parse(localStorage.getItem("visiblePanelList"));
  if (visiblePanels != null && visiblePanels != undefined) {
    for (i = 0; i < visiblePanels.length; i++) {
      $(visiblePanels[i]).removeClass("hidden_panel");
    }
  }

  $("#sessionCheck").change(function() {
    if(this.checked) {
      $("#sessionDiv").show("fast");
    }
    else{
      $("#sessionDiv").hide("fast");
    }
    savePanels();
  });

  $("#questionCheck").change(function() {
    if(this.checked) {
      $("#questionDiv").show("fast");
    }
    else{
      $("#questionDiv").hide("fast");
    }
    savePanels();
  });


  let activeSessionID = $('.bg-info').attr('id');
  function updatePage(){
    // update sessions
    let lectureID = $('#lectureID').attr("value");
    let sessionPage = $('#session_page').attr('value');
    let urlStr = ("/lecture/123/sessions/v1/?page="+sessionPage).replace('123', lectureID);
    $.ajax({
      url: urlStr,
      method: "GET",
      success: function(responseData){
          console.log(responseData);
          $('#sessionDiv').empty();
          $('#sessionDiv').html(responseData);
          // highlight active session
          $('tr').removeClass("bg-info");
          $('#'+activeSessionID.toString()).addClass('bg-info');
          addRowClickFunctionality();
          displaySessionActions();
        }
      });

    if(activeSessionID!=undefined){
      // update questions
      urlStr = "/session/123/questions/".replace('123', activeSessionID);
      $.ajax({
        url: urlStr,
        method: "GET",
        success: function(responseData){
            console.log(responseData);
            $('#questionDiv').empty();
            $('#questionDiv').html(responseData);
          }
        });
    }
  }
  setInterval(updatePage, 1000000);
  // addRowClickFunctionality();
  // displaySessionActions();
  updatePage();

  function displaySessionActions(){
    if(activeSessionID!=undefined){
      var $options = $("#" + activeSessionID + " .options").clone();
      $('#actionsPanel').html($options);
    }
  }

  function addRowClickFunctionality(){
    $('#session_table tbody tr').click(function(){
      $('tr').removeClass("bg-info");
      $(this).addClass("bg-info");
      activeSessionID = $(this).attr('id');
      displaySessionActions();
      updatePage();
    });
  }

  // $('#newSessionBtn').click(function(){
  //   $(this).removeAttr("href");
  // });


});
