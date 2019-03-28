let activeSessionID = -1

$(document).ready(function() {
  $('#session_table tbody tr').click(function(){
    $('tr').removeClass("table-active");
    $(this).addClass("table-active");
    activeSessionID = $(this).attr('id');
  });

  function updateSessions(){
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
          }
          html = html + "<th>" + (i+1).toString() + "</th>";
          html = html + "<td>" + session.start_time + "</td>";
          html = session.is_running ? html + "<td>" + "Session Running" + "</td>" : html + "<td>" + session.end_time + "</td>";
          html = html + "<td>" + session.runtime + "</td>";
          html = html + "</tr>"
          $("#session_table tbody").append(html);
          html = "";
        });
      }
    });

    let sessionID = "";
    $('.table-active').each(function() {
        sessionID = this.id;
    });
    endpoint = "/api/session/123/feedback/".replace('123', sessionID);
    $.ajax({
      url: endpoint,
      method: "GET",
      datatype: 'json',
      success: function(responseData){
        console.log(responseData);
        //todo - build pie chart using chart.js
      }
    });
  }
  setInterval(updateSessions, 3000);


  //pie charts
  labels = [];
  colours = [];
  data = [];

  for(var i=1; i<6; i++){
    new Chart(document.getElementById("pie-chart-" + i.toString()), {
      type: 'pie',
      data: {
        labels: ["Good", "Bad", "So-So"],
        datasets: [{
          label: "No. Responses",
          backgroundColor: ["#3cba9f","#c45850", "#c4c22f"],
          data: [734,784,433]
        }]
      },
      options: {
        title: {
          display: true,
          text: 'Overall Lecture Feedback'
        }
      }
    });
  }

  new Chart(document.getElementById("pie-chart-2"), {
    type: 'pie',
    data: {
      labels: ["Very Slow", "Little Slow", "Just Right", "Little Fast", "Very Fast"],
      datasets: [{
        label: "No. Responses",
        backgroundColor: ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"],
        data: [2478,5267,734,784,433]
      }]
    },
    options: {
      title: {
        display: true,
        text: 'Lecture Delivery Speed (No. Responses)'
      }
    }
  });

  new Chart(document.getElementById("pie-chart-3"), {
    type: 'pie',
    data: {
      labels: ["Very Difficult", "Slightly Difficult", "Normal", "Slightly Easy", "Very Easy"],
      datasets: [{
        label: "No. Responses",
        backgroundColor: ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"],
        data: [2478,5267,734,784,433]
      }]
    },
    options: {
      title: {
        display: true,
        text: 'Complexity of Lecture Content (No. Responses)'
      }
    }
  });

  new Chart(document.getElementById("pie-chart-4"), {
    type: 'pie',
    data: {
      labels: ["Very Well Presented", "Well Presented", "Not Well Presented"],
      datasets: [{
        label: "No. Responses",
        backgroundColor: ["#3e95cd", "#8e5ea2","#3cba9f"],
        data: [2478,5267,734]
      }]
    },
    options: {
      title: {
        display: true,
        text: 'Predicted world population (millions) in 2050'
      }
    }
  });

  new Chart(document.getElementById("pie-chart-5"), {
    type: 'pie',
    data: {
      labels: ["Africa", "Asia", "Europe", "Latin America", "North America"],
      datasets: [{
        label: "Population (millions)",
        backgroundColor: ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"],
        data: [2478,5267,734,784,433]
      }]
    },
    options: {
      title: {
        display: true,
        text: 'Predicted world population (millions) in 2050'
      }
    }
  });

});
