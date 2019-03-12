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
  //hide the panels the user previously had hidden
  var visiblePanels = JSON.parse(localStorage.getItem("visiblePanelList"));
  if (visiblePanels != null && visiblePanels != undefined) {
    for (i = 0; i < visiblePanels.length; i++) {
      $(visiblePanels[i]).removeClass("hidden_panel");
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


// for (var i = 1; i < 6; i++) {
//   var canvas = document.getElementById("canvas" + i.toString());
//   var ctx = canvas.getContext("2d");
//   ctx.font = "35px Arial";
//   ctx.fillText("JS Canvas Graph", 10, 50);
// }
