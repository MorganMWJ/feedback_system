let activeSessionID = -1
let charts = [];

$(document).ready(function() {
  $('#session_table tbody tr').click(function(){
    $('tr').removeClass("table-active");
    $(this).addClass("table-active");
    activeSessionID = $(this).attr('id');
  });

  function updatePage(){
    let lectureID = $('#lectureID').attr("value");
    let endpoint = '/api/lecture/123/sessions/'.replace('123', lectureID);
    $.ajax({
      url: endpoint,
      method: "GET",
      dataytype: 'json',
      success: function(responseData){
        console.log(responseData);
        var html = "";
        $("#session_table tbody").empty();
        $.each(responseData, function(i, session){
          html = html + "<tr id=" + session.id.toString() + " class='session_row ";
          if(activeSessionID==session.id || i==responseData.length-1){
            html = html + "table-active'>"
            activeSessionID = session.id;
          }
          html = html + "<th>" + (i+1).toString() + "</th>";
          html = html + "<td>" + session.code + "</td>";
          html = html + "<td>" + session.start_time + "</td>";
          html = session.is_running ? html + "<td>" + "Session Running" + "</td>" : html + "<td>" + session.end_time + "</td>";
          html = html + "<td>" + session.runtime + "</td>";
          html = html + "</tr>"
        });
        $("#session_table tbody").html(html);
      }
    });

    let sessionID = "";
    $('.table-active').each(function() {
        sessionID = this.id;
        endpoint = "/api/session/123/feedback/".replace('123', sessionID);
        $.ajax({
          url: endpoint,
          method: "GET",
          datatype: 'json',
          success: function(responseData){
            console.log(responseData);
            for(var i=0; i<responseData.feedback_summary.length; i++){
              if(charts.length<1){
                for(var i=0; i<5; i++){
                  let chart = new Chart(document.getElementById("pie-chart-" + (i+1).toString()), {
                    type: 'pie',
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
              }
              else{
                charts[i].data.labels = responseData.feedback_summary[i].labels;
                charts[i].data.datasets.data = responseData.feedback_summary[i].data;
                charts[i].data.datasets.backgroundColor = responseData.feedback_summary[i].colours;
                charts[i].options.title.text = responseData.feedback_summary[i].title;;
                charts[i].update();
              }
            }
          }
        });
    });
  }
  setInterval(updatePage, 1000);

});
