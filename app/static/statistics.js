$graph = $('.all-forklifts');
// Load the Visualization API and the corechart package.
google.charts.load('current', { packages: ['corechart'] });

// Set a callback to run when the Google Visualization API is loaded.
google.charts.setOnLoadCallback(drawChart);

// Callback that creates and populates a data table,
// instantiates the pie chart, passes in the data and
// draws it.
async function drawChart() {
  let status = $('#chart-status').val();
  let type = $('#chart-type').val();
  const resp = await axios.post(`${BASE_URL}/api/forklift_drivers/droplists`, {
    status,
    type,
  });

  console.log(resp.data);
  // Create the data table.
  var data = new google.visualization.DataTable();
  data.addColumn('string', 'Topping');
  data.addColumn('number', 'Slices');
  data.addRows(resp.data.data);

  // Set chart options
  var options = {
    title: `Droplist ${status}`,
    width: screen.width - 500,
    height: 300,
  };

  // Instantiate and draw our chart, passing in some options.
  let chart;
  if (type === 'bar') {
    chart = new google.visualization.BarChart(
      document.getElementById('chart_div')
    );
  } else if (type === 'pie') {
    chart = new google.visualization.PieChart(
      document.getElementById('chart_div')
    );
  }
  chart.draw(data, options);
}

$('#chart-status').on('change', (e) => {
  drawChart();
});

$('#chart-type').on('change', (e) => {
  drawChart();
});

// async function get_graph() {
//   let status = $('#chart-status').val();
//   let type = $('#chart-type').val();
//   const resp = await axios.post(`${BASE_URL}/api/forklift_drivers/droplists`, {
//     status,
//     type,
//   });
//   $('.graph-content').empty().append(`<img src="${resp.data}" class="chart"/>`);
// }

// $graph.on('click', get_graph);
