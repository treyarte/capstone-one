$graph = $('.all-forklifts');

async function get_graph() {
  let status = $('#chart-status').val();
  let type = $('#chart-type').val();
  const resp = await axios.post(`${BASE_URL}/api/forklift_drivers/droplists`, {
    status,
    type,
  });
  $('.graph-content').empty().append(`<img src="${resp.data}" class="chart"/>`);
}

$graph.on('click', get_graph);