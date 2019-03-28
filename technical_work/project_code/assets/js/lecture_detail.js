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
    $("#detailDiv").toggle("fast");
    // $("#detailDiv2").toggle("fast");
    // $("#detailDiv3").toggle("fast");
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

  // $(".session_row").click(function(event) {
  //   let pos = event.target.id
  //   $.ajax({url: `/session/${pos}/questions/`,
  //           type: "GET",
  //           dataytype: 'json',
  //           success: function(response){
  //             $("#exampleFormControl6").attr("placeholder", response.total_runtime);
  //           }}
  //   );
  // });

});


// function updateQuestions(){
//   console.log(item_num) // sanity check
//     $('.table_body').html('').load(
//         "{% url 'update_items' %}?item_num=" + item_num
//     );
// }
// setInterval(updateQuestions, 1000);


/* This code is functional AJAX example */
// function updateTime(){
//   $.ajax({url: "/lecture/3/",
//           type: "GET",
//           dataytype: 'json',
//           success: function(response){
//             $("#exampleFormControl6").attr("placeholder", response.total_runtime);
//           }});
// }
// setInterval(updateTime, 1000);
