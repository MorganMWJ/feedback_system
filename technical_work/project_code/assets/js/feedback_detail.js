let charts = [];


$(document).ready(function() {
  let chartType = "pie";
  let feedbackType = "all";
  let activeSessionID = localStorage.getItem("activeSessionID");

  function addRowClickFunctionality(){
    $('#session_table tbody tr').click(function(){
      $('tr').removeClass("bg-info");
      $(this).addClass("bg-info");
      activeSessionID = $(this).attr('id');
      updatePage();//remove
    });
  }
  addRowClickFunctionality();

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
        endpoint = "/api/feedbackdata/";
        $.ajax({
          url: endpoint,
          method: "GET",
          data: {session: activeSessionID, feedback_request: feedbackType},
          error: function(response){

          },
          success: function(responseData){
            console.log(responseData);
            const entries = Object.values(responseData);
            for(var i=0; i<entries.length; i++){
              if(typeof charts[i] === 'undefined'){
                let chart = new Chart(document.getElementById("pie-chart-" + (i+1).toString()), {
                  type: chartType,
                  data: {
                    labels: entries[i].labels,
                    datasets: [{
                      label: "No. Responses",
                      backgroundColor: entries[i].colours,
                      data: entries[i].data
                    }]
                  },
                  options: {
                    title: {
                      display: true,
                      text: entries[i].title
                    }
                  }
                });
                if(chartType=='bar'){
                  chart.options.scales.yAxes[0].ticks.min = 0;
                  chart.options.scales.yAxes[0].ticks.beginAtZero = true;
                  chart.options.scales.yAxes[0].ticks.stepSize = 1;
                  chart.update();
                }
                charts.push(chart);
              }
              else{
                charts[i].data.labels = entries[i].labels;
                for(var c=0; c<charts[i].data.datasets[0].data.length; c++){
                  charts[i].data.datasets[0].data[c] = entries[i].data[c];
                }
                charts[i].data.datasets.backgroundColor = entries[i].colours;
                charts[i].options.title.text = entries[i].title;
                charts[i].update();
              }
            }
          }
        });
      }
  }
  //setInterval(updatePage, 5000);
  //updatePage();



  $('#chart_choice').on('change', function() {
    chartType = this.value;
    while (charts.length) {
      charts.pop().destroy();
    }
    updatePage() //remove
  });

  $('#feedback_choice').on('change', function() {
    feedbackType = this.value;
    updatePage() //remove
  });

});
