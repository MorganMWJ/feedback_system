


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


  let activeSessionID = getActiveSession();
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
          highlightActiveSession();
          addRowClickFunctionality();
          paginationLinkSessionReset();
          displaySessionActions();
        }
      });

    if(getActiveSession()!=undefined){
      // update questions
      let questionPage = $('#question_page').attr('value');
      urlStr = ("/session/123/questions/?page="+questionPage).replace('123', getActiveSession());
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
  setInterval(updatePage, 1000);
  updatePage();

  function displaySessionActions(){
    if(getActiveSession()!=undefined){
      var $options = $("#" + getActiveSession() + " .options").clone();
      $('#actionsPanel').html($options);
    }
  }

  function highlightActiveSession(){
    if(getActiveSession()!=undefined && getActiveSession()!="undefined"){
      $('tr').removeClass("bg-info");
      $('#'+getActiveSession().toString()).addClass('bg-info');
    }
    else{
      $('#session_table tr:last').addClass('bg-info');
      setActiveSession($('#session_table tr:last').attr('id'));
    }
  }

  function addRowClickFunctionality(){
    $('#session_table tbody tr').click(function(){
      setActiveSession($(this).attr('id'));
      highlightActiveSession();
      displaySessionActions();
    });
  }

  function setActiveSession(id){
    activeSessionID = id;
    localStorage.setItem("activeSessionID", activeSessionID);
  }

  function getActiveSession(){
    try{
      activeSessionID = localStorage.getItem("activeSessionID");
    }
    catch(err){
      return undefined;
    }
    return activeSessionID;
  }

  /* Sets activeSession to undefined when navigation num_pages
     so it can be set to the last session on new page automatically */
  function paginationLinkSessionReset(){
    $('.pagination_link').each(function(){
      $(this).click(function(){
        setActiveSession(undefined);
      });
    });
  }


});
