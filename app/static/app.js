const BASE_URL = 'http://localhost:5000/api';

$graph = $('.all-forklifts');

$(document).ready(function () {
  $('[data-toggle="tooltip"]').tooltip();
});

async function get_graph() {
  const resp = await axios.get(`${BASE_URL}/forklift_drivers/droplists`);
  $('.graph-content').append(`<img src="${resp.data}" class="chart"/>`);
}

$graph.on('click', get_graph);
