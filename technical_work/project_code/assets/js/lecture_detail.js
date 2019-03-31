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


$(document).ready(function() {
  // //hide the panels the user previously had hidden
  // var visiblePanels = JSON.parse(localStorage.getItem("visiblePanelList"));
  // if (visiblePanels != null && visiblePanels != undefined) {
  //   for (i = 0; i < visiblePanels.length; i++) {
  //     $(visiblePanels[i]).removeClass("hidden_panel");
  //   }
  // }
  //
  // $("#toggleDetailBtn").click(function() {
  //   $("#detailDiv").toggle("fast");
  //   // $("#detailDiv2").toggle("fast");
  //   // $("#detailDiv3").toggle("fast");
  //   savePanels();
  // });
  //
  // $("#toggleSessionBtn").click(function() {
  //   $("#sessionDiv").toggle("fast");
  //   savePanels();
  // });
  //
  // $("#toggleQuestionBtn").click(function() {
  //   $("#questionDiv").toggle("fast");
  //   savePanels();
  // });
  //
  // $("#toggleGraphBtn").click(function() {
  //   $("#feedbackDiv").toggle("fast");
  //   savePanels();
  // });
  let activeSessionID = $('.bg-info').attr('id');

  function updatePage(){
    // update sessions
    let lectureID = $('#lectureID').attr("value");
    let urlStr = "{% url 'staff:lecture_sessions' 123 %}".replace('123', lectureID);
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
        }
      });

    // update questions
    urlStr = "{% url 'staff:session_questions' 123 %}".replace('123', activeSessionID);
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
  setInterval(updatePage, 1000);
  addRowClickFunctionality();


  function addRowClickFunctionality(){
    $('#session_table tbody tr').click(function(){
      $('tr').removeClass("bg-info");
      $(this).addClass("bg-info");
      activeSessionID = $(this).attr('id');
      updatePage();
    });
  }

});
