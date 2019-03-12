//save the panels user has open
function savePanels() {
  var hiddenPanels = [];
  $(".remember_visibility").each(function(index) {
    if ($(this).is(':hidden')) {
      hiddenPanels.push("#" + $(this).attr('id'));
    }
  });
  localStorage.setItem("hiddenPanelList", JSON.stringify(hiddenPanels));
}


$(document).ready(function() {
  //hide the panels the user previously had hidden
  var hiddenPanels = JSON.parse(localStorage.getItem("hiddenPanelList"));
  if (hiddenPanels != null && hiddenPanels != undefined) {
    for (i = 0; i < hiddenPanels.length; i++) {
      $(hiddenPanels[i]).hide();
    }
  }

  $("#toggleDetailBtn").click(function() {
    $("#detailDiv1").toggle("fast");
    $("#detailDiv2").toggle("fast");
    savePanels();
  });

  $("#toggleSessionBtn").click(function() {
    $("#sessionDiv").toggle("fast");
    savePanels();
  });

  $("#toggleQuestionBtn").click(function() {
    $("#questionDiv").toggle("fast");
    savePanels();
  });

  $("#toggleGraphBtn").click(function() {
    $("#feedbackDiv").toggle("fast");
    savePanels();
  });
});
