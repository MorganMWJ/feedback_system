let charts = [];


$(document).ready(function() {
  let chartType = "pie";
  let hasChartTypeChanged = false;
  let activeSessionID = localStorage.getItem("activeSessionID");

  function updatePage(){
    let lectureID = $('#lectureID').attr("value");
    let sessionPage = $('#session_page').attr('value');
    let endpoint = ''
    if(sessionPage == undefined){
      endpoint = '/lecture/123/sessions/v2/'.replace('123', lectureID);
    }
    else{
      endpoint = ('/lecture/123/sessions/v2/?page='+sessionPage).replace('123', lectureID);
    }
    $.ajax({
      url: endpoint,
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

      if(sessionPage != undefined){
        endpoint = "/api/session/123/feedback/".replace('123', activeSessionID);
        $.ajax({
          url: endpoint,
          method: "GET",
          datatype: 'json',
          success: function(responseData){
            console.log(responseData);
            for(var i=0; i<responseData.feedback_summary.length; i++){
              if(typeof charts[i] === 'undefined'){
                let chart = new Chart(document.getElementById("pie-chart-" + (i+1).toString()), {
                  type: chartType,
                  data: {
                    labels: responseData.feedback_summary[i].labels,
                    datasets: [{
                      label: "No. Responses",
                      backgroundColor: responseData.feedback_summary[i].colours,
                      data: responseData.feedback_summary[i].data
                    }]
                  },
                  options: {
                    title: {
                      display: true,
                      text: responseData.feedback_summary[i].title
                    }
                  }
                });
                charts.push(chart);
              }
              else{
                charts[i].data.labels = responseData.feedback_summary[i].labels;
                for(var c=0; c<charts[i].data.datasets[0].data.length; c++){
                  charts[i].data.datasets[0].data[c] = responseData.feedback_summary[i].data[c];
                }
                charts[i].data.datasets.backgroundColor = responseData.feedback_summary[i].colours;
                charts[i].options.title.text = responseData.feedback_summary[i].title;
                charts[i].update();
              }
            }
          }
        });
      }
  }
  setInterval(updatePage, 1000);
  updatePage();

  function addRowClickFunctionality(){
    $('#session_table tbody tr').click(function(){
      $('tr').removeClass("bg-info");
      $(this).addClass("bg-info");
      activeSessionID = $(this).attr('id');
    });
  }

  $('select').on('change', function() {
    chartType = this.value;
    while (charts.length) {
      charts.pop().destroy();
    }
  });

});
